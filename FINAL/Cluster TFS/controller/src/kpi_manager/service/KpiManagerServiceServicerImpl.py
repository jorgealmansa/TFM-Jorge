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


import logging, grpc
from common.method_wrappers.Decorator import MetricsPool, safe_and_metered_rpc_method
from common.proto.context_pb2 import Empty
from common.proto.kpi_manager_pb2_grpc import KpiManagerServiceServicer
from common.proto.kpi_manager_pb2 import KpiId, KpiDescriptor, KpiDescriptorFilter, KpiDescriptorList
# from kpi_manager.database.Kpi_DB import KpiDB
from kpi_manager.database.KpiDB import KpiDB
from kpi_manager.database.KpiModel import Kpi as KpiModel

LOGGER = logging.getLogger(__name__)
METRICS_POOL = MetricsPool('KpiManager', 'NBIgRPC')

class KpiManagerServiceServicerImpl(KpiManagerServiceServicer):
    def __init__(self):
        LOGGER.info('Init KpiManagerService')
        self.kpi_db_obj = KpiDB(KpiModel)
    
    @safe_and_metered_rpc_method(METRICS_POOL, LOGGER)
    def SetKpiDescriptor(self, request: KpiDescriptor, grpc_context: grpc.ServicerContext # type: ignore
                        ) -> KpiId: # type: ignore
        response = KpiId()
        LOGGER.info("Received gRPC message object: {:}".format(request))
        try:
            kpi_to_insert = KpiModel.convert_KpiDescriptor_to_row(request)
            if(self.kpi_db_obj.add_row_to_db(kpi_to_insert)):
                response.kpi_id.uuid = request.kpi_id.kpi_id.uuid
                # LOGGER.info("Added Row: {:}".format(response))
            return response
        except Exception as e:
            LOGGER.info("Unable to create KpiModel class object. {:}".format(e))
    
    @safe_and_metered_rpc_method(METRICS_POOL, LOGGER)        
    def GetKpiDescriptor(self, request: KpiId, grpc_context: grpc.ServicerContext # type: ignore
                         ) -> KpiDescriptor: # type: ignore
        response = KpiDescriptor()
        print("--> Received gRPC message object: {:}".format(request))
        LOGGER.info("Received gRPC message object: {:}".format(request))
        try: 
            kpi_id_to_search = request.kpi_id.uuid
            row = self.kpi_db_obj.search_db_row_by_id(KpiModel, 'kpi_id', kpi_id_to_search)
            if row is None:
                print ('No matching row found for kpi id: {:}'.format(kpi_id_to_search))
                LOGGER.info('No matching row found kpi id: {:}'.format(kpi_id_to_search))
                return Empty()
            else:
                response = KpiModel.convert_row_to_KpiDescriptor(row)
                return response
        except Exception as e:
            print ('Unable to search kpi id. {:}'.format(e))
            LOGGER.info('Unable to search kpi id. {:}'.format(e))
            raise e
    
    @safe_and_metered_rpc_method(METRICS_POOL, LOGGER)
    def DeleteKpiDescriptor(self, request: KpiId, grpc_context: grpc.ServicerContext # type: ignore
                            ) -> Empty: # type: ignore
        LOGGER.info("Received gRPC message object: {:}".format(request))
        try:
            kpi_id_to_search = request.kpi_id.uuid
            self.kpi_db_obj.delete_db_row_by_id(KpiModel, 'kpi_id', kpi_id_to_search)
        except Exception as e:
            LOGGER.info('Unable to search kpi id. {:}'.format(e))
        finally:
            return Empty()

    @safe_and_metered_rpc_method(METRICS_POOL, LOGGER)
    def SelectKpiDescriptor(self, filter: KpiDescriptorFilter, grpc_context: grpc.ServicerContext # type: ignore
                            ) -> KpiDescriptorList: # type: ignore
        LOGGER.info("Received gRPC message object: {:}".format(filter))
        response = KpiDescriptorList()
        try:
            rows = self.kpi_db_obj.select_with_filter(KpiModel, filter)
        except Exception as e:
            LOGGER.info('Unable to apply filter on kpi descriptor. {:}'.format(e))
        try:
            for row in rows:
                kpiDescriptor_obj = KpiModel.convert_row_to_KpiDescriptor(row)
                response.kpi_descriptor_list.append(kpiDescriptor_obj)
            return response
        except Exception as e:
            LOGGER.info('Unable to process filter response {:}'.format(e))
