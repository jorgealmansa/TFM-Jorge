# Copyright 2022-2024 ETSI SDG TeraFlowSDN (TFS) (https://tfs.etsi.org/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from common.proto.qkd_app_pb2 import AppId
from common.method_wrappers.ServiceExceptions import InvalidArgumentsException
from ._Builder import get_uuid_from_string, get_uuid_random

def app_get_uuid(app_id: AppId, allow_random: bool = False) -> str:
    """
    Retrieves or generates the UUID for an app.
    
    :param app_id: AppId object that contains the app UUID
    :param allow_random: If True, generates a random UUID if app_uuid is not set
    :return: App UUID as a string
    """
    app_uuid = app_id.app_uuid.uuid

    if app_uuid:
        return get_uuid_from_string(app_uuid)
    
    if allow_random:
        return get_uuid_random()

    raise InvalidArgumentsException([
        ('app_id.app_uuid.uuid', app_uuid),
    ], extra_details=['At least one UUID is required to identify the app.'])
