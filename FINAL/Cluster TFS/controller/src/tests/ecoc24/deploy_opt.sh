#!/bin/bash
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


# Delete old namespaces
kubectl delete namespace tfs-opt

# Delete secondary ingress controllers
kubectl delete -f src/tests/ecoc24/nginx-ingress-controller-opt.yaml

# Create secondary ingress controllers
kubectl apply -f src/tests/ecoc24/nginx-ingress-controller-opt.yaml

# Deploy TFS for OPT
source src/tests/ecoc24/deploy_specs_opt.sh
./deploy/all.sh
mv tfs_runtime_env_vars.sh tfs_runtime_env_vars_opt.sh
