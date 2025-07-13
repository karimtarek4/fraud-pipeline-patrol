from airflow.decorators import dag, branch_task
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import logging
import time
from airflow.utils.session import create_session
from airflow.models import DagRun
from airflow.utils.state import State
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.datasets import Dataset

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default DAG arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

@dag(
    schedule_interval='*/1 * * * *',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    description='Generate fake transaction data every 1 minute',
    is_paused_upon_creation=False,
)
def generate_and_partition_data_dag():

    @branch_task()
    def wait_for_other_dags(**context):
        while True:
            with create_session() as session:
                running = session.query(DagRun).filter(
                    DagRun.dag_id != context['dag'].dag_id,
                    DagRun.state == State.RUNNING
                ).count()
            if running == 0:
                return 'generate_data_task'
            print("Other DAGs are still running, waiting...")
            time.sleep(10)

    generate_data_task = BashOperator(
        task_id='generate_data_task',
        bash_command='cd /opt/airflow && python /opt/airflow/scripts/generate_synthetic_fraud_data.py',
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    # Define datasets for each partitioned table
    customers_dataset = Dataset("file:///opt/airflow/data/processed/customers/")
    merchants_dataset = Dataset("file:///opt/airflow/data/processed/merchants/")
    transactions_dataset = Dataset("file:///opt/airflow/data/processed/transactions/")
    login_attempts_dataset = Dataset("file:///opt/airflow/data/processed/login_attempts/")

    partition_data_task = BashOperator(
        task_id='partition_data_task',
        bash_command='cd /opt/airflow && python /opt/airflow/scripts/partition_data_with_duckdb.py',
        outlets=[customers_dataset, merchants_dataset, transactions_dataset, login_attempts_dataset]
    )

    # DAG dependencies
    wait_for_other_dags() >> [generate_data_task]
    generate_data_task >> partition_data_task

dag = generate_and_partition_data_dag()
