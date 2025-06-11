import kopf
import kubernetes
import subprocess

# Prefijos de Pods a considerar "críticos"
CRITICAL_PREFIXES = ["controller", "ingressnode", "egressnode", "middlenode"]

@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):
    """
    Se invoca al arrancar el operador Kopf.
    Cargamos la configuración in-cluster (o local, si falla la in-cluster).
    """
    try:
        kubernetes.config.load_incluster_config()
        print("[OPERATOR] Configuración in-cluster de K8s cargada.")
    except Exception as e:
        print(f"[OPERATOR] No se pudo cargar config in-cluster: {e}")
        print("[OPERATOR] Intentamos cargar config local con kubeconfig.")
        kubernetes.config.load_kube_config()


@kopf.on.event('pods')
def watch_pods(event, logger, **kwargs):
    """
    Observa los eventos 'ADDED', 'MODIFIED', 'DELETED' de todos los Pods.
    Como lanzaremos Kopf con '--namespace scenario',
    solo recibiremos los eventos del namespace 'scenario'.
    """
    obj = event.get('object')
    event_type = event.get('type')  # "ADDED", "MODIFIED", "DELETED"
    
    if not obj:
        return  # A veces puede llegar vacío

    pod_name = obj['metadata'].get('name', '')
    pod_phase = obj['status'].get('phase', '')

    # Chequeamos si el nombre del Pod empieza por alguno de los prefijos críticos
    if any(pod_name.startswith(prefix) for prefix in CRITICAL_PREFIXES):
        logger.info(f"[OPERATOR] Evento={event_type} Pod={pod_name}, Phase={pod_phase}")

        if event_type == "DELETED":
            logger.info(f"[OPERATOR] Pod crítico {pod_name} eliminado. Llamamos a runtimev2.py...")
            try:
                subprocess.run([
                    "python3",
                    "/home/p4/pot/controller/runtimev2.py",
                    "--p4info", "/home/p4/pot/p4/pot.p4.p4info.txt",
                    "--bmv2-json", "/home/p4/pot/p4/pot.json",
                    "--ssl"
                ], check=True)
                logger.info(f"[OPERATOR] Reconfiguración P4 completada.")
            except subprocess.CalledProcessError as e:
                logger.error(f"[OPERATOR] Error al ejecutar runtimev2.py: {e}")
            except Exception as ex:
                logger.error(f"[OPERATOR] Excepción inesperada: {ex}")
