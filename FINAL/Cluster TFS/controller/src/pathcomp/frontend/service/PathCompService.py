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

from common.Constants import ServiceNameEnum
from common.Settings import get_service_port_grpc
from common.tools.service.GenericGrpcService import GenericGrpcService
from common.proto.pathcomp_pb2_grpc import add_PathCompServiceServicer_to_server
from .PathCompServiceServicerImpl import PathCompServiceServicerImpl

class PathCompService(GenericGrpcService):
    def __init__(self, cls_name: str = __name__) -> None:
        port = get_service_port_grpc(ServiceNameEnum.PATHCOMP)
        super().__init__(port, cls_name=cls_name)
        self.pathcomp_servicer = PathCompServiceServicerImpl()

    def install_servicers(self):
        add_PathCompServiceServicer_to_server(self.pathcomp_servicer, self.server)
