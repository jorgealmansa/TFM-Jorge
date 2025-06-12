
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
from tests.tools.mock_qkd_nodes.YangValidator import YangValidator

def test_compliance_with_yang_models():
    validator = YangValidator('etsi-qkd-sdn-node', ['etsi-qkd-node-types'])
    response = requests.get('http://127.0.0.1:11111/restconf/data/etsi-qkd-sdn-node:qkd_node')
    data = response.json()
    assert validator.parse_to_dict(data) is not None
