## PASOS A SEGUIR
En este escenario se tienen los diferentes clústeres, los pasos a seguir son:
- Desplegar la InfluxDB (Código en Clúster OSM/PoT_isolate_controller)
- Desplegar los MiddleNodes (código en Cluster2)
- Desplegar Ingress, Egress, Host1 y Host2 (código en Cluster1)
- Desde el clúster de TFS se conecta y envía las reglas OPoT a los nodos (código en Clúster TFS)
- Prueba de conectividad entre Host1 y Host2
- Se ejecuta el código del redeploy.py (en Clúster OSM)
- EgressNode desplegado en otro clúster diferente con TDX
- Prueba de conectividad entre Host1 y Host2
## ARQUITECTURA
![image](https://github.com/user-attachments/assets/804b394e-b8b5-4ab8-a1e6-974f6e01575f)

