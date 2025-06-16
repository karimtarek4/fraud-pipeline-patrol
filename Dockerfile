FROM apache/airflow:2.8.1

# Install S3 provider (brings in boto3), MinIO client, and DuckDB
RUN pip install \
    apache-airflow-providers-amazon \
    minio \
    duckdb

# Install uv
RUN pip install uv

# Set workdir
WORKDIR /app


# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Switch to root to install system dependencies and copy files
USER root
RUN apt-get update && apt-get install -y git

# Copy project files into the container as root

# Copy project files into the container as root
COPY . .
# Ensure airflow user owns the /app directory and its contents
RUN chown -R airflow:0 /app

# Create .dbt directory and copy dbt profile
RUN mkdir -p /home/airflow/.dbt \
    && cp /app/dbt/fraud_detection/profiles.yml /home/airflow/.dbt/profiles.yml \
    && chown -R airflow:0 /home/airflow/.dbt


# Create results directory and set permissions
RUN mkdir -p /opt/airflow/data/results \
    && chown -R airflow:0 /opt/airflow/data/results

# Switch back to airflow user
USER airflow

# Create venv and install dependencies inside the container
RUN uv venv && uv pip install .

# Set environment variables so the venv is used by default
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
