# Copyright 2022-2024 ETSI OSG/SDG TeraFlowSDN (TFS) (https://tfs.etsi.org/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict, Final

from .. import (
    YANGChoice, YANGChoiceCase, YANGContainer, YANGContainerMember,
    YANGLeafMember, YANGListItem, YANGListMember)


class UnnumberedLinkHopMeta(type):
    """
    Metaclass for YANG container handler.

    YANG name: unnumbered-link-hop
    """

    class yang_container_descriptor(
            YANGContainerMember):
        """
        YANG container descriptor class.

        YANG name: unnumbered-link-hop
        """

        def __init__(self):
            super().__init__(UnnumberedLinkHop)

        def __get__(self, instance, owner=None) -> (
                'UnnumberedLinkHopMeta.yang_container_descriptor'):
            return super().__get__(instance, owner)

        def __call__(self) -> 'UnnumberedLinkHop':
            pass

        def __enter__(self) -> 'UnnumberedLinkHop':
            pass


class UnnumberedLinkHop(
        YANGContainer,
        metaclass=UnnumberedLinkHopMeta):
    """
    YANG container handler.

    YANG name: unnumbered-link-hop
    """

    _yang_name: Final[str] = 'unnumbered-link-hop'
    _yang_namespace: Final[str] = 'urn:ietf:params:xml:ns:yang:ietf-te-topology'
    _yang_module_name: Final[str] = 'ietf-te-topology'

    _yang_leaf_members: Final[Dict[str, YANGLeafMember]] = {

        'node-id': (
            node_id := YANGLeafMember(
                'node-id',
                'urn:ietf:params:xml:ns:yang:ietf-te-topology',
                'ietf-te-topology')),

        'link-tp-id': (
            link_tp_id := YANGLeafMember(
                'link-tp-id',
                'urn:ietf:params:xml:ns:yang:ietf-te-topology',
                'ietf-te-topology')),

        'direction': (
            direction := YANGLeafMember(
                'direction',
                'urn:ietf:params:xml:ns:yang:ietf-te-topology',
                'ietf-te-topology')),

        'hop-type': (
            hop_type := YANGLeafMember(
                'hop-type',
                'urn:ietf:params:xml:ns:yang:ietf-te-topology',
                'ietf-te-topology')),
    }

    _yang_container_members: Final[Dict[str, YANGContainerMember]] = {
    }

    _yang_list_members: Final[Dict[str, YANGListMember]] = {
    }

    _yang_choices: Final[Dict[str, YANGChoice]] = None

    def __new__(cls, *args, **kwargs) -> 'UnnumberedLinkHop':
        instance = super().__new__(cls)
        instance._yang_choices = {
        }
        return instance
