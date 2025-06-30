#!/bin/sh
# Script to add the Actual Data Postgres database to Metabase via API
# Requires: curl, jq

MB_HOSTNAME=${MB_HOSTNAME:-localhost}
MB_PORT=${MB_PORT:-3000}
ADMIN_EMAIL="kareem@gmail.com"
ADMIN_PASSWORD="K@reem2025!secure"

# Get Metabase session token
SESSION_ID=$(curl -s -X POST -H "Content-Type: application/json" \
  http://${MB_HOSTNAME}:${MB_PORT}/api/session \
  -d '{"username": "'${ADMIN_EMAIL}'", "password": "'${ADMIN_PASSWORD}'"}' | jq -r '.id')

# Add Actual Data Postgres database
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

echo "✅ Actual Data Postgres database is now available in Metabase."
