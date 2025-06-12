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

from common.method_wrappers.ServiceExceptions import InvalidArgumentsException
from common.proto.context_pb2 import LinkId
from ._Builder import get_uuid_from_string, get_uuid_random

optical_detail_sp = "Optical_link_detail"

def opticaldetail_get_uuid(
    link_id : LinkId,allow_random=False
) -> str:
    link_uuid = link_id.link_uuid.uuid
    if len(link_uuid) > 0:
        str_uuid=f"{link_uuid}{optical_detail_sp}"
        return get_uuid_from_string(str_uuid)

    if allow_random: return get_uuid_random()
    raise InvalidArgumentsException([
        ('link_id.link_uuid.uuid', link_uuid),
    ], extra_details=['At least one is required to produce a Optical Link Detail UUID'])
