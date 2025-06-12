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

import os
from flask import Flask, request
from YangValidator import YangValidator

app = Flask(__name__)


yang_validator = YangValidator('etsi-qkd-sdn-node', ['etsi-qkd-node-types'])


nodes = {
    '10.0.2.10:11111': {'node': {
            'qkdn_id': '00000001-0000-0000-0000-000000000000',
        },
        'qkdn_capabilities': {
        },
        'qkd_applications': {
            'qkd_app': [
                {
                    'app_id': '00000001-0001-0000-0000-000000000000',           
                    'client_app_id': [],
                    'app_statistics': {
                        'statistics': []
                    },
                    'app_qos': {
                    },
                    'backing_qkdl_id': []
                }
            ]
        },
        'qkd_interfaces': {
            'qkd_interface': [
                {
                    'qkdi_id': '100',
                    'qkdi_att_point': {
                    },
                    'qkdi_capabilities': {
                    }
                },
                {
                    'qkdi_id': '101',
                    'qkdi_att_point': {
                        'device':'10.0.2.10',
                        'port':'1001'
                    },
                    'qkdi_capabilities': {
                    }
                }
            ]
        },
        'qkd_links': {
            'qkd_link': [

            ]
        }
    },

    '10.0.2.10:22222': {'node': {
            'qkdn_id': '00000002-0000-0000-0000-000000000000',
        },
        'qkdn_capabilities': {
        },
        'qkd_applications': {
            'qkd_app': [
                {
                    'app_id': '00000002-0001-0000-0000-000000000000',           
                    'client_app_id': [],
                    'app_statistics': {
                        'statistics': []
                    },
                    'app_qos': {
                    },
                    'backing_qkdl_id': []
                }
            ]
        },
        'qkd_interfaces': {
            'qkd_interface': [
                {
                    'qkdi_id': '200',
                    'qkdi_att_point': {
                    },
                    'qkdi_capabilities': {
                    }
                },
                {
                    'qkdi_id': '201',
                    'qkdi_att_point': {
                        'device':'10.0.2.10',
                        'port':'2001'
                    },
                    'qkdi_capabilities': {
                    }
                },
                {
                    'qkdi_id': '202',
                    'qkdi_att_point': {
                        'device':'10.0.2.10',
                        'port':'2002'
                    },
                    'qkdi_capabilities': {
                    }
                }
            ]
        },
        'qkd_links': {
            'qkd_link': [

            ] 
        }
    },

    '10.0.2.10:33333': {'node': {
            'qkdn_id': '00000003-0000-0000-0000-000000000000',
        },
        'qkdn_capabilities': {
        },
        'qkd_applications': {
            'qkd_app': [
                {
                    'app_id': '00000003-0001-0000-0000-000000000000',           
                    'client_app_id': [],
                    'app_statistics': {
                        'statistics': []
                    },
                    'app_qos': {
                    },
                    'backing_qkdl_id': []
                }
            ]
        },
        'qkd_interfaces': {
            'qkd_interface': [
                {
                    'qkdi_id': '300',
                    'qkdi_att_point': {
                    },
                    'qkdi_capabilities': {
                    }
                },
                {
                    'qkdi_id': '301',
                    'qkdi_att_point': {
                        'device':'10.0.2.10',
                        'port':'3001'
                    },
                    'qkdi_capabilities': {
                    }
                }
            ]
        },
        'qkd_links': {
            'qkd_link': [

            ]
        }
    }
}


def get_side_effect(url):

    steps = url.lstrip('https://').lstrip('http://').rstrip('/')
    ip_port, _, _, header, *steps = steps.split('/')

    header_splitted = header.split(':')

    module = header_splitted[0]
    assert(module == 'etsi-qkd-sdn-node')

    tree = {'qkd_node': nodes[ip_port]['node'].copy()}

    if len(header_splitted) == 1 or not header_splitted[1]:
        value = nodes[ip_port].copy()
        value.pop('node')
        tree['qkd_node'].update(value)

        return tree, tree
    
    root = header_splitted[1]
    assert(root == 'qkd_node')

    if not steps:
        return tree, tree


    endpoint, *steps = steps
    
    value = nodes[ip_port][endpoint]

    if not steps:
        return_value = {endpoint:value}
        tree['qkd_node'].update(return_value)

        return return_value, tree

    

    '''
    element, *steps = steps

    container, key = element.split('=')
    
    # value = value[container][key]

    if not steps:
        return_value['qkd_node'][endpoint] = [value]
        return return_value

    '''
    raise Exception('Url too long')

        

def edit(from_dict, to_dict, create):
    for key, value in from_dict.items():
        if isinstance(value, dict):
            if key not in to_dict and create:
                to_dict[key] = {}
            edit(from_dict[key], to_dict[key], create)
        elif isinstance(value, list):
            to_dict[key].extend(value)
        else:
            to_dict[key] = value



def edit_side_effect(url, json, create):
    steps = url.lstrip('https://').lstrip('http://').rstrip('/')
    ip_port, _, _, header, *steps = steps.split('/')

    module, root = header.split(':')

    assert(module == 'etsi-qkd-sdn-node')
    assert(root == 'qkd_node')

    if not steps:
        edit(json, nodes[ip_port]['node'])
        return

    endpoint, *steps = steps

    if not steps:
        edit(json[endpoint], nodes[ip_port][endpoint], create)
        return


    '''
    element, *steps = steps

    container, key = element.split('=')

    if not steps:
        if key not in nodes[ip_port][endpoint][container] and create:
            nodes[ip_port][endpoint][container][key] = {}

        edit(json, nodes[ip_port][endpoint][container][key], create)
        return 0
    '''
    
    raise Exception('Url too long')






@app.get('/', defaults={'path': ''})
@app.get("/<string:path>")
@app.get('/<path:path>')
def get(path):
    msg, msg_validate = get_side_effect(request.base_url)
    print(msg_validate)
    yang_validator.parse_to_dict(msg_validate)
    return msg


@app.post('/', defaults={'path': ''})
@app.post("/<string:path>")
@app.post('/<path:path>')
def post(path):
    success = True
    reason = ''
    try:
        edit_side_effect(request.base_url, request.json, True)
    except Exception as e:
        reason = str(e)
        success = False
    return {'success': success, 'reason': reason}
    


@app.route('/', defaults={'path': ''}, methods=['PUT', 'PATCH'])
@app.route("/<string:path>", methods=['PUT', 'PATCH'])
@app.route('/<path:path>', methods=['PUT', 'PATCH'])
def patch(path):
    success = True
    reason = ''
    try:
        edit_side_effect(request.base_url, request.json, False)
    except Exception as e:
        reason = str(e)
        success = False
    return {'success': success, 'reason': reason}





# import json
# from mock import requests
# import pyangbind.lib.pybindJSON as enc
# from pyangbind.lib.serialise import pybindJSONDecoder as dec
# from yang.sbi.qkd.templates.etsi_qkd_sdn_node import etsi_qkd_sdn_node

# module = etsi_qkd_sdn_node()
# url = 'https://1.1.1.1/restconf/data/etsi-qkd-sdn-node:'

# # Get node all info
# z = requests.get(url).json()
# var = dec.load_json(z, None, None, obj=module)
# print(enc.dumps(var))


# Reset module variable because it is already filled
# module = etsi_qkd_sdn_node()

# # Get node basic info
# node = module.qkd_node
# z = requests.get(url + 'qkd_node').json()
# var = dec.load_json(z, None, None, obj=node)
# print(enc.dumps(var))


# # Get all apps
# apps = node.qkd_applications
# z = requests.get(url + 'qkd_node/qkd_applications').json()
# var = dec.load_json(z, None, None, obj=apps)
# print(enc.dumps(var))

# # Edit app 0
# app = apps.qkd_app['00000000-0001-0000-0000-000000000000']
# app.client_app_id = 'id_0'
# requests.put(url + 'qkd_node/qkd_applications/qkd_app=00000000-0001-0000-0000-000000000000', json=json.loads(enc.dumps(app)))

# # Create app 1
# app = apps.qkd_app.add('00000000-0001-0000-0000-000000000001')
# requests.post(url + 'qkd_node/qkd_applications/qkd_app=00000000-0001-0000-0000-000000000001', json=json.loads(enc.dumps(app)))

# # Get all apps
# apps = node.qkd_applications
# z = requests.get(url + 'qkd_node/qkd_applications').json()
# var = dec.load_json(z, None, None, obj=apps)
# print(enc.dumps(var))
