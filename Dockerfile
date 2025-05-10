FROM apache/airflow:2.8.1

# Install S3 provider (brings in boto3) and DuckDB
RUN pip install \
    apache-airflow-providers-amazon \
    duckdb
