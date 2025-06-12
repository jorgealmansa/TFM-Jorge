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

import json, libyang, logging
from typing import Any, Dict, List, Tuple
from ._Handler import _Handler
from .Tools import get_str
from .YangHandler import YangHandler

LOGGER = logging.getLogger(__name__)

class NetworkInstanceProtocolHandler(_Handler):
    def get_resource_key(self) -> str: return '/network_instance/protocols'
    def get_path(self) -> str:
        return '/openconfig-network-instance:network-instances/network-instance/protocols/protocol'

    def compose(
        self, resource_key : str, resource_value : Dict, yang_handler : YangHandler, delete : bool = False
    ) -> Tuple[str, str]:
        ni_name    = get_str(resource_value, 'name'  )          # test-svc
        identifier = get_str(resource_value, 'identifier')      # 'STATIC'
        proto_name = get_str(resource_value, 'protocol_name')   # 'STATIC'

        if ':' not in identifier:
            identifier = 'openconfig-policy-types:{:s}'.format(identifier)
        PATH_TMPL = '/network-instances/network-instance[name={:s}]/protocols/protocol[identifier={:s}][name={:s}]'
        str_path = PATH_TMPL.format(ni_name, identifier, proto_name)

        if delete:
            str_data = json.dumps({})
            return str_path, str_data

        #str_data = json.dumps({
        #    'identifier': identifier, 'name': name,
        #    'config': {'identifier': identifier, 'name': name, 'enabled': True},
        #    'static_routes': {'static': [{
        #        'prefix': prefix,
        #        'config': {'prefix': prefix},
        #        'next_hops': {
        #            'next-hop': [{
        #                'index': next_hop_index,
        #                'config': {'index': next_hop_index, 'next_hop': next_hop}
        #            }]
        #        }
        #    }]}
        #})

        yang_nis : libyang.DContainer = yang_handler.get_data_path('/openconfig-network-instance:network-instances')
        yang_ni : libyang.DContainer = yang_nis.create_path('network-instance[name="{:s}"]'.format(ni_name))
        yang_ni_prs : libyang.DContainer = yang_ni.create_path('protocols')
        yang_ni_pr_path = 'protocol[identifier="{:s}"][name="{:s}"]'.format(identifier, proto_name)
        yang_ni_pr : libyang.DContainer = yang_ni_prs.create_path(yang_ni_pr_path)
        yang_ni_pr.create_path('config/identifier', identifier)
        yang_ni_pr.create_path('config/name',       proto_name)
        yang_ni_pr.create_path('config/enabled',    True      )

        str_data = yang_ni_pr.print_mem('json')
        json_data = json.loads(str_data)
        json_data = json_data['openconfig-network-instance:protocol'][0]
        str_data = json.dumps(json_data)
        return str_path, str_data

    def parse(
        self, json_data : Dict, yang_handler : YangHandler
    ) -> List[Tuple[str, Dict[str, Any]]]:
        LOGGER.debug('[parse] json_data = {:s}'.format(str(json_data)))
        response = []
        return response
