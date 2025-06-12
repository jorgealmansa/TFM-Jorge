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

package org.etsi.tfs.policy.policy.model;

import static com.google.common.base.Preconditions.checkArgument;

import java.util.ArrayList;
import java.util.List;
import org.etsi.tfs.policy.common.Util;

public class PolicyRuleBasic {

    private String policyRuleId;
    private PolicyRuleState policyRuleState;
    private int priority;
    private List<PolicyRuleCondition> policyRuleConditions;
    private BooleanOperator booleanOperator;
    private List<PolicyRuleAction> policyRuleActions;
    private Boolean isValid;
    private String exceptionMessage;

    public PolicyRuleBasic(
            String policyRuleId,
            PolicyRuleState policyRuleState,
            int priority,
            List<PolicyRuleCondition> policyRuleConditions,
            BooleanOperator booleanOperator,
            List<PolicyRuleAction> policyRuleActions) {

        try {
            checkArgument(!policyRuleId.isBlank(), "Policy rule ID must not be empty.");
            this.policyRuleId = policyRuleId;
            this.policyRuleState = policyRuleState;
            checkArgument(priority >= 0, "Priority value must be greater or equal than zero.");
            this.priority = priority;
            checkArgument(!policyRuleConditions.isEmpty(), "Policy Rule conditions cannot be empty.");
            this.policyRuleConditions = policyRuleConditions;
            checkArgument(
                    booleanOperator != BooleanOperator.POLICYRULE_CONDITION_BOOLEAN_UNDEFINED,
                    "Boolean operator cannot be undefined");
            this.booleanOperator = booleanOperator;
            checkArgument(!policyRuleActions.isEmpty(), "Policy Rule actions cannot be empty.");
            this.policyRuleActions = policyRuleActions;
            this.isValid = true;

        } catch (Exception e) {
            this.policyRuleId = "";
            this.priority = 0;
            this.policyRuleConditions = new ArrayList<PolicyRuleCondition>();
            this.booleanOperator = BooleanOperator.POLICYRULE_CONDITION_BOOLEAN_UNDEFINED;
            this.policyRuleActions = new ArrayList<PolicyRuleAction>();
            this.isValid = false;
            this.exceptionMessage = e.getMessage();
        }
    }

    public boolean areArgumentsValid() {
        return isValid;
    }

    public String getExceptionMessage() {
        return exceptionMessage;
    }

    public String getPolicyRuleId() {
        return policyRuleId;
    }

    public PolicyRuleState getPolicyRuleState() {
        return policyRuleState;
    }

    public void setPolicyRuleState(PolicyRuleState state) {
        this.policyRuleState = state;
    }

    public int getPriority() {
        return priority;
    }

    public List<PolicyRuleCondition> getPolicyRuleConditions() {
        return policyRuleConditions;
    }

    public BooleanOperator getBooleanOperator() {
        return booleanOperator;
    }

    public List<PolicyRuleAction> getPolicyRuleActions() {
        return policyRuleActions;
    }

    @Override
    public String toString() {
        return String.format(
                "%s:{policyRuleId:\"%s\", %s, priority:%d, [%s], booleanOperator:\"%s\", [%s]}",
                getClass().getSimpleName(),
                policyRuleId,
                policyRuleState,
                priority,
                Util.toString(policyRuleConditions),
                booleanOperator.toString(),
                Util.toString(policyRuleActions));
    }
}
