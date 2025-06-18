from airflow.decorators import dag, task
from datetime import datetime, timedelta
import subprocess
import os
from dotenv import load_dotenv
from airflow.operators.trigger_dagrun import TriggerDagRunOperator


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

@task()
def run_score_transactions_task():
    """
    Runs the score_transactions.py script.
    """
    # Load environment variables from .env file
    SCRIPT_PATH = os.getenv('SCORE_TRANSACTIONS_SCRIPT_PATH', '/opt/airflow/scoring/scripts/score_transactions.py')
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
    schedule_interval=None,
    max_active_runs=1,
)
def score_transactions_dag():

    trigger_alert_users_dag_task = TriggerDagRunOperator(
        task_id='trigger_alert_users_dag_task',
        trigger_dag_id='alert_users_dag',
    )

    run_score_transactions_task() >> trigger_alert_users_dag_task

dag = score_transactions_dag()