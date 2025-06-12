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
import json
import logging
import ssl
import uuid
from typing import Dict
from flask.json import jsonify
from flask_restful import Resource
from flask import request

from common.Constants import DEFAULT_CONTEXT_NAME
from common.proto.context_pb2 import Slice, SliceStatusEnum, EndPointId, Constraint
from common.tools.grpc.Tools import grpc_message_to_json
from ..tools.Authentication import HTTP_AUTH
from ..tools.HttpStatusCodes import HTTP_BADREQUEST, HTTP_OK, HTTP_CREATED, HTTP_SERVERERROR
from werkzeug.exceptions import UnsupportedMediaType

from slice.client.SliceClient import SliceClient
from .bindings import load_json_data
from .bindings.network_slice_services import NetworkSliceServices

LOGGER = logging.getLogger(__name__)

class NSS_Services(Resource):
    @HTTP_AUTH.login_required
    def get(self):    
        response = jsonify({"message": "All went well!"})
        # TODO Return list of current network-slice-services
        return response

    @HTTP_AUTH.login_required
    def post(self):
        if not request.is_json:
            raise UnsupportedMediaType('JSON payload is required')
        request_data = json.dumps(request.json)
        response = jsonify({})
        response.status_code = HTTP_CREATED

        slices: NetworkSliceServices = load_json_data(request_data, NetworkSliceServices)[0]
        for ietf_slice in slices.slice_service:
            slice_request: Slice = Slice()
            # Meta information
            # TODO implement name and owner based on "tags"
            slice_request.slice_id.context_id.context_uuid.uuid = DEFAULT_CONTEXT_NAME
            slice_request.slice_id.slice_uuid.uuid = ietf_slice.service_id()
            # TODO map with admin status of IETF Slice
            slice_request.slice_status.slice_status = SliceStatusEnum.SLICESTATUS_PLANNED

            list_endpoints = []
            for sdp in ietf_slice.sdps().sdp:
                endpoint = EndPointId()
                endpoint.topology_id.context_id.context_uuid.uuid = DEFAULT_CONTEXT_NAME
                endpoint.device_id.device_uuid.uuid = sdp.node_id()
                endpoint.endpoint_uuid.uuid = sdp.sdp_id()
                list_endpoints.append(endpoint)
            slice_request.slice_endpoint_ids.extend(list_endpoints)

            # TODO Map connectivity_groups and connectivity constructs to real connections
            LOGGER.debug(f"Connection groups detected: {len(ietf_slice.connection_groups().connection_group())}")
            list_constraints = []
            for cg in ietf_slice.connection_groups().connection_group:
                for cc in cg.connectivity_construct:
                    if cc.slo_sle_policy.custom:
                        with cc.slo_sle_policy.custom as slo:
                            for metric_bound in slo.service_slo_sle_policy().metric_bounds().metric_bound:
                                metric_type = str(metric_bound.metric_type()).casefold()
                                if metric_type == "service-slo-two-way-bandwidth":  # TODO fix to two way!
                                    constraint = Constraint()
                                    metric_unit = metric_bound.metric_unit().casefold()
                                    capacity = float(metric_bound.bound())  # Assuming capacity already in Gbps
                                    if metric_unit == "mbps":
                                        capacity /= 1E3
                                    elif metric_unit != "gbps":
                                        LOGGER.warning(f"Invalided metric unit ({metric_bound.metric_unit()}), must be Mbps or Gbps")
                                        response.status_code = HTTP_SERVERERROR
                                        return response
                                    constraint.sla_capacity.capacity_gbps = capacity
                                    list_constraints.append(constraint)

                                elif metric_type == "service-slo-one-way-delay":
                                    if metric_bound.metric_unit().casefold() == "ms":
                                        latency = int(metric_bound.bound())
                                    else:
                                        LOGGER.warning(f"Invalided metric unit ({metric_bound.metric_unit()}), must be \"ms\" ")
                                        response.status_code = HTTP_SERVERERROR
                                        return response
                                    constraint = Constraint()
                                    constraint.sla_latency.e2e_latency_ms = latency
                                    list_constraints.append(constraint)

                                elif metric_type == "service-slo-availability":
                                    availability = float(metric_bound.bound())
                                    if availability > 100.0 or availability < 0.0:
                                        raise Exception(f'Slice SLO availability ({availability}) must be constrained [0,100]')
                                    constraint = Constraint()
                                    constraint.sla_availability.availability = availability
                                    # TODO not really necessary, remove after OFC2023
                                    constraint.sla_availability.num_disjoint_paths = 0
                                    constraint.sla_availability.all_active = False
                                    list_constraints.append(constraint)

            slice_request.slice_constraints.extend(list_constraints)
            LOGGER.debug(grpc_message_to_json(slice_request))  # TODO remove
            # TODO adding owner, needs to be recoded after updating the bindings
            owner = request.json["data"]["ietf-network-slice-service:network-slice-services"]["slice-service"][0]["service-tags"][0]["value"]
            slice_request.slice_owner.owner_string = owner
            slice_request.slice_owner.owner_uuid.uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, owner))
            slice_client = SliceClient()
            slice_client.CreateSlice(slice_request)
        return response
