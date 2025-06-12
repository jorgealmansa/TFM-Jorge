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
from typing import Dict, Set, Tuple
from common.Constants import DEFAULT_CONTEXT_NAME
from common.proto.context_pb2 import ContextId, ServiceStatusEnum, ServiceTypeEnum
from common.tools.grpc.Tools import grpc_message_to_json_string
from common.tools.object_factory.Context import json_context_id
from context.client.ContextClient import ContextClient
from .Fixtures import context_client        # pylint: disable=unused-import
from .Tools import do_rest_delete_request


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

REQUEST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'ietf-l3vpn-service.json')
ADMIN_CONTEXT_ID = ContextId(**json_context_id(DEFAULT_CONTEXT_NAME))


# pylint: disable=redefined-outer-name, unused-argument
def test_service_ietf_removal(
    context_client : ContextClient, # pylint: disable=redefined-outer-name
):
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

    service_uuids : Set[str] = set()
    for service in response.services:
        service_id = service.service_id
        assert service.service_status.service_status == ServiceStatusEnum.SERVICESTATUS_ACTIVE
        assert service.service_type == ServiceTypeEnum.SERVICETYPE_L3NM

        response = context_client.ListConnections(service_id)
        LOGGER.warning('  ServiceId[{:s}] => Connections[{:d}] = {:s}'.format(
            grpc_message_to_json_string(service_id), len(response.connections),
            grpc_message_to_json_string(response)
        ))
        assert len(response.connections) == 1

        service_uuids.add(service_id.service_uuid.uuid)

    # Identify service to delete
    assert len(service_uuids) == 1
    service_uuid = set(service_uuids).pop()

    URL = '/restconf/data/ietf-l3vpn-svc:l3vpn-svc/vpn-services/vpn-service={:s}/'.format(service_uuid)
    do_rest_delete_request(URL, logger=LOGGER, expected_status_codes={204})

    # Verify the scenario has no services/slices
    response = context_client.GetContext(ADMIN_CONTEXT_ID)
    assert len(response.service_ids) == 0
    assert len(response.slice_ids) == 0
