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
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.python_operator import  BranchPythonOperator
from airflow.models import DagRun
from airflow.utils.state import State
from airflow.utils.session import create_session
from airflow.utils.trigger_rule import TriggerRule
import time

# Sets the minimum logging level to INFO.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),  # avoid recalculating the start date by using a fixed date
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

with DAG(
    'generate_and_partition_data_dag',
    default_args=default_args,
    description='Generate fake transaction data every 1 minute',
    schedule_interval='*/1 * * * *',  # Run every 1 minute
    catchup=False,
    max_active_runs=1, # add max active runs to avoid overlapping
    is_paused_upon_creation=False
) as dag:
    
    def branch_should_wait(**context):
        dag_id = context['dag'].dag_id
        execution_date = context['execution_date']
        with create_session() as session:
            previous_runs = session.query(DagRun).filter(
                DagRun.dag_id == dag_id,
                DagRun.execution_date < execution_date,
                DagRun.state.in_([State.SUCCESS, State.FAILED, State.SKIPPED])
            ).count()
        if previous_runs > 0:
            return 'wait_for_dbt_not_running'
        else:
            return 'generate_data'
        
    def wait_until_dbt_not_running(**context):
        while True:
            with create_session() as session:
                running = session.query(DagRun).filter(
                    DagRun.dag_id == 'run_dbt_dag',
                    DagRun.state == State.RUNNING
                ).count()
            if running == 0:
                return True
            time.sleep(10)  # Wait 10 seconds before checking again

    branch_should_wait_task = BranchPythonOperator(
        task_id='branch_should_wait',
        python_callable=branch_should_wait,
        provide_context=True,
        dag=dag,
    )

    wait_for_dbt_not_running = PythonOperator(
        task_id='wait_for_dbt_not_running',
        python_callable=wait_until_dbt_not_running,
        provide_context=True,
        dag=dag,
    )

    # Task 1: Generate data "Overwrite"
    generate_data_task = BashOperator(
        task_id='generate_data',
        bash_command='cd /opt/airflow && python /opt/airflow/scripts/generate_synthetic_fraud_data.py',
        dag=dag,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    # Task 2: Partition data with DuckDB
    partition_data_task = BashOperator(
        task_id='partition_data',
        bash_command='cd /opt/airflow && python /opt/airflow/scripts/partition_data_with_duckdb.py',
        dag=dag,
    )

    # Trigger run_dbt_dag after upload is complete
    trigger_run_upload_to_minio_dag = TriggerDagRunOperator(
        task_id='trigger_run_upload_to_minio_dag',
        trigger_dag_id='upload_to_minio_dag',
    )

    # Set task dependencies for correct dynamic flow
    branch_should_wait_task >> [wait_for_dbt_not_running, generate_data_task]
    wait_for_dbt_not_running >> generate_data_task
    generate_data_task >> partition_data_task >> trigger_run_upload_to_minio_dag