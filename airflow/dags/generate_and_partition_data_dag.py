from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
from minio import Minio
from minio.error import S3Error
import pandas as pd
import logging
import duckdb

# Sets the minimum logging level to INFO.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),  # avoid recalculating the start date by using a fixed date
    'retries': 1,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    'generate_and_partition_data_dag',
    default_args=default_args,
    description='Generate fake transaction data every 1 minutes',
    schedule_interval='*/1 * * * *',  # Run every 1 minutes
    catchup=False,
    max_active_runs=1, # add max active runs to avoid overlapping
) as dag:
    
    # Task 1: Generate data "Overwrite"
    generate_data_task = BashOperator(
        task_id='generate_data',
        bash_command='cd /opt/airflow && python /opt/airflow/scripts/generate_synthetic_fraud_data.py',
        dag=dag,
    )

    # Task : Partition data with DuckDB
    partition_data_task = BashOperator(
        task_id='partition_data',
        bash_command='cd /opt/airflow && python /opt/airflow/scripts/partition_data_with_duckdb.py',
        dag=dag,
    )
    # Set task dependencies
    generate_data_task >> partition_data_task
