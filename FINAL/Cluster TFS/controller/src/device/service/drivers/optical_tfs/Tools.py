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

import json, logging, requests
from requests.auth import HTTPBasicAuth
from typing import Optional

LOGGER = logging.getLogger(__name__)

HTTP_OK_CODES = {
    200,    # OK
    201,    # Created
    202,    # Accepted
    204,    # No Content
}

def find_key(resource, key):
    return json.loads(resource[1])[key]

def get_lightpaths(root_url : str, resource_key : str,auth : Optional[HTTPBasicAuth] = None,
                   timeout : Optional[int] = None):
    headers = {'accept': 'application/json'}
    url = '{:s}/OpticalTFS/GetLightpaths'.format(root_url)

    result = []
    try:
        response = requests.get(url, timeout=timeout, headers=headers, verify=False, auth=auth)
    except requests.exceptions.Timeout:
        LOGGER.exception('Timeout connecting {:s}'.format(url))
        return result
    except Exception as e:  # pylint: disable=broad-except
        LOGGER.exception('Exception retrieving {:s}'.format(resource_key))
        result.append((resource_key, e))
        return result

    try:
        flows = json.loads(response.content)
    except Exception as e:  # pylint: disable=broad-except
        LOGGER.warning('Unable to decode reply: {:s}'.format(str(response.content)))
        result.append((resource_key, e))
        return result

    for flow in flows:
        flow_id = flow.get('flow_id')
        source = flow.get('src')
        destination = flow.get('dst')
        bitrate = flow.get('bitrate')

        endpoint_url = '/flows/flow[{:s}]'.format(flow_id)
        endpoint_data = {'flow_id': flow_id, 'src': source, 'dst': destination, 'bitrate': bitrate}
        result.append((endpoint_url, endpoint_data))

    return result


def add_lightpath(root_url, src_node, dst_node, bitrate,
                   auth : Optional[HTTPBasicAuth] = None, timeout : Optional[int] = None):

    headers = {'accept': 'application/json'}
    url = '{:s}/OpticalTFS/AddLightpath/{:s}/{:s}/{:s}'.format(
        root_url, src_node, dst_node, bitrate)

    results = []
    try:
        LOGGER.info('Lightpath request: {:s} <-> {:s} with {:s} bitrate'.format(
            str(src_node), str(dst_node), str(bitrate)))
        response = requests.put(url=url, timeout=timeout, headers=headers, verify=False, auth=auth)
        results.append(response.json())
        LOGGER.info('Response: {:s}'.format(str(response)))

    except Exception as e:  # pylint: disable=broad-except
        LOGGER.exception('Exception requesting Lightpath: {:s} <-> {:s} with {:s} bitrate'.format(
            str(src_node), str(dst_node), str(bitrate)))
        results.append(e)
    else:
        if response.status_code not in HTTP_OK_CODES:
            msg = 'Could not create Lightpath(status_code={:s} reply={:s}'
            LOGGER.error(msg.format(str(response.status_code), str(response)))
        results.append(response.status_code in HTTP_OK_CODES)

    return results



def del_lightpath(root_url, flow_id, src_node, dst_node, bitrate,
                   auth : Optional[HTTPBasicAuth] = None, timeout : Optional[int] = None):
    url = '{:s}/OpticalTFS/DelLightpath/{:s}/{:s}/{:s}/{:s}'.format(
        root_url, flow_id, src_node, dst_node, bitrate)
    headers = {'accept': 'application/json'}

    results = []

    try:
        response = requests.delete(
            url=url, timeout=timeout, headers=headers, verify=False, auth=auth)
    except Exception as e:  # pylint: disable=broad-except
        LOGGER.exception('Exception deleting Lightpath(uuid={:s})'.format(str(flow_id)))
        results.append(e)
    else:
        if response.status_code not in HTTP_OK_CODES:
            msg = 'Could not delete Lightpath(flow_id={:s}). status_code={:s} reply={:s}'
            LOGGER.error(msg.format(str(flow_id), str(response.status_code), str(response)))
        results.append(response.status_code in HTTP_OK_CODES)

    return results


def get_topology(root_url : str, resource_key : str,auth : Optional[HTTPBasicAuth] = None,
                   timeout : Optional[int] = None):
    headers = {'accept': 'application/json'}
    url = '{:s}/OpticalTFS/GetLinks'.format(root_url)

    result = []
    try:
        response = requests.get(url, timeout=timeout, headers=headers, verify=False, auth=auth)
    except requests.exceptions.Timeout:
        LOGGER.exception('Timeout connecting {:s}'.format(url))
        return result
    except Exception as e:  # pylint: disable=broad-except
        LOGGER.exception('Exception retrieving {:s}'.format(resource_key))
        result.append((resource_key, e))
        return result

    try:
        response = json.loads(response.content)
    except Exception as e:  # pylint: disable=broad-except
        LOGGER.warning('Unable to decode reply: {:s}'.format(str(response.content)))
        result.append((resource_key, e))
        return result
    
    result.append(response)
    return result
