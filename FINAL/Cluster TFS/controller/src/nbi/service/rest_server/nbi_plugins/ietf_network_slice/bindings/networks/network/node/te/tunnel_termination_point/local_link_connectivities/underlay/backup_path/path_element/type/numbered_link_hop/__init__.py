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


class NumberedLinkHopMeta(type):
    """
    Metaclass for YANG container handler.

    YANG name: numbered-link-hop
    """
    from .numbered_link_hop import NumberedLinkHop

    class yang_container_descriptor(
            YANGContainerMember):
        """
        YANG container descriptor class.

        YANG name: numbered-link-hop
        """

        def __init__(self):
            super().__init__(NumberedLinkHop)

        def __get__(self, instance, owner=None) -> (
                'NumberedLinkHopMeta.yang_container_descriptor'):
            return super().__get__(instance, owner)

        def __call__(self) -> 'NumberedLinkHop':
            pass

        def __enter__(self) -> 'NumberedLinkHop':
            pass


class NumberedLinkHop(
        YANGContainer,
        metaclass=NumberedLinkHopMeta):
    """
    YANG container handler.

    YANG name: numbered-link-hop
    """

    _yang_name: Final[str] = 'numbered-link-hop'
    _yang_namespace: Final[str] = 'urn:ietf:params:xml:ns:yang:ietf-te-topology'
    _yang_module_name: Final[str] = 'ietf-te-topology'

    _yang_leaf_members: Final[Dict[str, YANGLeafMember]] = {
    }

    _yang_container_members: Final[Dict[str, YANGContainerMember]] = {

        'numbered-link-hop': (
            numbered_link_hop := (  # YANGContainerMember(
                NumberedLinkHopMeta.
                NumberedLinkHop.
                yang_container_descriptor())),
    }

    _yang_list_members: Final[Dict[str, YANGListMember]] = {
    }

    _yang_choices: Final[Dict[str, YANGChoice]] = None

    def __new__(cls, *args, **kwargs) -> 'NumberedLinkHop':
        instance = super().__new__(cls)
        instance._yang_choices = {
        }
        return instance
