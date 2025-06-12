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

import pytest
import requests
from requests.exceptions import ConnectionError

def test_mock_qkd_node_responses():
    response = requests.get('http://127.0.0.1:11111/restconf/data/etsi-qkd-sdn-node:qkd_node')
    assert response.status_code == 200
    data = response.json()
    assert 'qkd_node' in data

def test_mock_node_failure_scenarios():
    try:
        response = requests.get('http://127.0.0.1:12345/restconf/data/etsi-qkd-sdn-node:qkd_node')
    except ConnectionError as e:
        assert isinstance(e, ConnectionError)
    else:
        pytest.fail("ConnectionError not raised as expected")
