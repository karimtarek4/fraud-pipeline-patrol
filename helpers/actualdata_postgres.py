"""
PostgreSQL connection helper for actual data service.

Provides connection utilities for the actualdata-postgres service
used in the fraud detection pipeline.
"""
import os

import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file (if not already loaded)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))


def get_actualdata_postgres_conn():
    """Connect to the actualdata-postgres service using environment credentials."""
    host = os.environ.get("ACTUALDATA_POSTGRES_HOST", "actualdata-postgres")
    port = os.environ.get("ACTUALDATA_POSTGRES_PORT", "5432")
    user = os.environ.get("ACTUALDATA_POSTGRES_USER", "actualdata")
    password = os.environ.get("ACTUALDATA_POSTGRES_PASSWORD", "actualdata_pass")
    db = os.environ.get("ACTUALDATA_POSTGRES_DB", "actualdata")
    return psycopg2.connect(
        host=host, port=port, user=user, password=password, dbname=db
    )
