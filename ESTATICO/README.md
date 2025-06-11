# ESCENARIO ESTÁTICO
## ARQUITECTURA
![image](https://github.com/user-attachments/assets/14eff26d-f011-427d-a5df-4509b2985dc4)
## DESPLIEGUE 

En este escenario hay 3 códigos explicados en el TFM. El k8s-deployments.yaml, que es el YAML encargado de desplegar los pods, el multus-networks.yaml, que definen los diferentes enlaces entre pods y el run-script-configmap.yaml, ConfigMap de los pods.

Para desplegar este escenario:
```
kubectl apply -f multus-networks.yaml
```
```
kubectl apply -f run-script-configmap.yaml
```
```
kubectl apply -f k8s-deployments.yaml
```

También es necesario copiar la carpeta de PoT_PRIVATEER.
