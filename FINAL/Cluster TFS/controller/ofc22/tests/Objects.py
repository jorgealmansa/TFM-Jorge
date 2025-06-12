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

from common.tools.object_factory.Device import json_device_id
from common.tools.object_factory.EndPoint import json_endpoint_id
from tests.tools.mock_osm.Tools import connection_point, wim_mapping

# ----- WIM Service Settings -------------------------------------------------------------------------------------------

SITE_ID_DC1 = '1'
DEV_ID_DC1  = json_device_id('R1-EMU')
EP_ID_DC1   = json_endpoint_id(DEV_ID_DC1, '13/1/2')

SITE_ID_DC2 = '2'
DEV_ID_DC2  = json_device_id('R3-EMU')
EP_ID_DC2   = json_endpoint_id(DEV_ID_DC2, '13/1/2')

WIM_SEP_DC1, WIM_MAP_DC1 = wim_mapping(SITE_ID_DC1, EP_ID_DC1)
WIM_SEP_DC2, WIM_MAP_DC2 = wim_mapping(SITE_ID_DC2, EP_ID_DC2)

WIM_MAPPING  = [
    WIM_MAP_DC1,
    WIM_MAP_DC2,
]

WIM_SRV_VLAN_ID = 300
WIM_SERVICE_TYPE = 'ELINE'
WIM_SERVICE_CONNECTION_POINTS = [
    connection_point(WIM_SEP_DC1, 'dot1q', WIM_SRV_VLAN_ID),
    connection_point(WIM_SEP_DC2, 'dot1q', WIM_SRV_VLAN_ID),
]
