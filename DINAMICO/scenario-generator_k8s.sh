#!/bin/bash
if ! kubectl get ns scenario >/dev/null 2>&1; then
  kubectl create ns scenario
fi
# Crea carpetas necesarias
mkdir -p logs
mkdir -p config
mkdir -p keys
mkdir -p k8s

# Número de nodos
NUM_MIDDLE_NODES=$(( $1 - 2 ))
NUM_NON_POT_NODES=$2

python3 parameters_generation/generate_pot_params2.py "$1" "$2"

# Solo si pasamos "k8s" como tercer argumento, generamos el YAML y levantamos contenedores
if [ -n "$3" ] && [ "$3" = "k8s" ]; then

  run='apiVersion: v1
kind: ConfigMap
metadata:
  name: pot-run-config
  namespace: scenario
data:
  run.sh: |
    #!/bin/sh

    if [ "$1" = "host" ]; then
        ethtool -K eth0 tx off sg off tso off
        if [ "$2" = "1" ]; then
            # Rutas para host1
            ip route add 10.1.2.0/24 via 10.1.1.2
        else
            # Rutas para host2
            ip route add 10.1.1.0/24 via 10.1.2.2
        fi

    elif [ $1 = "controller" ]; then
        sudo pip3 install confluent_kafka
        chmod 777 parameters_generation/gen_keys.sh
        parameters_generation/gen_keys.sh $2
        sudo chmod 777 keys/ca.crt
        sudo cp controller/switch.py /home/p4/tutorials/utils/p4runtime_lib/switch.py
        sudo influxd &
        sleep 5
        influx -execute "CREATE DATABASE int_telemetry_db"
        p4c-bm2-ss --p4v 16 --p4runtime-files p4/pot.p4.p4info.txt -o p4/pot.json p4/pot.p4
        sleep 15
        python3 -u controller/runtimev2.py --p4info p4/pot.p4.p4info.txt --bmv2-json p4/pot.json --ssl
        sleep 20
        sudo python3 controller/collector_kafka.py -c $2 &
    elif [ "$1" = "noPoT" ]; then
      sudo sysctl -w net.ipv4.ip_forward=1
        
      sudo ip route add 10.1.2.0/24 via 10.0.$(($2 + 1)).2

      if [ "$3" = "first" ]; then
        sudo ip route add 10.1.1.0/24 via 10.0.2.3
      else
        sudo ip route add 10.1.1.0/24 via 10.0."$2".4
      fi

    elif [ "$1" = "evil" ]; then
        sudo ip route add 10.1.2.0/24 via 10.11.0.100
        sudo ip route add 10.1.1.0/24 via 10.10.0.100

    else
        # Cualquier otro argumento: asumimos que es uno de tus nodos P4
        # (ingressnode, middlenode, egressnode, etc.)
        sleep 10
        sudo sysctl -w net.ipv4.ip_forward=0
        sudo chmod 777 keys/server_"$1".crt
        sudo simple_switch_grpc \
          -i 1@net1 -i 2@net2 -i 3@net3 \
          --no-p4 \
          --log-file "logs/$1" \
          -- \
            --grpc-server-ssl \
            --grpc-server-addr 0.0.0.0:9559 \
            --grpc-server-cacert keys/ca.crt \
            --grpc-server-cert keys/server_"$1".crt \
            --grpc-server-key keys/server_"$1".key \
            --grpc-server-with-client-auth &

    fi

    # Mantener el pod en ejecución
    tail -f /dev/null
  '
  echo "$run" > k8s/configmap.yaml
  kubectl apply -f k8s/configmap.yaml
  kubectl get configmap pot-run-config -n scenario -o jsonpath='{.data.run\.sh}' > k8s/run.sh
  chmod +x k8s/run.sh

echo "[3/3] Desplegando pods y redes"
cat <<EOF > k8s/k8s-compose-big.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: h1
  namespace: scenario
spec:
  replicas: 1
  selector:
    matchLabels:
      app: h1
  template:
    metadata:
      labels:
        app: h1
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
            {
              "name": "h1-net",
              "interface": "net1",
              "ips": ["10.1.1.3/24"],
              "gateway": "10.1.1.2",
              "mac": "02:42:0a:01:01:03"
            }
          ]
    spec:
      containers:
        - name: h1
          image: jorgealmansa/scapy:latest
          securityContext:
            capabilities:
              add: ["NET_ADMIN"]
          command:
            - /bin/sh
            - -c
            - |
              # Desactiva offloads en la interfaz principal
              ethtool -K eth0 tx off sg off tso off
              # Ajustar permisos y ejecutar el script
              chmod +x /home/p4/pot/k8s/run.sh
              /home/p4/pot/k8s/run.sh host 1
          volumeMounts:
            - mountPath: /home/p4/pot
              name: pot-volume
            - mountPath: /home/p4/pot/k8s/run.sh
              name: pot-run-config
              subPath: run.sh
      volumes:
        - name: pot-volume
          hostPath:
            path: /home/mw/PoT_PRIVATEER
            type: Directory
        - name: pot-run-config
          configMap:
            name: pot-run-config
            defaultMode: 0755
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ingressnode
  namespace: scenario
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ingressnode
  template:
    metadata:
      labels:
        app: ingressnode
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
            {
              "name": "h1-net",
              "interface": "net1",
              "ips": ["10.1.1.2/24"],
              "mac": "02:42:0a:01:01:02"
            },
            {
              "name": "ingress-net",
              "interface": "net2",
              "ips": ["10.0.1.3/24"],
              "mac": "02:42:0a:00:01:03"
            },
            {
              "name": "controller",
              "interface": "net3",
              "ips": ["10.0.0.11/24"],
              "mac": "02:42:0a:00:00:0b"
            }
          ]
    spec:
      containers:
        - name: ingressnode
          image: jorgealmansa/p4custom-kafka:latest
          securityContext:
            privileged: true
          command:
            - /bin/sh
            - -c
            - |
              chmod +x /home/p4/pot/k8s/run.sh
              /home/p4/pot/k8s/run.sh 11
          volumeMounts:
            - mountPath: /home/p4/pot
              name: pot-volume
            - mountPath: /home/p4/pot/k8s/run.sh
              name: pot-run-config
              subPath: run.sh
      volumes:
        - name: pot-volume
          hostPath:
            path: /home/mw/PoT_PRIVATEER
            type: Directory
        - name: pot-run-config
          configMap:
            name: pot-run-config
            defaultMode: 0755
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: egressnode
  namespace: scenario
spec:
  replicas: 1
  selector:
    matchLabels:
      app: egressnode
  template:
    metadata:
      labels:
        app: egressnode
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
            {
              "name": "zegress-net",
              "interface": "net1",
              "ips": ["10.0.$(( $NUM_MIDDLE_NODES + 1 )).2/24"],
              "mac": "02:42:0a:00:0$(( $NUM_MIDDLE_NODES + 1 )):02"
            },
            {
              "name": "zh2-net",
              "interface": "net2",
              "ips": ["10.1.2.2/24"],
              "mac": "02:42:0a:01:02:02"
            },
            {
              "name": "controller",
              "interface": "net3",
              "ips": ["10.0.0.$(( $NUM_MIDDLE_NODES + 12 ))/24"],
              "mac": "02:42:0a:00:00:$(printf '%02x' $(( $NUM_MIDDLE_NODES + 12 )))"
            }
          ]
    spec:
      containers:
        - name: egressnode
          image: jorgealmansa/p4custom-kafka:latest
          securityContext:
            privileged: true
          command:
            - /bin/sh
            - -c
            - |
              sudo chmod +x /home/p4/pot/k8s/run.sh
              sudo /home/p4/pot/k8s/run.sh $(( $NUM_MIDDLE_NODES + 12 ))
          volumeMounts:
            - mountPath: /home/p4/pot
              name: pot-volume
            - mountPath: /home/p4/pot/k8s/run.sh
              name: pot-run-config
              subPath: run.sh
      volumes:
        - name: pot-volume
          hostPath:
            path: /home/mw/PoT_PRIVATEER
            type: Directory
        - name: pot-run-config
          configMap:
            name: pot-run-config
            defaultMode: 0755
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: h2
  namespace: scenario
spec:
  replicas: 1
  selector:
    matchLabels:
      app: h2
  template:
    metadata:
      labels:
        app: h2
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
            {
              "name": "zh2-net",
              "interface": "net1",
              "ips": ["10.1.2.3/24"],
              "gateway": "10.1.2.2",
              "mac": "02:42:0a:01:02:03"
            }
          ]
    spec:
      containers:
        - name: h2
          image: jorgealmansa/scapy:latest
          securityContext:
            capabilities:
              add: ["NET_ADMIN"]
          command:
            - /bin/sh
            - -c
            - |
              ethtool -K eth0 tx off sg off tso off
              chmod +x /home/p4/pot/k8s/run.sh
              /home/p4/pot/k8s/run.sh host 2
          volumeMounts:
            - mountPath: /home/p4/pot
              name: pot-volume
            - mountPath: /home/p4/pot/k8s/run.sh
              name: pot-run-config
              subPath: run.sh
      volumes:
        - name: pot-volume
          hostPath:
            path: /home/mw/PoT_PRIVATEER
            type: Directory
        - name: pot-run-config
          configMap:
            name: pot-run-config
            defaultMode: 0755
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: controller-sa
  namespace: scenario
---
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: controller-role
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apiextensions.k8s.io"]
    resources: ["customresourcedefinitions"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["namespaces"]
    verbs: ["get", "list", "watch"]
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: controller-role-binding
  namespace: scenario
subjects:
  - kind: ServiceAccount
    name: controller-sa
    namespace: scenario
roleRef:
  kind: ClusterRole
  name: controller-role
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: controller
  namespace: scenario
spec:
  replicas: 1
  selector:
    matchLabels:
      app: controller
  template:
    metadata:
      labels:
        app: controller
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
            {
              "name": "controller",
              "interface": "net1",
              "ips": ["10.0.0.10/24"],
              "mac": "02:42:0a:00:00:0a"
            },
            {
              "name": "kafka-net",
              "interface": "net2",
              "ips": ["10.2.1.10/24"],
              "mac": "02:42:0a:02:01:0a"
            }
          ]
    spec:
      serviceAccountName: controller-sa
      containers:
        - name: controller
          image: jorgealmansa/p4custom-kafka:latest
          securityContext:
            privileged: true
          command:
            - /bin/sh
            - -c
            - |
              sudo sysctl -w net.ipv4.ip_forward=1
              sudo ip route add 192.168.49.0/24 via 10.244.0.1 dev eth0
              chmod +x /home/p4/pot/k8s/run.sh
              /home/p4/pot/k8s/run.sh controller $1
          volumeMounts:
            - mountPath: /home/p4/pot
              name: pot-volume
              readOnly: false
            - mountPath: /home/p4/pot/k8s/run.sh
              name: pot-run-config
              subPath: run.sh
              readOnly: false
        - name: operator
          image: jorgealmansa/p4custom-kafka:latest
          securityContext:
            privileged: true
          command: ["/bin/sh", "-c"]
          args:
            - |
              ip route add 10.96.0.0/12 via 169.254.1.1 dev eth0 || echo "Ruta ya configurada"
              sleep 45
              cp controller/switch.py /home/p4/tutorials/utils/p4runtime_lib/switch.py
              echo "Copia"
              kopf run --standalone controller/operator.py --namespace scenario
          volumeMounts:
            - mountPath: /home/p4/pot
              name: operator-code
              readOnly: false
      volumes:
        - name: pot-volume
          hostPath:
            path: /home/mw/PoT_PRIVATEER
            type: Directory
        - name: pot-run-config
          configMap:
            name: pot-run-config
            defaultMode: 0755
        - name: operator-code
          hostPath:
            path: /home/mw/PoT_PRIVATEER
            type: Directory


EOF


  for (( i=1; i<=$NUM_MIDDLE_NODES+$NUM_NON_POT_NODES; i++ )); do

    if [ $i -le $NUM_MIDDLE_NODES ]; then
        # Nodos middle con PoT
      if [[ $i -eq 1  && $NUM_NON_POT_NODES -gt 1 ]]; then
      # MiddleNode1 si hay mas numPots > 1
          cat <<-EOF >> k8s/k8s-compose-big.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: middlenode$i
  namespace: scenario
spec:
  replicas: 1
  selector:
    matchLabels:
      app: middlenode$i
  template:
    metadata:
      labels:
        app: middlenode$i
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
              {
              "name": "ingress-net",
              "interface": "net1",
              "ips": [ "10.0.1.2/24" ],
              "mac": "02:42:0a:00:01:02"
              },
              {
              "name": "middle1-middle$(( $NUM_MIDDLE_NODES + 1 ))-net",
              "interface": "net2",
              "ips": [ "10.0.$(( $i + 1 )).3/24" ],
              "mac": "02:42:0a:00:0$(( $i + 1 )):03"
              },
              {
              "name": "controller",
              "interface": "net3",
              "ips": [ "10.0.0.$(( $i + 11 ))/24" ],
              "mac": "02:42:0a:00:00:$(printf '%02x' $(( $i + 11 )))"
              }
          ]
    spec:
      containers:
      - name: middlenode$i
        image: jorgealmansa/p4custom-kafka:latest
        securityContext:
          privileged: true
        command:
        - /bin/sh
        - -c
        - |
            
            chmod +x /home/p4/pot/k8s/run.sh
            /home/p4/pot/k8s/run.sh $(( $i + 11 ))
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
        - mountPath: /home/p4/pot/k8s/run.sh
          name: pot-run-config
          subPath: run.sh
          
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/mw/PoT_PRIVATEER
          type: Directory
      - name: pot-run-config
        configMap:
          name: pot-run-config
          defaultMode: 0755
EOF
        
      elif [[ $i -eq 1  && $NUM_NON_POT_NODES -eq 1 ]]; then
          # MiddleNode1 si hay numPots = 1
          cat <<-EOF >> k8s/k8s-compose-big.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: middlenode$i
  namespace: scenario
spec:
  replicas: 1
  selector:
      matchLabels:
        app: middlenode$i
  template:
    metadata:
      labels:
        app: middlenode$i
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
              {
              "name": "ingress-net",
              "interface": "net1",
              "ips": [ "10.0.1.2/24" ],
              "mac": "02:42:0a:00:01:02"
              },
              {
              "name": "middle1-middle$(( $NUM_MIDDLE_NODES + 1 ))-net",
              "interface": "net2",
              "ips": [ "10.0.$(( $i + 1 )).3/24" ],
              "mac": "02:42:0a:00:0$(( $i + 1 )):03"
              },
              {
              "name": "controller",
              "interface": "net3",
              "ips": [ "10.0.0.$(( $i + 11 ))/24" ],
              "mac": "02:42:0a:00:00:$(printf '%02x' $(( $i + 11 )))"
              }
          ]
    spec:
      containers:
      - name: middlenode$i
        image: jorgealmansa/p4custom-kafka:latest
        securityContext:
          privileged: true
        command:
        - /bin/sh
        - -c
        - |
            
            chmod +x /home/p4/pot/k8s/run.sh
            /home/p4/pot/k8s/run.sh $(( $i + 11 ))
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
        - mountPath: /home/p4/pot/k8s/run.sh
          name: pot-run-config
          subPath: run.sh
          
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/mw/PoT_PRIVATEER
          type: Directory
      - name: pot-run-config
        configMap:
          name: pot-run-config
          defaultMode: 0755
EOF

      elif [[ $i -eq 1  ]]; then
          # MiddleNode1
          cat <<-EOF >> k8s/k8s-compose-big.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: middlenode$i
  namespace: scenario
spec:
  replicas: 1
  selector:
      matchLabels:
        app: middlenode$i
  template:
    metadata:
      labels:
        app: middlenode$i
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
              {
              "name": "ingress-net",
              "interface": "net1",
              "ips": [ "10.0.1.2/24" ],
              "mac": "02:42:0a:00:01:02"
              },
              {
              "name": "middle1-middle$(( $i + 1 ))-net",
              "interface": "net2",
              "ips": [ "10.0.$(( $i + 1 )).3/24" ],
              "mac": "02:42:0a:00:0$(( $i + 1 )):03"
              },
              {
              "name": "controller",
              "interface": "net3",
              "ips": [ "10.0.0.$(( $i + 11 ))/24" ],
              "mac": "02:42:0a:00:00:$(printf '%02x' $(( $i + 11 )))"
              }
          ]
    spec:
      containers:
      - name: middlenode$i
        image: jorgealmansa/p4custom-kafka:latest
        securityContext:
          privileged: true
        command:
        - /bin/sh
        - -c
        - |
            
            chmod +x /home/p4/pot/k8s/run.sh
            /home/p4/pot/k8s/run.sh $(( $i + 11 ))
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
        - mountPath: /home/p4/pot/k8s/run.sh
          name: pot-run-config
          subPath: run.sh
          
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/mw/PoT_PRIVATEER
          type: Directory
      - name: pot-run-config
        configMap:
          name: pot-run-config
          defaultMode: 0755
EOF
      elif [[ $i -eq $NUM_MIDDLE_NODES && $NUM_MIDDLE_NODES -eq 2 && $NUM_NON_POT_NODES -gt 1 ]]; then
          # Conexion nodos con PoT con los sin PoT
          cat <<-EOF >> k8s/k8s-compose-big.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: middlenode$i
  namespace: scenario
spec:
  replicas: 1
  selector:
      matchLabels:
        app: middlenode$i
  template:
    metadata:
      labels:
        app: middlenode$i
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
              {
              "name": "zegress-net",
              "interface": "net2",
              "ips": [ "10.0.$(( $i + 1 )).3/24" ],
              "mac": "02:42:0a:00:0$(( $i + 1 )):03"
              },
              {
              "name": "middle$(( $i ))-middle$(( $NUM_MIDDLE_NODES + $NUM_NON_POT_NODES ))-net",
              "interface": "net1",
              "ips": [ "10.0.$(( $NUM_MIDDLE_NODES + $NUM_NON_POT_NODES + 1 )).2/24" ],
              "mac": "02:42:0a:00:0$(( $NUM_MIDDLE_NODES + $NUM_NON_POT_NODES + 1 )):02"
              },
              {
              "name": "controller",
              "interface": "net3",
              "ips": [ "10.0.0.$(( $i + 11 ))/24" ],
              "mac": "02:42:0a:00:00:$(printf '%02x' $(( $i + 11 )))"
              }
          ]
    spec:
      containers:
      - name: middlenode$i
        image: jorgealmansa/p4custom-kafka:latest
        securityContext:
          privileged: true
        command:
        - /bin/sh
        - -c
        - |
            
            chmod +x /home/p4/pot/k8s/run.sh
            /home/p4/pot/k8s/run.sh $(( $i + 11 ))
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
        - mountPath: /home/p4/pot/k8s/run.sh
          name: pot-run-config
          subPath: run.sh
          
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/mw/PoT_PRIVATEER
          type: Directory
      - name: pot-run-config
        configMap:
          name: pot-run-config
          defaultMode: 0755
EOF

      elif [[ $i -eq $NUM_MIDDLE_NODES && $NUM_NON_POT_NODES -eq 0 ]]; then
        cat <<-EOF >> k8s/k8s-compose-big.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: middlenode$i
  namespace: scenario
spec:
  replicas: 1
  selector:
      matchLabels:
        app: middlenode$i
  template:
    metadata:
      labels:
        app: middlenode$i
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
              {
              "name": "zegress-net",
              "interface": "net2",
              "ips": [ "10.0.$(( $i + 1 )).3/24" ],
              "mac": "02:42:0a:00:0$(( $i + 1 )):03"
              },
              {
              "name": "middle$(( $i-1 ))-middle$(( $i ))-net",
              "interface": "net1",
              "ips": [ "10.0.$(( $i )).2/24" ],
              "mac": "02:42:0a:00:0$(( $i )):02"
              },
              {
              "name": "controller",
              "interface": "net3",
              "ips": [ "10.0.0.$(( $i + 11 ))/24" ],
              "mac": "02:42:0a:00:00:$(printf '%02x' $(( $i + 11 )))"
              }
          ]
    spec:
      containers:
      - name: middlenode$i
        image: jorgealmansa/p4custom-kafka:latest
        securityContext:
          privileged: true
        command:
        - /bin/sh
        - -c
        - |
            
            chmod +x /home/p4/pot/k8s/run.sh
            /home/p4/pot/k8s/run.sh $(( $i + 11 ))
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
        - mountPath: /home/p4/pot/k8s/run.sh
          name: pot-run-config
          subPath: run.sh
          
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/mw/PoT_PRIVATEER
          type: Directory
      - name: pot-run-config
        configMap:
          name: pot-run-config
          defaultMode: 0755

EOF

      elif [[ $i -eq $NUM_MIDDLE_NODES && $NUM_MIDDLE_NODES -gt 2 && $NUM_NON_POT_NODES -gt 1 ]]; then
          #Conexion nodo con PoT con egress
          cat <<-EOF >> k8s/k8s-compose-big.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: middlenode$i
  namespace: scenario
spec:
  replicas: 1
  selector:
      matchLabels:
        app: middlenode$i
  template:
    metadata:
      labels:
          app: middlenode$i
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
              {
              "name": "zegress-net",
              "interface": "net2",
              "ips": [ "10.0.$(( $i + 1 )).3/24" ],
              "mac": "02:42:0a:00:0$(( $i + 1 )):03"
              },
              {
              "name": "middle$(( $i-1 ))-middle$(( $i ))-net",
              "interface": "net1",
              "ips": [ "10.0.$(( $i )).2/24" ],
              "mac": "02:42:0a:00:0$(( $i )):02"
              },
              {
              "name": "controller",
              "interface": "net3",
              "ips": [ "10.0.0.$(( $i + 11 ))/24" ],
              "mac": "02:42:0a:00:00:$(printf '%02x' $(( $i + 11 )))"
              }
          ]
    spec:
      containers:
      - name: middlenode$i
        image: jorgealmansa/p4custom-kafka:latest
        securityContext:
          privileged: true
        command:
        - /bin/sh
        - -c
        - |
            
            chmod +x /home/p4/pot/k8s/run.sh
            /home/p4/pot/k8s/run.sh $(( $i + 11 ))
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
        - mountPath: /home/p4/pot/k8s/run.sh
          name: pot-run-config
          subPath: run.sh
          
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/mw/PoT_PRIVATEER
          type: Directory
      - name: pot-run-config
        configMap:
          name: pot-run-config
          defaultMode: 0755

EOF
      elif [[ $i -eq 2  && $NUM_MIDDLE_NODES -gt 2 && $NUM_NON_POT_NODES -gt 0 ]]; then
          #MiddleNode2 igual tienes que poner scripts
          cat <<-EOF >> k8s/k8s-compose-big.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: middlenode$i
  namespace: scenario
spec:
  replicas: 1
  selector:
      matchLabels:
        app: middlenode$i
  template:
    metadata:
      labels:
          app: middlenode$i
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
              {
              "name": "middle$(($i))-middle$(($i+1))-net",
              "interface": "net2",
              "ips": [ "10.0.$(( $i + 1 )).3/24" ],
              "mac": "02:42:0a:00:0$(( $i + 1 )):03"
              },
              {
              "name": "middle$(( $i ))-middle$(( $NUM_MIDDLE_NODES + $NUM_NON_POT_NODES ))-net",
              "interface": "net1",
              "ips": [ "10.0.$(( $NUM_MIDDLE_NODES + $NUM_NON_POT_NODES + 1 )).2/24" ],
              "mac": "02:42:0a:00:0$(( $NUM_MIDDLE_NODES + $NUM_NON_POT_NODES + 1 )):02"
              },
              {
              "name": "controller",
              "interface": "net3",
              "ips": [ "10.0.0.$(( $i + 11 ))/24" ],
              "mac": "02:42:0a:00:00:$(printf '%02x' $(( $i + 11 )))"
              }
          ]
    spec:
      containers:
      - name: middlenode$i
        image: jorgealmansa/p4custom-kafka:latest
        securityContext:
          privileged: true
        command:
        - /bin/sh
        - -c
        - |
            chmod +x /home/p4/pot/k8s/run.sh
            /home/p4/pot/k8s/run.sh $(( $i + 11 ))
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
        - mountPath: /home/p4/pot/k8s/run.sh
          name: pot-run-config
          subPath: run.sh
          
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/mw/PoT_PRIVATEER
          type: Directory
      - name: pot-run-config
        configMap:
          name: pot-run-config
          defaultMode: 0755

EOF

      elif [[ $i -eq 2  && $NUM_MIDDLE_NODES -gt 2 && $NUM_NON_POT_NODES -eq 0 ]]; then
      # MiddleNode2 igual tienes que poner script
          cat <<-EOF >> k8s/k8s-compose-big.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: middlenode$i
  namespace: scenario
spec:
  replicas: 1
  selector:
      matchLabels:
        app: middlenode$i
  template:
    metadata:
      labels:
        app: middlenode$i
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
              {
              "name": "middle$(($i))-middle$(($i+1))-net",
              "interface": "net2",
              "ips": [ "10.0.$(($i+1)).3/24" ],
              "mac": "02:42:0a:00:0$(($i+1)):03"
              },
              {
              "name": "middle$(($i-1))-middle$(($i))-net",
              "interface": "net1",
              "ips": [ "10.0.$(($i)).2/24" ],
              "mac": "02:42:0a:00:0$(($i)):02"
              },
              {
              "name": "controller",
              "interface": "net3",
              "ips": [ "10.0.0.$(( $i + 11 ))/24" ],
              "mac": "02:42:0a:00:00:$(printf '%02x' $(( $i + 11 )))"
              }
          ]
    spec:
      containers:
      - name: middlenode$i
        image: jorgealmansa/p4custom-kafka:latest
        securityContext:
          privileged: true
        command:
        - /bin/sh
        - -c
        - |
            
            chmod +x /home/p4/pot/k8s/run.sh
            /home/p4/pot/k8s/run.sh $(( $i + 11 ))
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
        - mountPath: /home/p4/pot/k8s/run.sh
          name: pot-run-config
          subPath: run.sh
          
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/mw/PoT_PRIVATEER
          type: Directory
      - name: pot-run-config
        configMap:
          name: pot-run-config
          defaultMode: 0755

EOF
      elif [[ $i -eq 2  && $NUM_NON_POT_NODES -eq 1 ]]; then
      # MiddleNode2 igual tienes que poner script
          cat <<-EOF >> k8s/k8s-compose-big.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: middlenode$i
  namespace: scenario
spec:
  replicas: 1
  selector:
      matchLabels:
        app: middlenode$i
  template:
    metadata:
      labels:
        app: middlenode$i
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
              {
              "name": "zegress-net",
              "interface": "net2",
              "ips": [ "10.0.$(($i+1)).3/24" ],
              "mac": "02:42:0a:00:0$(($i+1)):03"
              },
              {
              "name": "middle$(($i))-middle$(($i+1))-net",
              "interface": "net1",
              "ips": [ "10.0.$(($i+2)).2/24" ],
              "mac": "02:42:0a:00:0$(($i+2)):02"
              },
              {
              "name": "controller",
              "interface": "net3",
              "ips": [ "10.0.0.$(( $i + 11 ))/24" ],
              "mac": "02:42:0a:00:00:$(printf '%02x' $(( $i + 11 )))"
              }
          ]
    spec:
      containers:
      - name: middlenode$i
        image: jorgealmansa/p4custom-kafka:latest
        securityContext:
          privileged: true
        command:
        - /bin/sh
        - -c
        - |
            
            chmod +x /home/p4/pot/k8s/run.sh
            /home/p4/pot/k8s/run.sh $(( $i + 11 ))
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
        - mountPath: /home/p4/pot/k8s/run.sh
          name: pot-run-config
          subPath: run.sh
          
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/mw/PoT_PRIVATEER
          type: Directory
      - name: pot-run-config
        configMap:
          name: pot-run-config
          defaultMode: 0755

EOF
      elif [[ $i -eq $NUM_MIDDLE_NODES  && $NUM_NON_POT_NODES -eq 1 ]]; then
          # MiddleNode2 igual tienes que poner script
          cat <<-EOF >> k8s/k8s-compose-big.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: middlenode$i
  namespace: scenario
spec:
  replicas: 1
  selector:
      matchLabels:
        app: middlenode$i
  template:
    metadata:
      labels:
        app: middlenode$i
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
              {
              "name": "zegress-net",
              "interface": "net2",
              "ips": [ "10.0.$(($i+1)).3/24" ],
              "mac": "02:42:0a:00:0$(($i+1)):03"
              },
              {
              "name": "middle$(($i-1))-middle$(($i))-net",
              "interface": "net1",
              "ips": [ "10.0.$(($i)).2/24" ],
              "mac": "02:42:0a:00:0$(($i)):02"
              },
              {
              "name": "controller",
              "interface": "net3",
              "ips": [ "10.0.0.$(( $i + 11 ))/24" ],
              "mac": "02:42:0a:00:00:$(printf '%02x' $(( $i + 11 )))"
              }
          ]
    spec:
      containers:
      - name: middlenode$i
        image: jorgealmansa/p4custom-kafka:latest
        securityContext:
          privileged: true
        command:
        - /bin/sh
        - -c
        - |
            
            chmod +x /home/p4/pot/k8s/run.sh
            /home/p4/pot/k8s/run.sh $(( $i + 11 ))
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
        - mountPath: /home/p4/pot/k8s/run.sh
          name: pot-run-config
          subPath: run.sh
          
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/mw/PoT_PRIVATEER
          type: Directory
      - name: pot-run-config
        configMap:
          name: pot-run-config
          defaultMode: 0755

EOF
      else
      # Middle nodes intermedios con PoT
          cat <<-EOF >> k8s/k8s-compose-big.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: middlenode$i
  namespace: scenario
spec:
  replicas: 1
  selector:
      matchLabels:
        app: middlenode$i
  template:
    metadata:
      labels:
          app: middlenode$i
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
              {
              "name": "middle$(($i))-middle$(($i+1))-net",
              "interface": "net2",
              "ips": [ "10.0.$(($i+1)).3/24" ],
              "mac": "02:42:0a:00:0$(($i+1)):03"
              },
              {
              "name": "middle$(($i-1))-middle$(($i))-net",
              "interface": "net1",
              "ips": [ "10.0.$(($i)).2/24" ],
              "mac": "02:42:0a:00:0$(($i)):02"
              },
              {
              "name": "controller",
              "interface": "net3",
              "ips": [ "10.0.0.$(( $i + 11 ))/24" ],
              "mac": "02:42:0a:00:00:$(printf '%02x' $(( $i + 11 )))"
              }
          ]
    spec:
      containers:
      - name: middlenode$i
        image: jorgealmansa/p4custom-kafka:latest
        securityContext:
          privileged: true
        command:
        - /bin/sh
        - -c
        - |
            
            chmod +x /home/p4/pot/k8s/run.sh
            /home/p4/pot/k8s/run.sh $(( $i + 11 ))
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
        - mountPath: /home/p4/pot/k8s/run.sh
          name: pot-run-config
          subPath: run.sh
          
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/mw/PoT_PRIVATEER
          type: Directory
      - name: pot-run-config
        configMap:
          name: pot-run-config
          defaultMode: 0755

EOF
      fi
        ###############NODOS SIN POT################################   
            ## Quiero que al primer nodo se le asigne el bridge del MiddleNode1 y si, no hay mas nodo sin pot se les asigna el bridge del MiddleNode2
            # Si hay mas nodos sin PoT se le asigna el siguiente bridge del MiddleNode4
            #  Al ultimo nodo se le asignará siempre el bridge del MiddleNode2 y se le asignará el bridge del anterior
            # Para el resto de nodos se le asignaran dos bridges
	        # Middle nodes without PoT (not connected to the controller)

    elif [[ $NUM_NON_POT_NODES -ge 1 ]]; then
        # Nodos sin PoT (NUM_NON_POT_NODES)
      if [[ $NUM_NON_POT_NODES -eq 1 ]]; then
      # Solo 1 nodo sin PoT
          cat <<-EOF >> k8s/k8s-compose-big.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: middlenopot$i
  namespace: scenario
spec:
  replicas: 1
  selector:
      matchLabels:
        app: middlenopot$i
  template:
    metadata:
      labels:
          app: middlenopot$i
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
              {
              "name": "middle1-middle$(($i))-net",
              "interface": "net1",
              "ips": [ "10.0.2.4/24" ],
              "mac": "02:42:0a:00:02:04"
              },
              {
              "name": "middle2-middle$(($i))-net",
              "interface": "net2",
              "ips": [ "10.0.$(($i +1)).3/24" ],
              "mac": "02:42:0a:00:0$(($i +1)):03"
              }
          ]
    spec:
      containers:
      - name: middlenopot$i
        image: jorgealmansa/p4custom-kafka:latest
        securityContext:
          privileged: true
        command:
        - /bin/sh
        - -c
        - |
            
            chmod +x /home/p4/pot/k8s/run.sh
            /home/p4/pot/k8s/run.sh noPoT $i first
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
        - mountPath: /home/p4/pot/k8s/run.sh
          name: pot-run-config
          subPath: run.sh
            
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/mw/PoT_PRIVATEER
          type: Directory
      - name: pot-run-config
        configMap:
          name: pot-run-config
          defaultMode: 0755

EOF
      elif [[ ( $i -eq $(( $NUM_MIDDLE_NODES + 1 )) && $NUM_NON_POT_NODES -gt 1 ) ]]; then
        # Primer nodo sin PoT habiendo varios
        cat <<-EOF >> k8s/k8s-compose-big.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: middlenopot$i
  namespace: scenario
spec:
  replicas: 1
  selector:
      matchLabels:
        app: middlenopot$i
  template:
    metadata:
      labels:
          app: middlenopot$i
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
              {
              "name": "middle1-middle$(($i))-net",
              "interface": "net1",
              "ips": [ "10.0.2.4/24" ],
              "mac": "02:42:0a:00:02:04"
              },
              {
              "name": "middle$(( $i ))-middle$(( $i + 1 ))-net",
              "interface": "net2",
              "ips": [ "10.0.$(($i +1)).4/24" ],
              "mac": "02:42:0a:00:0$(($i +1)):04"
              }
          ]
    spec:
      containers:
      - name: middlenopot$i
        image: jorgealmansa/p4custom-kafka:latest
        securityContext:
          privileged: true
        command:
        - /bin/sh
        - -c
        - |
            
            chmod +x /home/p4/pot/k8s/run.sh
            /home/p4/pot/k8s/run.sh noPoT $i first
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
        - mountPath: /home/p4/pot/k8s/run.sh
          name: pot-run-config
          subPath: run.sh
            
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/mw/PoT_PRIVATEER
          type: Directory
      - name: pot-run-config
        configMap:
          name: pot-run-config
          defaultMode: 0755

EOF
      elif [ $i -eq $(( $NUM_MIDDLE_NODES + $NUM_NON_POT_NODES )) ]; then
        # Último nodo sin PoT
        cat <<-EOF >> k8s/k8s-compose-big.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: middlenopot$i
  namespace: scenario
spec:
  replicas: 1
  selector:
      matchLabels:
        app: middlenopot$i
  template:
    metadata:
      labels:
          app: middlenopot$i
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
              {
              "name": "middle2-middle$(($i))-net",
              "interface": "net1",
              "ips": [ "10.0.$(( $i + 1 )).3/24" ],
              "mac": "02:42:0a:00:0$(( $i + 1 )):03"
              },
              {
              "name": "middle$(( $i - 1))-middle$(( $i  ))-net",
              "interface": "net2",
              "ips": [ "10.0.$(($i)).2/24" ],
              "mac": "02:42:0a:00:0$(($i)):02"
              }
          ]
    spec:
      containers:
      - name: middlenopot$i
        image: jorgealmansa/p4custom-kafka:latest
        securityContext:
          privileged: true
        command:
        - /bin/sh
        - -c
        - |
            
            chmod +x /home/p4/pot/k8s/run.sh
            /home/p4/pot/k8s/run.sh noPoT $i 
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
        - mountPath: /home/p4/pot/k8s/run.sh
          name: pot-run-config
          subPath: run.sh
          
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/mw/PoT_PRIVATEER
          type: Directory
      - name: pot-run-config
        configMap:
          name: pot-run-config
          defaultMode: 0755

EOF
      else
        # Nodos sin PoT intermedios
        cat <<-EOF >> k8s/k8s-compose-big.yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: middlenopot$i
  namespace: scenario
spec:
  replicas: 1
  selector:
      matchLabels:
        app: middlenopot$i
  template:
    metadata:
      labels:
          app: middlenopot$i
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
              {
              "name": "middle$(( $i - 1 ))-middle$(( $i ))-net",
              "interface": "net1",
              "ips": [ "10.0.$(( $i )).2/24" ],
              "mac": "02:42:0a:00:0$(( $i )):02"
              },
              {
              "name": "middle$(( $i))-middle$(( $i + 1 ))-net",
              "interface": "net2",
              "ips": [ "10.0.$(( $i + 1 )).4/24" ],
              "mac": "02:42:0a:00:0$(( $i + 1 )):04"
              }
          ]
    spec:
      containers:
      - name: middlenopot$i
        image: jorgealmansa/p4custom-kafka:latest
        securityContext:
          privileged: true
        command:
        - /bin/sh
        - -c
        - |
            
            chmod +x /home/p4/pot/k8s/run.sh
            /home/p4/pot/k8s/run.sh noPoT $i 
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
        - mountPath: /home/p4/pot/k8s/run.sh
          name: pot-run-config
          subPath: run.sh
          
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/mw/PoT_PRIVATEER
          type: Directory
      - name: pot-run-config
        configMap:
          name: pot-run-config
          defaultMode: 0755

EOF
      fi
    else
      :
    fi
  done
  
cat <<EOF > k8s/networks.yaml

apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: h1-net
  namespace: scenario
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "type": "bridge",
      "bridge": "br-h1-i",
      "ipam": {
        "type": "static",
        "addresses": []
      }
    }
---
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: ingress-net
  namespace: scenario
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "type": "bridge",
      "bridge": "br-i-m1",
      "ipam": {
        "type": "static",
        "addresses": []
      }
    }
---
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: zegress-net
  namespace: scenario
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "type": "bridge",
      "bridge": "br-e",
      "ipam": {
        "type": "static",
        "addresses": []
      }
    }
---
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: zh2-net
  namespace: scenario
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "type": "bridge",
      "bridge": "br-e-h2",
      "ipam": {
        "type": "static",
        "addresses": []
      }
    }
---
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: controller
  namespace: scenario
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "type": "bridge",
      "bridge": "br-ctrl",
      "ipam": {
        "type": "static",
        "addresses": []
      }
    }
---
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: kafka-net
  namespace: scenario
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "type": "bridge",
      "bridge": "br-kafka",
      "ipam": {
        "type": "static",
        "subnet": "10.2.1.0/24",
        "rangeStart": "10.2.1.3",
        "rangeEnd": "10.2.1.254",
        "gateway": "10.2.1.1",
        "routes": [{"dst": "0.0.0.0/0"}]
      }
    }
---
EOF


  if [[ $NUM_NON_POT_NODES -gt 0 ]]; then
    cat <<-EOF >> k8s/networks.yaml
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: middle1-middle$(( $NUM_MIDDLE_NODES + 1 ))-net
  namespace: scenario
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "type": "bridge",
      "bridge": "br-m1-m$(( $NUM_MIDDLE_NODES + 1 ))",
      "ipam": {
        "type": "static",
        "addresses": []
      }
    }
---
EOF
  fi
  # PRIMER ENLACE ENTRE MIDDLE1-MIDDLE3 
  if [[ $NUM_MIDDLE_NODES -gt 2 && $NUM_NON_POT_NODES -gt 0 ]]; then
    for (( i=2; i<=$(($NUM_MIDDLE_NODES-1)); i++ ))
      do
      cat <<-EOF >> k8s/networks.yaml
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: middle$(($i))-middle$(($i+1))-net
  namespace: scenario
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "type": "bridge",
      "bridge": "br-m$(($i))-m$(($i+1))",
      "ipam": {
        "type": "static",
        "addresses": []
      }
    }
---
EOF
    done
  fi

  if [[ $NUM_NON_POT_NODES -gt 0 ]]; then
  # Redes para los nodos sin PoT
    for (( i=1; i<=$NUM_NON_POT_NODES; i++ )); do
    #SI SOLO HAY UN NODO, CREO LA RED ENTRE MIDDLE2-MIDDLE3
      if [ $NUM_NON_POT_NODES -eq 1 ]; then
        cat <<-EOF >> k8s/networks.yaml
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: middle2-middle$(( $NUM_MIDDLE_NODES + 1 ))-net
  namespace: scenario
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "type": "bridge",
      "bridge": "br-m2-m$(( $NUM_MIDDLE_NODES + 1 ))",
      "ipam": {
        "type": "static",
        "addresses": []
      }
    }
---
EOF
      #PARA EL ULTIMO NODO
      elif [ $NUM_NON_POT_NODES -eq $i ]; then
        cat <<-EOF >> k8s/networks.yaml
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: middle2-middle$(( i + $NUM_MIDDLE_NODES ))-net
  namespace: scenario
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "type": "bridge",
      "bridge": "br-m2-m$(( i + $NUM_MIDDLE_NODES ))",
      "ipam": {
        "type": "static",
        "addresses": []
      }
    }
---
EOF
      #PARA LOS NODOS DE EN MEDIO
      else
        cat <<-EOF >> k8s/networks.yaml
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: middle$(( i + $NUM_MIDDLE_NODES ))-middle$(( i + $NUM_MIDDLE_NODES + 1 ))-net
  namespace: scenario
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "type": "bridge",
      "bridge": "br-m$(( i + $NUM_MIDDLE_NODES ))-m$(( i + $NUM_MIDDLE_NODES + 1 ))",
      "ipam": {
        "type": "static",
        "addresses": []
      }
    }
---
EOF
      fi
    done
  fi

  if [[ $NUM_NON_POT_NODES -eq 0 ]]; then
    for (( i=1; i<=$(($NUM_MIDDLE_NODES-1)); i++ ))
  do
    cat <<-EOF >> k8s/networks.yaml
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: middle$(($i))-middle$(($i+1))-net
  namespace: scenario
spec:
  config: |
    {
      "cniVersion": "0.3.1",
      "type": "bridge",
      "bridge": "br-m$(($i))-m$(($i+1))",
      "ipam": {
        "type": "static",
        "addresses": []
      }
    }
---
EOF
    done
  fi

  kubectl apply -f k8s/networks.yaml
  sleep 5
  kubectl apply -f k8s/k8s-compose-big.yaml

fi
