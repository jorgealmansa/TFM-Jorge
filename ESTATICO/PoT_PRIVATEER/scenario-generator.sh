#!/bin/bash

# Number of nodes as an argument
NUM_MIDDLE_NODES=$(($1 - 2))

# Parameter generation
python3 parameters_generation/generate_pot_params.py $1

# Script executed in nodes
if [ -n "$2" ] && [ $2 = "docker" ]; then

    # Script content
    run='#!/bin/sh

    if [ $1 = "host" ]; then
        ethtool -K eth0 tx off sg off tso off
        if [ $2 = "1" ]; then
            ip route add 10.1.2.0/24 via 10.1.1.2
        else
            ip route add 10.1.1.0/24 via 10.1.2.2
        fi
    elif [ $1 = "controller" ]; then
        sudo pip3 install confluent_kafka
        parameters_generation/gen_keys.sh $2
        sudo chmod 777 keys/ca.crt
        sudo cp controller/switch.py /home/p4/tutorials/utils/p4runtime_lib/switch.py
        sudo influxd &
        sleep 10
        influx -execute "CREATE DATABASE int_telemetry_db"
        p4c-bm2-ss --p4v 16 --p4runtime-files p4/pot.p4.p4info.txt -o p4/pot.json p4/pot.p4
        sudo python3 controller/runtimev2.py --p4info p4/pot.p4.p4info.txt --bmv2-json p4/pot.json --ssl
        sleep 20
        sudo python3 controller/collector_kafka.py -c $2 &
    else
        sleep 10
        sudo sysctl -w net.ipv4.ip_forward=0
        sudo chmod 777 keys/server_$1.crt
        sudo simple_switch_grpc -i 1@eth1 -i 2@eth2 -i 3@eth0 --no-p4 --log-file logs/$1 -- --grpc-server-ssl --grpc-server-cacert keys/ca.crt --grpc-server-cert keys/server_$1.crt --grpc-server-key keys/server_$1.key --grpc-server-with-client-auth &

    fi
    tail -f /dev/null
    '

    # Script creation
    echo "$run" > docker/run.sh

    # Change script file permission
    chmod +x docker/run.sh
fi

cat <<EOF | kubectl apply -f -
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: h1-ingress-net
  namespace: scenario
spec:
  config: '{
    "cniVersion": "0.3.1",
    "type": "bridge",
    "bridge": "br-h1-i",
    "ipam": {
      "type": "static",
      "addresses": []
    }
  }'
---
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: ingress-middle1-net
  namespace: scenario
spec:
  config: '{
    "cniVersion": "0.3.1",
    "type": "bridge",
    "bridge": "br-i-m1",
    "ipam": {
      "type": "static",
      "addresses": []
    }
  }'
---
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: middle1-middle2-net
  namespace: scenario
spec:
  config: '{
    "cniVersion": "0.3.1",
    "type": "bridge",
    "bridge": "br-m1-m2",
    "ipam": {
      "type": "static",
      "addresses": []
    }
  }'
---
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: middle2-egress-net
  namespace: scenario
spec:
  config: '{
    "cniVersion": "0.3.1",
    "type": "bridge",
    "bridge": "br-m2-e",
    "ipam": {
      "type": "static",
      "addresses": []
    }
  }'
---
apiVersion: k8s.cni.cncf.io/v1
kind: NetworkAttachmentDefinition
metadata:
  name: egress-h2-net
  namespace: scenario
spec:
  config: '{
    "cniVersion": "0.3.1",
    "type": "bridge",
    "bridge": "br-e-h2",
    "ipam": {
      "type": "static",
      "addresses": []
    }
  }'
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: host1
  namespace: scenario
spec:
  replicas: 1
  selector:
    matchLabels:
      app: host1
  template:
    metadata:
      labels:
        app: host1
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
            {
              "name": "h1-ingress-net",
              "interface": "net1",
              "ips": [ "10.1.1.3/24" ],
              "gateway": "10.1.1.2"
            }
          ]
    spec:
      containers:
      - name: host1
        image: jorgealmansa/scapy:latest
        securityContext:
          capabilities:
            add: ["NET_ADMIN"]
        command:
          - /bin/sh
          - -c
          - |
            # Desactiva offloads
            ethtool -K eth0 tx off sg off tso off
            # Tu script
            /home/p4/pot/docker/run.sh host 1
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/cgtid5/PoT_PRIVATEER
          type: Directory

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: host2
  namespace: scenario
spec:
  replicas: 1
  selector:
    matchLabels:
      app: host2
  template:
    metadata:
      labels:
        app: host2
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
            {
              "name": "egress-h2-net",
              "interface": "net1",
              "ips": [ "10.1.2.3/24" ],
              "gateway": "10.1.2.2"
            }
          ]
    spec:
      containers:
      - name: host2
        image: jorgealmansa/scapy:latest
        securityContext:
          capabilities:
            add: ["NET_ADMIN"]
        command:
          - /bin/sh
          - -c
          - |
            ethtool -K eth0 tx off sg off tso off
            /home/p4/pot/docker/run.sh host 2
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/cgtid5/PoT_PRIVATEER
          type: Directory

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
              "name": "h1-ingress-net",
              "interface": "net1",
              "ips": [ "10.1.1.2/24" ]
            },
            {
              "name": "ingress-middle1-net",
              "interface": "net2",
              "ips": [ "10.0.1.3/24" ]
            }
          ]
    spec:
      containers:
      - name: ingressnode
        image: jorgealmansa/p4custom-java:latest
        securityContext:
          capabilities:
            add: ["NET_ADMIN"]
        command:
          - /bin/sh
          - -c
          - |
            # Habilitar forwarding en un "router"
            sysctl -w net.ipv4.ip_forward=1
            # Llama al script con param
            /home/p4/pot/docker/run.sh 11
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/cgtid5/PoT_PRIVATEER
          type: Directory

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: middlenode-1
  namespace: scenario
spec:
  replicas: 1
  selector:
    matchLabels:
      app: middlenode-1
  template:
    metadata:
      labels:
        app: middlenode-1
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
            {
              "name": "ingress-middle1-net",
              "interface": "net1",
              "ips": [ "10.0.1.2/24" ]
            },
            {
              "name": "middle1-middle2-net",
              "interface": "net2",
              "ips": [ "10.0.2.3/24" ]
            }
          ]
    spec:
      containers:
      - name: middlenode-1
        image: jorgealmansa/p4custom-java:latest
        securityContext:
          capabilities:
            add: ["NET_ADMIN"]
        command:
          - /bin/sh
          - -c
          - |
            sysctl -w net.ipv4.ip_forward=1
            /home/p4/pot/docker/run.sh 12
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/cgtid5/PoT_PRIVATEER
          type: Directory

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: middlenode-2
  namespace: scenario
spec:
  replicas: 1
  selector:
    matchLabels:
      app: middlenode-2
  template:
    metadata:
      labels:
        app: middlenode-2
      annotations:
        k8s.v1.cni.cncf.io/networks: |
          [
            {
              "name": "middle1-middle2-net",
              "interface": "net1",
              "ips": [ "10.0.2.2/24" ]
            },
            {
              "name": "middle2-egress-net",
              "interface": "net2",
              "ips": [ "10.0.3.3/24" ]
            }
          ]
    spec:
      containers:
      - name: middlenode-2
        image: jorgealmansa/p4custom-java:latest
        securityContext:
          capabilities:
            add: ["NET_ADMIN"]
        command:
          - /bin/sh
          - -c
          - |
            sysctl -w net.ipv4.ip_forward=1
            /home/p4/pot/docker/run.sh 13
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/cgtid5/PoT_PRIVATEER
          type: Directory

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
              "name": "middle2-egress-net",
              "interface": "net1",
              "ips": [ "10.0.3.2/24" ]
            },
            {
              "name": "egress-h2-net",
              "interface": "net2",
              "ips": [ "10.1.2.2/24" ]
            }
          ]
    spec:
      containers:
      - name: egressnode
        image: jorgealmansa/p4custom-java:latest
        securityContext:
          capabilities:
            add: ["NET_ADMIN"]
        command:
          - /bin/sh
          - -c
          - |
            sysctl -w net.ipv4.ip_forward=1
            /home/p4/pot/docker/run.sh 14
        volumeMounts:
        - mountPath: /home/p4/pot
          name: pot-volume
      volumes:
      - name: pot-volume
        hostPath:
          path: /home/cgtid5/PoT_PRIVATEER
          type: Directory


EOF


