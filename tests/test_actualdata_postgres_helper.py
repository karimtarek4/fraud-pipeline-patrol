"""
Unit tests for the actualdata_postgres.py helper module.

This file tests the get_actualdata_postgres_conn() function to ensure it:
1. Connects to actualdata-postgres with correct default parameters
2. Uses custom environment variables when provided
3. Properly handles connection errors

Developer Notes:
- Uses unittest.mock to avoid real database connections during testing
- Tests are isolated using fixtures to manage environment variables
- Each test verifies different scenarios (defaults, custom params, errors)
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from helpers.actualdata_postgres import get_actualdata_postgres_conn


@pytest.fixture
def mock_env_vars():
    """Fixture to safely manage environment variables during testing."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


def test_get_actualdata_postgres_conn_default_params(mock_env_vars):
    """Test get_actualdata_postgres_conn with default parameters."""
    # Remove any environment variables that could affect defaults
    for var in [
        "ACTUALDATA_POSTGRES_HOST",
        "ACTUALDATA_POSTGRES_PORT",
        "ACTUALDATA_POSTGRES_USER",
        "ACTUALDATA_POSTGRES_PASSWORD",
        "ACTUALDATA_POSTGRES_DB",
    ]:
        os.environ.pop(var, None)

    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        conn = get_actualdata_postgres_conn()

        mock_connect.assert_called_once_with(
            host="actualdata-postgres",
            port="5432",
            user="actualdata",
            password="actualdata_pass",
            dbname="actualdata",
        )
        assert conn == mock_conn


def test_get_actualdata_postgres_conn_custom_params(mock_env_vars):
    """Test get_actualdata_postgres_conn with custom environment variables."""
    os.environ["ACTUALDATA_POSTGRES_HOST"] = "custom-host"
    os.environ["ACTUALDATA_POSTGRES_PORT"] = "5439"
    os.environ["ACTUALDATA_POSTGRES_USER"] = "custom-user"
    os.environ["ACTUALDATA_POSTGRES_PASSWORD"] = "custom-password"
    os.environ["ACTUALDATA_POSTGRES_DB"] = "custom-db"

    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        conn = get_actualdata_postgres_conn()

        mock_connect.assert_called_once_with(
            host="custom-host",
            port="5439",
            user="custom-user",
            password="custom-password",
            dbname="custom-db",
        )
        assert conn == mock_conn


def test_get_actualdata_postgres_conn_connection_error():
    """Test that connection errors are properly propagated."""
    with patch("psycopg2.connect") as mock_connect:
        mock_connect.side_effect = Exception("Test connection error")

        with pytest.raises(Exception) as excinfo:
            get_actualdata_postgres_conn()

        assert "Test connection error" in str(excinfo.value)
