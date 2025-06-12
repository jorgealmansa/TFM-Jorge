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

import re,logging
import json
import lxml.etree as ET
from typing import Collection, Dict, Any



def add_value_from_tag(target : Dict, field_name: str, field_value : ET.Element, cast=None) -> None:
    if isinstance(field_value,str) or field_value is None or field_value.text is None: return
    field_value = field_value.text
    if cast is not None: field_value = cast(field_value)
    target[field_name] = field_value

def add_value_from_collection(target : Dict, field_name: str, field_value : Collection) -> None:
    if field_value is None or len(field_value) == 0: return
    target[field_name] = field_value


def generate_templates(resource_key: str, resource_value: str, channel:str) -> str:    # template management to be configured

    result_templates = []
    data={}
    data['name']=channel
    data['resource_key']=resource_key
    data['value']=resource_value
    #result_templates.append(create_physical_config(data))

    return result_templates


def extract_status (dic:dict,resource_key:str,xml_data:str,channel_name:str):
    
    xml_bytes = xml_data.encode("utf-8")
    root = ET.fromstring(xml_bytes)
    channel_name=channel_name if 'index'  not in channel_name else channel_name['index']
    index=None
    if channel_name.find('-') != -1 :
        index= channel_name.split("-")[1]
    
   
    namespaces = { "td": "http://openconfig.net/yang/terminal-device"}
    channels  = root.findall(f".//td:terminal-device/td:logical-channels/td:channel",namespaces) 
    for channel in channels : 
       
        index_ele= channel.find(f".//td:config[td:index='{index}']/td:{resource_key}",namespaces)
        if index_ele is not None :
           dic["status"]=index_ele.text
           print(index_ele.text)
    return dic


def extract_channel_xmlns (data_xml:str,is_opticalband:bool):
    xml_bytes = data_xml.encode("utf-8")
    root = ET.fromstring(xml_bytes) 
 
    namespace=None
    channels=None
  
    if (not is_opticalband) :
      
        optical_channel_namespaces = {
        'ns': 'urn:ietf:params:xml:ns:netconf:base:1.0',
          'oc': 'http://openconfig.net/yang/platform',
        }
       
        channels= root.find('.//{*}optical-channel',optical_channel_namespaces)
        if channels is not None :
          optical_channel_namespace = channels.tag.replace("optical-channel", "")
          namespace=optical_channel_namespace.replace("{", "").replace("}", "")
    else :       
        optical_band_namespaces= {
          'oc':'http://openconfig.net/yang/wavelength-router'
        }
        
        channels= root.find('.//{*}optical-bands',optical_band_namespaces)
        if channels is not None: 
          optical_channel_namespace = channels.tag.replace("optical-bands", "")
          namespace=optical_channel_namespace.replace("{", "").replace("}", "")
        
   
    return namespace
  
def extract_channels_based_on_channelnamespace (xml_data:str,channel_namespace:str,is_opticalband:bool):
    xml_bytes = xml_data.encode("utf-8")
    root = ET.fromstring(xml_bytes)
    channels=[]
   
    # Find the component names whose children include the "optical-channel" element
    if (not is_opticalband):
       namespace = {'namespace': 'http://openconfig.net/yang/platform','cn':channel_namespace}

       component_names = root.findall('.//namespace:component[cn:optical-channel]',namespace)

      # Extract and print the component names
       for component in component_names:
          component_name = component.find('namespace:name', namespace).text 
          channels.append({"index":component_name})
    else :
        namespaces = {
              'wr': 'http://openconfig.net/yang/wavelength-router',
              'fs': channel_namespace
        }
       
        wl = root.findall('.//fs:optical-band',namespaces=namespaces)
  
        for component in wl :
                index=component.find('.//fs:index',namespaces).text
                dest_port_name = component.find('.//fs:dest/fs:config/fs:port-name', namespaces).text

        # Retrieve port-name for source (assuming it exists in the XML structure)
                source_port_name = component.find('.//fs:source/fs:config/fs:port-name', namespaces).text
                channels.append({"index":index,"endpoints":(source_port_name,dest_port_name)})
             
        # Retrieve port-name for dest

    return channels
  
def extract_channels_based_on_type (xml_data:str):
    xml_bytes = xml_data.encode("utf-8")
    root = ET.fromstring(xml_bytes)

    namespace = {'oc': 'http://openconfig.net/yang/platform', 'typex': 'http://openconfig.net/yang/platform-types'}
    channel_names = []
    components = root.findall('.//oc:component', namespace)
    for component in components:
      
        type_element = component.find('.//oc:state/oc:type[.="oc-opt-types:OPTICAL_CHANNEL"]',namespaces=namespace)
    
        if type_element is not None and type_element.text == 'oc-opt-types:OPTICAL_CHANNEL':
            name_element = component.find('oc:name', namespace)
            if name_element is not None:
                channel_names.append(name_element.text)
    return channel_names            
    
def extract_value(resource_key:str,xml_data:str,dic:dict,channel_name:str,channel_namespace:str):
 
    xml_bytes = xml_data.encode("utf-8")
    root = ET.fromstring(xml_bytes)
    channel_name=channel_name if 'index'  not in channel_name else channel_name['index']
    namespace = {'oc': 'http://openconfig.net/yang/platform',
              'td': channel_namespace}

    element = root.find(f'.//oc:component[oc:name="{channel_name}"]', namespace)

    if element is not None:
      parameter= element.find(f'.//td:{resource_key}',namespace)
      if (parameter is not None):
        value = parameter.text
        dic[resource_key]=value
      else :
           logging.info("parameter is None")    
      
    else:
       logging.info("element is None")     
       print(" element not found.")
      
    return dic  


def extract_port_value (xml_string:list,port_name:str):

    xml_bytes = xml_string.encode("utf-8")
    root = ET.fromstring(xml_bytes)

    namespace = {"oc": "http://openconfig.net/yang/platform"}
    component=root.find(f".//oc:component[oc:name='{port_name}']", namespace)
    onos_index = component.find(
        f".//oc:property//oc:state/oc:name[.='onos-index']/../oc:value", namespace
    ).text
  
    return (port_name,onos_index)
            
           

  
def extract_tranceiver (data_xml:str,dic:dict):
    xml_bytes = data_xml.encode("utf-8")
    root = ET.fromstring(xml_bytes)
    namespaces = {
      'ns': 'urn:ietf:params:xml:ns:netconf:base:1.0',
      'oc': 'http://openconfig.net/yang/platform',
      'oc-terminal': 'http://openconfig.net/yang/terminal-device',
      'oc-platform-types': 'http://openconfig.net/yang/platform-types'
    }

 
    transceiver_components = root.findall('.//oc:component/oc:state/[oc:type="oc-platform-types:TRANSCEIVER"]../oc:state/oc:name', namespaces)
   
    component_names = [component.text for component in transceiver_components]
    dic['transceiver']=component_names
    return dic
  
def extract_interface (xml_data:str,dic:dict):
    xml_bytes = xml_data.encode("utf-8")
    root = ET.fromstring(xml_bytes)
    namespaces = {
    'ns': 'urn:ietf:params:xml:ns:netconf:base:1.0',
    'oc': 'http://openconfig.net/yang/interfaces',
    }
    ip_namespaces = {
    'oc': 'http://openconfig.net/yang/interfaces',
    'ip': 'http://openconfig.net/yang/interfaces/ip',
    }

    interfaces = root.findall('.//oc:interfaces/oc:interface', namespaces)
    interface_names = [interface.find('oc:name', namespaces).text for interface in interfaces]
    interface_enabled=[interface.find('oc:config/oc:enabled', namespaces).text for interface in interfaces]
    ip_address_element = root.find('.//ip:ip', ip_namespaces)
    interface_prefix_length=root.find('.//ip:prefix-length',ip_namespaces)
    if (len(interface_names) > 0):
       dic['interface']={"name":interface_names[0],'ip':ip_address_element.text,'enabled':interface_enabled[0],"prefix-length":interface_prefix_length.text}
    else :
        dic['interface']={}   
    return dic
  
def has_opticalbands(xml_data:str):
    xml_bytes = xml_data.encode("utf-8")
    root = ET.fromstring(xml_bytes)
 
    has_opticalbands=False
    elements= root.find('.//{*}optical-bands')

    if (elements is not None and len(elements) >0):
      has_opticalbands=True
    else :
      has_opticalbands=False
    return has_opticalbands
  
def extract_ports_based_on_type (xml_data:str):
    pattern = r':\s*PORT\b'
    xml_bytes = xml_data.encode("utf-8")
    root = ET.fromstring(xml_bytes)
    namespace = {'oc': 'http://openconfig.net/yang/platform', 'typex': 'http://openconfig.net/yang/platform-types'}
    ports = []
    components = root.findall(".//oc:state[oc:type]",namespace)
    for component in components:
         type_ele = component.find(".//oc:type",namespace)
         match = re.search(pattern, type_ele.text)
         if match is not None :
            name_element= component.find(".//oc:name",namespace)
            port_name =name_element.text       
            port_index=name_element.text.split("-")[1]
            port = (port_name,port_index)
            ports.append(port)
    return ports  
    
def transponder_values_extractor(data_xml:str,resource_keys:list,dic:dict):
   
    endpoints=[]
    is_opticalband=has_opticalbands(xml_data=data_xml)
    channel_namespace=extract_channel_xmlns(data_xml=data_xml,is_opticalband=is_opticalband)
    # channel_names=extract_channels_based_on_type(xml_data=data_xml) 
    # if len(channel_names)==0 :
    channel_names= extract_channels_based_on_channelnamespace(xml_data=data_xml,channel_namespace=channel_namespace,is_opticalband=is_opticalband)

    ports = extract_ports_based_on_type(data_xml)
    optical_channels_params=[]
    ports_result=[]
    if (is_opticalband):
        endpoints=channel_names
    else:
            
        for channel_name in channel_names:
            dic={}
            for resource_key in resource_keys  :
                
                if (resource_key != 'admin-state'):
                  
                    dic=extract_value(dic=dic,resource_key=resource_key,xml_data=data_xml
                                      ,channel_name=channel_name,channel_namespace=channel_namespace)  
                else : 
                    dic = extract_status(dic=dic,resource_key=resource_key,xml_data=data_xml, channel_name=channel_name) 
            dic["name"]=channel_name
            endpoints.append({"endpoint_uuid":{"uuid":channel_name}})
            optical_channels_params.append(dic)                
    #transceivers_dic=extract_tranceiver(data_xml=data_xml,dic={})
    transceivers_dic={"transceiver":[]}
    #interfaces_dic=extract_interface(xml_data=data_xml,dic={})
    if len(ports)>0 :
      for port in ports :
        endpoint_name,endpoint_id=port
        resource_key = '/endpoints/endpoint[{:s}]'.format(endpoint_id)
        resource_value = {'uuid': endpoint_id, 'type':endpoint_name}
        ports_result.append((resource_key, resource_value))
      
   
    return [transceivers_dic,optical_channels_params,channel_namespace,endpoints,ports_result]
