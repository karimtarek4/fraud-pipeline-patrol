"""
DAG to generate and partition synthetic fraud data for the pipeline.

This DAG generates synthetic fraud detection data and partitions it
for downstream processing. Configurable via Airflow Variables.
"""
import logging
import time
from datetime import datetime, timedelta

from airflow.datasets import Dataset
from airflow.decorators import branch_task, dag
from airflow.models import DagRun, Variable
from airflow.operators.bash import BashOperator
from airflow.utils.session import create_session
from airflow.utils.state import State
from airflow.utils.trigger_rule import TriggerRule

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get configuration from Airflow Variables
schedule = Variable.get("fraud_data_generation_schedule", default_var="*/1 * * * *")
enable_concurrency_check = Variable.get(
    "enable_dag_concurrency_check", default_var="true"
)
wait_seconds = int(Variable.get("dag_concurrency_wait_seconds", default_var="10"))
airflow_home = Variable.get("airflow_home_path", default_var="/opt/airflow")

# Default DAG arguments
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2023, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


@dag(
    schedule=schedule,  # Now configurable via Variables!
    start_date=datetime(2023, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    description="Generate fake transaction data - schedule configurable via Variables",
    is_paused_upon_creation=False,
)
def generate_and_partition_data_dag():
    """
    Define the data generation and partitioning DAG workflow.

    Creates a DAG that generates synthetic fraud data and partitions it
    for downstream processing by other DAGs in the pipeline.
    """

    @branch_task()
    def wait_for_other_dags(**context):
        # Check if concurrency control is enabled
        if enable_concurrency_check != "true":
            logger.info("DAG concurrency check disabled via Variables")
            return "generate_data_task"

        while True:
            with create_session() as session:
                running = (
                    session.query(DagRun)
                    .filter(
                        DagRun.dag_id != context["dag"].dag_id,
                        DagRun.state == State.RUNNING,
                    )
                    .count()
                )
            if running == 0:
                return "generate_data_task"
            logger.info(
                f"Other DAGs are still running, waiting {wait_seconds} seconds..."
            )
            time.sleep(wait_seconds)  # Configurable wait time

    generate_data_task = BashOperator(
        task_id="generate_data_task",
        bash_command=f"cd {airflow_home} && python {airflow_home}/scripts/generate_synthetic_fraud_data.py",
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    )

    # Define datasets for each partitioned table
    customers_dataset = Dataset(f"file://{airflow_home}/data/processed/customers/")
    merchants_dataset = Dataset(f"file://{airflow_home}/data/processed/merchants/")
    transactions_dataset = Dataset(
        f"file://{airflow_home}/data/processed/transactions/"
    )
    login_attempts_dataset = Dataset(
        f"file://{airflow_home}/data/processed/login_attempts/"
    )

    partition_data_task = BashOperator(
        task_id="partition_data_task",
        bash_command=f"cd {airflow_home} && python {airflow_home}/scripts/partition_data_with_duckdb.py",
        outlets=[
            customers_dataset,
            merchants_dataset,
            transactions_dataset,
            login_attempts_dataset,
        ],
    )

    # DAG dependencies
    wait_for_other_dags() >> [generate_data_task]
    generate_data_task >> partition_data_task


dag = generate_and_partition_data_dag()
