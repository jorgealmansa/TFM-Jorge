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


import json
from typing import Dict, Optional, Tuple
from common.DeviceTypes import DeviceTypeEnum
from common.proto.context_pb2 import Device
from common.tools.grpc.Tools import grpc_message_to_json_string

DEVICE_TYPE_TO_DEEPNESS = {
    DeviceTypeEnum.EMULATED_DATACENTER.value             : 90,
    DeviceTypeEnum.DATACENTER.value                      : 90,

    DeviceTypeEnum.TERAFLOWSDN_CONTROLLER.value          : 80,
    DeviceTypeEnum.EMULATED_IP_SDN_CONTROLLER.value      : 80,
    DeviceTypeEnum.IP_SDN_CONTROLLER.value               : 80,

    DeviceTypeEnum.EMULATED_PACKET_ROUTER.value          : 70,
    DeviceTypeEnum.PACKET_ROUTER.value                   : 70,

    DeviceTypeEnum.EMULATED_PACKET_SWITCH.value          : 60,
    DeviceTypeEnum.PACKET_SWITCH.value                   : 60,
    DeviceTypeEnum.EMULATED_P4_SWITCH.value              : 60,
    DeviceTypeEnum.P4_SWITCH.value                       : 60,

    DeviceTypeEnum.EMULATED_XR_CONSTELLATION.value       : 40,
    DeviceTypeEnum.XR_CONSTELLATION.value                : 40,

    DeviceTypeEnum.EMULATED_MICROWAVE_RADIO_SYSTEM.value : 40,
    DeviceTypeEnum.MICROWAVE_RADIO_SYSTEM.value          : 40,

    DeviceTypeEnum.EMULATED_OPEN_LINE_SYSTEM.value       : 30,
    DeviceTypeEnum.OPEN_LINE_SYSTEM.value                : 30,

    DeviceTypeEnum.EMULATED_PACKET_RADIO_ROUTER.value    : 10,
    DeviceTypeEnum.PACKET_RADIO_ROUTER.value             : 10,
    DeviceTypeEnum.EMULATED_OPTICAL_TRANSPONDER.value    : 10,
    DeviceTypeEnum.OPTICAL_TRANSPONDER.value             : 10,
    DeviceTypeEnum.EMULATED_OPTICAL_ROADM.value          : 10,
    DeviceTypeEnum.OPTICAL_ROADM.value                   : 10,

    DeviceTypeEnum.EMULATED_OPTICAL_SPLITTER.value       :  0,
    DeviceTypeEnum.NETWORK.value                         :  0, # network out of our control; always delegate
}

IGNORED_DEVICE_TYPES = {DeviceTypeEnum.EMULATED_OPTICAL_SPLITTER}
REMOTEDOMAIN_DEVICE_TYPES = {DeviceTypeEnum.NETWORK}

def get_device_controller_uuid(
    device : Device
) -> Optional[str]:
    controller_uuid = device.controller_id.device_uuid.uuid
    if len(controller_uuid) > 0: return controller_uuid
    #for config_rule in device.device_config.config_rules:
    #    if config_rule.WhichOneof('config_rule') != 'custom': continue
    #    if config_rule.custom.resource_key != '_controller': continue
    #    device_controller_id = json.loads(config_rule.custom.resource_value)
    #    return device_controller_id['uuid']
    return None

def _map_device_type(device : Device) -> DeviceTypeEnum:
    device_type = DeviceTypeEnum._value2member_map_.get(device.device_type) # pylint: disable=no-member
    if device_type is None:
        MSG = 'Unsupported DeviceType({:s}) for Device({:s})'
        raise Exception(MSG.format(str(device.device_type), grpc_message_to_json_string(device)))
    return device_type

def _map_resource_to_deepness(device_type : DeviceTypeEnum) -> int:
    deepness = DEVICE_TYPE_TO_DEEPNESS.get(device_type.value)
    if deepness is None: raise Exception('Unsupported DeviceType({:s})'.format(str(device_type.value)))
    return deepness

def get_device_type(
    device : Device, device_dict : Dict[str, Tuple[Dict, Device]], device_controller_uuid : Optional[str]
) -> DeviceTypeEnum:
    if device_controller_uuid is None: return _map_device_type(device)
    device_controller_tuple = device_dict.get(device_controller_uuid)
    if device_controller_tuple is None: raise Exception('Device({:s}) not found'.format(str(device_controller_uuid)))
    _,device = device_controller_tuple
    return _map_device_type(device)

def get_resource_classification(
    device : Device, device_dict : Dict[str, Tuple[Dict, Device]]
) -> Tuple[int, DeviceTypeEnum, Optional[str]]:
    device_controller_uuid = get_device_controller_uuid(device)
    device_type = get_device_type(device, device_dict, device_controller_uuid)
    resource_deepness = _map_resource_to_deepness(device_type)
    return resource_deepness, device_type, device_controller_uuid
