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

public class ConstraintTypeSlaAvailability implements ConstraintType<ConstraintSlaAvailability> {

    private final ConstraintSlaAvailability constraintSlaAvailability;

    public ConstraintTypeSlaAvailability(ConstraintSlaAvailability constraintSlaAvailability) {
        this.constraintSlaAvailability = constraintSlaAvailability;
    }

    @Override
    public ConstraintSlaAvailability getConstraintType() {
        return this.constraintSlaAvailability;
    }

    @Override
    public String toString() {
        return String.format("%s:{%s}", getClass().getSimpleName(), constraintSlaAvailability);
    }
}
