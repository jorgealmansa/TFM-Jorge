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

import logging, requests
from requests.auth import HTTPBasicAuth
from typing import Dict, List, Optional
from device.service.driver_api.ImportTopologyEnum import ImportTopologyEnum

GET_DEVICES_URL = '{:s}://{:s}:{:d}/tfs-api/devices'
GET_LINKS_URL   = '{:s}://{:s}:{:d}/tfs-api/links'
TIMEOUT = 30

HTTP_OK_CODES = {
    200,    # OK
    201,    # Created
    202,    # Accepted
    204,    # No Content
}

MAPPING_STATUS = {
    'DEVICEOPERATIONALSTATUS_UNDEFINED': 0,
    'DEVICEOPERATIONALSTATUS_DISABLED' : 1,
    'DEVICEOPERATIONALSTATUS_ENABLED'  : 2,
}

MAPPING_DRIVER = {
    'DEVICEDRIVER_UNDEFINED'            : 0,
    'DEVICEDRIVER_OPENCONFIG'           : 1,
    'DEVICEDRIVER_TRANSPORT_API'        : 2,
    'DEVICEDRIVER_P4'                   : 3,
    'DEVICEDRIVER_IETF_NETWORK_TOPOLOGY': 4,
    'DEVICEDRIVER_ONF_TR_532'           : 5,
    'DEVICEDRIVER_XR'                   : 6,
    'DEVICEDRIVER_IETF_L2VPN'           : 7,
    'DEVICEDRIVER_GNMI_OPENCONFIG'      : 8,
    'DEVICEDRIVER_OPTICAL_TFS'          : 9,
    'DEVICEDRIVER_IETF_ACTN'            : 10,
    'DEVICEDRIVER_OC'                   : 11,
}

MSG_ERROR = 'Could not retrieve devices in remote TeraFlowSDN instance({:s}). status_code={:s} reply={:s}'

LOGGER = logging.getLogger(__name__)

class TfsApiClient:
    def __init__(
        self, address : str, port : int, scheme : str = 'http',
        username : Optional[str] = None, password : Optional[str] = None
    ) -> None:
        self._devices_url = GET_DEVICES_URL.format(scheme, address, port)
        self._links_url = GET_LINKS_URL.format(scheme, address, port)
        self._auth = HTTPBasicAuth(username, password) if username is not None and password is not None else None

    def get_devices_endpoints(self, import_topology : ImportTopologyEnum = ImportTopologyEnum.DEVICES) -> List[Dict]:
        LOGGER.debug('[get_devices_endpoints] begin')
        LOGGER.debug('[get_devices_endpoints] import_topology={:s}'.format(str(import_topology)))

        reply = requests.get(self._devices_url, timeout=TIMEOUT, verify=False, auth=self._auth)
        if reply.status_code not in HTTP_OK_CODES:
            msg = MSG_ERROR.format(str(self._devices_url), str(reply.status_code), str(reply))
            LOGGER.error(msg)
            raise Exception(msg)

        if import_topology == ImportTopologyEnum.DISABLED:
            raise Exception('Unsupported import_topology mode: {:s}'.format(str(import_topology)))

        result = list()
        for json_device in reply.json()['devices']:
            device_uuid : str = json_device['device_id']['device_uuid']['uuid']
            device_type : str = json_device['device_type']
            #if not device_type.startswith('emu-'): device_type = 'emu-' + device_type
            device_status = json_device['device_operational_status']
            device_url = '/devices/device[{:s}]'.format(device_uuid)
            device_data = {
                'uuid': json_device['device_id']['device_uuid']['uuid'],
                'name': json_device['name'],
                'type': device_type,
                'status': MAPPING_STATUS[device_status],
                'drivers': [MAPPING_DRIVER[driver] for driver in json_device['device_drivers']],
            }
            result.append((device_url, device_data))

            for json_endpoint in json_device['device_endpoints']:
                endpoint_uuid = json_endpoint['endpoint_id']['endpoint_uuid']['uuid']
                endpoint_url = '/endpoints/endpoint[{:s}]'.format(endpoint_uuid)
                endpoint_data = {
                    'device_uuid': device_uuid,
                    'uuid': endpoint_uuid,
                    'name': json_endpoint['name'],
                    'type': json_endpoint['endpoint_type'],
                }
                result.append((endpoint_url, endpoint_data))

        if import_topology == ImportTopologyEnum.DEVICES:
            LOGGER.debug('[get_devices_endpoints] devices only; returning')
            return result

        reply = requests.get(self._links_url, timeout=TIMEOUT, verify=False, auth=self._auth)
        if reply.status_code not in HTTP_OK_CODES:
            msg = MSG_ERROR.format(str(self._links_url), str(reply.status_code), str(reply))
            LOGGER.error(msg)
            raise Exception(msg)

        for json_link in reply.json()['links']:
            link_uuid : str = json_link['link_id']['link_uuid']['uuid']
            link_url = '/links/link[{:s}]'.format(link_uuid)
            link_endpoint_ids = [
                (json_endpoint_id['device_id']['device_uuid']['uuid'], json_endpoint_id['endpoint_uuid']['uuid'])
                for json_endpoint_id in json_link['link_endpoint_ids']
            ]
            link_data = {
                'uuid': json_link['link_id']['link_uuid']['uuid'],
                'name': json_link['name'],
                'endpoints': link_endpoint_ids,
            }
            result.append((link_url, link_data))

        LOGGER.debug('[get_devices_endpoints] topology; returning')
        return result
