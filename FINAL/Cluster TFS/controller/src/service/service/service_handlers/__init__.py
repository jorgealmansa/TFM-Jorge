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

from common.proto.context_pb2 import DeviceDriverEnum, ServiceTypeEnum
from ..service_handler_api.FilterFields import FilterFieldEnum
from .l2nm_emulated.L2NMEmulatedServiceHandler import L2NMEmulatedServiceHandler
from .l2nm_ietfl2vpn.L2NM_IETFL2VPN_ServiceHandler import L2NM_IETFL2VPN_ServiceHandler
from .l2nm_openconfig.L2NMOpenConfigServiceHandler import L2NMOpenConfigServiceHandler
from .l3nm_emulated.L3NMEmulatedServiceHandler import L3NMEmulatedServiceHandler
from .l3nm_openconfig.L3NMOpenConfigServiceHandler import L3NMOpenConfigServiceHandler
from .l3nm_gnmi_openconfig.L3NMGnmiOpenConfigServiceHandler import L3NMGnmiOpenConfigServiceHandler
from .l3nm_ietf_actn.L3NMIetfActnServiceHandler import L3NMIetfActnServiceHandler
from .microwave.MicrowaveServiceHandler import MicrowaveServiceHandler
from .p4.p4_service_handler import P4ServiceHandler
from .tapi_tapi.TapiServiceHandler import TapiServiceHandler
from .tapi_xr.TapiXrServiceHandler import TapiXrServiceHandler
from .e2e_orch.E2EOrchestratorServiceHandler import E2EOrchestratorServiceHandler
from .oc.OCServiceHandler import OCServiceHandler
from .qkd.qkd_service_handler import QKDServiceHandler

SERVICE_HANDLERS = [
    (L2NMEmulatedServiceHandler, [
        {
            FilterFieldEnum.SERVICE_TYPE  : ServiceTypeEnum.SERVICETYPE_L2NM,
            FilterFieldEnum.DEVICE_DRIVER : DeviceDriverEnum.DEVICEDRIVER_UNDEFINED,
        }
    ]),
    (L2NMOpenConfigServiceHandler, [
        {
            FilterFieldEnum.SERVICE_TYPE  : ServiceTypeEnum.SERVICETYPE_L2NM,
            FilterFieldEnum.DEVICE_DRIVER : DeviceDriverEnum.DEVICEDRIVER_OPENCONFIG,
        }
    ]),
    (L3NMEmulatedServiceHandler, [
        {
            FilterFieldEnum.SERVICE_TYPE  : ServiceTypeEnum.SERVICETYPE_L3NM,
            FilterFieldEnum.DEVICE_DRIVER : DeviceDriverEnum.DEVICEDRIVER_UNDEFINED,
        }
    ]),
    (L3NMOpenConfigServiceHandler, [
        {
            FilterFieldEnum.SERVICE_TYPE  : ServiceTypeEnum.SERVICETYPE_L3NM,
            FilterFieldEnum.DEVICE_DRIVER : DeviceDriverEnum.DEVICEDRIVER_OPENCONFIG,
        }
    ]),
    (L3NMGnmiOpenConfigServiceHandler, [
        {
            FilterFieldEnum.SERVICE_TYPE  : ServiceTypeEnum.SERVICETYPE_L3NM,
            FilterFieldEnum.DEVICE_DRIVER : DeviceDriverEnum.DEVICEDRIVER_GNMI_OPENCONFIG,
        }
    ]),
    (L3NMIetfActnServiceHandler, [
        {
            FilterFieldEnum.SERVICE_TYPE  : ServiceTypeEnum.SERVICETYPE_L3NM,
            FilterFieldEnum.DEVICE_DRIVER : DeviceDriverEnum.DEVICEDRIVER_IETF_ACTN,
        }
    ]),
    (TapiServiceHandler, [
        {
            FilterFieldEnum.SERVICE_TYPE  : ServiceTypeEnum.SERVICETYPE_TAPI_CONNECTIVITY_SERVICE,
            FilterFieldEnum.DEVICE_DRIVER : [DeviceDriverEnum.DEVICEDRIVER_TRANSPORT_API],
        }
    ]),
    (TapiXrServiceHandler, [
        {
            FilterFieldEnum.SERVICE_TYPE  : ServiceTypeEnum.SERVICETYPE_TAPI_CONNECTIVITY_SERVICE,
            FilterFieldEnum.DEVICE_DRIVER : [DeviceDriverEnum.DEVICEDRIVER_XR],
        }
    ]),
    (MicrowaveServiceHandler, [
        {
            FilterFieldEnum.SERVICE_TYPE  : ServiceTypeEnum.SERVICETYPE_L2NM,
            FilterFieldEnum.DEVICE_DRIVER : [DeviceDriverEnum.DEVICEDRIVER_IETF_NETWORK_TOPOLOGY, DeviceDriverEnum.DEVICEDRIVER_ONF_TR_532],
        }
    ]),
    (P4ServiceHandler, [
        {
            FilterFieldEnum.SERVICE_TYPE: ServiceTypeEnum.SERVICETYPE_L2NM,
            FilterFieldEnum.DEVICE_DRIVER: DeviceDriverEnum.DEVICEDRIVER_P4,
        }
    ]),
    (L2NM_IETFL2VPN_ServiceHandler, [
        {
            FilterFieldEnum.SERVICE_TYPE  : ServiceTypeEnum.SERVICETYPE_L2NM,
            FilterFieldEnum.DEVICE_DRIVER : [DeviceDriverEnum.DEVICEDRIVER_IETF_L2VPN],
        }
    ]),
    (E2EOrchestratorServiceHandler, [
        {
            FilterFieldEnum.SERVICE_TYPE  : ServiceTypeEnum.SERVICETYPE_E2E,
            FilterFieldEnum.DEVICE_DRIVER : [DeviceDriverEnum.DEVICEDRIVER_OPTICAL_TFS],
        }
    ]),
    (OCServiceHandler, [
        {
            FilterFieldEnum.SERVICE_TYPE  : ServiceTypeEnum.SERVICETYPE_OPTICAL_CONNECTIVITY,
            FilterFieldEnum.DEVICE_DRIVER : DeviceDriverEnum.DEVICEDRIVER_OC,
        }
    ]),
    (QKDServiceHandler, [
        {
            FilterFieldEnum.SERVICE_TYPE  : ServiceTypeEnum.SERVICETYPE_QKD,
            FilterFieldEnum.DEVICE_DRIVER : [DeviceDriverEnum.DEVICEDRIVER_QKD],
        }
    ])
]
