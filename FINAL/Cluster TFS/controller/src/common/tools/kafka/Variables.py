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

import logging
from enum import Enum
from confluent_kafka.admin import AdminClient, NewTopic
from common.Settings import get_setting


LOGGER = logging.getLogger(__name__)
KFK_SERVER_ADDRESS_TEMPLATE = 'kafka-service.{:s}.svc.cluster.local:{:s}'

class KafkaConfig(Enum):

    @staticmethod
    def get_kafka_address() -> str:
        kafka_server_address = get_setting('KFK_SERVER_ADDRESS', default=None)
        if kafka_server_address is None:
            KFK_NAMESPACE        = get_setting('KFK_NAMESPACE')
            KFK_PORT             = get_setting('KFK_SERVER_PORT')
            kafka_server_address = KFK_SERVER_ADDRESS_TEMPLATE.format(KFK_NAMESPACE, KFK_PORT)
        return kafka_server_address
        
    @staticmethod
    def get_admin_client():
        SERVER_ADDRESS = KafkaConfig.get_kafka_address()
        ADMIN_CLIENT   = AdminClient({'bootstrap.servers': SERVER_ADDRESS })
        return ADMIN_CLIENT


class KafkaTopic(Enum):
    # TODO: Later to be populated from ENV variable.
    REQUEST            = 'topic_request' 
    RESPONSE           = 'topic_response'
    RAW                = 'topic_raw' 
    LABELED            = 'topic_labeled'
    VALUE              = 'topic_value'
    ALARMS             = 'topic_alarms'
    ANALYTICS_REQUEST  = 'topic_request_analytics'
    ANALYTICS_RESPONSE = 'topic_response_analytics'

    @staticmethod
    def create_all_topics() -> bool:
        """
            Method to create Kafka topics defined as class members
        """
        all_topics = [member.value for member in KafkaTopic]
        LOGGER.debug("Kafka server address is: {:} ".format(KafkaConfig.get_kafka_address()))
        if( KafkaTopic.create_new_topic_if_not_exists( all_topics )):
            LOGGER.debug("All topics are created sucsessfully or Already Exists")
            return True
        else:
            LOGGER.debug("Error creating all topics")
            return False
    
    @staticmethod
    def create_new_topic_if_not_exists(new_topics: list) -> bool:
        """
        Method to create Kafka topic if it does not exist.
        Args:
            list of topic: containing the topic name(s) to be created on Kafka
        """
        LOGGER.debug("Topics names to be verified and created: {:}".format(new_topics))
        for topic in new_topics:
            try:
                topic_metadata = KafkaConfig.get_admin_client().list_topics(timeout=5)
                # LOGGER.debug("Existing topic list: {:}".format(topic_metadata.topics))
                if topic not in topic_metadata.topics:
                    # If the topic does not exist, create a new topic
                    print("Topic {:} does not exist. Creating...".format(topic))
                    LOGGER.debug("Topic {:} does not exist. Creating...".format(topic))
                    new_topic = NewTopic(topic, num_partitions=1, replication_factor=1)
                    KafkaConfig.get_admin_client().create_topics([new_topic])
                else:
                    print("Topic name already exists: {:}".format(topic))
                    LOGGER.debug("Topic name already exists: {:}".format(topic))
            except Exception as e:
                LOGGER.debug("Failed to create topic: {:}".format(e))
                return False
        return True

# TODO: create all topics after the deployments (Telemetry and Analytics)
