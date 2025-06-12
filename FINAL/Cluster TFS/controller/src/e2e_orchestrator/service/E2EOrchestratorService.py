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

import logging

from common.Constants import ServiceNameEnum
from common.proto.e2eorchestrator_pb2_grpc import add_E2EOrchestratorServiceServicer_to_server
from common.Settings import get_service_port_grpc
from common.tools.service.GenericGrpcService import GenericGrpcService
from .E2EOrchestratorServiceServicerImpl import E2EOrchestratorServiceServicerImpl

LOGGER = logging.getLogger(__name__)


class E2EOrchestratorService(GenericGrpcService):
    def __init__(self, cls_name: str = __name__):
        port = get_service_port_grpc(ServiceNameEnum.E2EORCHESTRATOR)
        super().__init__(port, cls_name=cls_name)
        self.e2eorchestrator_servicer = E2EOrchestratorServiceServicerImpl()

    def install_servicers(self):
        add_E2EOrchestratorServiceServicer_to_server(
            self.e2eorchestrator_servicer, self.server
        )
