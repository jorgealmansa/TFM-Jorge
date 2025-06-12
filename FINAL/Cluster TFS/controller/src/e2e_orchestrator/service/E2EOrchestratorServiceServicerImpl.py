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

import copy
from common.method_wrappers.Decorator import MetricsPool, safe_and_metered_rpc_method
from common.proto.e2eorchestrator_pb2 import E2EOrchestratorRequest, E2EOrchestratorReply
from common.proto.context_pb2 import (
    Empty, Connection, EndPointId, Link, LinkId, TopologyDetails, Topology, Context, Service, ServiceId,
    ServiceTypeEnum, ServiceStatusEnum)
from common.proto.e2eorchestrator_pb2_grpc import E2EOrchestratorServiceServicer
from common.Settings import get_setting
from context.client.ContextClient import ContextClient
from service.client.ServiceClient import ServiceClient
from context.service.database.uuids.EndPoint import endpoint_get_uuid
from context.service.database.uuids.Device import device_get_uuid
from common.proto.vnt_manager_pb2 import VNTSubscriptionRequest
from common.tools.grpc.Tools import grpc_message_to_json_string
import grpc
import json
import logging
import networkx as nx
from threading import Thread
from websockets.sync.client import connect
from websockets.sync.server import serve
from common.Constants import DEFAULT_CONTEXT_NAME


LOGGER = logging.getLogger(__name__)
logging.getLogger("websockets").propagate = True

METRICS_POOL = MetricsPool("E2EOrchestrator", "RPC")


context_client: ContextClient = ContextClient()
service_client: ServiceClient = ServiceClient()

EXT_HOST = str(get_setting('WS_IP_HOST'))
EXT_PORT = str(get_setting('WS_IP_PORT'))

OWN_HOST = str(get_setting('WS_E2E_HOST'))
OWN_PORT = str(get_setting('WS_E2E_PORT'))


ALL_HOSTS = "0.0.0.0"

class SubscriptionServer(Thread):
    def __init__(self):
        Thread.__init__(self)
            
    def run(self):
        url = "ws://" + EXT_HOST + ":" + EXT_PORT
        request = VNTSubscriptionRequest()
        request.host = OWN_HOST
        request.port = OWN_PORT
        try: 
            LOGGER.debug("Trying to connect to {}".format(url))
            websocket = connect(url)
        except Exception as ex:
            LOGGER.error('Error connecting to {}'.format(url))
        else:
            with websocket:
                LOGGER.debug("Connected to {}".format(url))
                send = grpc_message_to_json_string(request)
                websocket.send(send)
                LOGGER.debug("Sent: {}".format(send))
                try:
                    message = websocket.recv()
                    LOGGER.debug("Received message from WebSocket: {}".format(message))
                except Exception as ex:
                    LOGGER.error('Exception receiving from WebSocket: {}'.format(ex))

            self._events_server()


    def _events_server(self):
        all_hosts = "0.0.0.0"

        try:
            server = serve(self._event_received, all_hosts, int(OWN_PORT))
        except Exception as ex:
            LOGGER.error('Error starting server on {}:{}'.format(all_hosts, OWN_PORT))
            LOGGER.error('Exception!: {}'.format(ex))
        else:
            with server:
                LOGGER.info("Running events server...: {}:{}".format(all_hosts, OWN_PORT))
                server.serve_forever()


    def _event_received(self, connection):
        LOGGER.info("EVENT received!")
        for message in connection:
            message_json = json.loads(message)
            # LOGGER.info("message_json: {}".format(message_json))

            # Link creation
            if 'link_id' in message_json:
                link = Link(**message_json)

                service = Service()
                service.service_id.service_uuid.uuid = link.link_id.link_uuid.uuid
                service.service_id.context_id.context_uuid.uuid = DEFAULT_CONTEXT_NAME
                service.service_type = ServiceTypeEnum.SERVICETYPE_OPTICAL_CONNECTIVITY
                service.service_status.service_status = ServiceStatusEnum.SERVICESTATUS_PLANNED
                service_client.CreateService(service)

                links = context_client.ListLinks(Empty()).links
                a_device_uuid = device_get_uuid(link.link_endpoint_ids[0].device_id)
                a_endpoint_uuid = endpoint_get_uuid(link.link_endpoint_ids[0])[2]
                z_device_uuid = device_get_uuid(link.link_endpoint_ids[1].device_id)
                z_endpoint_uuid = endpoint_get_uuid(link.link_endpoint_ids[1])[2]

                for _link in links:
                    for _endpoint_id in _link.link_endpoint_ids:
                        if _endpoint_id.device_id.device_uuid.uuid == a_device_uuid and \
                        _endpoint_id.endpoint_uuid.uuid == a_endpoint_uuid:
                            a_ep_id = _endpoint_id
                        elif _endpoint_id.device_id.device_uuid.uuid == z_device_uuid and \
                        _endpoint_id.endpoint_uuid.uuid == z_endpoint_uuid:
                            z_ep_id = _endpoint_id

                if (not 'a_ep_id' in locals()) or (not 'z_ep_id' in locals()):
                    error_msg = 'Could not get VNT link endpoints'
                    LOGGER.error(error_msg)
                    connection.send(error_msg)
                    return

                service.service_endpoint_ids.append(copy.deepcopy(a_ep_id))
                service.service_endpoint_ids.append(copy.deepcopy(z_ep_id))

                # service_client.UpdateService(service)
                connection.send(grpc_message_to_json_string(link))
            # Link removal
            elif 'link_uuid' in message_json:
                LOGGER.info('REMOVING VIRTUAL LINK')
                link_id = LinkId(**message_json)

                service_id = ServiceId()
                service_id.service_uuid.uuid = link_id.link_uuid.uuid
                service_id.context_id.context_uuid.uuid = DEFAULT_CONTEXT_NAME
                # service_client.DeleteService(service_id)
                connection.send(grpc_message_to_json_string(link_id))
                context_client.RemoveLink(link_id)
            # Topology received
            else:
                LOGGER.info('TOPOLOGY')
                topology_details = TopologyDetails(**message_json)

                context = Context()
                context.context_id.context_uuid.uuid = topology_details.topology_id.context_id.context_uuid.uuid
                context_client.SetContext(context)

                topology = Topology()
                topology.topology_id.context_id.CopyFrom(context.context_id)
                topology.topology_id.topology_uuid.uuid = topology_details.topology_id.topology_uuid.uuid
                context_client.SetTopology(topology)

                for device in topology_details.devices:
                    context_client.SetDevice(device)

                for link in topology_details.links:
                    context_client.SetLink(link)



class E2EOrchestratorServiceServicerImpl(E2EOrchestratorServiceServicer):
    def __init__(self):
        LOGGER.debug("Creating Servicer...")
        try:
            LOGGER.debug("Requesting subscription")
            sub_server = SubscriptionServer()
            sub_server.start()
            LOGGER.debug("Servicer Created")

        except Exception as ex:
            LOGGER.info("Exception!: {}".format(ex))


        
    @safe_and_metered_rpc_method(METRICS_POOL, LOGGER)
    def Compute(self, request: E2EOrchestratorRequest, context: grpc.ServicerContext) -> E2EOrchestratorReply:
        endpoints_ids = []
        for endpoint_id in request.service.service_endpoint_ids:
            endpoints_ids.append(endpoint_get_uuid(endpoint_id)[2])

        graph = nx.Graph()

        devices = context_client.ListDevices(Empty()).devices

        for device in devices:
            endpoints_uuids = [endpoint.endpoint_id.endpoint_uuid.uuid
                               for endpoint in device.device_endpoints]
            for ep in endpoints_uuids:
                graph.add_node(ep)

            for ep in endpoints_uuids:
                for ep_i in endpoints_uuids:
                    if ep == ep_i:
                        continue
                    graph.add_edge(ep, ep_i)

        links = context_client.ListLinks(Empty()).links
        for link in links:
            eps = []
            for endpoint_id in link.link_endpoint_ids:
                eps.append(endpoint_id.endpoint_uuid.uuid)
            graph.add_edge(eps[0], eps[1])


        shortest = nx.shortest_path(graph, endpoints_ids[0], endpoints_ids[1])

        path = E2EOrchestratorReply()
        path.services.append(copy.deepcopy(request.service))
        for i in range(0, int(len(shortest)/2)):
            conn = Connection()
            ep_a_uuid = str(shortest[i*2])
            ep_z_uuid = str(shortest[i*2+1])

            conn.connection_id.connection_uuid.uuid = str(ep_a_uuid) + '_->_' + str(ep_z_uuid)

            ep_a_id = EndPointId()
            ep_a_id.endpoint_uuid.uuid = ep_a_uuid
            conn.path_hops_endpoint_ids.append(ep_a_id)

            ep_z_id = EndPointId()
            ep_z_id.endpoint_uuid.uuid = ep_z_uuid
            conn.path_hops_endpoint_ids.append(ep_z_id)

            path.connections.append(conn)

        return path
