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

import logging, os
from common.Constants import DEFAULT_CONTEXT_NAME
from common.proto.context_pb2 import ContextId, ServiceStatusEnum, ServiceTypeEnum
from common.tools.descriptor.Loader import DescriptorLoader, check_descriptor_load_results
from common.tools.grpc.Tools import grpc_message_to_json_string
from common.tools.object_factory.Context import json_context_id
from context.client.ContextClient import ContextClient
from device.client.DeviceClient import DeviceClient
from service.client.ServiceClient import ServiceClient
from tests.Fixtures import context_client, device_client, service_client        # pylint: disable=unused-import

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

DESCRIPTOR_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'descriptors', 'service-bidir.json')
ADMIN_CONTEXT_ID = ContextId(**json_context_id(DEFAULT_CONTEXT_NAME))

def test_service_creation_bidir(
    context_client : ContextClient, # pylint: disable=redefined-outer-name
    device_client  : DeviceClient,  # pylint: disable=redefined-outer-name
    service_client : ServiceClient, # pylint: disable=redefined-outer-name
):
    # Load descriptors and validate the base scenario
    descriptor_loader = DescriptorLoader(
        descriptors_file=DESCRIPTOR_FILE, context_client=context_client, device_client=device_client,
        service_client=service_client
    )
    results = descriptor_loader.process()
    check_descriptor_load_results(results, descriptor_loader)

    # Verify the scenario has 1 service and 0 slices
    response = context_client.GetContext(ADMIN_CONTEXT_ID)
    assert len(response.service_ids) == 1
    assert len(response.slice_ids) == 0

    # Check there are no slices
    response = context_client.ListSlices(ADMIN_CONTEXT_ID)
    LOGGER.warning('Slices[{:d}] = {:s}'.format(len(response.slices), grpc_message_to_json_string(response)))
    assert len(response.slices) == 0

    # Check there is 1 service
    response = context_client.ListServices(ADMIN_CONTEXT_ID)
    LOGGER.warning('Services[{:d}] = {:s}'.format(len(response.services), grpc_message_to_json_string(response)))
    assert len(response.services) == 1

    for service in response.services:
        service_id = service.service_id
        assert service.service_status.service_status == ServiceStatusEnum.SERVICESTATUS_ACTIVE

        response = context_client.ListConnections(service_id)
        LOGGER.warning('  ServiceId[{:s}] => Connections[{:d}] = {:s}'.format(
            grpc_message_to_json_string(service_id), len(response.connections), grpc_message_to_json_string(response)))

        if service.service_type == ServiceTypeEnum.SERVICETYPE_OPTICAL_CONNECTIVITY:
            assert len(response.connections) == 2
        else:
            str_service = grpc_message_to_json_string(service)
            raise Exception('Unexpected ServiceType: {:s}'.format(str_service))
