#!/usr/bin/env python3

# Alejandro Peña Fernández && Jorge Almansa Garcia-Ochoa

import subprocess
import time

def obtener_db_output():
    """
    Ejecuta el comando para obtener los datos de la base de datos mediante kubectl
    y retorna la salida como una lista de líneas.
    """
    comando = ("kubectl exec -it controller -n scenario -- "
               "influx -database 'int_telemetry_db' -execute 'SELECT * FROM int_telemetry'")
    print("Ejecutando comando para obtener datos de la base de datos:")
    print(comando)
    try:
        result = subprocess.run(comando, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print("Error al ejecutar el comando:")
            print(result.stderr)
            return None
        return result.stdout.splitlines()
    except Exception as e:
        print("Excepción al ejecutar el comando:", e)
        return None

def existe_dropped_uno(lines):
    """
    Recorre las líneas de salida y busca si en la columna 'Dropped' (tercer campo)
    aparece el valor '1'. Se asume que los datos comienzan después de la línea de separación (----).
    """
    datos_iniciados = False
    for line in lines:
        if line.startswith("----"):
            datos_iniciados = True
            continue
        if datos_iniciados:
            if not line.strip():
                continue
            campos = line.split()
            if len(campos) >= 3 and campos[2] == "1":
                return True
    return False

def ejecutar_comando_ssh(comando_remoto):
    """
    Ejecuta un comando en el servidor remoto utilizando SSH a mw@192.168.159.60.
    """
    ssh_cmd = f"ssh mw@192.168.159.60 '{comando_remoto}'"
    print(f"Ejecutando comando SSH: {ssh_cmd}")
    try:
        subprocess.run(ssh_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Error al ejecutar el comando SSH:", e)

def ejecutar_comando_ssh_ubuntu(comando_remoto):
    """
    Ejecuta un comando en la máquina remota ubuntu@192.168.159.84.
    Se encadena la ejecución de múltiples comandos:
      1. Activar el entorno virtual.
      2. Cambiar al directorio 'controller/'.
      3. Modificar la línea en hackfest3/tests/Objects.py.
      4. Ejecutar los scripts de prueba y despliegue.
    """
    ssh_cmd = f"ssh ubuntu@192.168.159.84 \"{comando_remoto}\""
    print(f"Ejecutando comando SSH en ubuntu: {ssh_cmd}")
    try:
        subprocess.run(ssh_cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print("Error al ejecutar el comando SSH en ubuntu:", e)

def main():
    # Obtener salida de la base de datos
    lineas = obtener_db_output()
    if lineas is None:
        print("No se pudieron obtener los datos de la base de datos.")
        return

    # Verificar si en la columna "Dropped" se encontró el valor '1'
    if existe_dropped_uno(lineas):
        print("Se detectó un '1' en la columna 'Dropped'. Realizando las siguientes acciones...")

        # Ejecutar comando remoto vía SSH para borrar pods
        comando_remoto = "kubectl delete pods egressnode pod-1 -n scenario"
        ejecutar_comando_ssh(comando_remoto)

        # Ejecutar comando local para levantar la instancia (osm)
        comando_ns_create = "osm ns-create --ns_name Egress_Deploy --nsd_name Egress_NSD --vim_account PoT"
        print(f"\nEjecutando comando local: {comando_ns_create}")
        subprocess.run(comando_ns_create, shell=True)

        # Espera para que se despliegue la instancia
        time.sleep(25)

        # Construir el comando sed usando el delimitador '#' y la secuencia para insertar comillas simples
        sed_command = r"sed -i '179s#.*#DEVICE_SW4_IP_ADDR          = '\''192.168.159.57'\''#' hackfest3/tests/Objects.py"
        
        # Construir la cadena completa de comandos remotos
        comando_remoto_ubuntu = (
            "source tfs/bin/activate && "
            "cd controller && "
            "./hackfest3/run_test_03_delete_service.sh && "
            "./hackfest3/run_test_04_cleanup.sh && "
            + sed_command + " && "
            "source my_deploy.sh && "
            "./deploy/all.sh && "
            "./hackfest3/setup.sh && "
            "./hackfest3/run_test_01_bootstrap.sh && "
            "./hackfest3/run_test_02_create_service.sh"
        )
        ejecutar_comando_ssh_ubuntu(comando_remoto_ubuntu)

        # (Opcional) Comando final en local
        # comando_final = ("kubectl exec -it controller -n scenario -- "
        #                  "python3 -u controller/runtimev2.py --p4info p4/pot.p4.p4info.txt "
        #                  "--bmv2-json p4/pot.json --ssl")
        # print(f"\nEjecutando comando final: {comando_final}")
        # subprocess.run(comando_final, shell=True)
    else:
        print("No se encontró ningún '1' en la columna 'Dropped'. No se ejecutaron acciones.")

if __name__ == "__main__":
    main()
