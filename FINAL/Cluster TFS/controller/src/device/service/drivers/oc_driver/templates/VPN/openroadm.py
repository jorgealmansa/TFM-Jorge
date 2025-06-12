# Copyright 2022-2024 ETSI SDG TeraFlowSDN (TFS) (https://tfs.etsi.org/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



from yattag import Doc, indent
import logging
from .common  import seperate_port_config ,filter_config
from decimal import Decimal



create_mc_err= '''
 <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
<org-openroadm-device xmlns="http://org/openroadm/device">
  <interface>
    <name>MC-TTP-DEG2-RX-193.3</name>
    <description>Media-Channel-TTP-193.3THz-degree-2-in</description>
    <type>openROADM-if:mediaChannelTrailTerminationPoint</type>
    <administrative-state>inService</administrative-state>
    <supporting-circuit-pack-name>DEG2-AMPRX</supporting-circuit-pack-name>
    <supporting-port>DEG2-AMPRX-IN</supporting-port>
    <supporting-interface-list>OMS-DEG2-TTP-RX</supporting-interface-list>
    <mc-ttp xmlns="http://org/openroadm/media-channel-interfaces">
      <min-freq>193.25</min-freq>
      <max-freq>193.35</max-freq>
    </mc-ttp>
  </interface>
  <interface>
    <name>MC-TTP-DEG2-TX-193.3</name>
    <description>Media-Channel-TTP-193.3THz-degree-2-out</description>
    <type>openROADM-if:mediaChannelTrailTerminationPoint</type>
    <administrative-state>inService</administrative-state>
    <supporting-circuit-pack-name>DEG2-AMPTX</supporting-circuit-pack-name>
    <supporting-port>DEG2-AMPTX-OUT</supporting-port>
    <supporting-interface-list>OMS-DEG2-TTP-TX</supporting-interface-list>
    <mc-ttp xmlns="http://org/openroadm/media-channel-interfaces">
      <min-freq>193.25</min-freq>
      <max-freq>193.35</max-freq>
    </mc-ttp>
  </interface>
</org-openroadm-device>


</config>

'''

def define_interface_name (type:str,interface_list:str,freq:int)->str:
    interface_str = interface_list.split('-')
    port_rank=''
    port_type=''
    if (len(interface_str)==4):
        port_rank=interface_str[1]
        port_type=interface_str[3]
    elif (len(interface_str)==5):
        port_rank=interface_str[2]
        port_type=interface_str[3]
    else :
        port_rank=interface_list
        port_type=interface_list+'type'    
            
            
    return f'{type.upper()}-{port_rank}-{port_type}-{freq}'    
        
    
       
def create_media_channel (resources):
   
    frequency_dict=next((r for r in resources if r['resource_key']== 'frequency'),None)
    width_dict=next((r for r in resources if r['resource_key']== 'width'),None)
    interfaces_lists =next((r for r in resources if r['resource_key']== 'interfaces'),None)
    administrative_state= next((r for r in resources if r['resource_key']== 'administrative-state'),None)
    min_freq= int(Decimal(frequency_dict["value"])*1000) - (int(width_dict["value"])/2)
    max_freq = int(Decimal(frequency_dict["value"])*1000) + (int(width_dict["value"])/2)
    #config,_,_ = filter_config(resources=resources,unwanted_keys=unwanted_keys)
        
    or_device_ns="http://org/openroadm/device"
    or_interface_ns="http://org/openroadm/interfaces"

    results=[]
    logging.info(f"from openroadm mc {resources}")
    doc, tag, text = Doc().tagtext()
    with tag('config',xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"):
        with tag('org-openroadm-device', ('xmlns',or_device_ns)):
       
            for interface in interfaces_lists["value"]:
                port = next((r for r in interface if r['resource_key']=='supporting-port'),None)
                circuit_pack =next((r for r in interface if r['resource_key']=='supporting-circuit-pack-name'),None)
                interface_list = next((r for r in interface if r['resource_key']=='supporting-interface-list'),None)
                mc_name = define_interface_name('mc-ttp',interface_list['value'],frequency_dict['value'])
                interface.append({'resource_key':'mc_name','value':mc_name})
                with tag('interface'):
                    
                        with tag('name'):text(mc_name)
                        with tag('description'):text(f'Media-channel-{frequency_dict["value"]}THz')
                        with tag('type'):text("openROADM-if:mediaChannelTrailTerminationPoint")
                        with tag('administrative-state'):text(administrative_state["value"])
                        with tag('supporting-circuit-pack-name'):text(circuit_pack["value"])
                        with tag('supporting-port'):text(port["value"])
                        with tag('supporting-interface-list'):text(interface_list["value"])
                        with tag('mc-ttp',xmlns="http://org/openroadm/media-channel-interfaces"):
                            with tag('max-freq'):text(max_freq)
                            with tag('min-freq'):text(min_freq)
                     
       
                            
    result = indent(
                    doc.getvalue(),
                    indentation = ' '*2,
                    newline = ''
                )
    results.append(result)
    logging.info(f"from openroadm mc results {results}")
    return [results,resources]
        


       
def create_network_media_channel (resources):
    
    logging.info(f"nmc resources {resources}")
    
    unwanted_keys= ['max-freq','min-freq']
    #config,_,_ = filter_config(resources=resources,unwanted_keys=unwanted_keys)
        
    or_device_ns="http://org/openroadm/device"
    frequency_dict=next((r for r in resources if r['resource_key']== 'frequency'),None)
    width_dict=next((r for r in resources if r['resource_key']== 'width'),None)
    interfaces_lists =next((r for r in resources if r['resource_key']== 'interfaces'),None)
    administrative_state= next((r for r in resources if r['resource_key']== 'administrative-state'),None)
  

    results=[]
    doc, tag, text = Doc().tagtext()
    with tag('config',xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"):
        with tag('org-openroadm-device', ('xmlns',or_device_ns)):
              for interface in interfaces_lists["value"]:
                port = next((r for r in interface if r['resource_key']=='supporting-port'),None)
                circuit_pack =next((r for r in interface if r['resource_key']=='supporting-circuit-pack-name'),None)
                interface_list = next((r for r in interface if r['resource_key']=='mc_name'),None)
                nmc_name = define_interface_name('nmc-ctp',interface_list['value'],frequency_dict['value'])

                with tag('interface'):
                    
                        with tag('name'):text(nmc_name)
                        with tag('description'):text(f'Media-channel-{frequency_dict["value"]}THz')
                        with tag('type'):text("openROADM-if:networkMediaChannelConnectionTerminationPoint")
                        with tag('administrative-state'):text(administrative_state["value"])
                        with tag('supporting-circuit-pack-name'):text(circuit_pack["value"])
                        with tag('supporting-port'):text(port["value"])
                        with tag('supporting-interface-list'):text(interface_list["value"])
                        with tag('nmc-ctp',xmlns="http://org/openroadm/network-media-channel-interfaces"):
                            with tag('frequency'):text(frequency_dict['value'])
                            with tag('width'):text(width_dict['value'])
                            

                            
    result = indent(
                    doc.getvalue(),
                    indentation = ' '*2,
                    newline = ''
                )
    results.append(result)
    logging.info(f"nmc message {results}")
    return results
        

def network_media_channel_handler (resources):
     unwanted_keys=["config_type"]
     config,_,_ = filter_config(resources=resources,unwanted_keys=unwanted_keys)
     mc_list,resources_updated= create_media_channel(resources=config)
     nmc_list= create_network_media_channel(resources=resources_updated)
     mc_list.extend(nmc_list)
    
     return mc_list
