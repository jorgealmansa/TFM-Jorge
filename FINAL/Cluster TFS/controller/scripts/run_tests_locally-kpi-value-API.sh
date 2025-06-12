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


PROJECTDIR=`pwd`

cd $PROJECTDIR/src

RCFILE=$PROJECTDIR/coverage/.coveragerc
# KAFKA_IP=$(docker inspect kafka --format "{{.NetworkSettings.Networks.teraflowbridge.IPAddress}}")
# export KFK_SERVER_ADDRESS=${KAFKA_IP}:9092
export KFK_SERVER_ADDRESS='127.0.0.1:9092'
# helpful pytest flags: --log-level=INFO -o log_cli=true --verbose --maxfail=1 --durations=0
python3 -m pytest --log-level=DEBUG --log-cli-level=DEBUG -o log_cli=true --verbose \
    kpi_value_api/tests/test_kpi_value_api.py
