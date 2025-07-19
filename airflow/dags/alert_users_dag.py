"""
Alert Users DAG for Fraud Detection Pipeline.

This DAG handles the notification process for users who have been flagged
for potentially fraudulent activity by the ML scoring pipeline.
"""
import os
from datetime import datetime, timedelta

from airflow.datasets import Dataset
from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from helpers.actualdata_postgres import get_actualdata_postgres_conn

# Default arguments for the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 5, 10),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

# Use actual PostgreSQL endpoint for output data
postgres_host = os.environ.get("ACTUALDATA_POSTGRES_HOST", "actualdata-postgres")
postgres_port = os.environ.get("ACTUALDATA_POSTGRES_PORT", "5432")
postgres_db = os.environ.get("ACTUALDATA_POSTGRES_DB", "actualdata")
fraud_alerts_dataset = Dataset(
    f"postgresql://{postgres_host}:{postgres_port}/{postgres_db}/public/fraud_alerts"
)


@task()
def alert_customers_task():
    """
    Connect to Postgres and send alert emails to fraud-affected customers.

    Selects all customer_ids from fraud_alerts table and simulates sending emails.
    Only runs if alert notifications are enabled via Airflow Variables.
    """
    enable_alerts = Variable.get("enable_alert_notifications", default_var="true")

    if enable_alerts != "true":
        print("Alert notifications disabled via Variables - skipping customer alerts")
        return "Alerts disabled"

    try:
        conn = get_actualdata_postgres_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT customer_id FROM fraud_alerts;")
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
    description="Print number of records in fraud_alerts table in Postgres",
    catchup=False,
    is_paused_upon_creation=False,
    schedule=[fraud_alerts_dataset],
    max_active_runs=1,
)
def alert_users_dag():
    """
    Define the alert users DAG workflow.

    Creates a DAG that alerts customers about fraud detection results
    and optionally triggers Metabase dashboard initialization.
    """
    # Main alert task
    alert_task = alert_customers_task()

    # Branching decision function
    def decide_metabase_trigger(**context):
        """
        Decide whether to trigger Metabase or skip it based on Variables.

        Returns the task_id to execute next based on the enable_metabase_trigger
        Variable setting.
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
        task_id="decide_metabase_trigger",
        python_callable=decide_metabase_trigger,
    )

    # Metabase trigger task (only runs if branch chooses it)
    trigger_initialize_metabase_task = TriggerDagRunOperator(
        task_id="trigger_initialize_metabase_task",
        trigger_dag_id="initialize_metabase_dag",
    )

    # Skip task (runs if Metabase is disabled)
    skip_metabase_task = DummyOperator(task_id="skip_metabase_task")

    # Task dependencies - branch decides which path to take
    alert_task >> metabase_branch
    metabase_branch >> [trigger_initialize_metabase_task, skip_metabase_task]


dag = alert_users_dag()
