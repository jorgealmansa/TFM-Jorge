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
from common.proto.optical_attack_detector_pb2_grpc import \
    add_OpticalAttackDetectorServiceServicer_to_server
from common.Settings import get_service_port_grpc
from common.tools.service.GenericGrpcService import GenericGrpcService

from opticalattackdetector.service.OpticalAttackDetectorServiceServicerImpl import \
    OpticalAttackDetectorServiceServicerImpl

LOGGER = logging.getLogger(__name__)


class OpticalAttackDetectorService(GenericGrpcService):
    def __init__(self, cls_name: str = __name__):
        port = get_service_port_grpc(ServiceNameEnum.OPTICALATTACKDETECTOR)
        super().__init__(port, cls_name=cls_name)
        self.opticalattackdetector_servicer = OpticalAttackDetectorServiceServicerImpl()

    def install_servicers(self):
        add_OpticalAttackDetectorServiceServicer_to_server(
            self.opticalattackdetector_servicer, self.server
        )
