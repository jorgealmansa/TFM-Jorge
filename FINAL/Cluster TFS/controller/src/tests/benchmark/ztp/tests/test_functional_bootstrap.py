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
from common.proto.monitoring_pb2 import KpiDescriptorList
from common.tests.EventTools import EVENT_CREATE, EVENT_UPDATE, check_events
from common.tools.object_factory.Context import json_context_id
from common.tools.object_factory.Device import json_device_id
from common.tools.object_factory.Link import json_link_id
from common.tools.object_factory.Topology import json_topology_id
from context.client.ContextClient import ContextClient
from monitoring.client.MonitoringClient import MonitoringClient
from context.client.EventsCollector import EventsCollector
from common.proto.context_pb2 import Context, ContextId, Device, Empty, Topology
from device.client.DeviceClient import DeviceClient
from .Objects import CONTEXT_ID, CONTEXTS, DEVICES, TOPOLOGIES
from tests.Fixtures import context_client, device_client, monitoring_client

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_scenario_empty(context_client : ContextClient):  # pylint: disable=redefined-outer-name
    # ----- List entities - Ensure database is empty -------------------------------------------------------------------
    response = context_client.ListContexts(Empty())
    assert len(response.contexts) == 0

    response = context_client.ListDevices(Empty())
    assert len(response.devices) == 0


def test_prepare_scenario(context_client : ContextClient):  # pylint: disable=redefined-outer-name

    # ----- Create Contexts and Topologies -----------------------------------------------------------------------------
    for context in CONTEXTS:
        context_uuid = context['context_id']['context_uuid']['uuid']
        LOGGER.info('Adding Context {:s}'.format(context_uuid))
        response = context_client.SetContext(Context(**context))
        assert response.context_uuid.uuid == context_uuid

    for topology in TOPOLOGIES:
        context_uuid = topology['topology_id']['context_id']['context_uuid']['uuid']
        topology_uuid = topology['topology_id']['topology_uuid']['uuid']
        LOGGER.info('Adding Topology {:s}/{:s}'.format(context_uuid, topology_uuid))
        response = context_client.SetTopology(Topology(**topology))
        assert response.context_id.context_uuid.uuid == context_uuid
        assert response.topology_uuid.uuid == topology_uuid
        context_id = json_context_id(context_uuid)


def test_scenario_ready(context_client : ContextClient):  # pylint: disable=redefined-outer-name
    # ----- List entities - Ensure scenario is ready -------------------------------------------------------------------
    response = context_client.ListContexts(Empty())
    assert len(response.contexts) == len(CONTEXTS)

    response = context_client.ListTopologies(ContextId(**CONTEXT_ID))
    assert len(response.topologies) == len(TOPOLOGIES)

    response = context_client.ListDevices(Empty())
    assert len(response.devices) == 0


def test_devices_bootstraping(
    context_client : ContextClient, device_client : DeviceClient):  # pylint: disable=redefined-outer-name

    # ----- Create Devices and Validate Collected Events ---------------------------------------------------------------
    for device, connect_rules in DEVICES:
        device_uuid = device['device_id']['device_uuid']['uuid']
        LOGGER.info('Adding Device {:s}'.format(device_uuid))

        device_with_connect_rules = copy.deepcopy(device)
        device_with_connect_rules['device_config']['config_rules'].extend(connect_rules)
        response = device_client.AddDevice(Device(**device_with_connect_rules))
        assert response.device_uuid.uuid == device_uuid


def test_devices_bootstrapped(context_client : ContextClient):  # pylint: disable=redefined-outer-name
    # ----- List entities - Ensure bevices are created -----------------------------------------------------------------
    response = context_client.ListContexts(Empty())
    assert len(response.contexts) == len(CONTEXTS)

    response = context_client.ListTopologies(ContextId(**CONTEXT_ID))
    assert len(response.topologies) == len(TOPOLOGIES)

    response = context_client.ListDevices(Empty())
    assert len(response.devices) == len(DEVICES)


def test_links_created(context_client : ContextClient):  # pylint: disable=redefined-outer-name
    # ----- List entities - Ensure links are created -------------------------------------------------------------------
    response = context_client.ListContexts(Empty())
    assert len(response.contexts) == len(CONTEXTS)

    response = context_client.ListTopologies(ContextId(**CONTEXT_ID))
    assert len(response.topologies) == len(TOPOLOGIES)

    response = context_client.ListDevices(Empty())
    assert len(response.devices) == len(DEVICES)