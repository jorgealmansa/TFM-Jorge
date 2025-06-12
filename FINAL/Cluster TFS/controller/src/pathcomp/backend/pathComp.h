/*
 * Copyright 2022-2024 ETSI SDG TeraFlowSDN (TFS) (https://tfs.etsi.org/)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef _PATHCOMP_H
#define _PATHCOMP_H

#include <glib.h>
#include <glib/gstdio.h>
#include <glib-2.0/glib/gtypes.h>

///////////////////////////////////////////////////
// IP addressing of peer functional entities
///////////////////////////////////////////////////
extern struct in_addr pathComp_IpAddr;

// TCP Port for the REST API communication with the PATH COMP process
#define PATH_COMP_PORT 		8081       

// External Variables
extern GMainLoop * loop;

#endif