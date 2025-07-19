#!/usr/bin/env bash
# Don't run db init here since airflow-init-variables already handles it
# airflow db init

# Create admin user if it doesn't exist
airflow users create \
  --username "${AIRFLOW_ADMIN_USER}" \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email "${AIRFLOW_ADMIN_EMAIL}" \
  --password "${AIRFLOW_ADMIN_PASSWORD}" \
  || echo "Admin user already exists"

# Start Airflow services
airflow scheduler &
exec airflow webserver
