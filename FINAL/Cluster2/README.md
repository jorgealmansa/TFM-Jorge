# DESPLIEGUE MIDDLENODES
Este escenario despliega el MiddleNode1 y MiddleNode2 del Clúster 2.
Solamente hay que aplicar los manifiestos:

```
kubectl apply -f middle_networking.yaml
kubectl apply -f multus-networks.yaml
kubectl apply -f run-script-configmap.yaml
```
