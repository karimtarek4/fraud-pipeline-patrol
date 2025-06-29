#!/bin/sh
# Script to automate Metabase admin and user creation via API
# Requires: curl, jq

# --- CONFIGURABLE VARIABLES ---

# --- ADMIN USER CREDENTIALS (from user request) ---
MB_HOSTNAME=${MB_HOSTNAME:-localhost}
MB_PORT=${MB_PORT:-3000}
ADMIN_EMAIL="kareem@gmail.com"
ADMIN_PASSWORD="K@reem2025!secure"
ADMIN_FIRST_NAME="kareem"
ADMIN_LAST_NAME="tarek"

# --- WAIT FOR METABASE TO BE READY ---
echo "⌚︎ Waiting for Metabase to start on ${MB_HOSTNAME}:${MB_PORT}..."
while (! curl -s -m 5 http://${MB_HOSTNAME}:${MB_PORT}/api/session/properties -o /dev/null); do sleep 5; done

echo "😎 Creating admin user..."
SETUP_TOKEN=$(curl -s -m 5 -X GET \
    -H "Content-Type: application/json" \
    http://${MB_HOSTNAME}:${MB_PORT}/api/session/properties \
    | jq -r '."setup-token"')

MB_TOKEN=$(curl -s -X POST \
    -H "Content-type: application/json" \
    http://${MB_HOSTNAME}:${MB_PORT}/api/setup \
    -d '{
    "token": "'${SETUP_TOKEN}'",
    "user": {
        "email": "'${ADMIN_EMAIL}'",
        "first_name": "'${ADMIN_FIRST_NAME}'",
        "last_name": "'${ADMIN_LAST_NAME}'",
        "password": "'${ADMIN_PASSWORD}'"
    },
    "prefs": {
        "allow_tracking": false,
        "site_name": "Metabase Instance"
    }
}' | jq -r '.id')

if [ "$MB_TOKEN" = "null" ] || [ -z "$MB_TOKEN" ]; then
  echo "❌ Failed to create admin user. It may already exist or setup is already complete."
  exit 1
fi

# --- CREATE ADDITIONAL USERS ---
echo "👥 Creating basic users..."
# 1. Log in as admin to get a session token
SESSION_ID=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    http://${MB_HOSTNAME}:${MB_PORT}/api/session \
    -d '{"username": "'${ADMIN_EMAIL}'", "password": "'${ADMIN_PASSWORD}'"}' | jq -r '.id')

# --- ADD ACTUAL DATA POSTGRES DATABASE TO METABASE ---
echo "🗄️ Adding Actual Data Postgres database to Metabase..."
curl -s -X POST http://${MB_HOSTNAME}:${MB_PORT}/api/database \
  -H "Content-Type: application/json" \
  -H "X-Metabase-Session: ${SESSION_ID}" \
  -d '{
    "name": "Actual Data Postgres",
    "engine": "postgres",
    "details": {
      "host": "actualdata-postgres",
      "port": 5432,
      "dbname": "actualdata",
      "user": "actualdata",
      "password": "actualdata_pass",
      "ssl": false
    },
    "is_full_sync": true,
    "is_on_demand": false,
    "schedules": {}
  }'

echo "✅ Users and databases created! You can now log in as admin or basic users, and the Airflow Postgres and Actual Data Postgres databases are available in Metabase."
