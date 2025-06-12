# MEJORAS ESCENARIO DOCKER
## Geolocalización
Se ha añadido la geolocalización al código `/controller/collector_kafka.py`
## ContainerdID
Se ha añadido el ContainerID a cada nodo en el código código `/controller/collector_kafka.py`

## Despliegue
Para desplegar el escenario es necesario ejecutar:
```
./scenario-generator_nodes.sh x y docker
```
- Siendo x el número de nodos OPoT a desplegar
- Siendo y el número de nodos NOPoT a desplegar
### Prueba de conectividad
```
docker exec -it host1 -- ping 10.1.2.3
```
### InfluxDB
```
docker exec -it controller -- influx -database 'int_telemetry_db' -execute 'SELECT * FROM int_telemetry'
```
