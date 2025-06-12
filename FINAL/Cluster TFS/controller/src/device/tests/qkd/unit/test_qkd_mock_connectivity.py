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

import pytest, requests
from unittest.mock import patch
from device.service.drivers.qkd.QKDDriver import QKDDriver

MOCK_QKD_ADDRRESS = '127.0.0.1'
MOCK_PORT = 11111

@pytest.fixture
def qkd_driver():
    return QKDDriver(address=MOCK_QKD_ADDRRESS, port=MOCK_PORT, username='user', password='pass')

# Deliverable Test ID: SBI_Test_01
def test_qkd_driver_connection(qkd_driver):
    assert qkd_driver.Connect() is True

# Deliverable Test ID: SBI_Test_01
def test_qkd_driver_invalid_connection():
    qkd_driver = QKDDriver(address='127.0.0.1', port=12345, username='user', password='pass')  # Use invalid port directly
    assert qkd_driver.Connect() is False

# Deliverable Test ID: SBI_Test_10
@patch('device.service.drivers.qkd.QKDDriver2.requests.get')
def test_qkd_driver_timeout_connection(mock_get, qkd_driver):
    mock_get.side_effect = requests.exceptions.Timeout
    qkd_driver.timeout = 0.001  # Simulate very short timeout
    assert qkd_driver.Connect() is False

