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

# read Kafka stream from Kafka topic

import logging
from prometheus_client import Gauge
from common.proto.kpi_sample_types_pb2 import KpiSampleType

from common.proto.kpi_value_api_pb2 import KpiValue
from common.proto.kpi_manager_pb2 import KpiDescriptor

LOGGER         = logging.getLogger(__name__)
PROM_METRICS   = {}

class MetricWriterToPrometheus:
    '''
    This class exposes the *cooked KPI* on the endpoint to be scraped by the Prometheus server.
    cooked KPI value = KpiDescriptor (gRPC message) + KpiValue (gRPC message)
    '''
    def __init__(self):
        pass

    def merge_kpi_descriptor_and_kpi_value(self, kpi_descriptor, kpi_value):
            # Creating a dictionary from the kpi_descriptor's attributes
            cooked_kpi = {
                'kpi_id'         : kpi_descriptor.kpi_id.kpi_id.uuid,
                'kpi_description': kpi_descriptor.kpi_description,
                'kpi_sample_type': KpiSampleType.Name(kpi_descriptor.kpi_sample_type),
                'device_id'      : kpi_descriptor.device_id.device_uuid.uuid,
                'endpoint_id'    : kpi_descriptor.endpoint_id.endpoint_uuid.uuid,
                'service_id'     : kpi_descriptor.service_id.service_uuid.uuid,
                'slice_id'       : kpi_descriptor.slice_id.slice_uuid.uuid,
                'connection_id'  : kpi_descriptor.connection_id.connection_uuid.uuid,
                'link_id'        : kpi_descriptor.link_id.link_uuid.uuid,
                'time_stamp'     : kpi_value.timestamp.timestamp,
                'kpi_value'      : kpi_value.kpi_value_type.floatVal
            }
            LOGGER.debug("Cooked Kpi: {:}".format(cooked_kpi))
            return cooked_kpi

    def create_and_expose_cooked_kpi(self, kpi_descriptor: KpiDescriptor, kpi_value: KpiValue):
        # merge both gRPC messages into single varible.
        cooked_kpi = self.merge_kpi_descriptor_and_kpi_value(kpi_descriptor, kpi_value)
        tags_to_exclude = {'kpi_description', 'kpi_sample_type', 'kpi_value'}           
        metric_tags = [tag for tag in cooked_kpi.keys() if tag not in tags_to_exclude]  # These values will be used as metric tags
        metric_name = cooked_kpi['kpi_sample_type']
        try:
            if metric_name not in PROM_METRICS:     # Only register the metric, when it doesn't exists
                PROM_METRICS[metric_name] = Gauge ( 
                    metric_name,
                    cooked_kpi['kpi_description'],
                    metric_tags
                )
            LOGGER.debug("Metric is created with labels: {:}".format(metric_tags))
            PROM_METRICS[metric_name].labels(
                    kpi_id          = cooked_kpi['kpi_id'],
                    device_id       = cooked_kpi['device_id'],
                    endpoint_id     = cooked_kpi['endpoint_id'],
                    service_id      = cooked_kpi['service_id'],
                    slice_id        = cooked_kpi['slice_id'],
                    connection_id   = cooked_kpi['connection_id'],
                    link_id         = cooked_kpi['link_id'],
                    time_stamp      = cooked_kpi['time_stamp'],
                ).set(float(cooked_kpi['kpi_value']))
            LOGGER.debug("Metric pushed to the endpoints: {:}".format(PROM_METRICS[metric_name]))

        except ValueError as e:
            if 'Duplicated timeseries' in str(e):
                LOGGER.debug("Metric {:} is already registered. Skipping.".format(metric_name))
                print("Metric {:} is already registered. Skipping.".format(metric_name))
            else:
                LOGGER.error("Error while pushing metric: {}".format(e))
                raise

