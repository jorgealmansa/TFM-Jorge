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

import sqlalchemy
from common.Constants import ServiceNameEnum
from common.Settings import get_service_port_grpc
from common.proto.qos_profile_pb2_grpc import add_QoSProfileServiceServicer_to_server
from common.tools.service.GenericGrpcService import GenericGrpcService
from .QoSProfileServiceServicerImpl import QoSProfileServiceServicerImpl

class QoSProfileService(GenericGrpcService):
    def __init__(self, db_engine: sqlalchemy.engine.Engine, cls_name: str = __name__) -> None:
        port = get_service_port_grpc(ServiceNameEnum.QOSPROFILE)
        super().__init__(port, cls_name=cls_name)
        self.qos_profile_servicer = QoSProfileServiceServicerImpl(db_engine)

    def install_servicers(self):
        add_QoSProfileServiceServicer_to_server(self.qos_profile_servicer, self.server)
