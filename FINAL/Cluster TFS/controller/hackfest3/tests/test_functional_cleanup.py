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

import copy, logging, pytest
from common.Settings import get_setting
from common.tests.EventTools import EVENT_REMOVE, check_events
from common.tools.object_factory.Context import json_context_id
from common.tools.object_factory.Device import json_device_id
from common.tools.object_factory.Link import json_link_id
from common.tools.object_factory.Topology import json_topology_id
from context.client.ContextClient import ContextClient
from context.client.EventsCollector import EventsCollector
from common.proto.context_pb2 import ConfigActionEnum, ContextId, Device, DeviceId, Empty, Link, LinkId, TopologyId, DeviceOperationalStatusEnum
from device.client.DeviceClient import DeviceClient
from .Objects import CONTEXT_ID, CONTEXTS, DEVICES, LINKS, TOPOLOGIES

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@pytest.fixture(scope='session')
def context_client():
    _client = ContextClient(get_setting('CONTEXTSERVICE_SERVICE_HOST'), get_setting('CONTEXTSERVICE_SERVICE_PORT_GRPC'))
    yield _client
    _client.close()


@pytest.fixture(scope='session')
def device_client():
    _client = DeviceClient(get_setting('DEVICESERVICE_SERVICE_HOST'), get_setting('DEVICESERVICE_SERVICE_PORT_GRPC'))
    yield _client
    _client.close()

def test_scenario_cleanup(
    context_client : ContextClient, device_client : DeviceClient):  # pylint: disable=redefined-outer-name

    for link in LINKS:
        link_uuid = link['link_id']['link_uuid']['uuid']
        LOGGER.info('Removing Link {:s}'.format(link_uuid))
        link_id = link['link_id']
        context_client.RemoveLink(LinkId(**link_id))

    # ----- Delete Devices and Validate Collected Events ---------------------------------------------------------------
    for device, _, _ in DEVICES:

        device_id = device['device_id']
        device_uuid = device_id['device_uuid']['uuid']
        LOGGER.info('Deleting Device {:s}'.format(device_uuid))
        LOGGER.info("yes")
        #device_client.DeleteDevice(DeviceId(**device_id))
        context_client.RemoveDevice(DeviceId(**device_id))

    response = context_client.ListDevices(Empty())
    assert len(response.devices) == 0
    

    # ----- Delete Topologies and Validate Collected Events ------------------------------------------------------------
    for topology in TOPOLOGIES:
        topology_id = topology['topology_id']
        context_uuid = topology_id['context_id']['context_uuid']['uuid']
        topology_uuid = topology_id['topology_uuid']['uuid']
        LOGGER.info('Deleting Topology {:s}/{:s}'.format(context_uuid, topology_uuid))
        context_client.RemoveTopology(TopologyId(**topology_id))
        context_id = json_context_id(context_uuid)

    # ----- Delete Contexts and Validate Collected Events --------------------------------------------------------------
    for context in CONTEXTS:
        context_id = context['context_id']
        context_uuid = context_id['context_uuid']['uuid']
        LOGGER.info('Deleting Context {:s}'.format(context_uuid))
        context_client.RemoveContext(ContextId(**context_id))
