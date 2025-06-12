## DESPLIEGUE TFS
Se despliega el TeraflowSDN:
```
cd controller
source my_deploy.sh
./deploy/all.sh
```

## CONECTAR Y ENVIAR EL SERVICIO A LOS NODOS
```
./src/tests/hackfest3/setup.sh
./src/tests/hackfest3/run_test_01_bootstrap.sh
./src/tests/hackfest3/run_test_02_create_service.sh
```
## DESCONECTAR Y ELIMINAR EL SERVICIO A LOS NODOS
```
./src/tests/hackfest3/run_test_03_delete_service.sh
./src/tests/hackfest3/run_test_04_cleanup.sh 
```
