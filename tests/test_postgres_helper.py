"""
Unit tests for the postgres.py helper module.

This file tests the get_postgres_conn() function to ensure it:
1. Connects to PostgreSQL with correct default parameters
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

from helpers.postgres import get_postgres_conn


@pytest.fixture
def mock_env_vars():
    """Fixture to safely manage environment variables during testing."""
    original_env = os.environ.copy()  # Save current environment
    yield  # Let the test run
    # Cleanup: restore original environment variables
    os.environ.clear()
    os.environ.update(original_env)


def test_get_postgres_conn_default_params(mock_env_vars):
    """Test get_postgres_conn with default parameters."""
    # Clear any existing environment variables that might affect the test
    for key in [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
    ]:
        os.environ.pop(key, None)

    with patch("psycopg2.connect") as mock_connect:
        # Create a fake connection object that our mock will return
        mock_conn = MagicMock()

        # Set the mock to return our fake connection when called
        mock_connect.return_value = mock_conn

        # Call the function we're testing
        conn = get_postgres_conn()

        # Verify psycopg2.connect was called with the expected default parameters
        # These should match the defaults defined in helpers/postgres.py
        mock_connect.assert_called_once_with(
            host="localhost",  # Default from code
            port="5432",
            user="airflow",  # Default from code
            password="airflow",  # Default from code
            dbname="airflow",  # Default from code
        )

        # Make sure our function returns the mocked connection
        assert conn == mock_conn


def test_get_postgres_conn_custom_params(mock_env_vars):
    """Test get_postgres_conn with custom environment variables."""
    # Set custom environment variables to test different connection parameters
    os.environ["POSTGRES_HOST"] = "test-host"  # Custom database server
    os.environ["POSTGRES_PORT"] = "5433"  # Custom port (not default 5432)
    os.environ["POSTGRES_USER"] = "test-user"  # Custom username
    os.environ["POSTGRES_PASSWORD"] = "test-password"  # Custom password
    os.environ["POSTGRES_DB"] = "test-db"  # Custom database name

    with patch("psycopg2.connect") as mock_connect:
        # Create a fake connection object
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        # Call the function - it should now use our custom environment variables
        conn = get_postgres_conn()

        # Verify psycopg2.connect was called with our custom parameters
        # (not the defaults from the previous test)
        mock_connect.assert_called_once_with(
            host="test-host",
            port="5433",
            user="test-user",
            password="test-password",
            dbname="test-db",
        )

        # Verify the function returns the mocked connection
        assert conn == mock_conn


def test_get_postgres_conn_connection_error():
    """Test that connection errors are properly propagated."""
    with patch("psycopg2.connect") as mock_connect:
        # Make the mock connection raise an exception instead of connecting
        mock_connect.side_effect = Exception("Test connection error")

        # Verify that calling our function raises the expected exception
        with pytest.raises(Exception) as excinfo:
            get_postgres_conn()

        # Check that the error message is what we expect
        # This helps ensure the exception is properly propagated
        assert "Test connection error" in str(excinfo.value)
