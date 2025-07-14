from airflow.decorators import dag, task
from airflow.operators.python import BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import os
import sys
import os
sys.path.append('/opt/airflow')
from helpers.postgres import get_postgres_conn
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.datasets import Dataset




# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 10),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# Use actual PostgreSQL endpoint for output data
postgres_host = os.environ.get('ACTUALDATA_POSTGRES_HOST', 'actualdata-postgres')
postgres_port = os.environ.get('ACTUALDATA_POSTGRES_PORT', '5432')
postgres_db = os.environ.get('ACTUALDATA_POSTGRES_DB', 'actualdata')
fraud_alerts_dataset = Dataset(f"postgresql://{postgres_host}:{postgres_port}/{postgres_db}/public/fraud_alerts")



@task()
def alert_customers_task():
    """
    Connects to Postgres, selects all customer_ids from fraud_alerts, and simulates sending emails.
    Only runs if alert notifications are enabled via Variables.
    """
    enable_alerts = Variable.get("enable_alert_notifications", default_var="true")
    
    if enable_alerts != "true":
        print("Alert notifications disabled via Variables - skipping customer alerts")
        return "Alerts disabled"
    
    try:
        conn = get_postgres_conn()
        with conn.cursor() as cur:
            cur.execute('SELECT customer_id FROM fraud_alerts;')
            customer_ids = cur.fetchall()
            for row in customer_ids:
                customer_id = row[0]
                print(f"Sending email to customer {customer_id}...")
        conn.close()
        print(f"Successfully sent alerts to {len(customer_ids)} customers")
    except Exception as e:
        print(f"Failed to alert customers: {e}")
        raise

@dag(
    default_args=default_args,
    description='Print number of records in fraud_alerts table in Postgres',
    catchup=False,
    is_paused_upon_creation=False,
    schedule=[fraud_alerts_dataset],
    max_active_runs=1,
)
def alert_users_dag():

    # Main alert task
    alert_task = alert_customers_task()
    
    # Branching decision function
    def decide_metabase_trigger(**context):
        """
        Decides whether to trigger Metabase or skip it based on Variables.
        Returns the task_id to execute next.
        """
        enable_metabase = Variable.get("enable_metabase_trigger", default_var="true")
        
        if enable_metabase == "true":
            print("Metabase trigger enabled - will trigger initialize_metabase_dag")
            return "trigger_initialize_metabase_task"  # Return task_id to execute
        else:
            print("Metabase trigger disabled via Variables - skipping")
            return "skip_metabase_task"  # Return task_id to execute

    # Branch operator that actually controls the flow
    metabase_branch = BranchPythonOperator(
        task_id='decide_metabase_trigger',
        python_callable=decide_metabase_trigger,
    )
    
    # Metabase trigger task (only runs if branch chooses it)
    trigger_initialize_metabase_task = TriggerDagRunOperator(
        task_id='trigger_initialize_metabase_task',
        trigger_dag_id='initialize_metabase_dag',
    )
    
    # Skip task (runs if Metabase is disabled)
    skip_metabase_task = DummyOperator(
        task_id='skip_metabase_task'
    )

    # Task dependencies - branch decides which path to take
    alert_task >> metabase_branch
    metabase_branch >> [trigger_initialize_metabase_task, skip_metabase_task]

dag = alert_users_dag()
