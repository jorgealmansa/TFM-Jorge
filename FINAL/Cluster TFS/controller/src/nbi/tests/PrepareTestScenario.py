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

import enum, logging, os, pytest, requests, time
from typing import Any, Dict, List, Optional, Set, Union
from common.Constants import ServiceNameEnum
from common.Settings import (
    ENVVAR_SUFIX_SERVICE_HOST, ENVVAR_SUFIX_SERVICE_PORT_HTTP,
    get_env_var_name, get_service_baseurl_http, get_service_port_http
)
from context.client.ContextClient import ContextClient
from nbi.service.rest_server.RestServer import RestServer
from nbi.service.rest_server.nbi_plugins.etsi_bwm import register_etsi_bwm_api
from nbi.service.rest_server.nbi_plugins.ietf_l2vpn import register_ietf_l2vpn
from nbi.service.rest_server.nbi_plugins.ietf_l3vpn import register_ietf_l3vpn
from nbi.service.rest_server.nbi_plugins.ietf_network import register_ietf_network
from nbi.service.rest_server.nbi_plugins.tfs_api import register_tfs_api
from nbi.tests.MockService_Dependencies import MockService_Dependencies
from service.client.ServiceClient import ServiceClient
from slice.client.SliceClient import SliceClient
from tests.tools.mock_osm.MockOSM import MockOSM
from .Constants import USERNAME, PASSWORD, WIM_MAPPING

LOCAL_HOST = '127.0.0.1'
MOCKSERVICE_PORT = 10000
NBI_SERVICE_PORT = MOCKSERVICE_PORT + get_service_port_http(ServiceNameEnum.NBI)    # avoid privileged ports
os.environ[get_env_var_name(ServiceNameEnum.NBI, ENVVAR_SUFIX_SERVICE_HOST     )] = str(LOCAL_HOST)
os.environ[get_env_var_name(ServiceNameEnum.NBI, ENVVAR_SUFIX_SERVICE_PORT_HTTP)] = str(NBI_SERVICE_PORT)

@pytest.fixture(scope='session')
def mock_service():
    _service = MockService_Dependencies(MOCKSERVICE_PORT)
    _service.configure_env_vars()
    _service.start()
    yield _service
    _service.stop()

@pytest.fixture(scope='session')
def nbi_service_rest(mock_service : MockService_Dependencies):  # pylint: disable=redefined-outer-name, unused-argument
    _rest_server = RestServer()
    register_etsi_bwm_api(_rest_server)
    register_ietf_l2vpn(_rest_server)
    register_ietf_l3vpn(_rest_server)
    register_ietf_network(_rest_server)
    register_tfs_api(_rest_server)
    _rest_server.start()
    time.sleep(1) # bring time for the server to start
    yield _rest_server
    _rest_server.shutdown()
    _rest_server.join()

@pytest.fixture(scope='session')
def osm_wim(nbi_service_rest : RestServer): # pylint: disable=redefined-outer-name, unused-argument
    wim_url = 'http://{:s}:{:d}'.format(LOCAL_HOST, NBI_SERVICE_PORT)
    return MockOSM(wim_url, WIM_MAPPING, USERNAME, PASSWORD)

@pytest.fixture(scope='session')
def context_client(mock_service : MockService_Dependencies): # pylint: disable=redefined-outer-name, unused-argument
    _client = ContextClient()
    yield _client
    _client.close()

@pytest.fixture(scope='session')
def service_client(mock_service : MockService_Dependencies): # pylint: disable=redefined-outer-name, unused-argument
    _client = ServiceClient()
    yield _client
    _client.close()

@pytest.fixture(scope='session')
def slice_client(mock_service : MockService_Dependencies): # pylint: disable=redefined-outer-name, unused-argument
    _client = SliceClient()
    yield _client
    _client.close()

class RestRequestMethod(enum.Enum):
    GET    = 'get'
    POST   = 'post'
    PUT    = 'put'
    PATCH  = 'patch'
    DELETE = 'delete'

EXPECTED_STATUS_CODES : Set[int] = {
    requests.codes['OK'        ],
    requests.codes['CREATED'   ],
    requests.codes['ACCEPTED'  ],
    requests.codes['NO_CONTENT'],
}

def do_rest_request(
    method : RestRequestMethod, url : str, body : Optional[Any] = None, timeout : int = 10,
    allow_redirects : bool = True, expected_status_codes : Set[int] = EXPECTED_STATUS_CODES,
    logger : Optional[logging.Logger] = None
) -> Optional[Union[Dict, List]]:
    base_url = get_service_baseurl_http(ServiceNameEnum.NBI) or ''
    request_url = 'http://{:s}:{:s}@{:s}:{:d}{:s}{:s}'.format(
        USERNAME, PASSWORD, LOCAL_HOST, NBI_SERVICE_PORT, str(base_url), url
    )
    if logger is not None:
        msg = 'Request: {:s} {:s}'.format(str(method.value).upper(), str(request_url))
        if body is not None: msg += ' body={:s}'.format(str(body))
        logger.warning(msg)
    reply = requests.request(method.value, request_url, timeout=timeout, json=body, allow_redirects=allow_redirects)
    if logger is not None:
        logger.warning('Reply: {:s}'.format(str(reply.text)))
    assert reply.status_code in expected_status_codes, 'Reply failed with status code {:d}'.format(reply.status_code)

    if reply.content and len(reply.content) > 0: return reply.json()
    return None

def do_rest_get_request(
    url : str, body : Optional[Any] = None, timeout : int = 10,
    allow_redirects : bool = True, expected_status_codes : Set[int] = EXPECTED_STATUS_CODES,
    logger : Optional[logging.Logger] = None
) -> Optional[Union[Dict, List]]:
    return do_rest_request(
        RestRequestMethod.GET, url, body=body, timeout=timeout, allow_redirects=allow_redirects,
        expected_status_codes=expected_status_codes, logger=logger
    )

def do_rest_post_request(
    url : str, body : Optional[Any] = None, timeout : int = 10,
    allow_redirects : bool = True, expected_status_codes : Set[int] = EXPECTED_STATUS_CODES,
    logger : Optional[logging.Logger] = None
) -> Optional[Union[Dict, List]]:
    return do_rest_request(
        RestRequestMethod.POST, url, body=body, timeout=timeout, allow_redirects=allow_redirects,
        expected_status_codes=expected_status_codes, logger=logger
    )

def do_rest_put_request(
    url : str, body : Optional[Any] = None, timeout : int = 10,
    allow_redirects : bool = True, expected_status_codes : Set[int] = EXPECTED_STATUS_CODES,
    logger : Optional[logging.Logger] = None
) -> Optional[Union[Dict, List]]:
    return do_rest_request(
        RestRequestMethod.PUT, url, body=body, timeout=timeout, allow_redirects=allow_redirects,
        expected_status_codes=expected_status_codes, logger=logger
    )

def do_rest_patch_request(
    url : str, body : Optional[Any] = None, timeout : int = 10,
    allow_redirects : bool = True, expected_status_codes : Set[int] = EXPECTED_STATUS_CODES,
    logger : Optional[logging.Logger] = None
) -> Optional[Union[Dict, List]]:
    return do_rest_request(
        RestRequestMethod.PATCH, url, body=body, timeout=timeout, allow_redirects=allow_redirects,
        expected_status_codes=expected_status_codes, logger=logger
    )

def do_rest_delete_request(
    url : str, body : Optional[Any] = None, timeout : int = 10,
    allow_redirects : bool = True, expected_status_codes : Set[int] = EXPECTED_STATUS_CODES,
    logger : Optional[logging.Logger] = None
) -> Optional[Union[Dict, List]]:
    return do_rest_request(
        RestRequestMethod.DELETE, url, body=body, timeout=timeout, allow_redirects=allow_redirects,
        expected_status_codes=expected_status_codes, logger=logger
    )
