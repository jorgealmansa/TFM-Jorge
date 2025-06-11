### ARQUITECTURA
Se tienen dos arquitecturas para este caso.

## ARQUITECTURA SIN NODOS NOPOT
![image](https://github.com/user-attachments/assets/adf3ce5f-054d-4f88-b863-d301521e9554)

Siendo x el número de nodos PoT a desplegar

```
./scenario-generator_k8s.sh x 0 k8s
```

## ARQUITECTURA MIXTA
![image](https://github.com/user-attachments/assets/0037e2c1-ab7d-43ef-b697-667a6829ac89)

Siendo x el número de nodos PoT a desplegar e y el número de nodos sin PoT
```
./scenario-generator_k8s.sh x y k8s
```

## PRUEBA DE CONECTIVIDAD
```
kubectl exec -it host1 -n scenario -- ping 10.1.2.3
```

## MÉTRICAS EN LA INFLUXDB
```
kubectl exec -it controller -n scenario -- influx -database 'int_telemetry_db' -execute 'SELECT * FROM int_telemetry'
```
