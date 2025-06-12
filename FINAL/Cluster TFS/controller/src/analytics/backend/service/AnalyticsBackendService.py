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

import time
import json
import logging
import threading
from common.tools.service.GenericGrpcService import GenericGrpcService
from common.tools.kafka.Variables import KafkaConfig, KafkaTopic
from confluent_kafka import Consumer as KafkaConsumer
from confluent_kafka import KafkaError
from common.Constants import ServiceNameEnum
from common.Settings import get_service_port_grpc
from threading import Thread, Event
from .DaskStreaming import DaskStreamer

LOGGER = logging.getLogger(__name__)

class AnalyticsBackendService(GenericGrpcService):
    """
    Class listens for ...
    """
    def __init__(self, cls_name : str = __name__) -> None:
        LOGGER.info('Init AnalyticsBackendService')
        port = get_service_port_grpc(ServiceNameEnum.ANALYTICSBACKEND)
        super().__init__(port, cls_name=cls_name)
        self.running_threads = {}       # To keep track of all running analyzers 
        self.kafka_consumer = KafkaConsumer({'bootstrap.servers' : KafkaConfig.get_kafka_address(),
                                            'group.id'           : 'analytics-frontend',
                                            'auto.offset.reset'  : 'latest'})

    def install_servicers(self):
        threading.Thread(target=self.RequestListener, args=()).start()

    def RequestListener(self):
        """
        listener for requests on Kafka topic.
        """
        LOGGER.info("Request Listener is initiated ...")
        # print      ("Request Listener is initiated ...")
        consumer = self.kafka_consumer
        consumer.subscribe([KafkaTopic.ANALYTICS_REQUEST.value])
        while True:
            receive_msg = consumer.poll(2.0)
            if receive_msg is None:
                continue
            elif receive_msg.error():
                if receive_msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    LOGGER.error("Consumer error: {:}".format(receive_msg.error()))
                    # print       ("Consumer error: {:}".format(receive_msg.error()))
                    break
            try:
                analyzer      = json.loads(receive_msg.value().decode('utf-8'))
                analyzer_uuid = receive_msg.key().decode('utf-8')
                LOGGER.debug('Recevied Analyzer: {:} - {:}'.format(analyzer_uuid, analyzer))
                # print       ('Recevied Analyzer: {:} - {:}'.format(analyzer_uuid, analyzer))

                if analyzer["algo_name"] is None and analyzer["oper_mode"] is None:
                    self.StopDaskListener(analyzer_uuid)
                else:
                    self.StartDaskListener(analyzer_uuid, analyzer)
            except Exception as e:
                LOGGER.warning("Unable to consume message from topic: {:}. ERROR: {:}".format(KafkaTopic.ANALYTICS_REQUEST.value, e))
                # print         ("Unable to consume message from topic: {:}. ERROR: {:}".format(KafkaTopic.ANALYTICS_REQUEST.value, e))

    def StartDaskListener(self, analyzer_uuid, analyzer):
        kpi_list      = analyzer[ 'input_kpis'   ] 
        thresholds    = analyzer[ 'thresholds'   ]
        window_size   = analyzer[ 'window_size'  ]
        window_slider = analyzer[ 'window_slider']

        LOGGER.debug ("Received parameters: {:} - {:} - {:} - {:}".format(
            kpi_list, thresholds, window_size, window_slider))
        # print        ("Received parameters: {:} - {:} - {:} - {:}".format(
        #     kpi_list, thresholds, window_size, window_slider))
        try:
            stop_event = Event()
            thread     = Thread(
                target=DaskStreamer,
                # args=(analyzer_uuid, kpi_list, oper_list, thresholds, stop_event),
                args=(analyzer['output_kpis'][0] , kpi_list, thresholds, stop_event),
                kwargs={
                    "window_size"       : window_size,
                }
            )
            thread.start()
            self.running_threads[analyzer_uuid] = (thread, stop_event)
            # print      ("Initiated Analyzer backend: {:}".format(analyzer_uuid))
            LOGGER.info("Initiated Analyzer backend: {:}".format(analyzer_uuid))
            return True
        except Exception as e:
            # print       ("Failed to initiate Analyzer backend: {:}".format(e))
            LOGGER.error("Failed to initiate Analyzer backend: {:}".format(e))
            return False

    def StopDaskListener(self, analyzer_uuid):
        if analyzer_uuid in self.running_threads:
            try:
                thread, stop_event = self.running_threads[analyzer_uuid]
                stop_event.set()
                thread.join()
                del self.running_threads[analyzer_uuid]
                # print      ("Terminating backend (by TerminateBackend): Analyzer Id: {:}".format(analyzer_uuid))
                LOGGER.info("Terminating backend (by TerminateBackend): Analyzer Id: {:}".format(analyzer_uuid))
                return True
            except Exception as e:
                LOGGER.error("Failed to terminate. Analyzer Id: {:} - ERROR: {:}".format(analyzer_uuid, e))
                return False
        else:
            # print         ("Analyzer not found in active collectors. Analyzer Id: {:}".format(analyzer_uuid))
            LOGGER.warning("Analyzer not found in active collectors: Analyzer Id: {:}".format(analyzer_uuid))
