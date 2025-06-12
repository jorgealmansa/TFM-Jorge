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

import grpc, logging
from typing import Optional
from common.Constants import DEFAULT_CONTEXT_NAME
from common.proto.context_pb2 import Slice, SliceFilter, SliceId
from context.client.ContextClient import ContextClient

LOGGER = logging.getLogger(__name__)

def get_slice_by_id(
    context_client : ContextClient, slice_id : SliceId, rw_copy : bool = False, include_endpoint_ids : bool = True,
    include_constraints : bool = True, include_service_ids : bool = True, include_subslice_ids : bool = True,
    include_config_rules : bool = True
) -> Optional[Slice]:
    slice_filter = SliceFilter()
    slice_id = slice_filter.slice_ids.slice_ids.append(slice_id) # pylint: disable=no-member
    slice_filter.include_endpoint_ids = include_endpoint_ids
    slice_filter.include_constraints = include_constraints
    slice_filter.include_service_ids = include_service_ids
    slice_filter.include_subslice_ids = include_subslice_ids
    slice_filter.include_config_rules = include_config_rules

    try:
        ro_slices = context_client.SelectSlice(slice_filter)
        if len(ro_slices.slices) == 0: return None
        assert len(ro_slices.slices) == 1
        ro_slice = ro_slices.slices[0]
        if not rw_copy: return ro_slice
        rw_slice = Slice()
        rw_slice.CopyFrom(ro_slice)
        return rw_slice
    except grpc.RpcError as e:
        if e.code() != grpc.StatusCode.NOT_FOUND: raise # pylint: disable=no-member
        #LOGGER.exception('Unable to get slice({:s} / {:s})'.format(str(context_uuid), str(slice_uuid)))
        return None

def get_slice_by_uuid(
    context_client : ContextClient, slice_uuid : str, context_uuid : str = DEFAULT_CONTEXT_NAME,
    rw_copy : bool = False, include_endpoint_ids : bool = True, include_constraints : bool = True,
    include_service_ids : bool = True, include_subslice_ids : bool = True, include_config_rules : bool = True
) -> Optional[Slice]:
    slice_id = SliceId()
    slice_id.context_id.context_uuid.uuid = context_uuid    # pylint: disable=no-member
    slice_id.slice_uuid.uuid = slice_uuid                   # pylint: disable=no-member
    return get_slice_by_id(
        context_client, slice_id, rw_copy=rw_copy, include_endpoint_ids=include_endpoint_ids,
        include_constraints=include_constraints, include_service_ids=include_service_ids,
        include_subslice_ids=include_subslice_ids, include_config_rules=include_config_rules)
