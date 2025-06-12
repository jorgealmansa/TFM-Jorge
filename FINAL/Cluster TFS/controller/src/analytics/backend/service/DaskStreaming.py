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

import logging
import time
import json
from confluent_kafka import Consumer, Producer, KafkaException, KafkaError
import pandas as pd
from dask.distributed import Client, LocalCluster
from common.tools.kafka.Variables import KafkaConfig, KafkaTopic

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def SettingKafkaConsumerParams():
    return {'bootstrap.servers'  : KafkaConfig.get_kafka_address(),
            'group.id'           : 'analytics-backend',
            'auto.offset.reset'  : 'latest'}

def GetAggregationMappings(thresholds):
    agg_dict = {}
    for threshold_key in thresholds.keys():
        parts = threshold_key.split('_', 1)
        if len(parts) != 2:
            LOGGER.warning(f"Threshold key '{threshold_key}' does not follow the '<aggregation>_<metricName>' format. Skipping.")
            continue
        aggregation, metric_name = parts
        # Ensure that the aggregation function is valid in pandas
        if aggregation not in ['mean', 'min', 'max', 'first', 'last', 'std']:
            LOGGER.warning(f"Unsupported aggregation '{aggregation}' in threshold key '{threshold_key}'. Skipping.")
            continue
        agg_dict[threshold_key] = ('kpi_value', aggregation)
    return agg_dict


def ApplyThresholds(aggregated_df, thresholds):
    """
    Apply thresholds (TH-Fall and TH-Raise) based on the thresholds dictionary
    on the aggregated DataFrame.
    Args:       aggregated_df (pd.DataFrame): DataFrame with aggregated metrics.
                thresholds (dict): Thresholds dictionary with keys in the format '<aggregation>_<metricName>'.
    Returns:    pd.DataFrame: DataFrame with additional threshold columns.
    """
    for threshold_key, threshold_values in thresholds.items():
        if threshold_key not in aggregated_df.columns:

            LOGGER.warning(f"Threshold key '{threshold_key}' does not correspond to any aggregation result. Skipping threshold application.")
            continue
        if isinstance(threshold_values, (list, tuple)) and len(threshold_values) == 2:
            fail_th, raise_th = threshold_values
            aggregated_df["THRESHOLD_FALL"] = aggregated_df[threshold_key] < fail_th
            aggregated_df["THRESHOLD_RAISE"] = aggregated_df[threshold_key] > raise_th
            aggregated_df["value"] = aggregated_df[threshold_key]
        else:
            LOGGER.warning(f"Threshold values for '{threshold_key}' are not a list or tuple of length 2. Skipping threshold application.")
    return aggregated_df

def initialize_dask_client():
    """
    Initialize a local Dask cluster and client.
    """
    cluster = LocalCluster(n_workers=2, threads_per_worker=2)
    client = Client(cluster)
    LOGGER.info(f"Dask Client Initialized: {client}")
    return client, cluster

def initialize_kafka_producer():
    return Producer({'bootstrap.servers': KafkaConfig.get_kafka_address()})

def delivery_report(err, msg):
    if err is not None:
        LOGGER.error(f"Message delivery failed: {err}")
    else:
        LOGGER.info(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def process_batch(batch, agg_mappings, thresholds, key):
    """
    Process a batch of data and apply thresholds.
    Args:       batch (list of dict): List of messages from Kafka.
                agg_mappings (dict): Mapping from threshold key to aggregation function.
                thresholds (dict): Thresholds dictionary.
    Returns:    list of dict: Processed records ready to be sent to Kafka.
    """
    if not batch:
        LOGGER.info("Empty batch received. Skipping processing.")
        return []


    df = pd.DataFrame(batch)
    LOGGER.info(f"df {df} ")
    df['time_stamp'] = pd.to_datetime(df['time_stamp'], errors='coerce')
    df.dropna(subset=['time_stamp'], inplace=True)
    LOGGER.info(f"df {df} ")
    required_columns = {'time_stamp', 'kpi_id', 'kpi_value'}
    if not required_columns.issubset(df.columns):
        LOGGER.warning(f"Batch contains missing required columns. Required columns: {required_columns}. Skipping batch.")
        return []
    if df.empty:
        LOGGER.info("No data after filtering by KPI IDs. Skipping processing.")
        return []

    # Perform aggregations using named aggregation
    try:
        agg_dict = {key: value for key, value in agg_mappings.items()}

        df_agg_ = df.groupby(['window_start']).agg(**agg_dict).reset_index()

        #example: agg_dict = {'min_latency_E2E': ('kpi_value', 'min')

        #given that threshold has 1 value
        second_value_tuple = next(iter(agg_dict.values()))[1]
        #in case we have multiple thresholds!
        #second_values_tuples = [value[1] for value in agg_dict.values()]
        if second_value_tuple=="min":
            df_agg = df_agg_.min(numeric_only=True).to_frame().T
        elif second_value_tuple == "max":
            df_agg = df_agg_.max(numeric_only=True).to_frame().T
        elif second_value_tuple == "std":
            df_agg = df_agg_.sted(numeric_only=True).to_frame().T
        else:
            df_agg = df_agg_.mean(numeric_only=True).to_frame().T

        # Assign the first value of window_start from the original aggregated data
        df_agg['window_start'] = df_agg_['window_start'].iloc[0]

        # Reorder columns to place 'window_start' first if needed
        cols = ['window_start'] + [col for col in df_agg.columns if col != 'window_start']
        df_agg = df_agg[cols]

    except Exception as e:
        LOGGER.error(f"Aggregation error: {e}")
        return []

    # Apply thresholds


    df_thresholded = ApplyThresholds(df_agg, thresholds)
    df_thresholded['kpi_id'] = key
    df_thresholded['window_start'] = df_thresholded['window_start'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    # Convert aggregated DataFrame to list of dicts
    result = df_thresholded.to_dict(orient='records')
    LOGGER.info(f"Processed batch with {len(result)} records after aggregation and thresholding.")
    return result

def produce_result(result, producer, destination_topic):
    for record in result:
        try:
            producer.produce(
                destination_topic,
                key=str(record.get('kpi_id', '')),
                value=json.dumps(record),
                callback=delivery_report
            )
        except KafkaException as e:
            LOGGER.error(f"Failed to produce message: {e}")
    producer.flush()
    LOGGER.info(f"Produced {len(result)} aggregated records to '{destination_topic}'.")

def DaskStreamer(key, kpi_list, thresholds, stop_event,
                window_size="30s", time_stamp_col="time_stamp"):
    client, cluster = initialize_dask_client()
    consumer_conf   = SettingKafkaConsumerParams()
    consumer        = Consumer(consumer_conf)
    consumer.subscribe([KafkaTopic.VALUE.value])
    producer        = initialize_kafka_producer()

    # Parse window_size to seconds
    try:
        window_size_td = pd.to_timedelta(window_size)
        window_size_seconds = window_size_td.total_seconds()
    except Exception as e:
        LOGGER.error(f"Invalid window_size format: {window_size}. Error: {e}")
        window_size_seconds = 30 
    LOGGER.info(f"Batch processing interval set to {window_size_seconds} seconds.")

    # Extract aggregation mappings from thresholds
    agg_mappings = GetAggregationMappings(thresholds)
    if not agg_mappings:
        LOGGER.error("No valid aggregation mappings extracted from thresholds. Exiting streamer.")
        consumer.close()
        producer.flush()
        client.close()
        cluster.close()
        return
    try:
        batch = []
        last_batch_time = time.time()
        LOGGER.info("Starting to consume messages...")

        while not stop_event.is_set():
            msg = consumer.poll(1.0)

            if msg is None:
                current_time = time.time()
                if (current_time - last_batch_time) >= window_size_seconds and batch:
                    LOGGER.info("Time-based batch threshold reached. Processing batch.")
                    future = client.submit(process_batch, batch, agg_mappings, thresholds)
                    future.add_done_callback(lambda fut: produce_result(fut.result(), producer, KafkaTopic.ALARMS.value))
                    batch = []
                    last_batch_time = current_time
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    LOGGER.warning(f"End of partition reached {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                else:
                    LOGGER.error(f"Kafka error: {msg.error()}")
                continue

            try:
                message_value = json.loads(msg.value().decode('utf-8'))
            except json.JSONDecodeError as e:
                LOGGER.error(f"JSON decode error: {e}")
                continue

            try:
                message_timestamp = pd.to_datetime(message_value[time_stamp_col], errors='coerce')
                LOGGER.warning(f"message_timestamp: {message_timestamp}. Skipping message.")

                if pd.isna(message_timestamp):
                    LOGGER.warning(f"Invalid timestamp in message: {message_value}. Skipping message.")
                    continue
                window_start = message_timestamp.floor(window_size)
                LOGGER.warning(f"window_start: {window_start}. Skipping message.")
                message_value['window_start'] = window_start
            except Exception as e:
                LOGGER.error(f"Error processing timestamp: {e}. Skipping message.")
                continue

            if message_value['kpi_id'] not in kpi_list:
                LOGGER.debug(f"KPI ID '{message_value['kpi_id']}' not in kpi_list. Skipping message.")
                continue

            batch.append(message_value)

            current_time = time.time()
            if (current_time - last_batch_time) >= window_size_seconds and batch:
                LOGGER.info("Time-based batch threshold reached. Processing batch.")
                future = client.submit(process_batch, batch, agg_mappings, thresholds, key)
                future.add_done_callback(lambda fut: produce_result(fut.result(), producer, KafkaTopic.ALARMS.value))
                batch = []
                last_batch_time = current_time

    except Exception as e:
        LOGGER.exception(f"Error in Dask streaming process: {e}")
    finally:
        # Process any remaining messages in the batch
        if batch:
            LOGGER.info("Processing remaining messages in the batch.")
            future = client.submit(process_batch, batch, agg_mappings, thresholds)
            future.add_done_callback(lambda fut: produce_result(fut.result(), producer, KafkaTopic.ALARMS.value))
        consumer.close()
        producer.flush()
        LOGGER.info("Kafka consumer and producer closed.")
        client.close()
        cluster.close()
        LOGGER.info("Dask client and cluster closed.")
