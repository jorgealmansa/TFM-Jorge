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
from kpi_value_writer.service.KpiValueWriter import KpiValueWriter

from common.tools.kafka.Variables import KafkaTopic



LOGGER = logging.getLogger(__name__)

# -------- Initial Test ----------------
def test_validate_kafka_topics():
    LOGGER.debug(" >>> test_validate_kafka_topics: START <<< ")
    response = KafkaTopic.create_all_topics()
    assert isinstance(response, bool)

def test_KafkaConsumer():
    LOGGER.debug(" --->>> test_kafka_consumer: START <<<--- ")
    # kpi_value_writer = KpiValueWriter()
    # kpi_value_writer.RunKafkaConsumer()
