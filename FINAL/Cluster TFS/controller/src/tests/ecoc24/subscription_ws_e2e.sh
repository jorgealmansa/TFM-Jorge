#!/bin/bash
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


########################################################################################################################
# Read deployment settings
########################################################################################################################

# If not already set, set the namespace where CockroackDB will be deployed.
export SUBSCRIPTION_WS_NAMESPACE=${SUBSCRIPTION_WS_NAMESPACE:-"tfs-e2e"}

# If not already set, set the external port interface will be exposed to.
export SUBSCRIPTION_WS_EXT_PORT=${SUBSCRIPTION_WS_EXT_PORT:-"8761"}


########################################################################################################################
# Automated steps start here
########################################################################################################################


echo "Subscription WebSocket Port Mapping"
echo ">>> ExposeSubscription WebSocket port (${SUBSCRIPTION_WS_EXT_PORT}->${SUBSCRIPTION_WS_EXT_PORT})"
PATCH='{"data": {"'${SUBSCRIPTION_WS_EXT_PORT}'": "'${SUBSCRIPTION_WS_NAMESPACE}'/nbiservice:'${SUBSCRIPTION_WS_EXT_PORT}'"}}'
kubectl patch configmap nginx-ingress-tcp-microk8s-conf-e2e --namespace ingress --patch "${PATCH}"

PORT_MAP='{"containerPort": '${SUBSCRIPTION_WS_EXT_PORT}', "hostPort": '${SUBSCRIPTION_WS_EXT_PORT}'}'
CONTAINER='{"name": "nginx-ingress-microk8s", "ports": ['${PORT_MAP}']}'
PATCH='{"spec": {"template": {"spec": {"containers": ['${CONTAINER}']}}}}'
kubectl patch daemonset nginx-ingress-microk8s-controller-e2e --namespace ingress --patch "${PATCH}"
echo
