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

import logging

from websockets.sync.server import serve
from common.proto.vnt_manager_pb2 import VNTSubscriptionRequest
from common.Settings import get_setting
from context.client.ContextClient import ContextClient
from common.Constants import DEFAULT_CONTEXT_NAME, DEFAULT_TOPOLOGY_NAME
from common.tools.object_factory.Topology import json_topology_id
from common.tools.object_factory.Context import json_context_id
from common.proto.context_pb2 import ContextId, TopologyId
import json
import os
from vnt_manager.client.VNTManagerClient import VNTManagerClient

JSON_ADMIN_CONTEXT_ID = json_context_id(DEFAULT_CONTEXT_NAME)
ADMIN_CONTEXT_ID = ContextId(**JSON_ADMIN_CONTEXT_ID)
ADMIN_TOPOLOGY_ID = TopologyId(**json_topology_id(DEFAULT_TOPOLOGY_NAME, context_id=JSON_ADMIN_CONTEXT_ID))

vnt_manager_client: VNTManagerClient =  VNTManagerClient()
context_client:     ContextClient =     ContextClient()   

ALL_HOSTS = "0.0.0.0"
WS_E2E_PORT = int(get_setting('WS_E2E_PORT', default='8762'))

LOGGER = logging.getLogger(__name__)


def register_context_subscription():
    with serve(subcript_to_vnt_manager, ALL_HOSTS, WS_E2E_PORT, logger=LOGGER) as server:
        LOGGER.info("Running subscription server...: {}:{}".format(ALL_HOSTS, str(WS_E2E_PORT)))
        server.serve_forever()
        LOGGER.info("Exiting subscription server...")


def subcript_to_vnt_manager(websocket):
    for message in websocket:
        LOGGER.debug("Message received: {}".format(message))
        message_json = json.loads(message)
        request = VNTSubscriptionRequest()
        request.host = message_json['host']
        request.port = message_json['port']
        LOGGER.debug("Received gRPC from ws: {}".format(request))

        try:
            vntm_reply = vnt_manager_client.VNTSubscript(request)
            LOGGER.debug("Received gRPC from vntm: {}".format(vntm_reply))
        except Exception as e:
            LOGGER.error('Could not subscript to VTNManager: {}'.format(e))

        websocket.send(vntm_reply.subscription)
