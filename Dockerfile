FROM apache/airflow:2.8.1

# Install S3 provider (brings in boto3), MinIO client, and DuckDB
RUN pip install \
    apache-airflow-providers-amazon \
    minio \
    duckdb
