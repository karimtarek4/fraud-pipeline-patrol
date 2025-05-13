"""
This DAG:
Uploads parttioned data to MinIO while maintaining the directory structure.
"""

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
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
    dag_id='upload_to_minio_dag',
    default_args=default_args,
    description='Load partitioned data to MinIO',
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:

    # Task 2: Upload data to MinIO
    def upload_to_minio():
        try:
            # Get paths 
            airflow_home = os.environ.get('AIRFLOW_HOME', '/opt/airflow')
            data_path = Path(airflow_home) / 'data' / 'processed' 
            
            # Log paths for debugging
            logger.info(f"Airflow home: {airflow_home}")
            logger.info(f"Data path: {data_path}")
            
            # Check if the data directory exists
            if not data_path.exists():
                logger.error(f"Data directory not found: {data_path}")
                raise FileNotFoundError(f"Data directory not found: {data_path}")
            
            # .iterdir() returns all items inside directort (files and folders)
            # if d.is_dir()] if it's a directory not a file
            # d for d in d -> include d in the resulting list
            subdirs = [d for d in data_path.iterdir() if d.is_dir()]
            logger.info(f"Found {len(subdirs)} data subdirectories: {[d.name for d in subdirs]}")
            
            if not subdirs:
                logger.warning("No data subdirectories found in the processed directory")
                return "No data to upload"
                
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
            bucket_name = "fraud-data-processed"
            if not minio_client.bucket_exists(bucket_name):
                minio_client.make_bucket(bucket_name)
                logger.info(f"Bucket '{bucket_name}' created successfully")
            
            # Keep track of uploaded files
            total_files_uploaded = 0
            
            # Process each table directory
            for subdir in subdirs:
                table_name = subdir.name
                logger.info(f"Processing {table_name} directory")
                
                # Use recursive glob to find all parquet files in subdirectories
                # glob () -> use wild card to find files
                # list () -> return a list of pathes
                parquet_files = list(subdir.glob('**/*.parquet'))
                logger.info(f"Found {len(parquet_files)} parquet files in {table_name}")
                
                # Upload each file to MinIO, preserving the directory structure
                for file_path in parquet_files:
                    # relative_to(data_path) -> data / processed
                    rel_path = file_path.relative_to(data_path)
                    object_name = str(rel_path)
                    
                    logger.info(f"Uploading {file_path} to MinIO as {object_name}")
                    
                    # Upload file
                    minio_client.fput_object(
                        bucket_name,
                        object_name,
                        str(file_path)
                    )
                    
                    logger.info(f"Successfully uploaded {object_name}")
                    total_files_uploaded += 1
            
            return f"Successfully uploaded {total_files_uploaded} files from {len(subdirs)} directories to MinIO bucket {bucket_name}"
            
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
    upload_partitioned_data_to_minio_task = PythonOperator(
        task_id='upload_partitioned_data_to_minio',
        python_callable=upload_to_minio,
        dag=dag,
    )
    
    # Define task dependencies
    upload_partitioned_data_to_minio_task 
