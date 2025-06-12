/*
 * Copyright 2022-2024 ETSI SDG TeraFlowSDN (TFS) (https://tfs.etsi.org/)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.etsi.tfs.policy.context.model;

public class ConfigRuleTypeCustom implements ConfigRuleType<ConfigRuleCustom> {

    private final ConfigRuleCustom configRuleCustom;

    public ConfigRuleTypeCustom(ConfigRuleCustom configRuleCustom) {
        this.configRuleCustom = configRuleCustom;
    }

    @Override
    public ConfigRuleCustom getConfigRuleType() {
        return this.configRuleCustom;
    }

    @Override
    public String toString() {
        return String.format("%s:{%s}", getClass().getSimpleName(), configRuleCustom);
    }
}
