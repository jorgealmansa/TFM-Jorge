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

from typing import Optional, Set, Union
from common.tools.grpc.Tools import grpc_message_to_json
from ..gnmi.gnmi_pb2 import CapabilityRequest   # pylint: disable=no-name-in-module
from ..gnmi.gnmi_pb2_grpc import gNMIStub

def check_capabilities(
    stub : gNMIStub, username : str, password : str, timeout : Optional[int] = None
) -> Set[Union[str, int]]:
    metadata = [('username', username), ('password', password)]
    req = CapabilityRequest()
    reply = stub.Capabilities(req, metadata=metadata, timeout=timeout)

    data = grpc_message_to_json(reply)

    gnmi_version = data.get('gNMI_version')
    if gnmi_version is None or gnmi_version != '0.7.0':
        raise Exception('Unsupported gNMI version: {:s}'.format(str(gnmi_version)))

    #supported_models = {
    #    supported_model['name']: supported_model['version']
    #    for supported_model in data.get('supported_models', [])
    #}
    # TODO: check supported models and versions

    supported_encodings = {
        supported_encoding
        for supported_encoding in data.get('supported_encodings', [])
        if isinstance(supported_encoding, str)
    }
    if len(supported_encodings) == 0:
        # pylint: disable=broad-exception-raised
        raise Exception('No supported encodings found')
    if 'JSON_IETF' not in supported_encodings:
        # pylint: disable=broad-exception-raised
        raise Exception('JSON_IETF encoding not supported')
