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

import copy, json, logging, requests
from requests.auth import HTTPBasicAuth
from typing import Any, Dict, List, Set, Union

LOGGER = logging.getLogger(__name__)

DEFAULT_BASE_URL = '/restconf/v2/data'
DEFAULT_SCHEME   = 'https'
DEFAULT_TIMEOUT  = 120
DEFAULT_VERIFY   = False

HTTP_STATUS_OK         = 200
HTTP_STATUS_CREATED    = 201
HTTP_STATUS_ACCEPTED   = 202
HTTP_STATUS_NO_CONTENT = 204

HTTP_OK_CODES = {
    HTTP_STATUS_OK,
    HTTP_STATUS_CREATED,
    HTTP_STATUS_ACCEPTED,
    HTTP_STATUS_NO_CONTENT,
}

class RestApiClient:
    def __init__(self, address : str, port : int, settings : Dict[str, Any] = dict()) -> None:
        username = settings.get('username')
        password = settings.get('password')
        self._auth = HTTPBasicAuth(username, password) if username is not None and password is not None else None

        scheme   = settings.get('scheme',   DEFAULT_SCHEME  )
        base_url = settings.get('base_url', DEFAULT_BASE_URL)
        self._base_url = '{:s}://{:s}:{:d}{:s}'.format(scheme, address, int(port), base_url)

        self._timeout = int(settings.get('timeout', DEFAULT_TIMEOUT))
        self._verify  = bool(settings.get('verify', DEFAULT_VERIFY))

    def get(
        self, object_name : str, url : str,
        expected_http_status : Set[int] = {HTTP_STATUS_OK}
    ) -> Union[Dict, List]:
        MSG = 'Get {:s}({:s})'
        LOGGER.info(MSG.format(str(object_name), str(url)))
        response = requests.get(
            self._base_url + url,
            timeout=self._timeout, verify=self._verify, auth=self._auth
        )
        LOGGER.info('  Response[{:s}]: {:s}'.format(str(response.status_code), str(response.content)))

        if response.status_code in expected_http_status: return json.loads(response.content)

        MSG = 'Could not get {:s}({:s}): status_code={:s} reply={:s}'
        raise Exception(MSG.format(str(object_name), str(url), str(response.status_code), str(response)))

    def update(
        self, object_name : str, url : str, data : Dict, headers : Dict[str, Any] = dict(),
        expected_http_status : Set[int] = HTTP_OK_CODES
    ) -> None:
        headers = copy.deepcopy(headers)
        if 'content-type' not in {header_name.lower() for header_name in headers.keys()}:
            headers.update({'content-type': 'application/json'})

        MSG = 'Create/Update {:s}({:s}, {:s})'
        LOGGER.info(MSG.format(str(object_name), str(url), str(data)))
        response = requests.post(
            self._base_url + url, data=json.dumps(data), headers=headers,
            timeout=self._timeout, verify=self._verify, auth=self._auth
        )
        LOGGER.info('  Response[{:s}]: {:s}'.format(str(response.status_code), str(response.content)))

        if response.status_code in expected_http_status: return

        MSG = 'Could not create/update {:s}({:s}, {:s}): status_code={:s} reply={:s}'
        raise Exception(MSG.format(str(object_name), str(url), str(data), str(response.status_code), str(response)))

    def delete(
        self, object_name : str, url : str,
        expected_http_status : Set[int] = HTTP_OK_CODES
    ) -> None:
        MSG = 'Delete {:s}({:s})'
        LOGGER.info(MSG.format(str(object_name), str(url)))
        response = requests.delete(
            self._base_url + url,
            timeout=self._timeout, verify=self._verify, auth=self._auth
        )
        LOGGER.info('  Response[{:s}]: {:s}'.format(str(response.status_code), str(response.content)))

        if response.status_code in expected_http_status: return

        MSG = 'Could not delete {:s}({:s}): status_code={:s} reply={:s}'
        raise Exception(MSG.format(str(object_name), str(url), str(response.status_code), str(response)))
