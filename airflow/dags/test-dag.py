# import necessary libraries
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import logging
import os
import json
from minio import Minio
from minio.error import S3Error

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 10),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    dag_id='simple_pass_through',
    default_args=default_args,
    description='A simple DAG that connects to MinIO and lists buckets',
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:

    # Task 1: print a message
    def hello_world():
        print('Hello, Airflow!')

    # Task 2: connect to MinIO and list buckets
    def connect_to_minio():
        try:
            # Initialize MinIO client
            minio_endpoint = os.environ.get('MINIO_ENDPOINT', 'minio:9000')
            minio_access_key = os.environ.get('MINIO_ROOT_USER', 'minioadmin')
            minio_secret_key = os.environ.get('MINIO_ROOT_PASSWORD', 'minioadmin')
            
            print(f"Connecting to MinIO at {minio_endpoint} with access key {minio_access_key}")
            
            # Create client with anonymous access if credentials are not set
            client = Minio(
                minio_endpoint,
                access_key=minio_access_key,
                secret_key=minio_secret_key,
                secure=False  # Set to True if you're using HTTPS
            )
            
            # List all buckets
            buckets = client.list_buckets()
            print("Successfully connected to MinIO!")
            
            # Create a bucket if it doesn't exist
            bucket_name = "fraud-data"
            if not any(bucket.name == bucket_name for bucket in buckets):
                client.make_bucket(bucket_name)
                print(f"Bucket '{bucket_name}' created successfully.")
            else:
                print(f"Bucket '{bucket_name}' already exists.")
                
            # List all buckets again to confirm
            buckets = client.list_buckets()
            for bucket in buckets:
                print(f"Bucket: {bucket.name}, Created: {bucket.creation_date}")
                
            return "MinIO connection verified successfully!"
        except S3Error as e:
            print(f"Error connecting to MinIO: {e}")
            raise e

    # PythonOperator to run the first function
    t1 = PythonOperator(
        task_id='hello_world_task',
        python_callable=hello_world,
        dag=dag,
    )
    
    # PythonOperator to run the MinIO connection function
    t2 = PythonOperator(
        task_id='connect_to_minio_task',
        python_callable=connect_to_minio,
        dag=dag,
    )
    
    # Set task dependencies
    t1 >> t2