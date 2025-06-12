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
from typing import Any, List, Optional, Tuple, Union
from common.method_wrappers.Decorator import MetricsPool, metered_subclass_method
from common.proto.context_pb2 import ConfigActionEnum, ConfigRule, DeviceId, Service
from common.tools.object_factory.Device import json_device_id
from common.type_checkers.Checkers import chk_type
from service.service.service_handler_api.Tools import get_device_endpoint_uuids, get_endpoint_matching
from service.service.service_handler_api._ServiceHandler import _ServiceHandler
from service.service.service_handler_api.SettingsHandler import SettingsHandler
from service.service.task_scheduler.TaskExecutor import TaskExecutor
from .ConfigRules import setup_config_rules, teardown_config_rules

LOGGER = logging.getLogger(__name__)

METRICS_POOL = MetricsPool('Service', 'Handler', labels={'handler': 'l2nm_emulated'})

class L2NMEmulatedServiceHandler(_ServiceHandler):
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
        if len(endpoints) == 0: return []

        service_uuid = self.__service.service_id.service_uuid.uuid
        settings = self.__settings_handler.get('/settings')

        results = []
        for endpoint in endpoints:
            try:
                device_uuid, endpoint_uuid = get_device_endpoint_uuids(endpoint)

                device_obj = self.__task_executor.get_device(DeviceId(**json_device_id(device_uuid)))
                device_name = device_obj.name

                for config_rule in device_obj.device_config.config_rules:
                    raw_data = SettingsHandler._config_rule_to_raw(config_rule)
                    if raw_data is None: continue
                    action, key_or_path, value = raw_data
                    if action != ConfigActionEnum.CONFIGACTION_SET: continue
                    if not key_or_path.startswith('/endpoints/endpoint['): continue
                    if not key_or_path.endswith(']/settings'): continue
                    key_or_path = key_or_path.replace('/endpoints/', '/device[{:s}]/'.format(device_name))
                    LOGGER.debug('Setting key_or_path={:s} value={:s}'.format(str(key_or_path), str(value)))
                    self.__settings_handler.set(key_or_path, value)

                service_config_rules = self.__settings_handler.dump_config_rules()
                LOGGER.debug('service_config_rules={:s}'.format(str(service_config_rules)))

                endpoint_obj = get_endpoint_matching(device_obj, endpoint_uuid)
                endpoint_name = endpoint_obj.name
                endpoint_settings = self.__settings_handler.get_endpoint_settings(device_obj, endpoint_obj)
                endpoint_acls = self.__settings_handler.get_endpoint_acls(device_obj, endpoint_obj)

                MSG = 'device_uuid={:s} device_name={:s} endpoint_uuid={:s} endpoint_name={:s} endpoint_settings={:s}'
                str_endpoint_settings = str(None) if endpoint_settings is None else str(endpoint_settings.value)
                LOGGER.debug(MSG.format(
                    str(device_uuid), str(device_name), str(endpoint_uuid), str(endpoint_name), str_endpoint_settings
                ))

                json_config_rules = setup_config_rules(
                    service_uuid, connection_uuid, device_uuid, endpoint_uuid, endpoint_name,
                    settings, endpoint_settings, endpoint_acls)

                if len(json_config_rules) > 0:
                    del device_obj.device_config.config_rules[:]
                    for json_config_rule in json_config_rules:
                        device_obj.device_config.config_rules.append(ConfigRule(**json_config_rule))
                    self.__task_executor.configure_device(device_obj)

                if len(json_config_rules) > 0:
                    del device_obj.device_config.config_rules[:]
                    for json_config_rule in json_config_rules:
                        device_obj.device_config.config_rules.append(ConfigRule(**json_config_rule))
                    self.__task_executor.configure_device(device_obj)

                results.append(True)
            except Exception as e: # pylint: disable=broad-except
                LOGGER.exception('Unable to SetEndpoint({:s})'.format(str(endpoint)))
                results.append(e)

        return results

    @metered_subclass_method(METRICS_POOL)
    def DeleteEndpoint(
        self, endpoints : List[Tuple[str, str, Optional[str]]], connection_uuid : Optional[str] = None
    ) -> List[Union[bool, Exception]]:
        chk_type('endpoints', endpoints, list)
        if len(endpoints) == 0: return []

        service_uuid = self.__service.service_id.service_uuid.uuid
        settings = self.__settings_handler.get('/settings')

        results = []
        for endpoint in endpoints:
            try:
                device_uuid, endpoint_uuid = get_device_endpoint_uuids(endpoint)

                device_obj = self.__task_executor.get_device(DeviceId(**json_device_id(device_uuid)))
                device_name = device_obj.name

                for config_rule in device_obj.device_config.config_rules:
                    raw_data = SettingsHandler._config_rule_to_raw(config_rule)
                    if raw_data is None: continue
                    action, key_or_path, value = raw_data
                    if action != ConfigActionEnum.CONFIGACTION_SET: continue
                    if not key_or_path.startswith('/endpoints/endpoint['): continue
                    if not key_or_path.endswith(']/settings'): continue
                    key_or_path = key_or_path.replace('/endpoints/', '/device[{:s}]/'.format(device_name))
                    LOGGER.debug('Setting key_or_path={:s} value={:s}'.format(str(key_or_path), str(value)))
                    self.__settings_handler.set(key_or_path, value)

                service_config_rules = self.__settings_handler.dump_config_rules()
                LOGGER.debug('service_config_rules={:s}'.format(str(service_config_rules)))

                endpoint_obj = get_endpoint_matching(device_obj, endpoint_uuid)
                endpoint_name = endpoint_obj.name
                endpoint_settings = self.__settings_handler.get_endpoint_settings(device_obj, endpoint_obj)

                MSG = 'device_uuid={:s} device_name={:s} endpoint_uuid={:s} endpoint_name={:s} endpoint_settings={:s}'
                str_endpoint_settings = str(None) if endpoint_settings is None else str(endpoint_settings.value)
                LOGGER.debug(MSG.format(
                    str(device_uuid), str(device_name), str(endpoint_uuid), str(endpoint_name), str_endpoint_settings
                ))

                json_config_rules = teardown_config_rules(
                    service_uuid, connection_uuid, device_uuid, endpoint_uuid, endpoint_name,
                    settings, endpoint_settings)

                if len(json_config_rules) > 0:
                    del device_obj.device_config.config_rules[:]
                    for json_config_rule in json_config_rules:
                        device_obj.device_config.config_rules.append(ConfigRule(**json_config_rule))
                    self.__task_executor.configure_device(device_obj)

                results.append(True)
            except Exception as e: # pylint: disable=broad-except
                LOGGER.exception('Unable to DeleteEndpoint({:s})'.format(str(endpoint)))
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
