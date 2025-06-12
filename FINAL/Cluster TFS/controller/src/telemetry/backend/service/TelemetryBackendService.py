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

import json
import time
import random
import logging
import threading
from typing   import Any, Dict
from datetime import datetime, timezone
# from common.proto.context_pb2 import Empty
from confluent_kafka import Producer as KafkaProducer
from confluent_kafka import Consumer as KafkaConsumer
from confluent_kafka import KafkaError
from common.Constants import ServiceNameEnum
from common.Settings import get_service_port_grpc
from common.tools.kafka.Variables import KafkaConfig, KafkaTopic
from common.method_wrappers.Decorator import MetricsPool
from common.tools.service.GenericGrpcService import GenericGrpcService

LOGGER             = logging.getLogger(__name__)
METRICS_POOL       = MetricsPool('TelemetryBackend', 'backendService')

class TelemetryBackendService(GenericGrpcService):
    """
    Class listens for request on Kafka topic, fetches requested metrics from device.
    Produces metrics on both RESPONSE and VALUE kafka topics.
    """
    def __init__(self, cls_name : str = __name__) -> None:
        LOGGER.info('Init TelemetryBackendService')
        port = get_service_port_grpc(ServiceNameEnum.TELEMETRYBACKEND)
        super().__init__(port, cls_name=cls_name)
        self.kafka_producer = KafkaProducer({'bootstrap.servers' : KafkaConfig.get_kafka_address()})
        self.kafka_consumer = KafkaConsumer({'bootstrap.servers' : KafkaConfig.get_kafka_address(),
                                            'group.id'           : 'backend',
                                            'auto.offset.reset'  : 'latest'})
        self.running_threads = {}

    def install_servicers(self):
        threading.Thread(target=self.RequestListener).start()

    def RequestListener(self):
        """
        listener for requests on Kafka topic.
        """
        LOGGER.info('Telemetry backend request listener is running ...')
        # print      ('Telemetry backend request listener is running ...')
        consumer = self.kafka_consumer
        consumer.subscribe([KafkaTopic.REQUEST.value])
        while True:
            receive_msg = consumer.poll(2.0)
            if receive_msg is None:
                continue
            elif receive_msg.error():
                if receive_msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    # print("Consumer error: {}".format(receive_msg.error()))
                    break
            try: 
                collector = json.loads(receive_msg.value().decode('utf-8'))
                collector_id = receive_msg.key().decode('utf-8')
                LOGGER.debug('Recevied Collector: {:} - {:}'.format(collector_id, collector))
                # print('Recevied Collector: {:} - {:}'.format(collector_id, collector))

                if collector['duration'] == -1 and collector['interval'] == -1:
                    self.TerminateCollectorBackend(collector_id)
                else:
                    self.RunInitiateCollectorBackend(collector_id, collector)
            except Exception as e:
                LOGGER.warning("Unable to consumer message from topic: {:}. ERROR: {:}".format(KafkaTopic.REQUEST.value, e))
                # print         ("Unable to consumer message from topic: {:}. ERROR: {:}".format(KafkaTopic.REQUEST.value, e))

    def TerminateCollectorBackend(self, collector_id):
        if collector_id in self.running_threads:
            thread, stop_event = self.running_threads[collector_id]
            stop_event.set()
            thread.join()
            # print ("Terminating backend (by StopCollector): Collector Id: ", collector_id)
            del self.running_threads[collector_id]
            self.GenerateCollectorTerminationSignal(collector_id, "-1", -1)          # Termination confirmation to frontend.
        else:
            # print ('Backend collector {:} not found'.format(collector_id))
            LOGGER.warning('Backend collector {:} not found'.format(collector_id))

    def RunInitiateCollectorBackend(self, collector_id: str, collector: str):
        stop_event = threading.Event()
        thread = threading.Thread(target=self.InitiateCollectorBackend, 
                                  args=(collector_id, collector, stop_event))
        self.running_threads[collector_id] = (thread, stop_event)
        thread.start()

    def InitiateCollectorBackend(self, collector_id, collector, stop_event):
        """
        Method receives collector request and initiates collecter backend.
        """
        # print("Initiating backend for collector: ", collector_id)
        LOGGER.info("Initiating backend for collector: {:s}".format(str(collector_id)))
        start_time = time.time()
        while not stop_event.is_set():
            if int(collector['duration']) != -1 and time.time() - start_time >= collector['duration']:            # condition to terminate backend
                print("Execuation duration completed: Terminating backend: Collector Id: ", collector_id, " - ", time.time() - start_time)
                self.GenerateCollectorTerminationSignal(collector_id, "-1", -1)       # Termination confirmation to frontend.
                break
            self.ExtractKpiValue(collector_id, collector['kpi_id'])
            time.sleep(collector['interval'])

    def GenerateCollectorTerminationSignal(self, collector_id: str, kpi_id: str, measured_kpi_value: Any):
        """
        Method to write kpi Termination signat on RESPONSE Kafka topic
        """
        producer = self.kafka_producer
        kpi_value : Dict = {
            "kpi_id"    : kpi_id,
            "kpi_value" : measured_kpi_value,
        }
        producer.produce(
            KafkaTopic.RESPONSE.value, # TODO: to  the topic ...
            key      = collector_id,
            value    = json.dumps(kpi_value),
            callback = self.delivery_callback
        )
        producer.flush()

    def ExtractKpiValue(self, collector_id: str, kpi_id: str):
        """
        Method to extract kpi value.
        """
        measured_kpi_value = random.randint(1,100)                      # TODO: To be extracted from a device
        # print ("Measured Kpi value: {:}".format(measured_kpi_value))
        self.GenerateCollectorResponse(collector_id, kpi_id , measured_kpi_value)

    def GenerateCollectorResponse(self, collector_id: str, kpi_id: str, measured_kpi_value: Any):
        """
        Method to write kpi value on RESPONSE Kafka topic
        """
        producer = self.kafka_producer
        kpi_value : Dict = {
            "time_stamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "kpi_id"    : kpi_id,
            "kpi_value" : measured_kpi_value
        }
        producer.produce(
            KafkaTopic.VALUE.value, # TODO: to  the topic ...
            key      = collector_id,
            value    = json.dumps(kpi_value),
            callback = self.delivery_callback
        )
        producer.flush()

    def delivery_callback(self, err, msg):
        """
        Callback function to handle message delivery status.
        Args: err (KafkaError): Kafka error object.
              msg (Message): Kafka message object.
        """
        if err:
            LOGGER.error('Message delivery failed: {:}'.format(err))
            # print(f'Message delivery failed: {err}')
        #else:
        #    LOGGER.debug('Message delivered to topic {:}'.format(msg.topic()))
        #    # print(f'Message delivered to topic {msg.topic()}')
