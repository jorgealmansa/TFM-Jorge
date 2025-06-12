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

from influxdb import InfluxDBClient

class Influx():
  def __init__(self, host, port, username, password, database):
      self.client = InfluxDBClient(host=host, port=port, username=username, password=password, database=database)

  def write_KPI(self,time,kpi_id,kpi_sample_type,device_id,endpoint_id,service_id,kpi_value):
    data = [{
      "measurement": "samples",
      "time": time,
      "tags": {
          "kpi_id" : kpi_id,
          "kpi_sample_type": kpi_sample_type,
          "device_id"  : device_id,
          "endpoint_id" : endpoint_id,
          "service_id" : service_id
      },
      "fields": {
          "kpi_value": kpi_value
      }
    }]
    self.client.write_points(data)

  def read_KPI_points(self):
      results = self.client.query('select * from samples;')
      print(results.raw)

      points = results.get_points(tags={'kpi_id' : '1','device_id': '1', 'kpi_sample_type': '101'})
      for point in points:
          print("Time: %s, Value: %i" % (point['time'], point['kpi_value']))

      return points
##NUEVAS FUNCIONES PARA LAS MÉTRICAS
import time

def write_int_telemetry(client: InfluxDBClient, report) -> bool:
    """
    Inserta un punto de datos de telemetría INT en la medición 'int_telemetry'.
    
    Se espera que 'report' tenga los siguientes atributos:
      - address             : IP del switch (str)
      - service_path_identifier : identificador de la Service Path (int o str)
      - service_index       : índice del servicio (int)
      - rnd                 : valor RND (int)
      - cml                 : valor CML (int)
      - seq_number          : número de secuencia (int)
      - dropped             : bandera de dropped (int)
    
    El timestamp se obtiene en nanosegundos.
    """
    # Obtén el timestamp actual en nanosegundos
    timestamp_ns = int(time.time() * 1e9)
    
    data = [{
       "measurement": "int_telemetry",
       "time": timestamp_ns,
       "fields": {
           "Switch IP": report.address,
           "Service Path Identifier": report.service_path_identifier,
           "Service Index": report.service_index,
           "RND": report.rnd,
           "CML": report.cml,
           "Sequence Number": report.seq_number,
           "Dropped": report.dropped,
           "ServiceID": "57310caf-bcc4-4008-82b8-6cfa6263bbcd",
           "Geolocation": "10.1.2.0/24,ES,ES-M,Madrid,40.416775,-3.70379,50"
       }
    }]
    
    # Escribe los puntos en la base de datos; devuelve True si tuvo éxito.
    return client.write_points(data)
 



