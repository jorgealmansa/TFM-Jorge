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
from flask.json import jsonify
from flask_restful import Resource
from common.proto.context_pb2 import SliceStatusEnum
from common.tools.context_queries.Slice import get_slice_by_uuid
from common.tools.grpc.Tools import grpc_message_to_json
from context.client.ContextClient import ContextClient
from slice.client.SliceClient import SliceClient
from ..tools.Authentication import HTTP_AUTH
from ..tools.HttpStatusCodes import HTTP_GATEWAYTIMEOUT, HTTP_NOCONTENT, HTTP_OK, HTTP_SERVERERROR

LOGGER = logging.getLogger(__name__)

class NSS_Service(Resource):
    @HTTP_AUTH.login_required
    def get(self, slice_id : str):
        LOGGER.debug('GET Slice ID: {:s}'.format(str(slice_id)))
        try:
            context_client = ContextClient()

            target = get_slice_by_uuid(context_client, slice_id, rw_copy=True)
            if target is None:
                raise Exception('Slice({:s}) not found in database'.format(str(slice_id)))

            if target.slice_id.slice_uuid.uuid != slice_id: # pylint: disable=no-member
                raise Exception('Slice retrieval failed. Wrong Slice Id was returned')

            slice_ready_status = SliceStatusEnum.SLICESTATUS_ACTIVE
            slice_status = target.slice_status.slice_status # pylint: disable=no-member
            response = jsonify(grpc_message_to_json(target))
            response.status_code = HTTP_OK if slice_status == slice_ready_status else HTTP_GATEWAYTIMEOUT

        except Exception as e: # pylint: disable=broad-except
            LOGGER.exception('Something went wrong Retrieving Slice({:s})'.format(str(slice_id)))
            response = jsonify({'error': str(e)})
            response.status_code = HTTP_SERVERERROR
        return response


    @HTTP_AUTH.login_required
    def delete(self, slice_id : str):
        LOGGER.debug('DELETE Slice ID: {:s}'.format(str(slice_id)))
        try:
            context_client = ContextClient()
            target = get_slice_by_uuid(context_client, slice_id)

            response = jsonify({})
            response.status_code = HTTP_OK

            if target is None:
                LOGGER.warning('Slice({:s}) not found in database. Nothing done.'.format(str(slice_id)))
                response.status_code = HTTP_NOCONTENT
            else:
                if target.slice_id.slice_uuid.uuid != slice_id:  # pylint: disable=no-member
                    raise Exception('Slice retrieval failed. Wrong Slice Id was returned')
                slice_client = SliceClient()
                slice_client.DeleteSlice(target.slice_id)
                LOGGER.debug(f"Slice({slice_id}) successfully deleted")

        except Exception as e:  # pylint: disable=broad-except
            LOGGER.exception('Something went wrong Deleting Slice({:s})'.format(str(slice_id)))
            response = jsonify({'error': str(e)})
            response.status_code = HTTP_SERVERERROR
        return response