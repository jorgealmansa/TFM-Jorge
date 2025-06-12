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

import anytree, json, logging
from typing import Any, List, Optional, Tuple, Union
from common.proto.context_pb2 import ConfigActionEnum, ConfigRule, Device, EndPoint, ServiceConfig
from common.tools.grpc.Tools import grpc_message_to_json, grpc_message_to_json_string
from .AnyTreeTools import TreeNode, delete_subnode, dump_subtree, get_subnode, set_subnode_value
from .Tools import extract_endpoint_index, extract_index

LOGGER = logging.getLogger(__name__)

class SettingsHandler:
    def __init__(self, service_config : ServiceConfig, **settings) -> None:
        self.__resolver = anytree.Resolver(pathattr='name')
        self.__config = TreeNode('.')
        for config_rule in service_config.config_rules:
            self.update_config_rule(config_rule)

    @staticmethod
    def _config_rule_to_raw(config_rule : ConfigRule) -> Optional[Tuple[int, str, Any]]:
        action = config_rule.action
        kind = config_rule.WhichOneof('config_rule')
        if kind == 'custom':
            key_or_path = config_rule.custom.resource_key
            value = config_rule.custom.resource_value
            try:
                value = json.loads(value)
            except: # pylint: disable=bare-except
                pass
        elif kind == 'acl':
            device_uuid = config_rule.acl.endpoint_id.device_id.device_uuid.uuid
            endpoint_uuid = config_rule.acl.endpoint_id.endpoint_uuid.uuid
            endpoint_name, endpoint_index = extract_endpoint_index(endpoint_uuid)
            acl_ruleset_name = config_rule.acl.rule_set.name
            ACL_KEY_TEMPLATE = '/device[{:s}]/endpoint[{:s}]/index[{:d}]/acl_ruleset[{:s}]'
            key_or_path = ACL_KEY_TEMPLATE.format(device_uuid, endpoint_name,endpoint_index, acl_ruleset_name)
            value = grpc_message_to_json(config_rule.acl)
        else:
            MSG = 'Unsupported Kind({:s}) in ConfigRule({:s})'
            LOGGER.warning(MSG.format(str(kind), grpc_message_to_json_string(config_rule)))
            return None

        return action, key_or_path, value

    def get(self, key_or_path : Union[str, List[str]], default : Optional[Any] = None) -> Optional[TreeNode]:
        return get_subnode(self.__resolver, self.__config, key_or_path, default=default)

    def get_service_settings(self) -> Optional[TreeNode]:
        service_settings_uri = '/settings'
        service_settings = self.get(service_settings_uri)
        return service_settings

    def get_device_settings(self, device : Device) -> Optional[TreeNode]:
        device_keys = device.device_id.device_uuid.uuid, device.name

        for device_key in device_keys:
            endpoint_settings_uri = '/device[{:s}]/settings'.format(device_key)
            endpoint_settings = self.get(endpoint_settings_uri)
            if endpoint_settings is not None: return endpoint_settings

        return None

    def get_endpoint_settings(self, device : Device, endpoint : EndPoint) -> Optional[TreeNode]:
        device_keys   = device.device_id.device_uuid.uuid,       device.name
        endpoint_keys = endpoint.endpoint_id.endpoint_uuid.uuid, endpoint.name

        for device_key in device_keys:
            for endpoint_key in endpoint_keys:
                endpoint_settings_uri = '/device[{:s}]/endpoint[{:s}]/settings'.format(device_key, endpoint_key)
                endpoint_settings = self.get(endpoint_settings_uri)
                if endpoint_settings is not None: return endpoint_settings

        return None
    
    def get_endpoint_acls(self, device : Device, endpoint : EndPoint) -> List [Tuple]:
        endpoint_name = endpoint.name
        device_keys   = device.device_id.device_uuid.uuid,       device.name
        endpoint_keys = endpoint.endpoint_id.endpoint_uuid.uuid, endpoint.name
        acl_rules = []
        for device_key in device_keys:
            for endpoint_key in endpoint_keys:
                endpoint_settings_uri = '/device[{:s}]/endpoint[{:s}]'.format(device_key, endpoint_key)
                endpoint_settings = self.get(endpoint_settings_uri)
                if endpoint_settings is None: continue  
                endpoint_name, endpoint_index = extract_endpoint_index(endpoint_name)
                ACL_RULE_PREFIX = '/device[{:s}]/endpoint[{:s}]/'.format(device_key, endpoint_name)

                results = dump_subtree(endpoint_settings)
                for res_key, res_value in results: 
                    if not res_key.startswith(ACL_RULE_PREFIX): continue
                    if not "acl_ruleset" in res_key: continue
                    acl_index = extract_index(res_value)
                    if not 'index[{:d}]'.format(acl_index) in res_key: continue
                    acl_rules.append((res_key, res_value))
        return acl_rules

    def set(self, key_or_path : Union[str, List[str]], value : Any) -> None:
        set_subnode_value(self.__resolver, self.__config, key_or_path, value)

    def delete(self, key_or_path : Union[str, List[str]]) -> None:
        delete_subnode(self.__resolver, self.__config, key_or_path)

    def update_config_rule(self, config_rule : ConfigRule) -> None:
        raw_data = SettingsHandler._config_rule_to_raw(config_rule)
        if raw_data is None: return
        action, key_or_path, value = raw_data

        if action == ConfigActionEnum.CONFIGACTION_SET:
            self.set(key_or_path, value)
        elif action == ConfigActionEnum.CONFIGACTION_DELETE:
            self.delete(key_or_path)
        else:
            MSG = 'Unsupported Action({:s}) in ConfigRule({:s})'
            LOGGER.warning(MSG.format(str(action), grpc_message_to_json_string(config_rule)))
            return

    def dump_config_rules(self) -> List[Tuple[Any, Any]]:
        return dump_subtree(self.__config)
