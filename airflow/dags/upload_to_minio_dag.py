"""
Upload partitioned fraud detection data to MinIO storage.

This DAG uploads processed fraud detection data to MinIO while
maintaining the directory structure for downstream processing.
"""

import os
from datetime import datetime, timedelta

from airflow.datasets import Dataset
from airflow.decorators import dag
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

customers_dataset = Dataset("file:///opt/airflow/data/processed/customers/")
merchants_dataset = Dataset("file:///opt/airflow/data/processed/merchants/")
transactions_dataset = Dataset("file:///opt/airflow/data/processed/transactions/")
login_attempts_dataset = Dataset("file:///opt/airflow/data/processed/login_attempts/")

# Use actual MinIO endpoint path
minio_endpoint = os.environ.get("MINIO_ENDPOINT", "minio:9000")
minio_fraud_stg_data_dataset = Dataset(f"s3://{minio_endpoint}/fraud-data-processed/")

# Default arguments for the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 5, 10),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    default_args=default_args,
    description="Load partitioned data to MinIO",
    catchup=False,
    is_paused_upon_creation=False,
    schedule=[
        customers_dataset,
        merchants_dataset,
        transactions_dataset,
        login_attempts_dataset,
    ],
    max_active_runs=1,
)
def upload_to_minio_dag():
    """
    Define the MinIO upload DAG workflow.

    Creates a DAG that uploads partitioned fraud detection data
    to MinIO storage for downstream processing.
    """
    # Use Variable instead of environment variable for operational flexibility
    UPLOAD_SCRIPT_PATH = Variable.get(
        "upload_script_path",
        default_var="/opt/airflow/scripts/upload_fraud_data_to_minio.py",
    )

    upload_partitioned_data_to_minio_task = BashOperator(
        task_id="upload_partitioned_data_to_minio_task",
        bash_command=f"cd /opt/airflow && python {UPLOAD_SCRIPT_PATH}",
        outlets=[minio_fraud_stg_data_dataset],
    )

    upload_partitioned_data_to_minio_task


dag = upload_to_minio_dag()
