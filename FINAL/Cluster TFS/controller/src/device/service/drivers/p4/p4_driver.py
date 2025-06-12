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

"""
P4 driver plugin for the TeraFlow SDN controller.
"""

import os
import json
import logging
import threading
from typing import Any, Iterator, List, Optional, Tuple, Union
from common.method_wrappers.Decorator import MetricsPool, metered_subclass_method
from common.type_checkers.Checkers import chk_type, chk_length, chk_string
from .p4_common import matches_ipv4, matches_ipv6, valid_port,\
    P4_ATTR_DEV_ID, P4_ATTR_DEV_NAME, P4_ATTR_DEV_VENDOR,\
    P4_ATTR_DEV_HW_VER, P4_ATTR_DEV_SW_VER,\
    P4_ATTR_DEV_P4BIN, P4_ATTR_DEV_P4INFO, P4_ATTR_DEV_TIMEOUT,\
    P4_VAL_DEF_VENDOR, P4_VAL_DEF_HW_VER, P4_VAL_DEF_SW_VER,\
    P4_VAL_DEF_TIMEOUT
from .p4_manager import P4Manager, KEY_TABLE, KEY_ACTION, \
    KEY_ACTION_PROFILE, KEY_COUNTER, KEY_DIR_COUNTER, KEY_METER, KEY_DIR_METER,\
    KEY_CTL_PKT_METADATA
from .p4_client import WriteOperation

try:
    from _Driver import _Driver
except ImportError:
    from device.service.driver_api._Driver import _Driver

LOGGER = logging.getLogger(__name__)

DRIVER_NAME = 'p4'
METRICS_POOL = MetricsPool('Device', 'Driver', labels={'driver': DRIVER_NAME})

class P4Driver(_Driver):
    """
    P4Driver class inherits the abstract _Driver class to support P4 devices.

    Attributes
    ----------
    address : str
        IP address of the P4Runtime server running on the P4 device
    port : int
        transport port number of the P4Runtime server running on the P4 device
    **settings : map
        id : int
            P4 device datapath ID (Mandatory)
        name : str
            P4 device name (Optional)
        vendor : str
            P4 device vendor (Optional)
        hw_ver : str
            Hardware version of the P4 device (Optional)
        sw_ver : str
            Software version of the P4 device (Optional)
        p4bin : str
            Path to P4 binary file (Optional, but must be combined with p4info)
        p4info : str
            Path to P4 info file (Optional, but must be combined with p4bin)
        timeout : int
            Device timeout in seconds (Optional)
    """

    def __init__(self, address: str, port: int, **settings) -> None:
        super().__init__(settings.pop('name', DRIVER_NAME), address, port, **settings)
        self.__manager = None
        self.__address = address
        self.__port = int(port)
        self.__endpoint = None
        self.__settings = settings
        self.__id = None
        self.__vendor = P4_VAL_DEF_VENDOR
        self.__hw_version = P4_VAL_DEF_HW_VER
        self.__sw_version = P4_VAL_DEF_SW_VER
        self.__p4bin_path = None
        self.__p4info_path = None
        self.__timeout = P4_VAL_DEF_TIMEOUT
        self.__lock = threading.Lock()
        self.__started = threading.Event()
        self.__terminate = threading.Event()

        self.__parse_and_validate_settings()

        LOGGER.info("Initializing P4 device at %s:%d with settings:",
                    self.__address, self.__port)

        for key, value in settings.items():
            LOGGER.info("\t%8s = %s", key, value)

    def Connect(self) -> bool:
        """
        Establish a connection between the P4 device driver and a P4 device.

        :return: boolean connection status.
        """
        LOGGER.info("Connecting to P4 device %s ...", self.__endpoint)

        with self.__lock:
            # Skip if already connected
            if self.__started.is_set():
                return True

            # Dynamically devise an election ID
            election_id = (1, 0)

            # Spawn a P4 manager for this device
            self.__manager = P4Manager(
                device_id=self.__id,
                ip_address=self.__address,
                port=self.__port,
                election_id=election_id)
            assert self.__manager

            # Start the P4 manager
            try:
                self.__manager.start(self.__p4bin_path, self.__p4info_path)
            except Exception as ex:  # pylint: disable=broad-except
                raise Exception(ex) from ex

            LOGGER.info("\tConnected via P4Runtime")
            self.__started.set()

            return True

    def Disconnect(self) -> bool:
        """
        Terminate the connection between the P4 device driver and a P4 device.

        :return: boolean disconnection status.
        """
        LOGGER.info("Disconnecting from P4 device %s ...", self.__endpoint)

        # If not started, assume it is already disconnected
        if not self.__started.is_set():
            return True

        # P4 manager must already be instantiated
        assert self.__manager

        # Trigger termination of loops and processes
        self.__terminate.set()

        # Trigger connection tear down with the P4Runtime server
        self.__manager.stop()
        self.__manager = None

        LOGGER.info("\tDisconnected!")

        return True

    @metered_subclass_method(METRICS_POOL)
    def GetInitialConfig(self) -> List[Tuple[str, Any]]:
        """
        Retrieve the initial configuration of a P4 device.

        :return: list of initial configuration items.
        """
        initial_conf = []

        with self.__lock:
            if not initial_conf:
                LOGGER.warning("No initial configuration for P4 device %s ...",
                               self.__endpoint)
            return []

    @metered_subclass_method(METRICS_POOL)
    def GetConfig(self, resource_keys: List[str] = [])\
            -> List[Tuple[str, Union[Any, None, Exception]]]:
        """
        Retrieve the current configuration of a P4 device.

        :param resource_keys: P4 resource keys to retrieve.
        :return: list of values associated with the requested resource keys or
        None/Exception.
        """
        LOGGER.info(
            "Getting configuration from P4 device %s ...", self.__endpoint)

        # No resource keys means fetch all configuration
        if len(resource_keys) == 0:
            LOGGER.warning(
                "GetConfig with no resource keys "
                "implies getting all resource keys!")
            resource_keys = [
                obj_name for obj_name, _ in self.__manager.p4_objects.items()
            ]

        # Verify the input type
        chk_type("resources", resource_keys, list)

        with self.__lock:
            return self.__get_resources(resource_keys)

    @metered_subclass_method(METRICS_POOL)
    def SetConfig(self, resources: List[Tuple[str, Any]])\
            -> List[Union[bool, Exception]]:
        """
        Submit a new configuration to a P4 device.

        :param resources: P4 resources to set.
        :return: list of boolean results or Exceptions for resource key
        changes requested.
        """
        LOGGER.info(
            "Setting configuration to P4 device %s ...", self.__endpoint)

        if not resources or len(resources) == 0:
            LOGGER.warning(
                "SetConfig requires a list of resources to store "
                "into the device. Nothing is provided though.")
            return []

        assert isinstance(resources, list)

        with self.__lock:
            return self.__set_resources(resources)

    @metered_subclass_method(METRICS_POOL)
    def DeleteConfig(self, resources: List[Tuple[str, Any]])\
            -> List[Union[bool, Exception]]:
        """
        Revoke P4 device configuration.

        :param resources: list of tuples with resource keys to be deleted.
        :return: list of boolean results or Exceptions for resource key
        deletions requested.
        """
        LOGGER.info(
            "Deleting configuration from P4 device %s ...", self.__endpoint)

        if not resources or len(resources) == 0:
            LOGGER.warning(
                "DeleteConfig requires a list of resources to delete "
                "from the device. Nothing is provided though.")
            return []

        with self.__lock:
            return self.__delete_resources(resources)

    def GetResource(self, endpoint_uuid: str) -> Optional[str]:
        """
        Retrieve a certain resource from a P4 device.

        :param endpoint_uuid: target endpoint UUID.
        :return: The path of the endpoint or None if not found.
        """
        LOGGER.warning("GetResource() RPC not yet implemented by the P4 driver")
        return ""

    def GetState(self,
                 blocking=False,
                 terminate: Optional[threading.Event] = None) -> \
                 Iterator[Tuple[str, Any]]:
        """
        Retrieve the state of a P4 device.

        :param blocking: if non-blocking, the driver terminates the loop and
        returns.
        :param terminate: termination flag.
        :return: sequences of state sample.
        """
        LOGGER.warning("GetState() RPC not yet implemented by the P4 driver")
        return []

    @metered_subclass_method(METRICS_POOL)
    def SubscribeState(self, subscriptions: List[Tuple[str, float, float]])\
            -> List[Union[bool, Exception]]:
        """
        Subscribe to certain state information.

        :param subscriptions: list of tuples with resources to be subscribed.
        :return: list of results for resource subscriptions requested.
        """
        LOGGER.warning(
            "SubscribeState() RPC not yet implemented by the P4 driver")
        return [False for _ in subscriptions]

    @metered_subclass_method(METRICS_POOL)
    def UnsubscribeState(self, subscriptions: List[Tuple[str, float, float]])\
            -> List[Union[bool, Exception]]:
        """
        Unsubscribe from certain state information.

        :param subscriptions: list of tuples with resources to be unsubscribed.
        :return: list of results for resource un-subscriptions requested.
        """
        LOGGER.warning(
            "UnsubscribeState() RPC not yet implemented by the P4 driver")
        return [False for _ in subscriptions]

    def get_manager(self):
        """
        Get an instance of the P4 manager.

        :return: P4 manager instance
        """
        return self.__manager

    def __parse_and_validate_settings(self):
        """
        Verify that the driver inputs comply to what is expected.

        :return: void or exception in case of validation error
        """
        # Device endpoint information
        assert matches_ipv4(self.__address) or (matches_ipv6(self.__address)),\
            f"{self.__address} not a valid IPv4 or IPv6 address"
        assert valid_port(self.__port), \
            f"{self.__port} not a valid transport port"
        self.__endpoint = f"{self.__address}:{self.__port}"

        # Device ID
        try:
            self.__id = self.__settings.get(P4_ATTR_DEV_ID)
        except Exception as ex:
            LOGGER.error("P4 device ID is a mandatory setting")
            raise Exception from ex

        # Device name
        if P4_ATTR_DEV_NAME in self.__settings:
            self.__name = self.__settings.get(P4_ATTR_DEV_NAME)
        else:
            self.__name = str(self.__id)
            LOGGER.warning(
                "No device name is provided. Setting default name: %s",
                self.__name)

        # Device vendor
        if P4_ATTR_DEV_VENDOR in self.__settings:
            self.__vendor = self.__settings.get(P4_ATTR_DEV_VENDOR)
        else:
            LOGGER.warning(
                "No device vendor is provided. Setting default vendor: %s",
                self.__vendor)

        # Device hardware version
        if P4_ATTR_DEV_HW_VER in self.__settings:
            self.__hw_version = self.__settings.get(P4_ATTR_DEV_HW_VER)
        else:
            LOGGER.warning(
                "No HW version is provided. Setting default HW version: %s",
                self.__hw_version)

        # Device software version
        if P4_ATTR_DEV_SW_VER in self.__settings:
            self.__sw_version = self.__settings.get(P4_ATTR_DEV_SW_VER)
        else:
            LOGGER.warning(
                "No SW version is provided. Setting default SW version: %s",
                self.__sw_version)

        # Path to P4 binary file
        if P4_ATTR_DEV_P4BIN in self.__settings:
            self.__p4bin_path = self.__settings.get(P4_ATTR_DEV_P4BIN)
            assert os.path.exists(self.__p4bin_path),\
                "Invalid path to p4bin file"
            assert P4_ATTR_DEV_P4INFO in self.__settings,\
                "p4info and p4bin settings must be provided together"

        # Path to P4 info file
        if P4_ATTR_DEV_P4INFO in self.__settings:
            self.__p4info_path = self.__settings.get(P4_ATTR_DEV_P4INFO)
            assert os.path.exists(self.__p4info_path),\
                "Invalid path to p4info file"
            assert P4_ATTR_DEV_P4BIN in self.__settings,\
                "p4info and p4bin settings must be provided together"

        if (not self.__p4bin_path) or (not self.__p4info_path):
            LOGGER.warning(
                "No P4 binary and info files are provided, hence "
                "no pipeline will be installed on the whitebox device.\n"
                "This driver will attempt to manage whatever pipeline "
                "is available on the target device.")

        # Device timeout
        if P4_ATTR_DEV_TIMEOUT in self.__settings:
            self.__timeout = self.__settings.get(P4_ATTR_DEV_TIMEOUT)
            assert self.__timeout > 0,\
                "Device timeout must be a positive integer"
        else:
            LOGGER.warning(
                "No device timeout is provided. Setting default timeout: %s",
                self.__timeout)

    def __get_resources(self, resource_keys):
        """
        Retrieve the current configuration of a P4 device.

        :param resource_keys: P4 resource keys to retrieve.
        :return: list of values associated with the requested resource keys or
        None/Exception.
        """
        resources = []

        LOGGER.debug("GetConfig() -> Keys: %s", resource_keys)

        for resource_key in resource_keys:
            entries = []
            try:
                if KEY_TABLE == resource_key:
                    for table_name in self.__manager.get_table_names():
                        t_entries = self.__manager.table_entries_to_json(
                            table_name)
                        if t_entries:
                            entries.append(t_entries)
                elif KEY_COUNTER == resource_key:
                    for cnt_name in self.__manager.get_counter_names():
                        c_entries = self.__manager.counter_entries_to_json(
                            cnt_name)
                        if c_entries:
                            entries.append(c_entries)
                elif KEY_DIR_COUNTER == resource_key:
                    for d_cnt_name in self.__manager.get_direct_counter_names():
                        dc_entries = \
                            self.__manager.direct_counter_entries_to_json(
                                d_cnt_name)
                        if dc_entries:
                            entries.append(dc_entries)
                elif KEY_METER == resource_key:
                    for meter_name in self.__manager.get_meter_names():
                        m_entries = self.__manager.meter_entries_to_json(
                            meter_name)
                        if m_entries:
                            entries.append(m_entries)
                elif KEY_DIR_METER == resource_key:
                    for d_meter_name in self.__manager.get_direct_meter_names():
                        dm_entries = \
                            self.__manager.direct_meter_entries_to_json(
                                d_meter_name)
                        if dm_entries:
                            entries.append(dm_entries)
                elif KEY_ACTION_PROFILE == resource_key:
                    for ap_name in self.__manager.get_action_profile_names():
                        ap_entries = \
                            self.__manager.action_prof_member_entries_to_json(
                                ap_name)
                        if ap_entries:
                            entries.append(ap_entries)
                elif KEY_ACTION == resource_key:
                    #To be implemented or deprecated
                    pass
                elif '__endpoints__' == resource_key:
                    #Not Supported for P4 devices
                    pass
                elif KEY_CTL_PKT_METADATA == resource_key:
                    msg = f"{resource_key.capitalize()} is not a " \
                          f"retrievable resource"
                    raise Exception(msg)
                else:
                    msg = f"GetConfig failed due to invalid " \
                          f"resource key: {resource_key}"
                    raise Exception(msg)
                resources.append(
                    (resource_key, entries if entries else None)
                )
            except Exception as ex:  # pylint: disable=broad-except
                resources.append((resource_key, ex))

        return resources

    def __set_resources(self, resources):
        """
        Submit a new configuration to a P4 device.

        :param resources: P4 resources to set.
        :return: list of boolean results or Exceptions for resource key
        changes requested.
        """
        results = []

        for i, resource in enumerate(resources):
            str_resource_name = f"resources[#{i}]"
            resource_key = ""
            try:
                chk_type(
                    str_resource_name, resource, (list, tuple))
                chk_length(
                    str_resource_name, resource, min_length=2, max_length=2)
                resource_key, resource_value = resource
                chk_string(
                    str_resource_name, resource_key, allow_empty=False)
            except Exception as e:  # pylint: disable=broad-except
                LOGGER.exception(
                    "Exception validating %s: %s",
                    str_resource_name, str(resource_key))
                results.append(e)  # store the exception if validation fails
                continue

            try:
                resource_value = json.loads(resource_value)
            except Exception:  # pylint: disable=broad-except
                pass

            LOGGER.debug(
                "SetConfig() -> Key: %s - Value: %s",
                resource_key, resource_value)

            # Default operation is insert.
            # P4 manager has internal logic to judge whether an entry
            # to be inserted already exists, thus simply needs an update.
            operation = WriteOperation.insert

            try:
                self.__apply_operation(resource_key, resource_value, operation)
                results.append(True)
            except Exception as ex:  # pylint: disable=broad-except
                results.append(ex)

        print(results)

        return results

    def __delete_resources(self, resources):
        """
        Revoke P4 device configuration.

        :param resources: list of tuples with resource keys to be deleted.
        :return: list of boolean results or Exceptions for resource key
        deletions requested.
        """
        results = []

        for i, resource in enumerate(resources):
            str_resource_name = f"resources[#{i}]"
            resource_key = ""
            try:
                chk_type(
                    str_resource_name, resource, (list, tuple))
                chk_length(
                    str_resource_name, resource, min_length=2, max_length=2)
                resource_key, resource_value = resource
                chk_string(
                    str_resource_name, resource_key, allow_empty=False)
            except Exception as e:  # pylint: disable=broad-except
                LOGGER.exception(
                    "Exception validating %s: %s",
                    str_resource_name, str(resource_key))
                results.append(e)  # store the exception if validation fails
                continue

            try:
                resource_value = json.loads(resource_value)
            except Exception:  # pylint: disable=broad-except
                pass

            LOGGER.debug("DeleteConfig() -> Key: %s - Value: %s",
                         resource_key, resource_value)

            operation = WriteOperation.delete

            try:
                self.__apply_operation(resource_key, resource_value, operation)
                results.append(True)
            except Exception as ex:  # pylint: disable=broad-except
                results.append(ex)

        print(results)

        return results
    
    def __apply_operation(
            self, resource_key, resource_value, operation: WriteOperation):
        """
        Apply a write operation to a P4 resource.

        :param resource_key: P4 resource key
        :param resource_value: P4 resource value in JSON format
        :param operation: write operation (i.e., insert, update, delete)
        to apply
        :return: True if operation is successfully applied or raise Exception
        """
        # Apply settings to the various tables
        if KEY_TABLE == resource_key:
            self.__manager.table_entry_operation_from_json(
                resource_value, operation)
        elif KEY_COUNTER == resource_key:
            self.__manager.counter_entry_operation_from_json(
                resource_value, operation)
        elif KEY_DIR_COUNTER == resource_key:
            self.__manager.direct_counter_entry_operation_from_json(
                resource_value, operation)
        elif KEY_METER == resource_key:
            self.__manager.meter_entry_operation_from_json(
                resource_value, operation)
        elif KEY_DIR_METER == resource_key:
            self.__manager.direct_meter_entry_operation_from_json(
                resource_value, operation)
        elif KEY_ACTION_PROFILE == resource_key:
            self.__manager.action_prof_member_entry_operation_from_json(
                resource_value, operation)
            self.__manager.action_prof_group_entry_operation_from_json(
                resource_value, operation)
        elif KEY_CTL_PKT_METADATA == resource_key:
            msg = f"{resource_key.capitalize()} is not a " \
                  f"configurable resource"
            raise Exception(msg)
        elif resource_key == "clone_session":
            self.__manager.clone_session_entry_operation_from_json_p4(resource_value, operation)
        else:
            msg = f"{operation} on invalid key {resource_key}"
            LOGGER.error(msg)
            raise Exception(msg)

        LOGGER.debug("%s operation: %s", resource_key.capitalize(), operation)

        return True
