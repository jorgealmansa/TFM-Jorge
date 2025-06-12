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

import copy

def convert_to_dict(single_val:int)->dict:
    slot= dict()
    bin_num = bin(single_val)
    sliced_num=bin_num[2:]
    for i in range(len(sliced_num)):
        slot[str(i+1)]=int(sliced_num[i])
    return slot

def correct_slot(dic: dict) -> dict:
    _dict = copy.deepcopy(dic)
    keys_list = list(_dict.keys())
    if len(keys_list) < 20:
        num_keys = [int(i) for i in keys_list]
        if num_keys[-1] != 20:
            missed_keys = []
            diff = 20 - len(num_keys)
            #print(f"diff {diff}")
            for i in range(diff+1):
                missed_keys.append(num_keys[-1]+i)
            #print(f"missed_keys {missed_keys}")
            for key in missed_keys :
                _dict[key]=1
            #print(f"result {_dict}")
    return _dict
