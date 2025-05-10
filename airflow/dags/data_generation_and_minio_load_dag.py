"""
Data Generation and MinIO Load DAG

This DAG:
1. Runs the synthetic data generation script
2. Reads the generated Parquet files
3. Uploads them to the MinIO bucket
"""

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
from minio import Minio
from minio.error import S3Error
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 5, 10),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    dag_id='data_generation_and_minio_load',
    default_args=default_args,
    description='Generate synthetic fraud data and load it into MinIO',
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:

    # Task 1: Generate data
    generate_data_task = BashOperator(
        task_id='generate_data',
        bash_command='cd /opt/airflow && python /opt/airflow/scripts/generate_synthetic_fraud_data.py',
        dag=dag,
    )

    # Task 2: Upload data to MinIO
    def upload_to_minio():
        try:
            # Get paths 
            airflow_home = os.environ.get('AIRFLOW_HOME', '/opt/airflow')
            data_path = Path(airflow_home) / 'data' / 'raw'
            
            # Log paths for debugging
            logger.info(f"Airflow home: {airflow_home}")
            logger.info(f"Data path: {data_path}")
            
            # Check if the data directory exists
            if not data_path.exists():
                logger.error(f"Data directory not found: {data_path}")
                raise FileNotFoundError(f"Data directory not found: {data_path}")
            
            # List the files in the raw directory
            files = list(data_path.glob('*.parquet'))
            logger.info(f"Found {len(files)} Parquet files")
            
            if not files:
                logger.warning("No Parquet files found in the data directory")
                return "No files to upload"
                
            # Initialize MinIO client
            minio_endpoint = os.environ.get('MINIO_ENDPOINT', 'minio:9000')
            minio_access_key = os.environ.get('MINIO_ROOT_USER', 'minioadmin')
            minio_secret_key = os.environ.get('MINIO_ROOT_PASSWORD', 'minioadmin')
            
            logger.info(f"Connecting to MinIO at {minio_endpoint}")
            
            # Create MinIO client
            minio_client = Minio(
                minio_endpoint,
                access_key=minio_access_key,
                secret_key=minio_secret_key,
                secure=False  # Set to True if using HTTPS
            )
            
            # Create bucket if it doesn't exist
            bucket_name = "fraud-data"
            if not minio_client.bucket_exists(bucket_name):
                minio_client.make_bucket(bucket_name)
                logger.info(f"Bucket '{bucket_name}' created successfully")
            
            # Upload each file to MinIO
            for file_path in files:
                file_name = file_path.name
                object_name = file_name
                
                logger.info(f"Uploading {file_name} to MinIO bucket {bucket_name}")
                
                # Upload file
                minio_client.fput_object(
                    bucket_name,
                    object_name,
                    str(file_path)
                )
                
                logger.info(f"Successfully uploaded {file_name} to MinIO")
            
            return f"Successfully uploaded {len(files)} files to MinIO bucket {bucket_name}"
            
        except FileNotFoundError as e:
            logger.error(f"File not found error: {e}")
            raise
        except S3Error as e:
            logger.error(f"MinIO error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    # Create the upload task
    upload_to_minio_task = PythonOperator(
        task_id='upload_to_minio',
        python_callable=upload_to_minio,
        dag=dag,
    )
    
    # Define task dependencies
    generate_data_task >> upload_to_minio_task 
