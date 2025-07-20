"""
Airflow DAG to initialize Metabase dashboards and configurations.

This DAG sets up Metabase with the necessary dashboards, cards,
and database connections for fraud detection visualization.
"""
import os
from datetime import datetime, timedelta

from airflow.decorators import dag
from airflow.models import Variable
from airflow.operators.bash import BashOperator

# Default arguments for the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 7, 4),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


@dag(
    default_args=default_args,
    description="Run the initialize_metabase.py script to set up Metabase",
    schedule=None,
    catchup=False,
    is_paused_upon_creation=False,
)
def initialize_metabase_dag():
    """
    Define the Metabase initialization DAG workflow.

    Creates a DAG that initializes Metabase with fraud detection
    dashboards and database connections.
    """
    # Use Variable for script path operational flexibility
    METABASE_SCRIPT_PATH = Variable.get(
        "metabase_script_path",
        default_var="/opt/airflow/metabase/scripts/initialize_metabase.py",
    )

    run_initialize_metabase = BashOperator(
        task_id="run_initialize_metabase",
        bash_command=f"python {METABASE_SCRIPT_PATH}",
        env=os.environ.copy(),
    )

    run_initialize_metabase


dag = initialize_metabase_dag()
