"""
DAG to generate fraud alert visualizations using the create_fraud_alert_viz.py script.
"""

from airflow.decorators import dag
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

@dag(
    default_args=default_args,
    description='Generate fraud alert visualizations',
    schedule_interval=None,
    catchup=False,
    is_paused_upon_creation=False,
    max_active_runs=1,
)
def visualize_alert_data_dag():
    script_path = os.getenv('CREATE_FRAUD_ALERT_VIZ_PATH', '/opt/airflow/scripts/visualize_alert_data.py')

    generate_visualizations_task = BashOperator(
        task_id='generate_visualizations_task',
        bash_command=f'cd /opt/airflow && python {script_path}',
    )

    generate_visualizations_task

dag = visualize_alert_data_dag()
