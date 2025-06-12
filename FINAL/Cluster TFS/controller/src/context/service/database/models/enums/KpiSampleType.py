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

import enum, functools
from common.proto.kpi_sample_types_pb2 import KpiSampleType
from ._GrpcToEnum import grpc_to_enum

# IMPORTANT: Entries of enum class ORM_KpiSampleTypeEnum should be named as in
#            the proto files removing the prefixes. For example, proto item
#            KpiSampleType.KPISAMPLETYPE_BYTES_RECEIVED should be declared as
#            BYTES_RECEIVED. If item name does not match, automatic mapping of
#            proto enums to database enums will fail.
class ORM_KpiSampleTypeEnum(enum.Enum):
    UNKNOWN                  = KpiSampleType.KPISAMPLETYPE_UNKNOWN
    PACKETS_TRANSMITTED      = KpiSampleType.KPISAMPLETYPE_PACKETS_TRANSMITTED
    PACKETS_RECEIVED         = KpiSampleType.KPISAMPLETYPE_PACKETS_RECEIVED
    BYTES_TRANSMITTED        = KpiSampleType.KPISAMPLETYPE_BYTES_TRANSMITTED
    BYTES_RECEIVED           = KpiSampleType.KPISAMPLETYPE_BYTES_RECEIVED
    LINK_TOTAL_CAPACITY_GBPS = KpiSampleType.KPISAMPLETYPE_LINK_TOTAL_CAPACITY_GBPS
    LINK_USED_CAPACITY_GBPS  = KpiSampleType.KPISAMPLETYPE_LINK_USED_CAPACITY_GBPS

grpc_to_enum__kpi_sample_type = functools.partial(
    grpc_to_enum, KpiSampleType, ORM_KpiSampleTypeEnum)
