from airflow.decorators import dag, task
from datetime import datetime, timedelta
import os
import sys
import os
sys.path.append('/opt/airflow')
from helpers.postgres import get_postgres_conn
from airflow.operators.trigger_dagrun import TriggerDagRunOperator


# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 10),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

@task()
def alert_customers_task():
    """
    Connects to Postgres, selects all customer_ids from fraud_alerts, and simulates sending emails.
    """
    try:
        conn = get_postgres_conn()
        with conn.cursor() as cur:
            cur.execute('SELECT customer_id FROM fraud_alerts;')
            customer_ids = cur.fetchall()
            for row in customer_ids:
                customer_id = row[0]
                print(f"Sending email to customer {customer_id}...")
        conn.close()
    except Exception as e:
        print(f"Failed to alert customers: {e}")

@dag(
    default_args=default_args,
    description='Print number of records in fraud_alerts table in Postgres',
    catchup=False,
    is_paused_upon_creation=False,
    schedule_interval=None,
    max_active_runs=1,
)
def alert_users_dag():

    trigger_initialize_metabase_task = TriggerDagRunOperator(
        task_id='trigger_initialize_metabase_task',
        trigger_dag_id='initialize_metabase_dag',
    )

    alert_customers_task() >> trigger_initialize_metabase_task

dag = alert_users_dag()
