Esta parte despliega el host1, host2, Ingress y Egress.

## Despliegue Host1, Host2 e Ingress
```
kubectl apply -f run-script-configmap.yaml
kubectl apply -f multus-network.yaml
kubectl apply -f ingress-tfs.yaml
```
## Despliegue Egress
```
osm ns-create --ns_name Egress_Deploy  --nsd_name Egress_NSD_2   --vim_account PoT_inicial
```
