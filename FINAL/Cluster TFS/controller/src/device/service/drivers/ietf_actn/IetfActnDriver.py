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

import json, logging, requests, threading
from typing import Any, Iterator, List, Optional, Tuple, Union
from common.method_wrappers.Decorator import MetricsPool, metered_subclass_method
from common.type_checkers.Checkers import chk_string, chk_type
from device.service.driver_api._Driver import _Driver, RESOURCE_ENDPOINTS, RESOURCE_SERVICES
from .handlers.EthtServiceHandler import EthtServiceHandler
from .handlers.OsuTunnelHandler import OsuTunnelHandler
from .handlers.RestApiClient import RestApiClient
from .Tools import get_etht_services, get_osu_tunnels, parse_resource_key

LOGGER = logging.getLogger(__name__)

ALL_RESOURCE_KEYS = [
    RESOURCE_ENDPOINTS,
    RESOURCE_SERVICES,
]

DRIVER_NAME = 'ietf_actn'
METRICS_POOL = MetricsPool('Device', 'Driver', labels={'driver': DRIVER_NAME})

class IetfActnDriver(_Driver):
    def __init__(self, address: str, port: int, **settings) -> None:
        super().__init__(DRIVER_NAME, address, port, **settings)
        self.__lock = threading.Lock()
        self.__started = threading.Event()
        self.__terminate = threading.Event()
        self._rest_api_client = RestApiClient(address, port, settings=settings)
        self._handler_osu_tunnel = OsuTunnelHandler(self._rest_api_client)
        self._handler_etht_service = EthtServiceHandler(self._rest_api_client)

    def Connect(self) -> bool:
        with self.__lock:
            if self.__started.is_set(): return True
            try:
                self._rest_api_client.get('Check Credentials', '')
            except requests.exceptions.Timeout:
                LOGGER.exception('Timeout exception checking connectivity')
                return False
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception('Unhandled exception checking connectivity')
                return False
            else:
                self.__started.set()
                return True

    def Disconnect(self) -> bool:
        with self.__lock:
            self.__terminate.set()
            return True

    @metered_subclass_method(METRICS_POOL)
    def GetInitialConfig(self) -> List[Tuple[str, Any]]:
        with self.__lock:
            return []

    @metered_subclass_method(METRICS_POOL)
    def GetConfig(self, resource_keys : List[str] = []) -> List[Tuple[str, Union[Any, None, Exception]]]:
        chk_type('resources', resource_keys, list)
        results = []
        with self.__lock:
            if len(resource_keys) == 0: resource_keys = ALL_RESOURCE_KEYS
            for i, resource_key in enumerate(resource_keys):
                chk_string('resource_key[#{:d}]'.format(i), resource_key, allow_empty=False)

                try:
                    _results = list()

                    if resource_key == RESOURCE_ENDPOINTS:
                        # Add mgmt endpoint by default
                        resource_key = '/endpoints/endpoint[mgmt]'
                        resource_value = {'uuid': 'mgmt', 'name': 'mgmt', 'type': 'mgmt'}
                        results.append((resource_key, resource_value))
                    elif resource_key == RESOURCE_SERVICES:
                        get_osu_tunnels(self._handler_osu_tunnel, _results)
                        get_etht_services(self._handler_etht_service, _results)
                    else:
                        # check if resource key is for a specific OSU tunnel or ETHT service, and get them accordingly
                        osu_tunnel_name, etht_service_name = parse_resource_key(resource_key)
                        if osu_tunnel_name is not None:
                            get_osu_tunnels(self._handler_osu_tunnel, _results, osu_tunnel_name=osu_tunnel_name)
                        if etht_service_name is not None:
                            get_etht_services(self._handler_etht_service, _results, etht_service_name=etht_service_name)

                    results.extend(_results)
                except Exception as e:
                    results.append((resource_key, e))

        return results

    @metered_subclass_method(METRICS_POOL)
    def SetConfig(self, resources: List[Tuple[str, Any]]) -> List[Union[bool, Exception]]:
        results = []
        if len(resources) == 0: return results
        with self.__lock:
            for resource_key, resource_value in resources:
                LOGGER.info('resource: key({:s}) => value({:s})'.format(str(resource_key), str(resource_value)))
                try:
                    _results = list()

                    if isinstance(resource_value, str): resource_value = json.loads(resource_value)
                    osu_tunnel_name, etht_service_name = parse_resource_key(resource_key)

                    if osu_tunnel_name is not None:
                        succeeded = self._handler_osu_tunnel.update(resource_value)
                        _results.append(succeeded)

                    if etht_service_name is not None:
                        succeeded = self._handler_etht_service.update(resource_value)
                        _results.append(succeeded)

                    results.extend(_results)
                except Exception as e:
                    results.append(e)

        return results

    @metered_subclass_method(METRICS_POOL)
    def DeleteConfig(self, resources: List[Tuple[str, Any]]) -> List[Union[bool, Exception]]:
        results = []
        if len(resources) == 0: return results
        with self.__lock:
            for resource_key, resource_value in resources:
                LOGGER.info('resource: key({:s}) => value({:s})'.format(str(resource_key), str(resource_value)))
                try:
                    _results = list()

                    if isinstance(resource_value, str): resource_value = json.loads(resource_value)
                    osu_tunnel_name, etht_service_name = parse_resource_key(resource_key)

                    if osu_tunnel_name is not None:
                        succeeded = self._handler_osu_tunnel.delete(osu_tunnel_name)
                        _results.append(succeeded)

                    if etht_service_name is not None:
                        succeeded = self._handler_etht_service.delete(etht_service_name)
                        _results.append(succeeded)

                    results.extend(_results)
                except Exception as e:
                    results.append(e)

        return results

    @metered_subclass_method(METRICS_POOL)
    def SubscribeState(self, subscriptions : List[Tuple[str, float, float]]) -> List[Union[bool, Exception]]:
        # TODO: IETF ACTN does not support monitoring by now
        return [False for _ in subscriptions]

    @metered_subclass_method(METRICS_POOL)
    def UnsubscribeState(self, subscriptions : List[Tuple[str, float, float]]) -> List[Union[bool, Exception]]:
        # TODO: IETF ACTN does not support monitoring by now
        return [False for _ in subscriptions]

    def GetState(
        self, blocking=False, terminate : Optional[threading.Event] = None
    ) -> Iterator[Tuple[float, str, Any]]:
        # TODO: IETF ACTN does not support monitoring by now
        return []
