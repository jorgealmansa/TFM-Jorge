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

# RFC 8466 - L2VPN Service Model (L2SM)
# Ref: https://datatracker.ietf.org/doc/html/rfc8466

from flask_restful import Resource
from nbi.service.rest_server.RestServer import RestServer
from .L2VPN_Services import L2VPN_Services
from .L2VPN_Service import L2VPN_Service
from .L2VPN_SiteNetworkAccesses import L2VPN_SiteNetworkAccesses

URL_PREFIX = '/restconf/data/ietf-l2vpn-svc:l2vpn-svc'

def _add_resource(rest_server : RestServer, resource : Resource, *urls, **kwargs):
    urls = [(URL_PREFIX + url) for url in urls]
    rest_server.add_resource(resource, *urls, **kwargs)

def register_ietf_l2vpn(rest_server : RestServer):
    _add_resource(rest_server, L2VPN_Services,
        '/vpn-services')
    _add_resource(rest_server, L2VPN_Service,
        '/vpn-services/vpn-service=<vpn_id>', '/vpn-services/vpn-service=<vpn_id>/')
    _add_resource(rest_server, L2VPN_SiteNetworkAccesses,
        '/sites/site=<site_id>/site-network-accesses', '/sites/site=<site_id>/site-network-accesses/')
