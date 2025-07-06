# Metabase Initialization Script

This directory contains a script to automate the setup of Metabase for your analytics stack. The script is triggered by Airflow and will:
- Wait for Metabase to be ready before proceeding
- Handle admin user creation or login
- Add a Postgres database connection.
- Imports cards and dashboards from JSON files.

### Usage

1. Ensure Metabase is running and accessible at the configured host/port.
2. Automatic creation of admin user to bypass wizard screen
3. Pre-made Cards and dashboards JSON files in `../metadata/metabase_cards.json` and `../metadata/metabase_dashboard.json` - These are pre-fetched via Metabase API
4. A Docker/Airflow, trigger the corresponding DAG to run this script inside the container.
