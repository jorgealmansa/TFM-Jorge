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
from typing import Any, Dict, List, Union

def json_constraint_custom(constraint_type : str, constraint_value : Union[str, Dict[str, Any]]) -> Dict:
    if not isinstance(constraint_value, str): constraint_value = json.dumps(constraint_value, sort_keys=True)
    return {'custom': {'constraint_type': constraint_type, 'constraint_value': constraint_value}}

def json_constraint_schedule(start_timestamp : float, duration_days : float) -> Dict:
    return {'schedule': {'start_timestamp': start_timestamp, 'duration_days': duration_days}}

def json_constraint_endpoint_location_region(endpoint_id : Dict, region : str) -> Dict:
    return {'endpoint_location': {'endpoint_id': endpoint_id, 'location': {'region': region}}}

def json_constraint_endpoint_location_gps(endpoint_id : Dict, latitude : float, longitude : float) -> Dict:
    gps_position = {'latitude': latitude, 'longitude': longitude}
    return {'endpoint_location': {'endpoint_id': endpoint_id, 'location': {'gps_position': gps_position}}}

def json_constraint_endpoint_priority(endpoint_id : Dict, priority : int) -> Dict:
    return {'endpoint_priority': {'endpoint_id': endpoint_id, 'priority': priority}}

def json_constraint_sla_capacity(capacity_gbps : float) -> Dict:
    return {'sla_capacity': {'capacity_gbps': capacity_gbps}}

def json_constraint_sla_latency(e2e_latency_ms : float) -> Dict:
    return {'sla_latency': {'e2e_latency_ms': e2e_latency_ms}}

def json_constraint_sla_availability(num_disjoint_paths : int, all_active : bool, availability : float) -> Dict:
    return {'sla_availability': {
        'num_disjoint_paths': num_disjoint_paths, 'all_active': all_active, 'availability': availability
    }}

def json_constraint_sla_isolation(isolation_levels : List[int]) -> Dict:
    return {'sla_isolation': {'isolation_level': isolation_levels}}

def json_constraint_exclusions(
    is_permanent : bool = False, device_ids : List[Dict] = [], endpoint_ids : List[Dict] = [],
    link_ids : List[Dict] = []
) -> Dict:
    return {'exclusions': {
        'is_permanent' : is_permanent,
        'device_ids'   : device_ids,
        'endpoint_ids' : endpoint_ids,
        'link_ids'     : link_ids,
    }}
