from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging
import subprocess

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 10),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

def run_score_transactions():
    """
    Runs the score_transactions.py script.
    """
    SCRIPT_PATH = '/opt/airflow/scoring/scripts/score_transactions.py'
    logging.info(f"Running scoring script: {SCRIPT_PATH}")
    result = subprocess.run(['python', SCRIPT_PATH], capture_output=True, text=True)
    logging.info(f"Script output:\n{result.stdout}")
    if result.returncode != 0:
        logging.error(f"Script failed with error:\n{result.stderr}")
        raise Exception("score_transactions.py failed")
    logging.info("Scoring script completed successfully.")

with DAG(
    dag_id='score_transactions_dag',
    default_args=default_args,
    description='Run scoring logic on transactions after DBT models are built',
    catchup=False,
    is_paused_upon_creation=False,
    schedule_interval=None,
    max_active_runs=1,
) as dag:

    score_transactions_task = PythonOperator(
        task_id='score_transactions',
        python_callable=run_score_transactions,
        dag=dag,
    )

    score_transactions_task