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
# RCFILE=$PROJECTDIR/coverage/.coveragerc
# coverage run --rcfile=$RCFILE --append -m pytest --log-level=INFO --verbose \
#     kpi_manager/tests/test_unitary.py

# python3 kpi_manager/tests/test_unitary.py

RCFILE=$PROJECTDIR/coverage/.coveragerc
CRDB_SQL_ADDRESS=$(kubectl get service --namespace ${CRDB_NAMESPACE} cockroachdb-public -o 'jsonpath={.spec.clusterIP}')
export CRDB_URI="cockroachdb://tfs:tfs123@${CRDB_SQL_ADDRESS}:26257/tfs_kpi_mgmt?sslmode=require"
python3 -m pytest --log-level=DEBUG --log-cli-level=DEBUG --verbose \
    kpi_manager/tests/test_kpi_db.py
