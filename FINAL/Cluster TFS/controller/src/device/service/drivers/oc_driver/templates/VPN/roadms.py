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




def create_media_channel_old (resources):
        optical_band_namespaces="http://flex-scale-project.eu/yang/flex-scale-mg-on"
        results=[]
        unwanted_keys=['destination_port','source_port','channel_namespace'
                       ,'frequency','operational-mode','target-output-power',
                       "admin-state","flow_handled","channel_num"]
        config,ports,index= seperate_port_config(resources,unwanted_keys=unwanted_keys)
        

        doc, tag, text = Doc().tagtext()
        #with tag('config'):
        with tag('config',xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"):
            with tag('wavelength-router', xmlns="http://openconfig.net/yang/wavelength-router"):
                with tag('media-channels'):
                    n = 0
                    if 'destination_port' in ports:
                        n = len(ports['destination_port'])
                    else:
                        n = len(ports['source_port'])
                    for i in range(0, n):
                        #with tag('channel', operation="create"):
                        with tag('channel'):
                            with tag('index'):text(str(int(index)+i))
                            with tag('config'):
                                #with tag('index'):text(index)
                                for resource in config:
                                   
                                    if resource['resource_key'] == "index":
                                        with tag('index'):text(str(int(index)+i))
                                    elif resource['resource_key']== 'optical-band-parent'    :
                                        with tag('optical-band-parent',xmlns=optical_band_namespaces):text(resource['value'])
                                    else:
                                        with tag(resource['resource_key']):text(resource['value'])
                            if ('destination_port' in ports) and (ports['destination_port'][i] is not None):         
                                with tag('dest'):
                                    with tag('config'):  
                                        with tag('port-name'):text(ports['destination_port'][i])   
                            if ('source_port' in ports) and (ports['source_port'][i] is not None):                    
                                with tag('source'):
                                        with tag('config'):  
                                            with tag('port-name'):text(ports['source_port'][i])     
                            
                            
        result = indent(
                    doc.getvalue(),
                    indentation = ' '*2,
                    newline = ''
                )
        results.append(result)
        return results
             
 
 
 
def create_media_channel (resources):
        optical_band_namespaces="http://flex-scale-project.eu/yang/flex-scale-mg-on"
        results=[]
        unwanted_keys=['destination_port','source_port','channel_namespace'
                       ,'frequency','operational-mode','target-output-power',
                       "admin-state","handled_flow","channel_num"]
      
        config,ports,index=filter_config(resources,unwanted_keys)

        doc, tag, text = Doc().tagtext()
        #with tag('config'):
        with tag('config',xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"):
            with tag('wavelength-router', xmlns="http://openconfig.net/yang/wavelength-router"):
                with tag('media-channels'):
                    n = 0
                 
                    for flow in ports:
                        src,dest=flow
                        #with tag('channel', operation="create"):
                        with tag('channel'):
                            with tag('index'):text(str(int(index)+n))
                            with tag('config'):
                                #with tag('index'):text(index)
                                for resource in config:
                                   
                                    if resource['resource_key'] == "index":
                                        with tag('index'):text(str(int(index)+n))
                                    elif resource['resource_key']== 'optical-band-parent'    :
                                        with tag('optical-band-parent',xmlns=optical_band_namespaces):text(resource['value'])
                                    else:
                                        with tag(resource['resource_key']):text(resource['value'])
                            if dest is not None and dest != '0':         
                                with tag('dest'):
                                    with tag('config'):  
                                        with tag('port-name'):text(dest)   
                            if src is not None and src != '0':                    
                                with tag('source'):
                                        with tag('config'):  
                                            with tag('port-name'):text(src)     
                        n+=1    
                            
        result = indent(
                    doc.getvalue(),
                    indentation = ' '*2,
                    newline = ''
                )
        results.append(result)
        return results
             
                
 

         
def create_media_channel_v2 (resources):
    optical_band_namespaces="http://flex-scale-project.eu/yang/flex-scale-mg-on"
    results=[]
    unwanted_keys=['destination_port','source_port','channel_namespace'
                ,'frequency','operational-mode','target-output-power',
               "handled_flow","channel_num"]

    config,ports,index=filter_config(resources,unwanted_keys)

    n = 0
    for flow in ports:
        doc, tag, text = Doc().tagtext()
        with tag('config',xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"):
            with tag('wavelength-router', xmlns="http://openconfig.net/yang/wavelength-router"):
                    with tag('media-channels'):
                        
                    
                            src,dest=flow
                            with tag('channel', operation="create"):
                            #with tag('channel'):
                                with tag('index'):text(str(int(index)+n))
                                with tag('config'):
                                    #with tag('index'):text(index)
                                    for resource in config:
                                        
                                        if resource['resource_key'] == "index":
                                            with tag('index'):text(str(int(index)+n))
                                        elif resource['resource_key']== 'optical-band-parent'    :
                                            with tag('optical-band-parent',xmlns=optical_band_namespaces):text(int(resource['value'])+int(n))
                                        elif resource['resource_key']== 'admin-state'    :
                                            with tag('admin-status'):text(resource['value'])
                                        else:
                                            with tag(resource['resource_key']):text(resource['value'])
                                    
                            
                                if src is not None and src != '0':                    
                                    with tag('source'):
                                            with tag('config'):  
                                                with tag('port-name'):text(src)     
                                if dest is not None and dest != '0':                    
                                    with tag('dest'):
                                            with tag('config'):  
                                                with tag('port-name'):text(dest)     
        n+=1    
                            
        result = indent(
                    doc.getvalue(),
                    indentation = ' '*2,
                    newline = ''
                )
        results.append(result)
    return results
        
                


def create_optical_band_old (resources) :
    results =[]
    unwanted_keys=['destination_port','source_port','channel_namespace','frequency','optical-band-parent','flow_handled']
    config,ports,index= seperate_port_config(resources,unwanted_keys=unwanted_keys)
  
    doc, tag, text = Doc().tagtext()
    #with tag('config'):
    with tag('config',xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"):
      with tag('wavelength-router', xmlns="http://openconfig.net/yang/wavelength-router"):
        with tag('optical-bands',xmlns="http://flex-scale-project.eu/yang/flex-scale-mg-on"):
            n = 0
            if 'destination_port' in ports:
                n = len(ports['destination_port'])
            else:
                n = len(ports['source_port'])
            for i in range(0, n):
                #with tag('optical-band', operation="create"):
                with tag('optical-band'):
                    if index is not None:
                        with tag('index'):text(str(int(index)+i))
                    with tag('config'):
                        #if index is not None:
                        #    with tag('index'):text(str(int(index)+i))
                        for resource in config:       
                            if resource['resource_key'] == "index":
                                with tag('index'):text(str(int(index)+i))
                            else:
                                with tag(resource['resource_key']):text(resource['value'])
                        with tag('admin-status'):text('ENABLED')       
                        #with tag('fiber-parent'):text(ports['destination_port'] if 'destination_port' in ports else ports['source_port'])       
                    if ('destination_port' in ports) and (ports['destination_port'][i] is not None):        
                        with tag('dest'):
                            with tag('config'):
                                with tag('port-name'):text(ports['destination_port'][i])
                    if ('source_port' in ports) and (ports['source_port'][i] is not None):        
                        with tag('source'):
                            with tag('config'):  
                                with tag('port-name'):text(ports['source_port'][i])   
                            
                                
    result = indent(
                doc.getvalue(),
                indentation = ' '*2,
                newline = ''
            )
    results.append(result)
    return results




def create_optical_band (resources) :
    results =[]
    unwanted_keys=['destination_port','source_port','channel_namespace','frequency','optical-band-parent','handled_flow']
    config,ports,index= filter_config(resources,unwanted_keys=unwanted_keys)

    #with tag('config'):
    n = 0
    for flow in ports:
        doc, tag, text = Doc().tagtext()
        with tag('config',xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"):
            with tag('wavelength-router', xmlns="http://openconfig.net/yang/wavelength-router"):
                with tag('optical-bands',xmlns="http://flex-scale-project.eu/yang/flex-scale-mg-on"):
                   
                
                        #with tag('optical-band', operation="create"):
                        src,dest=flow

                        with tag('optical-band'):
                            if index is not None:
                                with tag('index'):text(str(int(index)+n))
                            with tag('config'):
                                #if index is not None:
                                #    with tag('index'):text(str(int(index)+i))
                                for resource in config:       
                                    if resource['resource_key'] == "index":
                                        with tag('index'):text(str(int(index)+n))
                                    else:
                                        with tag(resource['resource_key']):text(resource['value'])
                                with tag('admin-status'):text('ENABLED')       
                                #with tag('fiber-parent'):text(ports['destination_port'] if 'destination_port' in ports else ports['source_port'])       
                            if dest is not None and dest != '0':        
                                with tag('dest'):
                                    with tag('config'):
                                        with tag('port-name'):text(dest)
                            if src is not None and src !='0':        
                                with tag('source'):
                                    with tag('config'):  
                                        with tag('port-name'):text(src)   
        n +=1                
                                
                                
        result = indent(
                    doc.getvalue(),
                    indentation = ' '*2,
                    newline = ''
                )
        results.append(result)
    return results


def disable_media_channel (resources):
    
    results=[]
    unwanted_keys=['destination_port','source_port','channel_namespace','frequency','operational-mode', 'optical-band-parent']
    config,ports,index= seperate_port_config(resources,unwanted_keys=unwanted_keys)
    
    doc, tag, text = Doc().tagtext()
    #with tag('config'):
    with tag('config',xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"):
      with tag('wavelength-router', xmlns="http://openconfig.net/yang/wavelength-router"):
        with tag('media-channels'):
            with tag("channel",operation="delete"):
                with tag('index'):text(str(int(index)))
                with tag('config'):
                    with tag('index'):text(str(int(index)))
                            
    result = indent(
                doc.getvalue(),
                indentation = ' '*2,
                newline = ''
            )
    results.append(result)
    return results
                        
def disable_optical_band (resources:list,state:str):
    results=[]
    unwanted_keys=['destination_port','source_port','channel_namespace','frequency','operational-mode', 'optical-band-parent']
    config,ports,index= seperate_port_config(resources,unwanted_keys=unwanted_keys)
    doc, tag, text = Doc().tagtext()
    #with tag('config'):
    with tag('config',xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"):
      with tag('wavelength-router', xmlns="http://openconfig.net/yang/wavelength-router"):
        with tag('optical-bands',xmlns="http://flex-scale-project.eu/yang/flex-scale-mg-on"):
            with tag('optical-band'):
                if index is not None:
                    with tag('index'):text(index)
                with tag('config'):
                    with tag('index'):text(index)
                    with tag('admin-status'):text(state)  
    result = indent(
                doc.getvalue(),
                indentation = ' '*2,
                newline = ''
            )
    results.append(result)
    return results                          


def delete_optical_band (resources:list):
    results=[]
    unwanted_keys=['destination_port','source_port','channel_namespace','frequency','operational-mode', 'optical-band-parent']
    config,ports,index= seperate_port_config(resources,unwanted_keys=unwanted_keys)
    doc, tag, text = Doc().tagtext()
    #with tag('config'):
    with tag('config',xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"):
      with tag('wavelength-router', xmlns="http://openconfig.net/yang/wavelength-router"):
        with tag('optical-bands',xmlns="http://flex-scale-project.eu/yang/flex-scale-mg-on"):
            with tag('optical-band',operation="delete"):
                if index is not None:
                    with tag('index'):text(index)
                with tag('config'):
                    with tag('index'):text(index)
                   
    result = indent(
                doc.getvalue(),
                indentation = ' '*2,
                newline = ''
            )
    results.append(result)
    return results
