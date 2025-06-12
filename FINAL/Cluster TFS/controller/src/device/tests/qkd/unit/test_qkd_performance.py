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

# tests/unit/test_qkd_performance.py

import pytest, time
from device.service.drivers.qkd.QKDDriver2 import QKDDriver

MOCK_QKD_ADDRRESS = '127.0.0.1'
MOCK_PORT = 11111

def test_performance_under_load():
    driver = QKDDriver(address=MOCK_QKD_ADDRRESS, port=MOCK_PORT, username='user', password='pass')
    driver.Connect()
    
    start_time = time.time()
    for _ in range(1000):
        driver.GetConfig(['/qkd_interfaces/qkd_interface'])
    end_time = time.time()
    
    assert (end_time - start_time) < 60
