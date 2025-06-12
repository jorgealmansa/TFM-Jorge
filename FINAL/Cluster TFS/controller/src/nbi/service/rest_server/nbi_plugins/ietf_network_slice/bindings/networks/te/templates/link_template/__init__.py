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

from typing import Dict, Final, Iterator, List, Tuple

from .. import (
    YANGChoice, YANGChoiceCase, YANGContainer, YANGContainerMember,
    YANGLeafMember, YANGListItem, YANGListMember)


class LinkTemplateMeta(type):
    """
    Metaclass for YANG list item handler.

    YANG name: link-template
    """
    from .te_link_attributes import TeLinkAttributes

    class yang_list_descriptor(
            YANGListMember):
        """
        YANG list descriptor class.

        YANG name: link-template
        """

        def __init__(self):
            super().__init__(LinkTemplate)

        def __get__(self, instance, owner=None) -> (
                'LinkTemplateMeta.yang_list_descriptor'):
            return super().__get__(instance, owner)

        def __call__(self) -> List['LinkTemplate']:
            pass

        def __iter__(self, key) -> Iterator['LinkTemplate']:
            return super().__iter__()

        def __getitem__(self, key) -> 'LinkTemplate':
            return super()[key]

        def __enter__(self) -> (
                'LinkTemplateMeta.yang_list_descriptor'):
            pass


class LinkTemplate(
        YANGListItem,
        metaclass=LinkTemplateMeta):
    """
    YANG list item handler.

    YANG name: link-template
    """

    _yang_name: Final[str] = 'link-template'
    _yang_namespace: Final[str] = 'urn:ietf:params:xml:ns:yang:ietf-te-topology'
    _yang_module_name: Final[str] = 'ietf-te-topology'

    _yang_list_key_names: Final[Tuple[str]] = (
        'name',
    )

    _yang_leaf_members: Final[Dict[str, YANGLeafMember]] = {

        'reference-change-policy': (
            reference_change_policy := YANGLeafMember(
                'reference-change-policy',
                'urn:ietf:params:xml:ns:yang:ietf-te-topology',
                'ietf-te-topology')),

        'name': (
            name := YANGLeafMember(
                'name',
                'urn:ietf:params:xml:ns:yang:ietf-te-topology',
                'ietf-te-topology')),

        'priority': (
            priority := YANGLeafMember(
                'priority',
                'urn:ietf:params:xml:ns:yang:ietf-te-topology',
                'ietf-te-topology')),
    }

    _yang_container_members: Final[Dict[str, YANGContainerMember]] = {

        'te-link-attributes': (
            te_link_attributes := (  # YANGContainerMember(
                LinkTemplateMeta.
                TeLinkAttributes.
                yang_container_descriptor())),
    }

    _yang_list_members: Final[Dict[str, YANGListMember]] = {
    }

    _yang_choices: Final[Dict[str, YANGChoice]] = None

    def __new__(cls, *args, **kwargs) -> 'LinkTemplate':
        instance = super().__new__(cls)
        instance._yang_choices = {
        }
        return instance
