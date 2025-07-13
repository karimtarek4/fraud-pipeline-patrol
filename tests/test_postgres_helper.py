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
import pytest
from unittest.mock import patch, MagicMock
from helpers.postgres import get_postgres_conn

@pytest.fixture
def mock_env_vars():
    """
    Fixture to safely manage environment variables during testing.
    
    What it does (simple):
    - Saves current environment variables before each test
    - Restores them after each test finishes
    - This prevents tests from affecting each other
    
    Developer Notes:
    - Uses copy() to create a snapshot of current env vars
    - yield allows test to run, then cleanup code executes
    - Ensures test isolation by restoring original state
    """
    original_env = os.environ.copy()  # Save current environment
    yield  # Let the test run
    # Cleanup: restore original environment variables
    os.environ.clear()
    os.environ.update(original_env)

def test_get_postgres_conn_default_params(mock_env_vars):
    """
    Test get_postgres_conn with default parameters.
    
    What this test does (simple):
    - Calls the postgres connection function without any custom settings
    - Checks that it tries to connect with the expected default values
    - Makes sure it returns a connection object
    
    Developer Notes:
    - Uses @patch to mock psycopg2.connect, preventing real DB connections
    - MagicMock creates a fake connection object for testing
    - assert_called_once_with() verifies the function was called with exact parameters
    - Tests the "happy path" scenario with default configuration
    """
    with patch('psycopg2.connect') as mock_connect:
        # Create a fake connection object that our mock will return
        mock_conn = MagicMock()

        # Set the mock to return our fake connection when called
        mock_connect.return_value = mock_conn
        
        # Call the function we're testing
        conn = get_postgres_conn()
        
        # Verify psycopg2.connect was called with the expected default parameters
        # These should match the defaults defined in helpers/postgres.py
        mock_connect.assert_called_once_with(
            host="postgres",        # Default PostgreSQL host (from actual implementation)
            port="5432",           # Default PostgreSQL port
            user="airflow",        # Default username
            password="airflow",    # Default password
            dbname="airflow"       # Default database name (psycopg2 uses 'dbname', not 'database')
        )
        
        # Make sure our function returns the mocked connection
        assert conn == mock_conn

def test_get_postgres_conn_custom_params(mock_env_vars):
    """
    Test get_postgres_conn with custom environment variables.
    
    What this test does (simple):
    - Sets custom database connection settings using environment variables
    - Calls the postgres connection function
    - Checks that it uses our custom settings instead of defaults
    
    Developer Notes:
    - Simulates a production environment where DB settings come from env vars
    - Tests that the function correctly reads from os.environ
    - Verifies all custom parameters are passed through to psycopg2.connect
    - Uses mock_env_vars fixture to ensure cleanup after test
    """
    # Set custom environment variables to test different connection parameters
    os.environ["POSTGRES_HOST"] = "test-host"       # Custom database server
    os.environ["POSTGRES_PORT"] = "5433"            # Custom port (not default 5432)
    os.environ["POSTGRES_USER"] = "test-user"       # Custom username
    os.environ["POSTGRES_PASSWORD"] = "test-password"  # Custom password
    os.environ["POSTGRES_DB"] = "test-db"           # Custom database name
    
    with patch('psycopg2.connect') as mock_connect:
        # Create a fake connection object
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        # Call the function - it should now use our custom environment variables
        conn = get_postgres_conn()
        
        # Verify psycopg2.connect was called with our custom parameters
        # (not the defaults from the previous test)
        mock_connect.assert_called_once_with(
            host="test-host",        # Should use our custom host
            port="5433",            # Should use our custom port
            user="test-user",       # Should use our custom user
            password="test-password", # Should use our custom password
            dbname="test-db"        # Should use our custom database (psycopg2 uses 'dbname')
        )
        
        # Verify the function returns the mocked connection
        assert conn == mock_conn

def test_get_postgres_conn_connection_error():
    """
    Test that connection errors are properly propagated.
    
    What this test does (simple):
    - Simulates a database connection failure
    - Calls the postgres connection function
    - Checks that the error is properly passed up to the caller
    
    Developer Notes:
    - Uses side_effect to make the mock raise an exception instead of returning a value
    - Tests error handling and exception propagation
    - Ensures that database connection failures don't get swallowed silently
    - Uses pytest.raises() context manager to assert an exception occurs
    - This is important for debugging production issues
    """
    with patch('psycopg2.connect') as mock_connect:
        # Make the mock connection raise an exception instead of connecting
        mock_connect.side_effect = Exception("Test connection error")
        
        # Verify that calling our function raises the expected exception
        with pytest.raises(Exception) as excinfo:
            get_postgres_conn()
        
        # Check that the error message is what we expect
        # This helps ensure the exception is properly propagated
        assert "Test connection error" in str(excinfo.value)
