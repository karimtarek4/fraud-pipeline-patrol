"""
Airflow DAG for machine learning transaction scoring and fraud detection.

This DAG processes transaction data through ML models to generate
fraud scores and predictions for downstream analysis.
"""
import os
import subprocess  # nosec B404
from datetime import datetime, timedelta

from airflow.datasets import Dataset
from airflow.decorators import dag, task
from airflow.models import Variable
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

# Use actual MinIO endpoint path for input data
minio_endpoint = os.environ.get("MINIO_ENDPOINT", "minio:9000")
minio_fraud_mart_data_dataset = Dataset(
    f"s3://{minio_endpoint}/fraud-data-processed/marts/"
)

# Use actual PostgreSQL endpoint for output data
postgres_host = os.environ.get("ACTUALDATA_POSTGRES_HOST", "actualdata-postgres")
postgres_port = os.environ.get("ACTUALDATA_POSTGRES_PORT", "5432")
postgres_db = os.environ.get("ACTUALDATA_POSTGRES_DB", "actualdata")
fraud_alerts_dataset = Dataset(
    f"postgresql://{postgres_host}:{postgres_port}/{postgres_db}/public/fraud_alerts"
)


# Default arguments for the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 5, 10),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


@task()
def run_score_transactions_task():
    """Run the ML transaction scoring script with configurable path."""
    # Use Variable instead of environment variable for operational flexibility
    SCRIPT_PATH = Variable.get(
        "scoring_script_path",
        default_var="/opt/airflow/scoring/scripts/score_transactions.py",
    )

    # Use absolute path for security
    result = subprocess.run(  # nosec B603 B607
        ["/app/.venv/bin/python", SCRIPT_PATH],
        capture_output=True,
        text=True,
        check=False,
        timeout=300,  # 5 minute timeout
    )
    if result.stdout:
        print(f"Script output:\n{result.stdout}")
    if result.returncode != 0:
        print(f"Script failed with error:\n{result.stderr}")
        raise Exception("score_transactions.py failed")
    print("Scoring script completed successfully.")


@dag(
    default_args=default_args,
    description="Run scoring logic on transactions after DBT models are built",
    catchup=False,
    is_paused_upon_creation=False,
    schedule=[minio_fraud_mart_data_dataset],
    max_active_runs=1,
)
def ml_transaction_scoring_dag():
    """
    Define the ML transaction scoring DAG workflow.

    Creates a DAG that processes transactions through ML models
    to generate fraud scores and alerts.
    """
    score_transactions_task = run_score_transactions_task.override(
        outlets=[fraud_alerts_dataset]  # This task produces the PostgreSQL dataset
    )()

    score_transactions_task


dag = ml_transaction_scoring_dag()
