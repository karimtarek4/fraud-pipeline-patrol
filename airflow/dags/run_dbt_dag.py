from airflow.decorators import dag
from airflow.operators.bash import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime, timedelta
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 10),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

@dag(
    default_args=default_args,
    description='Run DBT models after data is uploaded to MinIO',
    catchup=False,
    is_paused_upon_creation=False,
    schedule_interval=None,
    max_active_runs=1,
)
def run_dbt_dag():

    # Read environment variables from .env
    DBT_PROJECT_DIR = os.getenv('DBT_PROJECT_DIR', '/app/dbt/fraud_detection')
    HOME = os.getenv('HOME', '/home/airflow')
    S3_ENDPOINT = os.getenv('S3_ENDPOINT', 'minio:9000')
    MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'minio:9000')
    MINIO_ROOT_USER = os.getenv('MINIO_ROOT_USER', 'minioadmin')
    MINIO_ROOT_PASSWORD = os.getenv('MINIO_ROOT_PASSWORD', 'minioadmin')

    install_dbt_deps_task = BashOperator(
        task_id='install_dbt_deps_task',
        bash_command='export PATH="/app/.venv/bin:$PATH" && cd $DBT_PROJECT_DIR && dbt deps --profiles-dir /home/airflow/.dbt',
        env={
            'DBT_PROJECT_DIR': DBT_PROJECT_DIR
        },
    )

    run_dbt_task = BashOperator(
        task_id='run_dbt_task',
        bash_command='export PATH="/app/.venv/bin:$PATH" && cd $DBT_PROJECT_DIR && dbt run --profiles-dir /home/airflow/.dbt',
        env={
            'DBT_PROJECT_DIR': DBT_PROJECT_DIR,
            'HOME': HOME,
            'S3_ENDPOINT': S3_ENDPOINT,
            'MINIO_ENDPOINT': MINIO_ENDPOINT,
            'MINIO_ROOT_USER': MINIO_ROOT_USER,
            'MINIO_ROOT_PASSWORD': MINIO_ROOT_PASSWORD,
        },
    )

    trigger_ml_transaction_scoring_dag_task = TriggerDagRunOperator(
        task_id='trigger_ml_transaction_scoring_dag_task',
        trigger_dag_id='ml_transaction_scoring_dag',
    )

    install_dbt_deps_task >> run_dbt_task >> trigger_ml_transaction_scoring_dag_task

dag = run_dbt_dag()
