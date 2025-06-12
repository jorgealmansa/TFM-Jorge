# Copyright 2022-2023 ETSI TeraFlowSDN - TFS OSG (https://tfs.etsi.org/)
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

"""
P4 service handler for the TeraFlowSDN controller.
"""
#import yaml
import json
import logging
from typing import Any, List, Optional, Tuple, Union
from common.method_wrappers.Decorator import MetricsPool, metered_subclass_method
from common.proto.context_pb2 import ConfigRule, DeviceId, Service
from common.tools.object_factory.ConfigRule import json_config_rule_delete, json_config_rule_set
from common.tools.object_factory.Device import json_device_id
from common.type_checkers.Checkers import chk_type
from service.service.service_handler_api._ServiceHandler import _ServiceHandler
from service.service.task_scheduler.TaskExecutor import TaskExecutor

LOGGER = logging.getLogger(__name__)

METRICS_POOL = MetricsPool('Service', 'Handler', labels={'handler': 'p4'})

# def load_switches_conf(ssl):
#     keys=[]
#     with open('~/controller/src/tests/hackfest3/pot/switches.json', 'r') as json_file:
#         #data = json.load(json_file)
#         data = yaml.safe_load(json_file)
#     return data


def create_routing_set(rule):
    return json_config_rule_set(
        'table',
        {
            'table-name': "PoT.routing_table",
            'match-fields' : [
                {
                    'match-field': 'hdr.inner_ipv4.dstAddr',
                    'match-value': rule["match"]["dstAddr"]

                },
                {
                    'match-field': 'standard_metadata.ingress_port',
                    'match-value': str(rule["match"]["ingress_port"]) 
                }
            ],
            'action-name': 'PoT.ipv4_forward',
            'action-params': [
                    {
                        'action-param': 'srcAddr',
                        'action-value': rule["action_params"]["srcAddr"]
                    },
                    {
                        'action-param': 'dstAddr',
                        'action-value': rule["action_params"]["dstAddr"]
                    },
                    {
                        'action-param': 'port',
                        'action-value': str(rule["action_params"]["port"]) 
                    }
            ]
        }
    )

def create_ingress_pot_set(rule):
    return json_config_rule_set(
        'table',
        {
            'table-name': "PoT.t_pot",
            'match-fields' : [
                {
                    'match-field': 'hdr.nshPot.servicePathIdentifier',
                    'match-value': str(rule["match"]["servicePathIdentifier"])
                },
                {
                    'match-field': 'hdr.nshPot.serviceIndex',
                    'match-value': str(rule["match"]["serviceIndex"])
                },
                {
                    'match-field': 'hdr.ipv4.dstAddr',
                    'match-value': rule["match"]["dstAddr"]
                }
            ],
            'action-name': 'PoT.pot_ingress',
            'action-params': [
                    {
                        'action-param': 'prime',
                        'action-value': str(rule["action_params"]["prime"])
                    },
                    {
                        'action-param': 'identifier',
                        'action-value': str(rule["action_params"]["identifier"])
                    },
                    {
                        'action-param': 'serviceIndex',
                        'action-value': str(rule["action_params"]["serviceIndex"])
                    },
                    {
                        'action-param': 'secretShare',
                        'action-value': str(rule["action_params"]["secretShare"])
                    },
                    {
                        'action-param': 'publicPol',
                        'action-value': str(rule["action_params"]["publicPol"])
                    },
                    {
                        'action-param': 'lpc',
                        'action-value': str(rule["action_params"]["lpc"])
                    },
                    {
                        'action-param': 'upstreamMask',
                        'action-value': str(rule["action_params"]["upstreamMask"])
                    },
                    {
                        'action-param': 'magic_M',
                        'action-value': str(rule["action_params"]["magic_M"])
                    },
                    {
                        'action-param': 'magic_a',
                        'action-value': str(rule["action_params"]["magic_a"])
                    },
                    {
                        'action-param': 'magic_s',
                        'action-value': str(rule["action_params"]["magic_s"])
                    }
            ]
        }
    )

def create_forward_pot_set(rule):
    return json_config_rule_set(
        'table',
        {
            'table-name': "PoT.t_pot",
            'match-fields' : [
                {
                    'match-field': 'hdr.nshPot.servicePathIdentifier',
                    'match-value': str(rule["match"]["servicePathIdentifier"])
                },
                {
                    'match-field': 'hdr.nshPot.serviceIndex',
                    'match-value': str(rule["match"]["serviceIndex"])
                },
                {
                    'match-field': 'hdr.ipv4.dstAddr',
                    'match-value': rule["match"]["dstAddr"]
                }
            ],
            'action-name': 'PoT.pot_forward',
            'action-params': [
                    {
                        'action-param': 'prime',
                        'action-value': str(rule["action_params"]["prime"])
                    },
                    {
                        'action-param': 'secretShare',
                        'action-value': str(rule["action_params"]["secretShare"])
                    },
                    {
                        'action-param': 'publicPol',
                        'action-value': str(rule["action_params"]["publicPol"])
                    },
                    {
                        'action-param': 'lpc',
                        'action-value': str(rule["action_params"]["lpc"])
                    },
                    {
                        'action-param': 'upstreamMask',
                        'action-value': str(rule["action_params"]["upstreamMask"])
                    },                
                    {
                        'action-param': 'downstreamMask',
                        'action-value': str(rule["action_params"]["downstreamMask"])
                    },
                    {
                        'action-param': 'magic_M',
                        'action-value': str(rule["action_params"]["magic_M"])
                    },
                    {
                        'action-param': 'magic_a',
                        'action-value': str(rule["action_params"]["magic_a"])
                    },
                    {
                        'action-param': 'magic_s',
                        'action-value': str(rule["action_params"]["magic_s"])
                    }
            ]
        }
    )

def create_egress_pot_set(rule):
    return json_config_rule_set(
        'table',
        {
            'table-name': "PoT.t_pot",
            'match-fields' : [
                {
                    'match-field': 'hdr.nshPot.servicePathIdentifier',
                    'match-value': str(rule["match"]["servicePathIdentifier"])
                },
                {
                    'match-field': 'hdr.nshPot.serviceIndex',
                    'match-value': str(rule["match"]["serviceIndex"])
                },
                {
                    'match-field': 'hdr.ipv4.dstAddr',
                    'match-value': rule["match"]["dstAddr"]
                }
            ],
            'action-name': 'PoT.pot_egress',
            'action-params': [
                    {
                        'action-param': 'prime',
                        'action-value': str(rule["action_params"]["prime"])
                    },
                    {
                        'action-param': 'secretShare',
                        'action-value': str(rule["action_params"]["secretShare"])
                    },
                    {
                        'action-param': 'publicPol',
                        'action-value': str(rule["action_params"]["publicPol"])
                    },
                    {
                        'action-param': 'lpc',
                        'action-value': str(rule["action_params"]["lpc"])
                    },
                    {
                        'action-param': 'validator_key',
                        'action-value': str(rule["action_params"]["validator_key"])
                    },                
                    {
                        'action-param': 'downstreamMask',
                        'action-value': str(rule["action_params"]["downstreamMask"])
                    },
                    {
                        'action-param': 'magic_M',
                        'action-value': str(rule["action_params"]["magic_M"])
                    },
                    {
                        'action-param': 'magic_a',
                        'action-value': str(rule["action_params"]["magic_a"])
                    },
                    {
                        'action-param': 'magic_s',
                        'action-value': str(rule["action_params"]["magic_s"])
                    }
            ]
        }
    )

#### ------------------------- CREAR NUEVAS FUNCIONES PARA AÑADIR METRICAS A LA INFLUXDB ------------------------------
def create_clone_session_set(rule):
    """
    Crea una regla de configuración para la clone session.
    Se espera que 'rule' tenga el siguiente formato:
      {
         "clone_session_id": <int>,
         "replicas": [
             { "egress_port": <int>, "instance": <int> },
             ...
         ]
      }
    """
    return json_config_rule_set(
        # ⬇  la clave adecuada para el driver P4
        'clone_session',
        rule
    )
    


def create_metrics_myegress_set(rule):
    LOGGER.info("Creando regla metrics_myegress con parámetros: %s", rule)
    rule_set = json_config_rule_set(
        'table',
        {
            'table-name': 'MyEgress.metrics_table',
            "default-action": True,
            'match-fields' : [],
            'action-name': 'MyEgress.send_metrics',
            'action-params': [
                {
                    'action-param': 'srcAddr',
                    'action-value': rule["action_params"]["srcAddr"]
                },
                {
                    'action-param': 'dstAddr',
                    'action-value': rule["action_params"]["dstAddr"]
                },
                {
                    'action-param': 'port',
                    'action-value': str(rule["action_params"]["port"])
                },
                {
                    'action-param': 'ipSrcAddr',
                    'action-value': rule["action_params"]["ipSrcAddr"]
                },
                {
                    'action-param': 'ipDstAddr',
                    'action-value': rule["action_params"]["ipDstAddr"]
                }
            ]
        }
    )
    LOGGER.debug("Regla metrics_myegress creada: %s", rule_set)
    return rule_set


def create_clone_pot_set(rule):
    LOGGER.info("Creando regla clone_pot con parámetros: %s", rule)
    rule_set = json_config_rule_set(
        'table',
        {
            'table-name': "PoT.clone_table",
            'match-fields': [
                {
                    'match-field': 'hdr.inner_ipv4.dstAddr',
                    'match-value': rule["match"]["dstAddr"]
                },
                {
                    'match-field': 'standard_metadata.ingress_port',
                    'match-value': str(rule["match"]["ingress_port"])
                }
            ],
            'action-name': 'PoT.do_clone',
            'action-params': []
        }
    )
    LOGGER.debug("Regla clone_pot creada: %s", rule_set)
    return rule_set
    
## ----------------------------------------------------------------
def create_rule_set(endpoint_a, endpoint_b):
    return json_config_rule_set(
        'table',
        {
            'table-name': 'IngressPipeImpl.l2_exact_table',
            'match-fields': [
                {
                    'match-field': 'standard_metadata.ingress_port',
                    'match-value': endpoint_a
                }
            ],
            'action-name': 'IngressPipeImpl.set_egress_port',
            'action-params': [
                {
                    'action-param': 'port',
                    'action-value': endpoint_b
                }
            ]
        }
    )

def create_rule_del(endpoint_a, endpoint_b):
    return json_config_rule_delete(
        'table',
        {
            'table-name': 'IngressPipeImpl.l2_exact_table',
            'match-fields': [
                {
                    'match-field': 'standard_metadata.ingress_port',
                    'match-value': endpoint_a
                }
            ],
            'action-name': 'IngressPipeImpl.set_egress_port',
            'action-params': [
                {
                    'action-param': 'port',
                    'action-value': endpoint_b
                }
            ]
        }
    )
    
def create_int_set(endpoint_a, id):
    return json_config_rule_set(
        'table',
        {
            'table-name': 'EgressPipeImpl.int_table',
       	    'match-fields': [
                {
                    'match-field': 'standard_metadata.ingress_port',
                    'match-value': endpoint_a
                }
            ],
            'action-name': 'EgressPipeImpl.add_int_header',
            'action-params': [
                {
                    'action-param': 'swid',
                    'action-value': id
                }
            ]
        }
    )
    
def create_int_del(endpoint_a, id):
    return json_config_rule_delete(
        'table',
        {
            'table-name': 'EgressPipeImpl.int_table',
       	    'match-fields': [
                {
                    'match-field': 'standard_metadata.ingress_port',
                    'match-value': endpoint_a
                }
            ],
            'action-name': 'EgressPipeImpl.add_int_header',
            'action-params': [
                {
                    'action-param': 'swid',
                    'action-value': id
                }
            ]
        }
    )

def find_names(uuid_a, uuid_b, device_endpoints):
    endpoint_a, endpoint_b = None, None
    for endpoint in device_endpoints:
        if endpoint.endpoint_id.endpoint_uuid.uuid == uuid_a:
            endpoint_a = endpoint.name
        elif endpoint.endpoint_id.endpoint_uuid.uuid == uuid_b:
            endpoint_b = endpoint.name
            
    return (endpoint_a, endpoint_b)

class P4ServiceHandler(_ServiceHandler):
    def __init__(self,
                 service: Service,
                 task_executor : TaskExecutor,
                 **settings) -> None:
        """ Initialize Driver.
            Parameters:
                service
                    The service instance (gRPC message) to be managed.
                task_executor
                    An instance of Task Executor providing access to the
                    service handlers factory, the context and device clients,
                    and an internal cache of already-loaded gRPC entities.
                **settings
                    Extra settings required by the service handler.
        """
        self.__service = service
        self.__task_executor = task_executor # pylint: disable=unused-private-member

    @metered_subclass_method(METRICS_POOL)
    def SetEndpoint(
        self, endpoints : List[Tuple[str, str, Optional[str]]],
        connection_uuid : Optional[str] = None
    ) -> List[Union[bool, Exception]]:
        """ Create/Update service endpoints form a list.
            Parameters:
                endpoints: List[Tuple[str, str, Optional[str]]]
                    List of tuples, each containing a device_uuid,
                    endpoint_uuid and, optionally, the topology_uuid
                    of the endpoint to be added.
                connection_uuid : Optional[str]
                    If specified, is the UUID of the connection this endpoint is associated to.
            Returns:
                results: List[Union[bool, Exception]]
                    List of results for endpoint changes requested.
                    Return values must be in the same order as the requested
                    endpoints. If an endpoint is properly added, True must be
                    returned; otherwise, the Exception that is raised during
                    the processing must be returned.
        """
        chk_type('endpoints', endpoints, list)
        if len(endpoints) == 0: return []

        service_uuid = self.__service.service_id.service_uuid.uuid

        history = {}

        #switches_conf = load_switches_conf()

        switches_conf = {
    "switches": [
        {
            "name": "ingressNode",
            "address": "10.0.0.11:50001",
            "device_id": 0,
            "proto_dump_file": "logs/ingressNode-p4runtime-requests.txt",
            "routing_rules": [
                {
                    "match": {
                        "dstAddr": "10.1.2.3",
                        "prefix_len": 32,
                        "ingress_port": 1
                    },
                    "action_params": {
                        "srcAddr": "02:42:0a:00:01:03",
                        "dstAddr": "02:42:0a:00:01:02",
                        "port": 2
                    }
                },
                {
                    "match": {
                        "dstAddr": "10.1.1.3",
                        "prefix_len": 32,
                        "ingress_port": 2
                    },
                    "action_params": {
                        "srcAddr": "02:42:0a:01:01:02",
                        "dstAddr": "02:42:0a:01:01:03",
                        "port": 1
                    }
                }
            ],
            "pot_ingress_rules": [
                {
                    "match": {
                        "servicePathIdentifier": 0,
                        "serviceIndex": 0,
                        "dstAddr": "10.1.2.3"
                    },
                    "action_params": {
                        "prime": 67,
                        "identifier": 55,
                        "serviceIndex": 4,
                        "secretShare": 27,
                        "publicPol": 39,
                        "lpc": 23,
                        "upstreamMask": 146869573393610114342393678683896652534,
                        "magic_M": 128207979,
                        "magic_a": 0,
                        "magic_s": 1
                    }
                }
            ],
            "pot_forward_rules": [],
            "pot_egress_rules": [
                {
                    "match": {
                        "servicePathIdentifier": 23,
                        "serviceIndex": 1,
                        "dstAddr": "10.1.1.3"
                    },
                    "action_params": {
                        "prime": 67,
                        "secretShare": 20,
                        "publicPol": 15,
                        "lpc": 14,
                        "downstreamMask": 143601276342503236205411786209848811681,
                        "validator_key": 41,
                        "magic_M": 128207979,
                        "magic_a": 0,
                        "magic_s": 1
                    }
                }
            ],
            "metrics_rules": [
                {
                    "action_params": {
                        "srcAddr": "02:42:0a:00:00:0b",
                        "dstAddr": "02:42:0a:00:00:0a",
                        "port": 3,
                        "ipSrcAddr": "10.0.0.11",
                        "ipDstAddr": "10.0.0.10"
                    }
                }
            ],
            "clone_rules": [
                {
                    "match": {
                        "dstAddr": "10.1.1.3",
                        "prefix_len": 32,
                        "ingress_port": 2
                    }
                },
                {
                    "match": {
                        "dstAddr": "10.1.2.3",
                        "prefix_len": 32,
                        "ingress_port": 1
                    }
                }
            ]
        },
        {
            "name": "middleNode1",
            "address": "10.0.0.12:50002",
            "device_id": 0,
            "proto_dump_file": "logs/middleNode1-p4runtime-requests.txt",
            "routing_rules": [
                {
                    "match": {
                        "dstAddr": "10.1.2.3",
                        "prefix_len": 32,
                        "ingress_port": 1
                    },
                    "action_params": {
                        "srcAddr": "02:42:0a:00:02:03",
                        "dstAddr": "02:42:0a:00:02:02",
                        "port": 2
                    }
                },
                {
                    "match": {
                        "dstAddr": "10.1.1.3",
                        "prefix_len": 32,
                        "ingress_port": 2
                    },
                    "action_params": {
                        "srcAddr": "02:42:0a:00:01:02",
                        "dstAddr": "02:42:0a:00:01:03",
                        "port": 1
                    }
                }
            ],
            "pot_ingress_rules": [],
            "pot_forward_rules": [
                {
                    "match": {
                        "servicePathIdentifier": 55,
                        "serviceIndex": 3,
                        "dstAddr": "10.1.2.3"
                    },
                    "action_params": {
                        "prime": 67,
                        "secretShare": 53,
                        "publicPol": 46,
                        "lpc": 64,
                        "upstreamMask": 15180578988935745112926307198552111400,
                        "downstreamMask": 146869573393610114342393678683896652534,
                        "magic_M": 128207979,
                        "magic_a": 0,
                        "magic_s": 1
                    }
                },
                {
                    "match": {
                        "servicePathIdentifier": 23,
                        "serviceIndex": 2,
                        "dstAddr": "10.1.1.3"
                    },
                    "action_params": {
                        "prime": 67,
                        "secretShare": 24,
                        "publicPol": 5,
                        "lpc": 34,
                        "upstreamMask": 143601276342503236205411786209848811681,
                        "downstreamMask": 298153798124507005819734556658846497010,
                        "magic_M": 128207979,
                        "magic_a": 0,
                        "magic_s": 1
                    }
                }
            ],
            "pot_egress_rules": [],
            "metrics_rules": [
                {
                    "action_params": {
                        "srcAddr": "02:42:0a:00:00:0c",
                        "dstAddr": "02:42:0a:00:00:0a",
                        "port": 3,
                        "ipSrcAddr": "10.0.0.12",
                        "ipDstAddr": "10.0.0.10"
                    }
                }
            ],
            "clone_rules": [
                {
                    "match": {
                        "dstAddr": "10.1.1.3",
                        "prefix_len": 32,
                        "ingress_port": 2
                    }
                },
                {
                    "match": {
                        "dstAddr": "10.1.2.3",
                        "prefix_len": 32,
                        "ingress_port": 1
                    }
                }
            ]
        },
        {
            "name": "middleNode2",
            "address": "10.0.0.13:50003",
            "device_id": 0,
            "proto_dump_file": "logs/middleNode2-p4runtime-requests.txt",
            "routing_rules": [
                {
                    "match": {
                        "dstAddr": "10.1.2.3",
                        "prefix_len": 32,
                        "ingress_port": 1
                    },
                    "action_params": {
                        "srcAddr": "02:42:0a:00:03:03",
                        "dstAddr": "02:42:0a:00:03:02",
                        "port": 2
                    }
                },
                {
                    "match": {
                        "dstAddr": "10.1.1.3",
                        "prefix_len": 32,
                        "ingress_port": 2
                    },
                    "action_params": {
                        "srcAddr": "02:42:0a:00:02:02",
                        "dstAddr": "02:42:0a:00:02:03",
                        "port": 1
                    }
                }
            ],
            "pot_ingress_rules": [],
            "pot_forward_rules": [
                {
                    "match": {
                        "servicePathIdentifier": 55,
                        "serviceIndex": 2,
                        "dstAddr": "10.1.2.3"
                    },
                    "action_params": {
                        "prime": 67,
                        "secretShare": 24,
                        "publicPol": 5,
                        "lpc": 34,
                        "upstreamMask": 56168529814869005761369283072504101980,
                        "downstreamMask": 15180578988935745112926307198552111400,
                        "magic_M": 128207979,
                        "magic_a": 0,
                        "magic_s": 1
                    }
                },
                {
                    "match": {
                        "servicePathIdentifier": 23,
                        "serviceIndex": 3,
                        "dstAddr": "10.1.1.3"
                    },
                    "action_params": {
                        "prime": 67,
                        "secretShare": 53,
                        "publicPol": 46,
                        "lpc": 64,
                        "upstreamMask": 298153798124507005819734556658846497010,
                        "downstreamMask": 37072395828899922671573580013679142842,
                        "magic_M": 128207979,
                        "magic_a": 0,
                        "magic_s": 1
                    }
                }
            ],
            "pot_egress_rules": [],
            "metrics_rules": [
                {
                    "action_params": {
                        "srcAddr": "02:42:0a:00:00:0d",
                        "dstAddr": "02:42:0a:00:00:0a",
                        "port": 3,
                        "ipSrcAddr": "10.0.0.13",
                        "ipDstAddr": "10.0.0.10"
                    }
                }
            ],
            "clone_rules": [
                {
                    "match": {
                        "dstAddr": "10.1.1.3",
                        "prefix_len": 32,
                        "ingress_port": 2
                    }
                },
                {
                    "match": {
                        "dstAddr": "10.1.2.3",
                        "prefix_len": 32,
                        "ingress_port": 1
                    }
                }
            ]
        },
        {
            "name": "egressNode",
            "address": "10.0.0.14:50004",
            "device_id": 0,
            "proto_dump_file": "logs/egressNode-p4runtime-requests.txt",
            "routing_rules": [
                {
                    "match": {
                        "dstAddr": "10.1.2.3",
                        "prefix_len": 32,
                        "ingress_port": 1
                    },
                    "action_params": {
                        "srcAddr": "02:42:0a:01:02:02",
                        "dstAddr": "02:42:0a:01:02:03",
                        "port": 2
                    }
                },
                {
                    "match": {
                        "dstAddr": "10.1.1.3",
                        "prefix_len": 32,
                        "ingress_port": 2
                    },
                    "action_params": {
                        "srcAddr": "02:42:0a:00:03:02",
                        "dstAddr": "02:42:0a:00:03:03",
                        "port": 1
                    }
                }
            ],
            "pot_ingress_rules": [
                {
                    "match": {
                        "servicePathIdentifier": 0,
                        "serviceIndex": 0,
                        "dstAddr": "10.1.1.3"
                    },
                    "action_params": {
                        "prime": 67,
                        "identifier": 23,
                        "serviceIndex": 4,
                        "secretShare": 27,
                        "publicPol": 39,
                        "lpc": 23,
                        "upstreamMask": 37072395828899922671573580013679142842,
                        "magic_M": 128207979,
                        "magic_a": 0,
                        "magic_s": 1
                    }
                }
            ],
            "pot_forward_rules": [],
            "pot_egress_rules": [
                {
                    "match": {
                        "servicePathIdentifier": 55,
                        "serviceIndex": 1,
                        "dstAddr": "10.1.2.3"
                    },
                    "action_params": {
                        "prime": 67,
                        "secretShare": 20,
                        "publicPol": 15,
                        "lpc": 14,
                        "downstreamMask": 56168529814869005761369283072504101980,
                        "validator_key": 41,
                        "magic_M": 128207979,
                        "magic_a": 0,
                        "magic_s": 1
                    }
                }
            ],
            "metrics_rules": [
                {
                    "action_params": {
                        "srcAddr": "02:42:0a:00:00:0e",
                        "dstAddr": "02:42:0a:00:00:0a",
                        "port": 3,
                        "ipSrcAddr": "10.0.0.14",
                        "ipDstAddr": "10.0.0.10"
                    }
                }
            ],
            "clone_rules": [
                {
                    "match": {
                        "dstAddr": "10.1.1.3",
                        "prefix_len": 32,
                        "ingress_port": 2
                    }
                },
                {
                    "match": {
                        "dstAddr": "10.1.2.3",
                        "prefix_len": 32,
                        "ingress_port": 1
                    }
                }
            ]
        }
    ]
}
        
        results = []
        index = {}
        i = 0
        for endpoint in endpoints:        
            device_uuid, endpoint_uuid = endpoint[0:2] # ignore topology_uuid by now
            if device_uuid in history:       
                try:
                    matched_endpoint_uuid = history.pop(device_uuid)
                    device = self.__task_executor.get_device(DeviceId(**json_device_id(device_uuid)))

                    del device.device_config.config_rules[:]
                    
                    # Find names from uuids
                    (endpoint_a, endpoint_b) = find_names(matched_endpoint_uuid, endpoint_uuid, device.device_endpoints)
                    if endpoint_a is None:
                        LOGGER.exception('Unable to find name of endpoint({:s})'.format(str(matched_endpoint_uuid)))
                        raise Exception('Unable to find name of endpoint({:s})'.format(str(matched_endpoint_uuid)))
                    if endpoint_b is None:
                        LOGGER.exception('Unable to find name of endpoint({:s})'.format(str(endpoint_uuid)))
                        raise Exception('Unable to find name of endpoint({:s})'.format(str(endpoint_uuid)))

                    # # One way
                    # rule = create_rule_set(endpoint_a, endpoint_b) 
                    # device.device_config.config_rules.append(ConfigRule(**rule))
                    # # The other way
                    # rule = create_rule_set(endpoint_b, endpoint_a) 
                    # device.device_config.config_rules.append(ConfigRule(**rule))
                    
                    #rule = create_int_set(endpoint_a, device.name[-1])
                    #device.device_config.config_rules.append(ConfigRule(**rule))

                    ###CREO QUE HABRÍA QUE LLAMAR A LAS REGLAS DEFINIDAS PREVIAMENTE AQUÍ
                    
                    switch = switches_conf["switches"][int(device.name[-1])-1]
                    LOGGER.info(device.name)

                    # LOGGER.exception("LOG para depurar")

                    # Routing rules
                    # LOGGER.exception("Reglas de routing")
                    for rule in switch["routing_rules"]:
                        ruledef = create_routing_set(rule)
                        device.device_config.config_rules.append(ConfigRule(**ruledef))

                    # LOGGER.exception("Reglas PoT de entrada")
                    for rule in switch["pot_ingress_rules"]:
                        ruledef = create_ingress_pot_set(rule)
                        device.device_config.config_rules.append(ConfigRule(**ruledef))
                    
                    # LOGGER.exception("Reglas PoT de forwarding")
                    for rule in switch["pot_forward_rules"]:
                        ruledef = create_forward_pot_set(rule)
                        device.device_config.config_rules.append(ConfigRule(**ruledef))
                    
                    LOGGER.info("Reglas Influx DB")
                    for rule in switch["metrics_rules"]:
                        ruledef = create_metrics_myegress_set(rule)
                        device.device_config.config_rules.append(ConfigRule(**ruledef))
                    
                    LOGGER.info("Clone rules")
                    for rule in switch["clone_rules"]:
                        ruledef = create_clone_pot_set(rule)
                        device.device_config.config_rules.append(ConfigRule(**ruledef))
                    
                    # LOGGER.exception("Reglas PoT de salida")
                    for rule in switch["pot_egress_rules"]:
                        ruledef = create_egress_pot_set(rule)
                        device.device_config.config_rules.append(ConfigRule(**ruledef))
                    
                    LOGGER.info("Clone session rule")
                    clone_session_ruledef = create_clone_session_set({
                        "clone_session_id": 1,
                        "replicas": [
                            { "egress_port": 3, "instance": 1 }
                        ]
                    })
                    device.device_config.config_rules.append(ConfigRule(**clone_session_ruledef))
                    

                    self.__task_executor.configure_device(device)
            
                    results.append(True)
                    results[index[device_uuid]] = True

                except Exception as e:
                    LOGGER.exception('Unable to SetEndpoint({:s})'.format(str(endpoint)))
                    results.append(e)
            else:
                history[device_uuid] = endpoint_uuid
                index[device_uuid] = i
                results.append(False)
            i = i+1

        return results

    @metered_subclass_method(METRICS_POOL)
    def DeleteEndpoint(
        self, endpoints : List[Tuple[str, str, Optional[str]]],
        connection_uuid : Optional[str] = None
    ) -> List[Union[bool, Exception]]:
        """ Delete service endpoints form a list.
            Parameters:
                endpoints: List[Tuple[str, str, Optional[str]]]
                    List of tuples, each containing a device_uuid,
                    endpoint_uuid, and the topology_uuid of the endpoint
                    to be removed.
                connection_uuid : Optional[str]
                    If specified, is the UUID of the connection this endpoint is associated to.
            Returns:
                results: List[Union[bool, Exception]]
                    List of results for endpoint deletions requested.
                    Return values must be in the same order as the requested
                    endpoints. If an endpoint is properly deleted, True must be
                    returned; otherwise, the Exception that is raised during
                    the processing must be returned.
        """
        chk_type('endpoints', endpoints, list)
        if len(endpoints) == 0: return []

        service_uuid = self.__service.service_id.service_uuid.uuid

        history = {}
        
        results = []
        index = {}
        i = 0
        for endpoint in endpoints:        
            device_uuid, endpoint_uuid = endpoint[0:2] # ignore topology_uuid by now
            if device_uuid in history:       
                try:
                    matched_endpoint_uuid = history.pop(device_uuid)
                    device = self.__task_executor.get_device(DeviceId(**json_device_id(device_uuid)))

                    del device.device_config.config_rules[:]

                    # Find names from uuids
                    (endpoint_a, endpoint_b) = find_names(matched_endpoint_uuid, endpoint_uuid, device.device_endpoints)
                    if endpoint_a is None:
                        LOGGER.exception('Unable to find name of endpoint({:s})'.format(str(matched_endpoint_uuid)))
                        raise Exception('Unable to find name of endpoint({:s})'.format(str(matched_endpoint_uuid)))
                    if endpoint_b is None:
                        LOGGER.exception('Unable to find name of endpoint({:s})'.format(str(endpoint_uuid)))
                        raise Exception('Unable to find name of endpoint({:s})'.format(str(endpoint_uuid)))

                    # One way
                    #rule = create_rule_del(endpoint_a, endpoint_b) 
                    #device.device_config.config_rules.append(ConfigRule(**rule))
                    # The other way
                    #rule = create_rule_del(endpoint_b, endpoint_a) 
                    #device.device_config.config_rules.append(ConfigRule(**rule))

                    #rule = create_int_del(endpoint_a, device.name[-1])
                    #device.device_config.config_rules.append(ConfigRule(**rule))

                    self.__task_executor.configure_device(device)
            
                    results.append(True)
                    results[index[device_uuid]] = True
                except Exception as e:
                    LOGGER.exception('Unable to SetEndpoint({:s})'.format(str(endpoint)))
                    results.append(e)
            else:
                history[device_uuid] = endpoint_uuid
                index[device_uuid] = i
                results.append(False)
            i = i+1

        return results

    @metered_subclass_method(METRICS_POOL)
    def SetConstraint(self, constraints: List[Tuple[str, Any]]) \
            -> List[Union[bool, Exception]]:
        """ Create/Update service constraints.
            Parameters:
                constraints: List[Tuple[str, Any]]
                    List of tuples, each containing a constraint_type and the
                    new constraint_value to be set.
            Returns:
                results: List[Union[bool, Exception]]
                    List of results for constraint changes requested.
                    Return values must be in the same order as the requested
                    constraints. If a constraint is properly set, True must be
                    returned; otherwise, the Exception that is raised during
                    the processing must be returned.
        """
        chk_type('constraints', constraints, list)
        if len(constraints) == 0: return []

        msg = '[SetConstraint] Method not implemented. Constraints({:s}) are being ignored.'
        LOGGER.warning(msg.format(str(constraints)))
        return [True for _ in range(len(constraints))]

    @metered_subclass_method(METRICS_POOL)
    def DeleteConstraint(self, constraints: List[Tuple[str, Any]]) \
            -> List[Union[bool, Exception]]:
        """ Delete service constraints.
            Parameters:
                constraints: List[Tuple[str, Any]]
                    List of tuples, each containing a constraint_type pointing
                    to the constraint to be deleted, and a constraint_value
                    containing possible additionally required values to locate
                    the constraint to be removed.
            Returns:
                results: List[Union[bool, Exception]]
                    List of results for constraint deletions requested.
                    Return values must be in the same order as the requested
                    constraints. If a constraint is properly deleted, True must
                    be returned; otherwise, the Exception that is raised during
                    the processing must be returned.
        """
        chk_type('constraints', constraints, list)
        if len(constraints) == 0: return []

        msg = '[DeleteConstraint] Method not implemented. Constraints({:s}) are being ignored.'
        LOGGER.warning(msg.format(str(constraints)))
        return [True for _ in range(len(constraints))]

    @metered_subclass_method(METRICS_POOL)
    def SetConfig(self, resources: List[Tuple[str, Any]]) \
            -> List[Union[bool, Exception]]:
        """ Create/Update configuration for a list of service resources.
            Parameters:
                resources: List[Tuple[str, Any]]
                    List of tuples, each containing a resource_key pointing to
                    the resource to be modified, and a resource_value
                    containing the new value to be set.
            Returns:
                results: List[Union[bool, Exception]]
                    List of results for resource key changes requested.
                    Return values must be in the same order as the requested
                    resource keys. If a resource is properly set, True must be
                    returned; otherwise, the Exception that is raised during
                    the processing must be returned.
        """
        chk_type('resources', resources, list)
        if len(resources) == 0: return []

        msg = '[SetConfig] Method not implemented. Resources({:s}) are being ignored.'
        LOGGER.warning(msg.format(str(resources)))
        return [True for _ in range(len(resources))]

    @metered_subclass_method(METRICS_POOL)
    def DeleteConfig(self, resources: List[Tuple[str, Any]]) \
            -> List[Union[bool, Exception]]:
        """ Delete configuration for a list of service resources.
            Parameters:
                resources: List[Tuple[str, Any]]
                    List of tuples, each containing a resource_key pointing to
                    the resource to be modified, and a resource_value containing
                    possible additionally required values to locate the value
                    to be removed.
            Returns:
                results: List[Union[bool, Exception]]
                    List of results for resource key deletions requested.
                    Return values must be in the same order as the requested
                    resource keys. If a resource is properly deleted, True must
                    be returned; otherwise, the Exception that is raised during
                    the processing must be returned.
        """
        chk_type('resources', resources, list)
        if len(resources) == 0: return []

        msg = '[SetConfig] Method not implemented. Resources({:s}) are being ignored.'
        LOGGER.warning(msg.format(str(resources)))
        return [True for _ in range(len(resources))]
