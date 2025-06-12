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

from enum import Enum

class DeviceTypeEnum(Enum):

    # Abstractions
    NETWORK                         = 'network'

    # Emulated device types
    EMULATED_CLIENT                 = 'emu-client'
    EMULATED_DATACENTER             = 'emu-datacenter'
    EMULATED_IP_SDN_CONTROLLER      = 'emu-ip-sdn-controller'
    EMULATED_MICROWAVE_RADIO_SYSTEM = 'emu-microwave-radio-system'
    EMULATED_OPEN_LINE_SYSTEM       = 'emu-open-line-system'
    EMULATED_OPTICAL_ROADM          = 'emu-optical-roadm'
    EMULATED_OPTICAL_TRANSPONDER    = 'emu-optical-transponder'
    EMULATED_OPTICAL_SPLITTER       = 'emu-optical-splitter'        # passive component required for XR Constellation
    EMULATED_P4_SWITCH              = 'emu-p4-switch'
    EMULATED_PACKET_RADIO_ROUTER    = 'emu-packet-radio-router'
    EMULATED_PACKET_ROUTER          = 'emu-packet-router'
    EMULATED_PACKET_SWITCH          = 'emu-packet-switch'
    EMULATED_XR_CONSTELLATION       = 'emu-xr-constellation'

    # Real device types
    CLIENT                          = 'client'
    DATACENTER                      = 'datacenter'
    IP_SDN_CONTROLLER               = 'ip-sdn-controller'
    MICROWAVE_RADIO_SYSTEM          = 'microwave-radio-system'
    OPEN_LINE_SYSTEM                = 'open-line-system'
    OPTICAL_ROADM                   = 'optical-roadm'
    OPTICAL_TRANSPONDER             = 'optical-transponder'
    P4_SWITCH                       = 'p4-switch'
    PACKET_RADIO_ROUTER             = 'packet-radio-router'
    PACKET_ROUTER                   = 'packet-router'
    PACKET_SWITCH                   = 'packet-switch'
    XR_CONSTELLATION                = 'xr-constellation'
    QKD_NODE                        = 'qkd-node'
    OPEN_ROADM                      = 'openroadm'

    # ETSI TeraFlowSDN controller
    TERAFLOWSDN_CONTROLLER          = 'teraflowsdn'
