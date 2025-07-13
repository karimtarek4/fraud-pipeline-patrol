from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import os

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 7, 4),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

@dag(
    default_args=default_args,
    description='Run the initialize_metabase.py script to set up Metabase',
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=False,
)
def initialize_metabase_dag():
    # Use Variable for script path operational flexibility
    METABASE_SCRIPT_PATH = Variable.get('metabase_script_path', default_var='/opt/airflow/metabase/scripts/initialize_metabase.py')
    
    run_initialize_metabase = BashOperator(
        task_id='run_initialize_metabase',
        bash_command=f'python {METABASE_SCRIPT_PATH}',
        env=os.environ.copy(),
    )

    run_initialize_metabase

dag = initialize_metabase_dag()
