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


class TeMeta(type):
    """
    Metaclass for YANG container handler.

    YANG name: te
    """
    from .geolocation import Geolocation
    from .nsrlg import Nsrlg

    class yang_container_descriptor(
            YANGContainerMember):
        """
        YANG container descriptor class.

        YANG name: te
        """

        def __init__(self):
            super().__init__(Te)

        def __get__(self, instance, owner=None) -> (
                'TeMeta.yang_container_descriptor'):
            return super().__get__(instance, owner)

        def __call__(self) -> 'Te':
            pass

        def __enter__(self) -> 'Te':
            pass


class Te(
        YANGContainer,
        metaclass=TeMeta):
    """
    YANG container handler.

    YANG name: te
    """

    _yang_name: Final[str] = 'te'
    _yang_namespace: Final[str] = 'urn:ietf:params:xml:ns:yang:ietf-te-topology'
    _yang_module_name: Final[str] = 'ietf-te-topology'

    _yang_leaf_members: Final[Dict[str, YANGLeafMember]] = {

        'preference': (
            preference := YANGLeafMember(
                'preference',
                'urn:ietf:params:xml:ns:yang:ietf-te-topology',
                'ietf-te-topology')),

        'name': (
            name := YANGLeafMember(
                'name',
                'urn:ietf:params:xml:ns:yang:ietf-te-topology',
                'ietf-te-topology')),

        'optimization-criterion': (
            optimization_criterion := YANGLeafMember(
                'optimization-criterion',
                'urn:ietf:params:xml:ns:yang:ietf-te-topology',
                'ietf-te-topology')),
    }

    _yang_container_members: Final[Dict[str, YANGContainerMember]] = {

        'geolocation': (
            geolocation := (  # YANGContainerMember(
                TeMeta.
                Geolocation.
                yang_container_descriptor())),
    }

    _yang_list_members: Final[Dict[str, YANGListMember]] = {

        'nsrlg': (
            nsrlg := (  # YANGListMember(
                TeMeta.
                Nsrlg.
                yang_list_descriptor())),
    }

    _yang_choices: Final[Dict[str, YANGChoice]] = None

    def __new__(cls, *args, **kwargs) -> 'Te':
        instance = super().__new__(cls)
        instance._yang_choices = {
        }
        return instance
