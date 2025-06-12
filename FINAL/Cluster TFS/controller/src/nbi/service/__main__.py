# Copyright 2022-2024 ETSI SDG TeraFlowSDN (TFS) (https://tfs.etsi.org/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging, signal, sys, threading
from prometheus_client import start_http_server
from common.Constants import ServiceNameEnum
from common.Settings import (
    ENVVAR_SUFIX_SERVICE_HOST, ENVVAR_SUFIX_SERVICE_PORT_GRPC,
    get_env_var_name, get_log_level, get_metrics_port,
    wait_for_environment_variables
)
from .NbiService import NbiService
from .rest_server.RestServer import RestServer
from .rest_server.nbi_plugins.etsi_bwm import register_etsi_bwm_api
from .rest_server.nbi_plugins.ietf_hardware import register_ietf_hardware
from .rest_server.nbi_plugins.ietf_l2vpn import register_ietf_l2vpn
from .rest_server.nbi_plugins.ietf_l3vpn import register_ietf_l3vpn
from .rest_server.nbi_plugins.ietf_network import register_ietf_network
from .rest_server.nbi_plugins.ietf_network_slice import register_ietf_nss
from .rest_server.nbi_plugins.ietf_acl import register_ietf_acl
from .rest_server.nbi_plugins.qkd_app import register_qkd_app
from .rest_server.nbi_plugins.tfs_api import register_tfs_api
from .context_subscription import register_context_subscription

terminate = threading.Event()
LOGGER = None

def signal_handler(signal, frame): # pylint: disable=redefined-outer-name, unused-argument
    LOGGER.warning('Terminate signal received')
    terminate.set()

def main():
    global LOGGER # pylint: disable=global-statement

    log_level = get_log_level()
    logging.basicConfig(level=log_level)
    LOGGER = logging.getLogger(__name__)

    wait_for_environment_variables([
        get_env_var_name(ServiceNameEnum.CONTEXT, ENVVAR_SUFIX_SERVICE_HOST     ),
        get_env_var_name(ServiceNameEnum.CONTEXT, ENVVAR_SUFIX_SERVICE_PORT_GRPC),
        get_env_var_name(ServiceNameEnum.DEVICE,  ENVVAR_SUFIX_SERVICE_HOST     ),
        get_env_var_name(ServiceNameEnum.DEVICE,  ENVVAR_SUFIX_SERVICE_PORT_GRPC),
        get_env_var_name(ServiceNameEnum.SERVICE, ENVVAR_SUFIX_SERVICE_HOST     ),
        get_env_var_name(ServiceNameEnum.SERVICE, ENVVAR_SUFIX_SERVICE_PORT_GRPC),
    ])

    signal.signal(signal.SIGINT,  signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    LOGGER.info('Starting...')

    # Start metrics server
    metrics_port = get_metrics_port()
    start_http_server(metrics_port)

    # Starting NBI service
    grpc_service = NbiService()
    grpc_service.start()

    rest_server = RestServer()
    register_etsi_bwm_api(rest_server)
    register_ietf_hardware(rest_server)
    register_ietf_l2vpn(rest_server)  # Registering L2VPN entrypoint
    register_ietf_l3vpn(rest_server)  # Registering L3VPN entrypoint
    register_ietf_network(rest_server)
    register_ietf_nss(rest_server)  # Registering NSS entrypoint
    register_ietf_acl(rest_server)
    register_qkd_app(rest_server)
    register_tfs_api(rest_server)
    rest_server.start()

    register_context_subscription()

    LOGGER.debug('Configured Resources:')
    for resource in rest_server.api.resources:
        LOGGER.debug(' - {:s}'.format(str(resource)))

    LOGGER.debug('Configured Rules:')
    for rule in rest_server.app.url_map.iter_rules():
        LOGGER.debug(' - {:s}'.format(str(rule)))

    # Wait for Ctrl+C or termination signal
    while not terminate.wait(timeout=1.0): pass

    LOGGER.info('Terminating...')
    grpc_service.stop()
    rest_server.shutdown()
    rest_server.join()

    LOGGER.info('Bye')
    return 0

if __name__ == '__main__':
    sys.exit(main())
