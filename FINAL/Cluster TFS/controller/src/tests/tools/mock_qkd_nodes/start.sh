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

#!/bin/bash
cd "$(dirname "$0")"

# Function to kill all background processes
killbg() {
    for p in "${pids[@]}" ; do
        kill "$p";
    done
}

trap killbg EXIT
pids=()

# Set FLASK_APP and run the Flask instances on different ports
export FLASK_APP=wsgi
flask run --host 0.0.0.0 --port 11111 & 
pids+=($!)

flask run --host 0.0.0.0 --port 22222 & 
pids+=($!)

flask run --host 0.0.0.0 --port 33333 & 
pids+=($!)

# Wait for all background processes to finish
wait

