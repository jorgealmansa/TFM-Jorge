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

from nbi.service.rest_server.nbi_plugins.ietf_hardware.Hardware import Hardware
from nbi.service.rest_server.nbi_plugins.ietf_hardware.HardwareMultipleDevices import HardwareMultipleDevices
from nbi.service.rest_server.RestServer import RestServer

URL_PREFIX_DEVICE   = "/restconf/data/device=<path:device_uuid>/ietf-network-hardware-inventory:network-hardware-inventory"
URL_PREFIX_HARDWARE = "/restconf/data/ietf-network-hardware-inventory:network-hardware-inventory"

def register_ietf_hardware(rest_server: RestServer):
    rest_server.add_resource(Hardware, URL_PREFIX_DEVICE)
    rest_server.add_resource(HardwareMultipleDevices, URL_PREFIX_HARDWARE)
