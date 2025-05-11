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

BUCKET_NAME = "fraud-data"
RAW_PREFIX = "raw"

with DAG(
    'data_generation',
    default_args=default_args,
    description='Generate transaction data every 1 minutes',
    schedule_interval='*/1 * * * *',  # Run every 1 minutes
    catchup=False,
    max_active_runs=1, # add max active runs to avoid overlapping
) as dag:
    
    # Task 1: Generate data
    generate_data_task = BashOperator(
        task_id='generate_data',
        bash_command='cd /opt/airflow && python /opt/airflow/scripts/generate_synthetic_fraud_data.py',
        dag=dag,
    )

    generate_data_task