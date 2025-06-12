# Copyright 2022-2024 ETSI SDG TeraFlowSDN (TFS) (https://tfs.etsi.org/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import grpc, json, logging
from uuid import uuid4
from common.method_wrappers.Decorator import MetricsPool, safe_and_metered_rpc_method
from common.method_wrappers.ServiceExceptions import InvalidArgumentException
from common.proto.analytics_frontend_pb2 import Analyzer, AnalyzerId
from common.proto.automation_pb2 import ZSMCreateRequest, ZSMService, ZSMServiceID, ZSMServiceState, ZSMCreateUpdate
from common.proto.automation_pb2_grpc import AutomationServiceServicer
from common.proto.context_pb2 import Service, ServiceId
from common.proto.kpi_manager_pb2 import KpiId, KpiDescriptor
from common.proto.policy_pb2 import PolicyRuleService, PolicyRuleState
from common.proto.policy_action_pb2 import PolicyRuleAction, PolicyRuleActionConfig
from common.proto.policy_condition_pb2 import PolicyRuleCondition
from common.proto.telemetry_frontend_pb2 import Collector, CollectorId

from analytics.frontend.client.AnalyticsFrontendClient import AnalyticsFrontendClient
from automation.client.PolicyClient import PolicyClient
from context.client.ContextClient import ContextClient
from kpi_manager.client.KpiManagerClient import KpiManagerClient
from telemetry.frontend.client.TelemetryFrontendClient import TelemetryFrontendClient

LOGGER = logging.getLogger(__name__)
METRICS_POOL = MetricsPool('Automation', 'RPC')

class AutomationServiceServicerImpl(AutomationServiceServicer):
    def __init__(self):
        LOGGER.info('Init AutomationService')

    @safe_and_metered_rpc_method(METRICS_POOL,LOGGER)
    def ZSMCreate(self, request : ZSMCreateRequest, context : grpc.ServicerContext) -> ZSMService:

        # check that service does not exist
        context_client = ContextClient()
        kpi_manager_client = KpiManagerClient()
        policy_client = PolicyClient()
        telemetry_frontend_client = TelemetryFrontendClient()
        analytics_frontend_client = AnalyticsFrontendClient()

        try:

            # TODO: Remove static variables(get them from ZSMCreateRequest)
            # TODO: Refactor policy component (remove unnecessary variables)

            ####### GET Context #######################
            LOGGER.info('Get the service from Context: ')
            service: Service = context_client.GetService(request.serviceId)
            LOGGER.info('Service ({:s}) :'.format(str(service)))
            ###########################################

            ####### SET Kpi Descriptor LAT ################
            LOGGER.info('Set Kpi Descriptor LAT: ')

            if(len(service.service_constraints) == 0):
                raise InvalidArgumentException("service_constraints" , "empty",  []);

            if(len(service.service_constraints) > 1):
                raise InvalidArgumentException("service_constraints" , ">1",  []);

            if(service.service_constraints[0].sla_latency is None ):
                raise InvalidArgumentException("sla_latency", "empty", []);

            ## Static Implementation Applied only in case of SLA Latency Constraint ##

            # KPI Descriptor
            kpi_descriptor_lat = KpiDescriptor()
            kpi_descriptor_lat.kpi_sample_type = 701 #'KPISAMPLETYPE_SERVICE_LATENCY_MS'  #static service.service_constraints[].sla_latency.e2e_latency_ms
            kpi_descriptor_lat.service_id.service_uuid.uuid = request.serviceId.service_uuid.uuid
            kpi_descriptor_lat.kpi_id.kpi_id.uuid = str(uuid4())

            kpi_id_lat: KpiId = kpi_manager_client.SetKpiDescriptor(kpi_descriptor_lat)
            LOGGER.info('The kpi_id_lat({:s})'.format(str(kpi_id_lat)))
            ###########################################

            ####### SET Kpi Descriptor TX ################
            LOGGER.info('Set Kpi Descriptor TX: ')

            kpi_descriptor_tx = KpiDescriptor()
            kpi_descriptor_tx.kpi_sample_type = 101  # static KPISAMPLETYPE_PACKETS_TRANSMITTED
            kpi_descriptor_tx.service_id.service_uuid.uuid = request.serviceId.service_uuid.uuid
            kpi_descriptor_tx.kpi_id.kpi_id.uuid = str(uuid4())

            kpi_id_tx: KpiId = kpi_manager_client.SetKpiDescriptor(kpi_descriptor_tx)
            LOGGER.info('The kpi_id_tx({:s})'.format(str(kpi_id_tx)))
            ###########################################

            ####### SET Kpi Descriptor RX ################
            LOGGER.info('Set Kpi Descriptor RX: ')

            kpi_descriptor_rx = KpiDescriptor()
            kpi_descriptor_rx.kpi_sample_type = 102  # static KPISAMPLETYPE_PACKETS_RECEIVED
            kpi_descriptor_rx.service_id.service_uuid.uuid = request.serviceId.service_uuid.uuid
            kpi_descriptor_rx.kpi_id.kpi_id.uuid = str(uuid4())

            kpi_id_rx: KpiId = kpi_manager_client.SetKpiDescriptor(kpi_descriptor_rx)
            LOGGER.info('kpi_id_rx({:s})'.format(str(kpi_id_rx)))
            ###########################################



            ####### START Collector TX #################
            collect_tx = Collector()
            collect_tx.collector_id.collector_id.uuid = str(uuid4())
            collect_tx.kpi_id.kpi_id.uuid = kpi_id_tx.kpi_id.uuid
            collect_tx.duration_s = 20000  # static
            collect_tx.interval_s = 1  # static
            LOGGER.info('Start Collector TX'.format(str(collect_tx)))

            collect_id_tx: CollectorId = telemetry_frontend_client.StartCollector(collect_tx)
            LOGGER.info('collect_id_tx({:s})'.format(str(collect_id_tx)))
            #############################################

            ####### START Collector RX ##################
            collect_rx = Collector()
            collect_rx.collector_id.collector_id.uuid = str(uuid4())
            collect_rx.kpi_id.kpi_id.uuid = kpi_id_rx.kpi_id.uuid
            collect_rx.duration_s = 20000  # static
            collect_rx.interval_s = 1  # static
            LOGGER.info('Start Collector RX'.format(str(collect_rx)))

            collect_id_rx: CollectorId = telemetry_frontend_client.StartCollector(collect_rx)
            LOGGER.info('collect_id_tx({:s})'.format(str(collect_id_rx)))
            ###############################################

            ####### START Analyzer LAT ################
            analyzer = Analyzer()
            analyzer.analyzer_id.analyzer_id.uuid = str(uuid4())
            analyzer.algorithm_name = 'Test_Aggregate_and_Threshold'  # static
            analyzer.operation_mode = 2
            analyzer.input_kpi_ids.append(kpi_id_rx)
            analyzer.input_kpi_ids.append(kpi_id_tx)
            analyzer.output_kpi_ids.append(kpi_id_lat)

            thresholdStr = service.service_constraints[0].custom.constraint_type

            _threshold_dict = {thresholdStr: (0, int(service.service_constraints[0].custom.constraint_value))}
            analyzer.parameters['thresholds'] = json.dumps(_threshold_dict)
            analyzer.parameters['window_size'] = "60s"
            analyzer.parameters['window_slider'] = "30s"

            analyzer_id_lat: AnalyzerId = analytics_frontend_client.StartAnalyzer(analyzer)
            LOGGER.info('analyzer_id_lat({:s})'.format(str(analyzer_id_lat)))
            ###########################################################

            ####### SET Policy LAT ################
            policy_lat = PolicyRuleService()
            policy_lat.serviceId.service_uuid.uuid = request.serviceId.service_uuid.uuid
            policy_lat.serviceId.context_id.context_uuid.uuid = request.serviceId.context_id.context_uuid.uuid

            # PolicyRuleBasic
            policy_lat.policyRuleBasic.priority = 0
            policy_lat.policyRuleBasic.policyRuleId.uuid.uuid = str(uuid4())
            policy_lat.policyRuleBasic.booleanOperator = 2

            # PolicyRuleAction
            policyRuleActionConfig = PolicyRuleActionConfig()
            policyRuleActionConfig.action_key = ""
            policyRuleActionConfig.action_value = ""

            policyRuleAction = PolicyRuleAction()
            policyRuleAction.action = 5
            policyRuleAction.action_config.append(policyRuleActionConfig)
            policy_lat.policyRuleBasic.actionList.append(policyRuleAction)

            # for constraint in service.service_constraints:

                # PolicyRuleCondition
            policyRuleCondition = PolicyRuleCondition()
            policyRuleCondition.kpiId.kpi_id.uuid = kpi_id_lat.kpi_id.uuid
            policyRuleCondition.numericalOperator = 5
            policyRuleCondition.kpiValue.floatVal = 300

            policy_lat.policyRuleBasic.conditionList.append(policyRuleCondition)

            policy_rule_state: PolicyRuleState = policy_client.PolicyAddService(policy_lat)
            LOGGER.info('policy_rule_state({:s})'.format(str(policy_rule_state)))

        except grpc.RpcError as e:
            if e.code() != grpc.StatusCode.NOT_FOUND: raise  # pylint: disable=no-member
            LOGGER.exception('Unable to get Service({:s})'.format(str(request)))
            context_client.close()
            kpi_manager_client.close()
            policy_client.close()
            telemetry_frontend_client.close()
            return None

        context_client.close()
        kpi_manager_client.close()
        policy_client.close()
        telemetry_frontend_client.close()
        return ZSMService()

    @safe_and_metered_rpc_method(METRICS_POOL,LOGGER)
    def ZSMUpdate(self, request : ZSMCreateUpdate, context : grpc.ServicerContext) -> ZSMService:
        LOGGER.info('NOT IMPLEMENTED ZSMUpdate')
        return ZSMService()

    @safe_and_metered_rpc_method(METRICS_POOL,LOGGER)
    def ZSMDelete(self, request : ZSMServiceID, context : grpc.ServicerContext) -> ZSMServiceState:
        LOGGER.info('NOT IMPLEMENTED ZSMDelete')
        return ZSMServiceState()

    @safe_and_metered_rpc_method(METRICS_POOL,LOGGER)
    def ZSMGetById(self, request : ZSMServiceID, context : grpc.ServicerContext) -> ZSMService:
        LOGGER.info('NOT IMPLEMENTED ZSMGetById')
        return ZSMService()


    @safe_and_metered_rpc_method(METRICS_POOL,LOGGER)
    def ZSMGetByService(self, request : ServiceId, context : grpc.ServicerContext) -> ZSMService:
        LOGGER.info('NOT IMPLEMENTED ZSMGetByService')
        return ZSMService()
