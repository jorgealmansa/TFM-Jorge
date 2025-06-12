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

source /var/teraflow/tfs_runtime_env_vars.sh
export PYTHONPATH=/var/teraflow
pytest --verbose --log-level=INFO \
    --junitxml=/opt/results/report_onboarding.xml \
    /var/teraflow/tests/eucnc24/tests/test_onboarding.py
