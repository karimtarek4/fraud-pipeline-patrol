from airflow.decorators import dag, task
from airflow.models import Variable
from datetime import datetime, timedelta
import subprocess
import os
from dotenv import load_dotenv
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.datasets import Dataset


# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

# Use actual MinIO endpoint path for input data
minio_endpoint = os.environ.get('MINIO_ENDPOINT', 'minio:9000')
minio_fraud_mart_data_dataset = Dataset(f"s3://{minio_endpoint}/fraud-data-processed/marts/")

# Use actual PostgreSQL endpoint for output data
postgres_host = os.environ.get('ACTUALDATA_POSTGRES_HOST', 'actualdata-postgres')
postgres_port = os.environ.get('ACTUALDATA_POSTGRES_PORT', '5432')
postgres_db = os.environ.get('ACTUALDATA_POSTGRES_DB', 'actualdata')
fraud_alerts_dataset = Dataset(f"postgresql://{postgres_host}:{postgres_port}/{postgres_db}/public/fraud_alerts")


# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 10),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

@task()
def run_score_transactions_task():
    """
    Runs the score_transactions.py script using configurable path from Variables.
    """
    # Use Variable instead of environment variable for operational flexibility
    SCRIPT_PATH = Variable.get('scoring_script_path', default_var='/opt/airflow/scoring/scripts/score_transactions.py')
    
    result = subprocess.run(['python', SCRIPT_PATH], capture_output=True, text=True)
    if result.stdout:
        print(f"Script output:\n{result.stdout}")
    if result.returncode != 0:
        print(f"Script failed with error:\n{result.stderr}")
        raise Exception("score_transactions.py failed")
    print("Scoring script completed successfully.")

@dag(
    default_args=default_args,
    description='Run scoring logic on transactions after DBT models are built',
    catchup=False,
    is_paused_upon_creation=False,
    schedule=[minio_fraud_mart_data_dataset],
    max_active_runs=1,
)
def ml_transaction_scoring_dag():

    score_transactions_task = run_score_transactions_task.override(
        outlets=[fraud_alerts_dataset]  # This task produces the PostgreSQL dataset
    )()

    score_transactions_task 

dag = ml_transaction_scoring_dag()