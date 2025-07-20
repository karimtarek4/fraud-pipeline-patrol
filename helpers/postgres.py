"""
PostgreSQL connection helper for main database service.

Provides connection utilities for the main PostgreSQL database
used in the fraud detection pipeline.
"""
import os

import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file (if not already loaded)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))


def get_postgres_conn():
    """Connect to the Postgres service using environment credentials."""
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    user = os.environ.get("POSTGRES_USER", "airflow")
    password = os.environ.get("POSTGRES_PASSWORD", "airflow")
    db = os.environ.get("POSTGRES_DB", "airflow")
    return psycopg2.connect(
        host=host, port=port, user=user, password=password, dbname=db
    )
