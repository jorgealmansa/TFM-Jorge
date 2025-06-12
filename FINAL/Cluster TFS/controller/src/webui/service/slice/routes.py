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

import grpc
from flask import current_app, redirect, render_template, Blueprint, flash, session, url_for
from common.proto.context_pb2 import IsolationLevelEnum, Slice, SliceId, SliceStatusEnum
from common.tools.context_queries.Context import get_context
from common.tools.context_queries.EndPoint import get_endpoint_names
from common.tools.context_queries.Slice import get_slice_by_uuid
from context.client.ContextClient import ContextClient
from slice.client.SliceClient import SliceClient

slice = Blueprint('slice', __name__, url_prefix='/slice')

context_client = ContextClient()
slice_client = SliceClient()

@slice.get('/')
def home():
    if 'context_uuid' not in session or 'topology_uuid' not in session:
        flash("Please select a context!", "warning")
        return redirect(url_for("main.home"))
    context_uuid = session['context_uuid']

    context_client.connect()

    context_obj = get_context(context_client, context_uuid, rw_copy=False)
    if context_obj is None:
        flash('Context({:s}) not found'.format(str(context_uuid)), 'danger')
        device_names, endpoints_data = list(), list()
    else:
        try:
            slices = context_client.ListSlices(context_obj.context_id)
            slices = slices.slices
        except grpc.RpcError as e:
            if e.code() != grpc.StatusCode.NOT_FOUND: raise
            if e.details() != 'Context({:s}) not found'.format(context_uuid): raise
            slices, device_names, endpoints_data = list(), dict(), dict()
        else:
            endpoint_ids = list()
            for slice_ in slices:
                endpoint_ids.extend(slice_.slice_endpoint_ids)
            device_names, endpoints_data = get_endpoint_names(context_client, endpoint_ids)

    context_client.close()
    return render_template(
        'slice/home.html', slices=slices, device_names=device_names, endpoints_data=endpoints_data,
        sse=SliceStatusEnum)


@slice.route('add', methods=['GET', 'POST'])
def add():
    flash('Add slice route called', 'danger')
    raise NotImplementedError()
    #return render_template('slice/home.html')


@slice.get('<path:slice_uuid>/detail')
def detail(slice_uuid: str):
    if 'context_uuid' not in session or 'topology_uuid' not in session:
        flash("Please select a context!", "warning")
        return redirect(url_for("main.home"))
    context_uuid = session['context_uuid']

    try:
        context_client.connect()

        slice_obj = get_slice_by_uuid(context_client, slice_uuid, rw_copy=False)
        if slice_obj is None:
            flash('Context({:s})/Slice({:s}) not found'.format(str(context_uuid), str(slice_uuid)), 'danger')
            slice_obj = Slice()
        else:
            device_names, endpoints_data = get_endpoint_names(context_client, slice_obj.slice_endpoint_ids)

        context_client.close()

        return render_template(
            'slice/detail.html', slice=slice_obj, device_names=device_names, endpoints_data=endpoints_data,
            sse=SliceStatusEnum, ile=IsolationLevelEnum)
    except Exception as e:
        flash('The system encountered an error and cannot show the details of this slice.', 'warning')
        current_app.logger.exception(e)
        return redirect(url_for('slice.home'))

@slice.get('<path:slice_uuid>/delete')
def delete(slice_uuid: str):
    if 'context_uuid' not in session or 'topology_uuid' not in session:
        flash("Please select a context!", "warning")
        return redirect(url_for("main.home"))
    context_uuid = session['context_uuid']

    try:
        request = SliceId()
        request.slice_uuid.uuid = slice_uuid
        request.context_id.context_uuid.uuid = context_uuid
        slice_client.connect()
        slice_client.DeleteSlice(request)
        slice_client.close()

        flash('Slice "{:s}" deleted successfully!'.format(slice_uuid), 'success')
    except Exception as e:
        flash('Problem deleting slice "{:s}": {:s}'.format(slice_uuid, str(e.details())), 'danger')
        current_app.logger.exception(e) 
    return redirect(url_for('slice.home'))
