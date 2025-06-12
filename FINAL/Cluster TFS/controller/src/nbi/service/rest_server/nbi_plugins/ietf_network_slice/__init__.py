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

# IETF draft-ietf-teas-ietf-network-slice-nbi-yang-02 - IETF Network Slice Service YANG Model
# Ref: https://datatracker.ietf.org/doc/draft-ietf-teas-ietf-network-slice-nbi-yang/

from flask_restful import Resource
from nbi.service.rest_server.RestServer import RestServer
from .NSS_Services import NSS_Services
from .NSS_Service import NSS_Service

URL_PREFIX = '/restconf/data/ietf-network-slice-service:ietf-nss'

def _add_resource(rest_server : RestServer, resource : Resource, *urls, **kwargs):
    urls = [(URL_PREFIX + url) for url in urls]
    rest_server.add_resource(resource, *urls, **kwargs)

def register_ietf_nss(rest_server : RestServer):
    _add_resource(rest_server, NSS_Services, '/network-slice-services')
    _add_resource(rest_server, NSS_Service, '/network-slice-services/slice-service=<string:slice_id>')
