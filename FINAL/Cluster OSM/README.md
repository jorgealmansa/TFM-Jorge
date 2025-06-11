# DESPLIEGUE

## Desplegar InfluxDB
```
cd PoT_isolate_controller
kubectl apply -f run-script-configmap.yaml
kubectl apply -f multus-networks.yaml
kubectl apply -f controller_isolate.yaml
```
## Redespliegue EgressNode en otro Clúster empleando OSM MANO

Una vez desplegados todos los nodos y que haya conectividad entre host1 y host2, se procede al redespliegue, ejecutando:
```
python redeploy.py
```
Se redespliega el nuevo Egress empleando OSM MANO y vuelve a haber conectividad entre Host1 y Host2.
