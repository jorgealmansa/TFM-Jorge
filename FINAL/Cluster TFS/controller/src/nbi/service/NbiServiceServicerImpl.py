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

import grpc, logging
from common.method_wrappers.Decorator import MetricsPool, safe_and_metered_rpc_method
from common.proto.context_pb2 import (
    AuthenticationResult, Empty, Service, ServiceId, ServiceIdList, ServiceStatus, TeraFlowController)
from common.proto.nbi_pb2_grpc import NbiServiceServicer

LOGGER = logging.getLogger(__name__)

METRICS_POOL = MetricsPool('NBI', 'RPC')

class NbiServiceServicerImpl(NbiServiceServicer):
    def __init__(self):
        LOGGER.info('Creating Servicer...')
        LOGGER.info('Servicer Created')

    @safe_and_metered_rpc_method(METRICS_POOL, LOGGER)
    def CheckCredentials(self, request : TeraFlowController, context : grpc.ServicerContext) -> AuthenticationResult:
        LOGGER.warning('NOT IMPLEMENTED')
        return AuthenticationResult()

    @safe_and_metered_rpc_method(METRICS_POOL, LOGGER)
    def GetConnectivityServiceStatus(self, request : ServiceId, context : grpc.ServicerContext) -> ServiceStatus:
        LOGGER.warning('NOT IMPLEMENTED')
        return ServiceStatus()

    @safe_and_metered_rpc_method(METRICS_POOL, LOGGER)
    def CreateConnectivityService(self, request : Service, context : grpc.ServicerContext) -> ServiceId:
        LOGGER.warning('NOT IMPLEMENTED')
        return ServiceId()

    @safe_and_metered_rpc_method(METRICS_POOL, LOGGER)
    def EditConnectivityService(self, request : Service, context : grpc.ServicerContext) -> ServiceId:
        LOGGER.warning('NOT IMPLEMENTED')
        return ServiceId()

    @safe_and_metered_rpc_method(METRICS_POOL, LOGGER)
    def DeleteConnectivityService(self, request : Service, context : grpc.ServicerContext) -> Empty:
        LOGGER.warning('NOT IMPLEMENTED')
        return Empty()

    @safe_and_metered_rpc_method(METRICS_POOL, LOGGER)
    def GetAllActiveConnectivityServices(self, request : Empty, context : grpc.ServicerContext) -> ServiceIdList:
        LOGGER.warning('NOT IMPLEMENTED')
        return ServiceIdList()

    @safe_and_metered_rpc_method(METRICS_POOL, LOGGER)
    def ClearAllConnectivityServices(self, request : Empty, context : grpc.ServicerContext) -> Empty:
        LOGGER.warning('NOT IMPLEMENTED')
        return Empty()
