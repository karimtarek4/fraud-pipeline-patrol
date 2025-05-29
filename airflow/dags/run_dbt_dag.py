from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor
from datetime import datetime, timedelta

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 10),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id='run_dbt_dag',
    default_args=default_args,
    description='Run DBT models after data is uploaded to MinIO',
    schedule_interval='*/10 * * * *',  # Every 10 minutes
    catchup=False,
    is_paused_upon_creation=False
) as dag:

    run_dbt = BashOperator(
        task_id='run_dbt',
        bash_command='export PATH="/app/.venv/bin:$PATH" && cd $DBT_PROJECT_DIR && dbt run --profiles-dir /home/airflow/.dbt',
        env={
            'DBT_PROJECT_DIR': '/app/dbt/fraud_detection',
            'HOME': '/home/airflow',
            'S3_ENDPOINT': 'minio:9000',
            'MINIO_ENDPOINT': 'minio:9000',
            'MINIO_ROOT_USER': 'minioadmin',
            'MINIO_ROOT_PASSWORD': 'minioadmin',
        },
    )

    run_dbt
