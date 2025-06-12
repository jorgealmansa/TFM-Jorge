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

import grpc, logging, sqlalchemy
from typing import Iterator

import grpc._channel
from common.method_wrappers.Decorator import MetricsPool, safe_and_metered_rpc_method
from common.proto.context_pb2 import Constraint, ConstraintActionEnum, Constraint_QoSProfile, Constraint_Schedule, Empty, QoSProfileId
from common.proto.qos_profile_pb2 import QoSProfile, QoDConstraintsRequest
from common.proto.qos_profile_pb2_grpc import QoSProfileServiceServicer
from .database.QoSProfile import set_qos_profile, delete_qos_profile, get_qos_profile, get_qos_profiles


LOGGER = logging.getLogger(__name__)

METRICS_POOL = MetricsPool('QoSProfile', 'RPC')

class QoSProfileServiceServicerImpl(QoSProfileServiceServicer):
    def __init__(self, db_engine: sqlalchemy.engine.Engine) -> None:
        LOGGER.debug('Servicer Created')
        self.db_engine = db_engine

    def _get_metrics(self) -> MetricsPool: return METRICS_POOL

    @safe_and_metered_rpc_method(METRICS_POOL, LOGGER)
    def CreateQoSProfile(self, request: QoSProfile, context: grpc.ServicerContext) -> QoSProfile:
        qos_profile = get_qos_profile(self.db_engine, request.qos_profile_id.qos_profile_id.uuid)
        if qos_profile is not None:
            context.set_details(f'QoSProfile {request.qos_profile_id.qos_profile_id.uuid} already exists')
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            return QoSProfile()
        return set_qos_profile(self.db_engine, request)

    @safe_and_metered_rpc_method(METRICS_POOL, LOGGER)
    def UpdateQoSProfile(self, request: QoSProfile, context: grpc.ServicerContext) -> QoSProfile:
        qos_profile = get_qos_profile(self.db_engine, request.qos_profile_id.qos_profile_id.uuid)
        if qos_profile is None:
            context.set_details(f'QoSProfile {request.qos_profile_id.qos_profile_id.uuid} not found')
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return QoSProfile()
        return set_qos_profile(self.db_engine, request)

    @safe_and_metered_rpc_method(METRICS_POOL, LOGGER)
    def DeleteQoSProfile(self, request: QoSProfileId, context: grpc.ServicerContext) -> Empty:
        qos_profile = get_qos_profile(self.db_engine, request.qos_profile_id.uuid)
        if qos_profile is None:
            context.set_details(f'QoSProfile {request.qos_profile_id.uuid} not found')
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return QoSProfile()
        return delete_qos_profile(self.db_engine, request.qos_profile_id.uuid)

    @safe_and_metered_rpc_method(METRICS_POOL, LOGGER)
    def GetQoSProfile(self, request: QoSProfileId, context: grpc.ServicerContext) -> QoSProfile:
        qos_profile = get_qos_profile(self.db_engine, request.qos_profile_id.uuid)
        if qos_profile is None:
            context.set_details(f'QoSProfile {request.qos_profile_id.uuid} not found')
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return QoSProfile()
        return qos_profile

    @safe_and_metered_rpc_method(METRICS_POOL, LOGGER)
    def GetQoSProfiles(self, request: Empty, context: grpc.ServicerContext) -> Iterator[QoSProfile]:
        yield from get_qos_profiles(self.db_engine, request)


    @safe_and_metered_rpc_method(METRICS_POOL, LOGGER)
    def GetConstraintListFromQoSProfile(self, request: QoDConstraintsRequest, context: grpc.ServicerContext) -> Iterator[Constraint]:
        qos_profile = get_qos_profile(self.db_engine, request.qos_profile_id.qos_profile_id.uuid)
        if qos_profile is None:
            context.set_details(f'QoSProfile {request.qos_profile_id.qos_profile_id.uuid} not found')
            context.set_code(grpc.StatusCode.NOT_FOUND)
            yield Constraint()

        qos_profile_constraint = Constraint_QoSProfile()
        qos_profile_constraint.qos_profile_name = qos_profile.name
        qos_profile_constraint.qos_profile_id.CopyFrom(qos_profile.qos_profile_id)
        constraint_qos = Constraint()
        constraint_qos.action = ConstraintActionEnum.CONSTRAINTACTION_SET
        constraint_qos.qos_profile.CopyFrom(qos_profile_constraint)
        yield constraint_qos
        constraint_schedule = Constraint()
        constraint_schedule.action = ConstraintActionEnum.CONSTRAINTACTION_SET
        constraint_schedule.schedule.CopyFrom(Constraint_Schedule(start_timestamp=request.start_timestamp, duration_days=request.duration/86400))
        yield constraint_schedule
