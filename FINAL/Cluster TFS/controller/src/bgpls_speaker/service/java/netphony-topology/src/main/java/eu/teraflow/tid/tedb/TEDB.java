// Copyright 2022-2024 ETSI SDG TeraFlowSDN (TFS) (https://tfs.etsi.org/)

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//      http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package eu.teraflow.tid.tedb;

import java.util.LinkedList;

/**
 * Base Interface for a Generic Traffic Engineering Database
 * @author ogondio
 *
 */
public interface TEDB {

	public void initializeFromFile(String file);

	public void initializeFromFile(String file, String learnFrom);


	public boolean isITtedb(); //FIXME: Remove!
	
	public String printTopology();

	public LinkedList<InterDomainEdge> getInterDomainLinks();

}
