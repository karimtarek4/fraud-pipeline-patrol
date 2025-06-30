import os
import json
import requests
import time
import logging

CARDS_FILE = os.path.join(os.path.dirname(__file__), '../metadata/metabase_cards.json')
DASHBOARDS_FILE = os.path.join(os.path.dirname(__file__), '../metadata/metabase_dashboard.json')

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

MB_HOSTNAME = os.environ.get('MB_HOSTNAME', 'localhost')
MB_PORT = os.environ.get('MB_PORT', '3000')
ADMIN_EMAIL = "kareem@gmail.com"
ADMIN_PASSWORD = "K@reem2025!secure"
ADMIN_FIRST_NAME = "kareem"
ADMIN_LAST_NAME = "tarek"
METABASE_URL = f"http://{MB_HOSTNAME}:{MB_PORT}"
USERNAME = ADMIN_EMAIL
PASSWORD = ADMIN_PASSWORD

def wait_for_metabase():
    """Wait until Metabase is ready to accept API requests."""
    url = f"http://{MB_HOSTNAME}:{MB_PORT}/api/session/properties"
    logger.info(f"⌚︎ Waiting for Metabase to start on {MB_HOSTNAME}:{MB_PORT}...")
    while True:
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                logger.info("Metabase is up!")
                break
        except Exception:
            pass
        time.sleep(5)

def get_session_token():
    """Authenticate as admin and return the session token."""
    resp = requests.post(
        f"{METABASE_URL}/api/session",
        json={"username": USERNAME, "password": PASSWORD}
    )
    resp.raise_for_status()
    logger.info("Authenticated and obtained session token.")
    return resp.json()["id"]

def create_admin_user():
    """Create the Metabase admin user via the setup API (if not already created)."""
    url = f"http://{MB_HOSTNAME}:{MB_PORT}/api/session/properties"
    setup_token = requests.get(url).json().get("setup-token")
    if not setup_token:
        logger.error("❌ Failed to get setup token. Setup may already be complete.")
        return False
    payload = {
        "token": setup_token,
        "user": {
            "email": ADMIN_EMAIL,
            "first_name": ADMIN_FIRST_NAME,
            "last_name": ADMIN_LAST_NAME,
            "password": ADMIN_PASSWORD
        },
        "prefs": {
            "allow_tracking": False,
            "site_name": "Metabase Instance"
        }
    }
    resp = requests.post(f"http://{MB_HOSTNAME}:{MB_PORT}/api/setup", json=payload)
    if resp.status_code != 200:
        logger.error("❌ Failed to create admin user. It may already exist or setup is already complete.")
        return False
    logger.info("😎 Created admin user.")
    return True

def get_or_create_session_token():
    """
    Try to log in as admin and get a session token. If login fails, attempt to create the admin user, then log in again.
    Returns the session token string, or None if all attempts fail.
    """
    try:
        return get_session_token()
    except Exception as e:
        logger.warning(f"Admin login failed, attempting to create admin user... {e}")
        if not create_admin_user():
            logger.error("❌ Could not create admin user.")
            return None
        try:
            return get_session_token()
        except Exception as e2:
            logger.error(f"❌ Login failed after admin creation. {e2}")
            return None

def add_actualdata_postgres(session_id):
    """Add the Actual Data Postgres database to Metabase."""
    db_payload = {
        "name": "MainDB",
        "engine": "postgres",
        "details": {
            "host": "actualdata-postgres",
            "port": 5432,
            "dbname": "actualdata",
            "user": "actualdata",
            "password": "actualdata_pass",
            "ssl": False
        },
        "is_full_sync": True,
        "is_on_demand": False,
        "schedules": {}
    }
    resp = requests.post(f"http://{MB_HOSTNAME}:{MB_PORT}/api/database", headers={"X-Metabase-Session": session_id}, json=db_payload)
    resp.raise_for_status()
    logger.info("🗄️ Added MainDB database to Metabase.")

def create_cards(session_id):
    """Create all cards from the hardcoded JSON file."""
    with open(CARDS_FILE) as f:
        cards = json.load(f)
    logger.info(f"Found {len(cards)} cards in {CARDS_FILE}. Cloning...")
    for card in cards:
        resp = requests.post(f"{METABASE_URL}/api/card", headers={"X-Metabase-Session": session_id}, json=card)
        if resp.status_code == 200:
            logger.info(f"Created: {card['name']}")
        else:
            logger.error(f"Failed to Create: {card['name']} | Status: {resp.status_code} | {resp.text}")

def create_dashboards(session_id):
    """Create all dashboards from the hardcoded JSON file."""
    with open(DASHBOARDS_FILE) as f:
        dashboards = json.load(f)
    logger.info(f"Found {len(dashboards)} dashboards in {DASHBOARDS_FILE}. Cloning...")
    for dash in dashboards:
        resp = requests.post(f"{METABASE_URL}/api/dashboard", headers={"X-Metabase-Session": session_id}, json=dash)
        if resp.status_code == 200:
            logger.info(f"Created dashboard: {dash['name']}")
        else:
            logger.error(f"Failed to Create dashboard: {dash['name']} | Status: {resp.status_code} | {resp.text}")

def main():
    logger.info("--- Metabase Initialization Script Start ---")
    wait_for_metabase()
    session_id = get_or_create_session_token()
    if not session_id:
        logger.error("❌ Could not obtain a session token. Exiting.")
        return
    logger.info(f"Authenticated as admin. Session ID: {session_id}")
    add_actualdata_postgres(session_id)
    create_cards(session_id)
    create_dashboards(session_id)
    logger.info("✅ Users, databases, cards, and dashboards created! You can now log in as admin or basic users, and the Airflow Postgres and MainDB databases are available in Metabase.")
    logger.info("--- Metabase Initialization Script End ---")

if __name__ == "__main__":
    main()
