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

import json, logging
from typing import Any, Dict, List, Optional, Tuple, Union
from common.method_wrappers.Decorator import MetricsPool, metered_subclass_method
from common.proto.context_pb2 import ConfigRule, DeviceId, Service
from common.tools.object_factory.ConfigRule import json_config_rule_delete, json_config_rule_set
from common.tools.object_factory.Device import json_device_id
from common.type_checkers.Checkers import chk_type
from service.service.service_handler_api.Tools import get_device_endpoint_uuids, get_endpoint_matching
from service.service.service_handler_api._ServiceHandler import _ServiceHandler
from service.service.service_handler_api.SettingsHandler import SettingsHandler
from service.service.task_scheduler.TaskExecutor import TaskExecutor

LOGGER = logging.getLogger(__name__)

def check_endpoint(endpoint : str, service_uuid : str) -> Tuple[str, str]:
    endpoint_split = endpoint.split(':')
    if len(endpoint_split) != 2:
        raise Exception('Endpoint({:s}) is malformed for Service({:s})'.format(str(endpoint), str(service_uuid)))
    return endpoint_split

METRICS_POOL = MetricsPool('Service', 'Handler', labels={'handler': 'microwave'})

class MicrowaveServiceHandler(_ServiceHandler):
    def __init__(   # pylint: disable=super-init-not-called
        self, service : Service, task_executor : TaskExecutor, **settings
    ) -> None:
        self.__service = service
        self.__task_executor = task_executor
        self.__settings_handler = SettingsHandler(service.service_config, **settings)

    @metered_subclass_method(METRICS_POOL)
    def SetEndpoint(
        self, endpoints : List[Tuple[str, str, Optional[str]]], connection_uuid : Optional[str] = None
    ) -> List[Union[bool, Exception]]:

        chk_type('endpoints', endpoints, list)
        if len(endpoints) != 2: return []

        service_uuid = self.__service.service_id.service_uuid.uuid
        settings = self.__settings_handler.get('/settings')
        json_settings : Dict = {} if settings is None else settings.value
        vlan_id = json_settings.get('vlan_id', 121)

        results = []
        try:
            device_uuid_src, endpoint_uuid_src = get_device_endpoint_uuids(endpoints[0])
            device_uuid_dst, endpoint_uuid_dst = get_device_endpoint_uuids(endpoints[1])

            if device_uuid_src != device_uuid_dst:
                raise Exception('Different Src-Dst devices not supported by now')
            device_uuid = device_uuid_src

            device_obj = self.__task_executor.get_device(DeviceId(**json_device_id(device_uuid)))
            endpoint_name_src = get_endpoint_matching(device_obj, endpoint_uuid_src).name
            endpoint_name_dst = get_endpoint_matching(device_obj, endpoint_uuid_dst).name

            # endpoints are retrieved in the following format --> '/endpoints/endpoint[172.26.60.243:9]'
            node_id_src, tp_id_src = check_endpoint(endpoint_name_src, service_uuid)
            node_id_dst, tp_id_dst = check_endpoint(endpoint_name_dst, service_uuid)

            json_config_rule = json_config_rule_set('/services/service[{:s}]'.format(service_uuid), {
                'uuid'       : service_uuid,
                'node_id_src': node_id_src,
                'tp_id_src'  : tp_id_src,
                'node_id_dst': node_id_dst,
                'tp_id_dst'  : tp_id_dst,
                'vlan_id'    : vlan_id,
            })
            del device_obj.device_config.config_rules[:]
            device_obj.device_config.config_rules.append(ConfigRule(**json_config_rule))
            self.__task_executor.configure_device(device_obj)
            results.append(True)
        except Exception as e: # pylint: disable=broad-except
            LOGGER.exception('Unable to SetEndpoint for Service({:s})'.format(str(service_uuid)))
            results.append(e)

        return results

    @metered_subclass_method(METRICS_POOL)
    def DeleteEndpoint(
        self, endpoints : List[Tuple[str, str, Optional[str]]], connection_uuid : Optional[str] = None
    ) -> List[Union[bool, Exception]]:

        chk_type('endpoints', endpoints, list)
        if len(endpoints) != 2: return []

        service_uuid = self.__service.service_id.service_uuid.uuid

        results = []
        try:
            device_uuid_src, _ = get_device_endpoint_uuids(endpoints[0])
            device_uuid_dst, _ = get_device_endpoint_uuids(endpoints[1])

            if device_uuid_src != device_uuid_dst:
                raise Exception('Different Src-Dst devices not supported by now')
            device_uuid = device_uuid_src

            device_obj = self.__task_executor.get_device(DeviceId(**json_device_id(device_uuid)))

            json_config_rule = json_config_rule_delete('/services/service[{:s}]'.format(service_uuid), {
                'uuid': service_uuid
            })
            del device_obj.device_config.config_rules[:]
            device_obj.device_config.config_rules.append(ConfigRule(**json_config_rule))
            self.__task_executor.configure_device(device_obj)
            results.append(True)
        except Exception as e: # pylint: disable=broad-except
            LOGGER.exception('Unable to DeleteEndpoint for Service({:s})'.format(str(service_uuid)))
            results.append(e)

        return results

    @metered_subclass_method(METRICS_POOL)
    def SetConstraint(self, constraints : List[Tuple[str, Any]]) -> List[Union[bool, Exception]]:
        chk_type('constraints', constraints, list)
        if len(constraints) == 0: return []

        msg = '[SetConstraint] Method not implemented. Constraints({:s}) are being ignored.'
        LOGGER.warning(msg.format(str(constraints)))
        return [True for _ in range(len(constraints))]

    @metered_subclass_method(METRICS_POOL)
    def DeleteConstraint(self, constraints : List[Tuple[str, Any]]) -> List[Union[bool, Exception]]:
        chk_type('constraints', constraints, list)
        if len(constraints) == 0: return []

        msg = '[DeleteConstraint] Method not implemented. Constraints({:s}) are being ignored.'
        LOGGER.warning(msg.format(str(constraints)))
        return [True for _ in range(len(constraints))]

    @metered_subclass_method(METRICS_POOL)
    def SetConfig(self, resources : List[Tuple[str, Any]]) -> List[Union[bool, Exception]]:
        chk_type('resources', resources, list)
        if len(resources) == 0: return []

        results = []
        for resource in resources:
            try:
                resource_value = json.loads(resource[1])
                self.__settings_handler.set(resource[0], resource_value)
                results.append(True)
            except Exception as e: # pylint: disable=broad-except
                LOGGER.exception('Unable to SetConfig({:s})'.format(str(resource)))
                results.append(e)

        return results

    @metered_subclass_method(METRICS_POOL)
    def DeleteConfig(self, resources : List[Tuple[str, Any]]) -> List[Union[bool, Exception]]:
        chk_type('resources', resources, list)
        if len(resources) == 0: return []

        results = []
        for resource in resources:
            try:
                self.__settings_handler.delete(resource[0])
            except Exception as e: # pylint: disable=broad-except
                LOGGER.exception('Unable to DeleteConfig({:s})'.format(str(resource)))
                results.append(e)

        return results
