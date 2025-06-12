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


from flask import current_app, render_template, Blueprint, flash, session, redirect, url_for
from common.proto.context_pb2 import Empty, OpticalLink, LinkId, OpticalLinkList
from common.tools.context_queries.EndPoint import get_endpoint_names
from common.tools.context_queries.Topology import get_topology
from context.client.ContextClient import ContextClient

optical_link = Blueprint('optical_link', __name__, url_prefix='/optical_link')
context_client = ContextClient()

@optical_link.get('/')
def home():
    if 'context_uuid' not in session or 'topology_uuid' not in session:
        flash("Please select a context!", "warning")
        return redirect(url_for("main.home"))

    context_uuid = session['context_uuid']
    topology_uuid = session['topology_uuid']

    links, endpoint_ids = list(), list()
    device_names, endpoints_data = dict(), dict()

    context_client.connect()
    grpc_topology = get_topology(context_client, topology_uuid, context_uuid=context_uuid, rw_copy=False)
    if grpc_topology is None:
        flash('Context({:s})/Topology({:s}) not found'.format(str(context_uuid), str(topology_uuid)), 'danger')
    else:
        grpc_links : OpticalLinkList = context_client.GetOpticalLinkList(Empty())
        for link_ in grpc_links.optical_links:
            links.append(link_)
            endpoint_ids.extend(link_.link_endpoint_ids)
        device_names, endpoints_data = get_endpoint_names(context_client, endpoint_ids)
    context_client.close()

    return render_template(
        'optical_link/home.html', links=links, device_names=device_names,
        endpoints_data=endpoints_data
    )


@optical_link.route('detail/<path:link_uuid>', methods=('GET', 'POST'))
def detail(link_uuid: str):
    context_client.connect()
    # pylint: disable=no-member
    link_id = LinkId()
    link_id.link_uuid.uuid = link_uuid
    link_obj = context_client.GetOpticalLink(link_id)
    c_slots=s_slots=l_slots=None
    if link_obj is None:
        flash('Optical Link({:s}) not found'.format(str(link_uuid)), 'danger')
        link_obj = OpticalLink()
        device_names, endpoints_data = dict(), dict()
    else:
        device_names, endpoints_data = get_endpoint_names(context_client, link_obj.link_endpoint_ids)
        c_slots = link_obj.optical_details.c_slots
        l_slots = link_obj.optical_details.l_slots
        s_slots = link_obj.optical_details.s_slots

    context_client.close()

    return render_template(
        'optical_link/detail.html', link=link_obj, device_names=device_names,
        endpoints_data=endpoints_data, c_slots=c_slots, l_slots=l_slots, s_slots=s_slots
    )


@optical_link.get('<path:link_uuid>/delete')
def delete(link_uuid):
    try:
        request = LinkId()
        request.link_uuid.uuid = link_uuid # pylint: disable=no-member
        context_client.connect()
        context_client.DeleteOpticalLink(request)
        context_client.close()

        flash(f'Optical Link "{link_uuid}" deleted successfully!', 'success')
    except Exception as e: # pylint: disable=broad-except
        flash(f'Problem deleting link "{link_uuid}": {e.details()}', 'danger')
        current_app.logger.exception(e)
    return redirect(url_for('optical_link.home'))


@optical_link.get("delete_all")
def delete_all():
    try:
        context_client.connect()
        optical_link_list : OpticalLinkList = context_client.GetOpticalLinkList(Empty())
        for optical_link in optical_link_list.optical_links:
            context_client.DeleteOpticalLink(optical_link.link_id)
        context_client.close()
        flash(f"All Optical Link Deleted Successfully",'success')
    except Exception as e:
        flash(f"Problem in delete all optical link  => {e}",'danger')
    return redirect(url_for('optical_link.home'))
