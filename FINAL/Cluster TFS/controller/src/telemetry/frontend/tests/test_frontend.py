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

import os
import pytest
import logging

from common.Constants import ServiceNameEnum
from common.proto.telemetry_frontend_pb2 import CollectorId, CollectorList
from common.proto.context_pb2 import Empty
from common.tools.kafka.Variables import KafkaTopic
from common.Settings import ( 
    get_service_port_grpc, get_env_var_name, ENVVAR_SUFIX_SERVICE_HOST, ENVVAR_SUFIX_SERVICE_PORT_GRPC)

from telemetry.frontend.client.TelemetryFrontendClient import TelemetryFrontendClient
from telemetry.frontend.service.TelemetryFrontendService import TelemetryFrontendService
from telemetry.frontend.tests.Messages import (
     create_collector_request, create_collector_id, create_collector_filter)
from telemetry.frontend.service.TelemetryFrontendServiceServicerImpl import TelemetryFrontendServiceServicerImpl


###########################
# Tests Setup
###########################

LOCAL_HOST = '127.0.0.1'

TELEMETRY_FRONTEND_PORT = str(get_service_port_grpc(ServiceNameEnum.TELEMETRY))
os.environ[get_env_var_name(ServiceNameEnum.TELEMETRY, ENVVAR_SUFIX_SERVICE_HOST     )] = str(LOCAL_HOST)
os.environ[get_env_var_name(ServiceNameEnum.TELEMETRY, ENVVAR_SUFIX_SERVICE_PORT_GRPC)] = str(TELEMETRY_FRONTEND_PORT)

LOGGER = logging.getLogger(__name__)

@pytest.fixture(scope='session')
def telemetryFrontend_service():
    LOGGER.info('Initializing TelemetryFrontendService...')

    _service = TelemetryFrontendService()
    _service.start()

    # yield the server, when test finishes, execution will resume to stop it
    LOGGER.info('Yielding TelemetryFrontendService...')
    yield _service

    LOGGER.info('Terminating TelemetryFrontendService...')
    _service.stop()

    LOGGER.info('Terminated TelemetryFrontendService...')

@pytest.fixture(scope='session')
def telemetryFrontend_client(
        telemetryFrontend_service : TelemetryFrontendService
    ):
    LOGGER.info('Initializing TelemetryFrontendClient...')
    _client = TelemetryFrontendClient()

    # yield the server, when test finishes, execution will resume to stop it
    LOGGER.info('Yielding TelemetryFrontendClient...')
    yield _client

    LOGGER.info('Closing TelemetryFrontendClient...')
    _client.close()

    LOGGER.info('Closed TelemetryFrontendClient...')


###########################
# Tests Implementation of Telemetry Frontend
###########################

# ------- Re-structuring Test ---------
# --- "test_validate_kafka_topics" should be run before the functionality tests ---
def test_validate_kafka_topics():
    LOGGER.debug(" >>> test_validate_kafka_topics: START <<< ")
    response = KafkaTopic.create_all_topics()
    assert isinstance(response, bool)

# ----- core funtionality test -----
def test_StartCollector(telemetryFrontend_client):
    LOGGER.info(' >>> test_StartCollector START: <<< ')
    response = telemetryFrontend_client.StartCollector(create_collector_request())
    LOGGER.debug(str(response))
    assert isinstance(response, CollectorId)

def test_StopCollector(telemetryFrontend_client):
    LOGGER.info(' >>> test_StopCollector START: <<< ')
    response = telemetryFrontend_client.StopCollector(create_collector_id())
    LOGGER.debug(str(response))
    assert isinstance(response, Empty)

def test_SelectCollectors(telemetryFrontend_client):
    LOGGER.info(' >>> test_SelectCollectors START: <<< ')
    response = telemetryFrontend_client.SelectCollectors(create_collector_filter())
    LOGGER.debug(str(response))
    assert isinstance(response, CollectorList)

# # ----- Non-gRPC method tests ----- 
# def test_RunResponseListener():
#     LOGGER.info(' >>> test_RunResponseListener START: <<< ')
#     TelemetryFrontendServiceObj = TelemetryFrontendServiceServicerImpl()
#     response = TelemetryFrontendServiceObj.RunResponseListener()     # becasue Method "run_kafka_listener" is not define in frontend.proto
#     LOGGER.debug(str(response))
#     assert isinstance(response, bool)
