Esta parte despliega el host1, host2, Ingress y Egress.

## Despliegue Host1, Host2, Ingress y Egress
```
kubectl apply -f run-script-configmap.yaml
kubectl apply -f multus-network.yaml
./deploy-tdx.sh
```
