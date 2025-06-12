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

from nbi.service.rest_server.RestServer import RestServer
from .Resources import BwInfo, BwInfoId

URL_PREFIX = '/restconf/bwm/v1'

# Use 'path' type since some identifiers might contain char '/' and Flask is unable to recognize them in 'string' type.
RESOURCES = [
    # (endpoint_name, resource_class, resource_url)
    ('api.bw_info',         BwInfo,     '/bw_allocations'),
    ('api.bw_info_id',      BwInfoId,   '/bw_allocations/<path:allocationId>'),
]

def register_etsi_bwm_api(rest_server : RestServer):
    for endpoint_name, resource_class, resource_url in RESOURCES:
        rest_server.add_resource(resource_class, URL_PREFIX + resource_url, endpoint=endpoint_name)
