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


class BundledLinkMeta(type):
    """
    Metaclass for YANG list item handler.

    YANG name: bundled-link
    """

    class yang_list_descriptor(
            YANGListMember):
        """
        YANG list descriptor class.

        YANG name: bundled-link
        """

        def __init__(self):
            super().__init__(BundledLink)

        def __get__(self, instance, owner=None) -> (
                'BundledLinkMeta.yang_list_descriptor'):
            return super().__get__(instance, owner)

        def __call__(self) -> List['BundledLink']:
            pass

        def __iter__(self, key) -> Iterator['BundledLink']:
            return super().__iter__()

        def __getitem__(self, key) -> 'BundledLink':
            return super()[key]

        def __enter__(self) -> (
                'BundledLinkMeta.yang_list_descriptor'):
            pass


class BundledLink(
        YANGListItem,
        metaclass=BundledLinkMeta):
    """
    YANG list item handler.

    YANG name: bundled-link
    """

    _yang_name: Final[str] = 'bundled-link'
    _yang_namespace: Final[str] = 'urn:ietf:params:xml:ns:yang:ietf-te-topology'
    _yang_module_name: Final[str] = 'ietf-te-topology'

    _yang_list_key_names: Final[Tuple[str]] = (
        'sequence',
    )

    _yang_leaf_members: Final[Dict[str, YANGLeafMember]] = {

        'sequence': (
            sequence := YANGLeafMember(
                'sequence',
                'urn:ietf:params:xml:ns:yang:ietf-te-topology',
                'ietf-te-topology')),

        'src-tp-ref': (
            src_tp_ref := YANGLeafMember(
                'src-tp-ref',
                'urn:ietf:params:xml:ns:yang:ietf-te-topology',
                'ietf-te-topology')),

        'des-tp-ref': (
            des_tp_ref := YANGLeafMember(
                'des-tp-ref',
                'urn:ietf:params:xml:ns:yang:ietf-te-topology',
                'ietf-te-topology')),
    }

    _yang_container_members: Final[Dict[str, YANGContainerMember]] = {
    }

    _yang_list_members: Final[Dict[str, YANGListMember]] = {
    }

    _yang_choices: Final[Dict[str, YANGChoice]] = None

    def __new__(cls, *args, **kwargs) -> 'BundledLink':
        instance = super().__new__(cls)
        instance._yang_choices = {
        }
        return instance
