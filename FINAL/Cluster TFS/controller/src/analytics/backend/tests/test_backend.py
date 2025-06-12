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

import time, json
from typing import Dict
import logging
from threading import Event, Thread
from common.tools.kafka.Variables import KafkaTopic
from analytics.backend.service.AnalyticsBackendService import AnalyticsBackendService
from analytics.backend.tests.messages import get_kpi_id_list, get_operation_list, get_threshold_dict
from .messages import create_analyzer, create_analyzer_dask
from threading import Thread, Event
from ..service.DaskStreaming import DaskStreamer

LOGGER = logging.getLogger(__name__)


###########################
# Tests Implementation of Telemetry Backend
###########################

# --- "test_validate_kafka_topics" should be run before the functionality tests ---
def test_validate_kafka_topics():
    LOGGER.debug(" >>> test_validate_kafka_topics: START <<< ")
    response = KafkaTopic.create_all_topics()
    assert isinstance(response, bool)


# --- To test Dask Streamer functionality ---
# def test_StartDaskStreamer():   # Directly from the Streamer class
#     LOGGER.debug(" >>> test_StartSparkStreamer: START <<< ")
#     stop_event = Event()
#     kpi_list = ["1e22f180-ba28-4641-b190-2287bf446666", "6e22f180-ba28-4641-b190-2287bf448888", 'kpi_3']
#     oper_list = ['avg', 'min', 'max',]
#     thresholds = {
#         'avg_value': (10.0, 90.0),
#         'min_value': (5.0, 95.0),
#         'max_value': (15.0, 85.0),
#         'latency'  : (2.0, 10.0)
#     }

#     # Start the DaskStreamer in a separate thread
#     streamer_thread = Thread(
#         target=DaskStreamer,
#         args=("analytics_stream", kpi_list, oper_list, thresholds, stop_event),
#         kwargs={
#             "window_size": "60s",
#             "win_slide_duration": "30s",
#             "time_stamp_col": "time_stamp"
#         }
#     )
#     streamer_thread.start()
#     try:
#         while True:
#             time.sleep(10)
#     except KeyboardInterrupt:
#         LOGGER.info("KeyboardInterrupt received. Stopping streamer...")
#         stop_event.set()
#         streamer_thread.join()
#         LOGGER.info("Streamer stopped gracefully.")

# --- To test Start Streamer functionality ---
# def test_StartDaskStreamer():
#     LOGGER.debug(" >>> test_StartBaskStreamer: START <<< ")
#     analyzer_obj = create_analyzer_dask()
#     # LOGGER.info("Created Analyzer Object: {:}".format(analyzer_obj))
#     analyzer_uuid = analyzer_obj.analyzer_id.analyzer_id.uuid
#     analyzer_to_generate : Dict = {
#         "algo_name"       : analyzer_obj.algorithm_name,
#         "input_kpis"      : [k.kpi_id.uuid for k in analyzer_obj.input_kpi_ids],
#         "output_kpis"     : [k.kpi_id.uuid for k in analyzer_obj.output_kpi_ids],
#         "oper_mode"       : analyzer_obj.operation_mode,
#         "thresholds"      : json.loads(analyzer_obj.parameters["thresholds"]),
#         "oper_list"       : json.loads(analyzer_obj.parameters["oper_list"]),
#         # "oper_list"       : analyzer_obj.parameters["oper_list"],
#         "window_size"     : analyzer_obj.parameters["window_size"],
#         "window_slider"   : analyzer_obj.parameters["window_slider"],
#         # "store_aggregate" : analyzer_obj.parameters["store_aggregate"] 
#     }
#     AnalyticsBackendServiceObj = AnalyticsBackendService()
#     LOGGER.info("Analyzer to be generated: {:}".format((analyzer_to_generate)))
#     response = AnalyticsBackendServiceObj.StartDaskListener(analyzer_uuid, analyzer_to_generate)
#     assert isinstance(response, bool)
#     time.sleep(100)
#     LOGGER.info('Initiating StopRequestListener...')
#     # AnalyticsBackendServiceObj = AnalyticsBackendService()
#     response = AnalyticsBackendServiceObj.StopDaskListener(analyzer_uuid)
#     LOGGER.debug(str(response)) 
#     assert isinstance(response, bool)

# --- To test Start Streamer functionality ---
# def test_StartSparkStreamer():
#     LOGGER.debug(" >>> test_StartSparkStreamer: START <<< ")
#     analyzer_obj = create_analyzer()
#     analyzer_uuid = analyzer_obj.analyzer_id.analyzer_id.uuid
#     analyzer_to_generate : Dict = {
#         "algo_name"       : analyzer_obj.algorithm_name,
#         "input_kpis"      : [k.kpi_id.uuid for k in analyzer_obj.input_kpi_ids],
#         "output_kpis"     : [k.kpi_id.uuid for k in analyzer_obj.output_kpi_ids],
#         "oper_mode"       : analyzer_obj.operation_mode,
#         "thresholds"      : json.loads(analyzer_obj.parameters["thresholds"]),
#         "window_size"     : analyzer_obj.parameters["window_size"],
#         "window_slider"   : analyzer_obj.parameters["window_slider"],
#         # "store_aggregate" : analyzer_obj.parameters["store_aggregate"] 
#     }
#     AnalyticsBackendServiceObj = AnalyticsBackendService()
#     response = AnalyticsBackendServiceObj.StartSparkStreamer(analyzer_uuid, analyzer_to_generate)
#     assert isinstance(response, bool)

# --- To TEST StartRequestListenerFunctionality
# def test_StartRequestListener():
#     LOGGER.info('test_RunRequestListener')
#     AnalyticsBackendServiceObj = AnalyticsBackendService()
#     AnalyticsBackendServiceObj.stop_event = Event()
#     listener_thread = Thread(target=AnalyticsBackendServiceObj.RequestListener, args=())
#     listener_thread.start()

#     time.sleep(100)

    # AnalyticsBackendServiceObj.stop_event.set()
    # LOGGER.info('Backend termination initiated. waiting for termination... 10 seconds')
    # listener_thread.join(timeout=10)
    # assert not listener_thread.is_alive(), "RequestListener thread did not terminate as expected."
    # LOGGER.info('Completed test_RunRequestListener')

# To test START and STOP communication together
# def test_StopRequestListener():
#     LOGGER.info('test_RunRequestListener')
#     LOGGER.info('Initiating StartRequestListener...')
#     AnalyticsBackendServiceObj = AnalyticsBackendService()
#     response_thread = AnalyticsBackendServiceObj.StartRequestListener() # response is Tuple (thread, stop_event)
#     # LOGGER.debug(str(response_thread))
#     time.sleep(10)
#     LOGGER.info('Initiating StopRequestListener...')
#     AnalyticsBackendServiceObj = AnalyticsBackendService()
#     response = AnalyticsBackendServiceObj.StopRequestListener(response_thread)
#     LOGGER.debug(str(response)) 
#     assert isinstance(response, bool)

# To independently tests the SparkListener functionality
# def test_SparkListener():
#     LOGGER.info('test_RunRequestListener')
#     AnalyticsBackendServiceObj = AnalyticsBackendService()
#     response = AnalyticsBackendServiceObj.RunSparkStreamer(
#         get_kpi_id_list(), get_operation_list(), get_threshold_dict()
#         )
#     LOGGER.debug(str(response))
#     assert isinstance(response, bool)
