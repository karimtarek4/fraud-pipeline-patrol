"""
This DAG:
Uploads parttioned data to MinIO while maintaining the directory structure.
"""

from airflow.decorators import dag
from airflow.operators.bash import BashOperator
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.operators.trigger_dagrun import TriggerDagRunOperator



# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 10),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
@dag(
    default_args=default_args,
    description='Load partitioned data to MinIO',
    catchup=False,
    is_paused_upon_creation=False,
    schedule_interval=None,
    max_active_runs=1,
)
def upload_to_minio_dag():

    UPLOAD_SCRIPT_PATH = os.getenv('UPLOAD_SCRIPT_PATH', '/opt/airflow/scripts/upload_fraud_data_to_minio.py')
    upload_partitioned_data_to_minio_task = BashOperator(
        task_id='upload_partitioned_data_to_minio_task',
        bash_command=f'cd /opt/airflow && python {UPLOAD_SCRIPT_PATH}',
    )

    trigger_run_dbt_dag_task = TriggerDagRunOperator(
        task_id='trigger_run_dbt_dag_task',
        trigger_dag_id='run_dbt_dag',
    )

    upload_partitioned_data_to_minio_task >> trigger_run_dbt_dag_task

dag = upload_to_minio_dag()
