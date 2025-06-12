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

from flask_restful import Resource
from nbi.service.rest_server.RestServer import RestServer
from .Acl import Acl
from .Acls import Acls

URL_PREFIX = '/restconf/data'

def __add_resource(rest_server: RestServer, resource: Resource, *urls, **kwargs):
    urls = [(URL_PREFIX + url) for url in urls]
    rest_server.add_resource(resource, *urls, **kwargs)

def register_ietf_acl(rest_server: RestServer):
    __add_resource(
        rest_server,
        Acls,
        '/device=<path:device_uuid>/ietf-access-control-list:acls',
    )

    __add_resource(
        rest_server,
        Acl,
        '/device=<path:device_uuid>/ietf-access-control-list:acl=<path:acl_name>',
        '/device=<path:device_uuid>/ietf-access-control-list:acl=<path:acl_name>/',
    )
