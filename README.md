# TFM-Jorge
Se tienen 3 escenarios diferentes:
- Estático
- Dinámico
- Final
### Escenario estático
El escenario estático está compuesto por 4 switches BMv2 OPoT, 2 hosts, un controlador y un broker de Kafka. 
### Escenario dinámico
Este escenario está compuesto por x switches OPoT, y switches NOPoT, 2 hosts, un controlador y un broker de Kafka. Al ser dinámico se despliegan cuantos nodos quiera el cliente.
### Escenario final
Este escenario emula una bajada de confianza en la red. Para ello se añade un switch NOPoT entre medias para que el TTL no se cumpla.
Está compuesto por:
- IngressNode y EgressNode desplegados en TEEs empleando CoCo en Clúster1
- MiddleNodes desplegados en Clúster2
- Host1, Host2 y EvilNode en Clúster1
- InfluxDB para recoger las métricas desplegada en el Clúster OSM
- Código que evalúa la confianza de la red desde el Clúster OSM
- Controlador Teraflow desplegado en Clúster TFS
- Redespliegue de EgressNode en TEE empleando CoCo en Clúster 3
