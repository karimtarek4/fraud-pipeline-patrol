#!/bin/bash
# Batch clone all Metabase cards using curl and jq
# Requires: jq

METABASE_URL="http://localhost:3000"
USERNAME="kareem@gmail.com"
PASSWORD="K@reem2025!secure"

# Authenticate and get session token
SESSION_ID=$(curl -s -X POST -H "Content-Type: application/json" \
  "$METABASE_URL/api/session" \
  -d '{"username": "'$USERNAME'", "password": "'$PASSWORD'"}' | jq -r '.id')

if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" == "null" ]; then
  echo "Failed to get Metabase session token."
  exit 1
fi

echo "Session ID: $SESSION_ID"

# Use hardcoded JSON file for cards to clone
CARDS_FILE="$(dirname "$0")/metabase_cards_to_clone.json"
CARD_COUNT=$(jq 'length' "$CARDS_FILE")
echo "Found $CARD_COUNT cards in $CARDS_FILE. Cloning..."

for i in $(seq 0 $(($CARD_COUNT - 1))); do
  CARD=$(jq ".[$i]" "$CARDS_FILE")
  NAME=$(echo "$CARD" | jq -r '.name')
  RESP=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "X-Metabase-Session: $SESSION_ID" -H "Content-Type: application/json" \
    -d "$CARD" "$METABASE_URL/api/card")
  if [ "$RESP" == "200" ]; then
    echo "Cloned: $NAME"
  else
    echo "Failed to clone: $NAME | Status: $RESP"
  fi
done

# Use hardcoded JSON file for dashboards to clone
DASHBOARDS_FILE="$(dirname "$0")/metabase_dashboards_to_clone_cleaned.json"
DASHBOARD_COUNT=$(jq 'length' "$DASHBOARDS_FILE")
echo "Found $DASHBOARD_COUNT dashboards in $DASHBOARDS_FILE. Cloning..."

for i in $(seq 0 $(($DASHBOARD_COUNT - 1))); do
  DASHBOARD=$(jq ".[$i]" "$DASHBOARDS_FILE")
  NAME=$(echo "$DASHBOARD" | jq -r '.name')
  RESP=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "X-Metabase-Session: $SESSION_ID" -H "Content-Type: application/json" \
    -d "$DASHBOARD" "$METABASE_URL/api/dashboard")
  if [ "$RESP" == "200" ]; then
    echo "Cloned dashboard: $NAME"
  else
    echo "Failed to clone dashboard: $NAME | Status: $RESP"
  fi
done
