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


rm -rf tmp/exec

echo "Collecting logs for E2E..."
mkdir -p tmp/exec/e2e
kubectl --namespace tfs-e2e logs deployments/contextservice server > tmp/exec/e2e/context.log
kubectl --namespace tfs-e2e logs deployments/deviceservice server > tmp/exec/e2e/device.log
kubectl --namespace tfs-e2e logs deployments/serviceservice server > tmp/exec/e2e/service.log
kubectl --namespace tfs-e2e logs deployments/pathcompservice frontend > tmp/exec/e2e/pathcomp-frontend.log
kubectl --namespace tfs-e2e logs deployments/pathcompservice backend > tmp/exec/e2e/pathcomp-backend.log
kubectl --namespace tfs-e2e logs deployments/sliceservice server > tmp/exec/e2e/slice.log
printf "\n"

echo "Collecting logs for IP..."
mkdir -p tmp/exec/ip
kubectl --namespace tfs-ip logs deployments/contextservice server > tmp/exec/ip/context.log
kubectl --namespace tfs-ip logs deployments/deviceservice server > tmp/exec/ip/device.log
kubectl --namespace tfs-ip logs deployments/serviceservice server > tmp/exec/ip/service.log
kubectl --namespace tfs-ip logs deployments/pathcompservice frontend > tmp/exec/ip/pathcomp-frontend.log
kubectl --namespace tfs-ip logs deployments/pathcompservice backend > tmp/exec/ip/pathcomp-backend.log
kubectl --namespace tfs-ip logs deployments/sliceservice server > tmp/exec/ip/slice.log
printf "\n"

echo "Done!"
