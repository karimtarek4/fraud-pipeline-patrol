# Metabase Initialization Script

This directory contains a script to automate the setup of Metabase for your analytics. The script is triggered by Airflow and will:
- Wait for Metabase to be ready before proceeding
- Handle admin user creation or login
- Add a Postgres database connection.
- Imports default cards and dashboards from JSON files.