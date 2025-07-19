"""
Unit tests for generate_synthetic_fraud_data.py script.

This file tests the data generation functions to ensure they:
1. Create the expected number of records
2. Generate fields within valid ranges and with proper data types
3. Apply fraud logic correctly
4. Write files to correct paths with proper content

Developer Notes:
- Uses unittest.mock to avoid actual file I/O during testing
- Tests are isolated using fixtures and mocks
- Each test verifies specific data generation logic or file operations
- Uses pandas testing utilities for DataFrame comparisons
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import the functions we want to test
sys.path.append(str(Path(__file__).parent.parent))
from scripts.generate_synthetic_fraud_data import (  # noqa: E402
    ensure_dirs,
    generate_customers,
    generate_login_attempts,
    generate_merchants,
    generate_transactions,
    main,
)


class TestDataGenerationLogic:
    """Test the core data generation functions for correctness and validity."""

    def test_generate_customers_record_count(self):
        """Test that generate_customers creates the expected number of records."""
        # Test with default parameters
        customers = generate_customers(start_id=1001, num_customers=100)
        assert len(customers) == 100, f"Expected 100 customers, got {len(customers)}"

        # Test with different parameters
        customers = generate_customers(start_id=5000, num_customers=50)
        assert len(customers) == 50, f"Expected 50 customers, got {len(customers)}"

    def test_generate_customers_field_validity(self):
        """Test that customer fields are within valid ranges and have correct types."""
        customers = generate_customers(start_id=2000, num_customers=10)

        # Test CustomerID sequence
        expected_ids = list(range(2000, 2010))
        actual_ids = customers["CustomerID"].tolist()
        assert (
            actual_ids == expected_ids
        ), f"CustomerID sequence incorrect: {actual_ids}"

        # Test Age range (business requirement: 18-65)
        ages = customers["Age"]
        assert ages.min() >= 18, f"Minimum age {ages.min()} below 18"
        assert ages.max() <= 65, f"Maximum age {ages.max()} above 65"
        assert ages.dtype == "int64", f"Age should be int64, got {ages.dtype}"

        # Test AvgTransactionAmount range (business requirement: 50-200)
        avg_amounts = customers["AvgTransactionAmount"]
        assert (
            avg_amounts.min() >= 50
        ), f"Min transaction amount {avg_amounts.min()} below 50"
        assert (
            avg_amounts.max() <= 200
        ), f"Max transaction amount {avg_amounts.max()} above 200"

        # Test PastFraudCount values (should only be 0, 1, or 2)
        fraud_counts = customers["PastFraudCount"].unique()
        valid_counts = {0, 1, 2}
        assert set(fraud_counts).issubset(
            valid_counts
        ), f"Invalid fraud counts: {fraud_counts}"

        # Test geographic coordinates (business requirement: reasonable US coordinates)
        lats = customers["HomeLat"]
        lons = customers["HomeLon"]
        assert (
            lats.min() >= 30.0 and lats.max() <= 45.0
        ), f"Latitude out of range: {lats.min()}-{lats.max()}"
        assert (
            lons.min() >= -100.0 and lons.max() <= -70.0
        ), f"Longitude out of range: {lons.min()}-{lons.max()}"

        # Test required fields exist
        required_fields = [
            "CustomerID",
            "Age",
            "HomeDevice",
            "HomeIP",
            "ingestion_date",
        ]
        for field in required_fields:
            assert field in customers.columns, f"Missing required field: {field}"
            assert customers[field].notna().all(), f"Field {field} contains null values"

    def test_generate_merchants_logic(self):
        """Test merchant generation logic and risk score mapping."""
        merchants = generate_merchants(start_id=3000, num_merchants=20)

        # Test record count
        assert len(merchants) == 20, f"Expected 20 merchants, got {len(merchants)}"

        # Test risk score mapping logic
        risk_map = {
            "Groceries": 0.1,
            "Retail": 0.2,
            "Travel": 0.15,
            "Online": 0.25,
            "Gambling": 0.8,
            "Crypto": 0.7,
        }

        for _, merchant in merchants.iterrows():
            category = merchant["Category"]
            risk_score = merchant["MerchantRiskScore"]
            expected_risk = risk_map[category]
            assert (
                risk_score == expected_risk
            ), f"Merchant {merchant['MerchantID']}: category {category} should have risk {expected_risk}, got {risk_score}"

        # Test that all categories are valid
        valid_categories = set(risk_map.keys())
        actual_categories = set(merchants["Category"].unique())
        assert actual_categories.issubset(
            valid_categories
        ), f"Invalid categories found: {actual_categories - valid_categories}"

    def test_generate_transactions_customer_relationship(self):
        """Test that transactions are properly linked to customers and respect customer baselines."""
        # Create small test datasets
        customers = generate_customers(start_id=1000, num_customers=3)
        merchants = generate_merchants(start_id=2000, num_merchants=2)

        # Generate transactions with low average to reduce variability in tests
        transactions = generate_transactions(customers, merchants, avg_txs_per_cust=2.0)

        # Test that all customer IDs in transactions exist in customers
        customer_ids = set(customers["CustomerID"])
        transaction_customer_ids = set(transactions["CustomerID"])
        assert transaction_customer_ids.issubset(
            customer_ids
        ), f"Transaction customer IDs not found in customers: {transaction_customer_ids - customer_ids}"


class TestFileOperations:
    """Test file writing operations and directory creation."""

    @patch("os.makedirs")
    def test_ensure_dirs_creation(self, mock_makedirs):
        """Test that ensure_dirs creates directories correctly."""
        test_dirs = ["/test/dir1", "/test/dir2", "/test/dir3"]
        ensure_dirs(test_dirs)

        # Verify os.makedirs was called for each directory with exist_ok=True
        assert (
            mock_makedirs.call_count == 3
        ), f"Expected 3 calls to makedirs, got {mock_makedirs.call_count}"

        for test_dir in test_dirs:
            mock_makedirs.assert_any_call(test_dir, exist_ok=True)

    @patch("pandas.DataFrame.to_parquet")
    @patch("scripts.generate_synthetic_fraud_data.ensure_dirs")
    @patch("pathlib.Path.resolve")
    def test_main_file_writing(self, mock_resolve, mock_ensure_dirs, mock_to_parquet):
        """Test that main() writes all expected files to correct paths."""
        # Mock the path resolution to return a known test path
        mock_path = MagicMock()
        mock_path.parent.parent = Path("/test/project")
        mock_resolve.return_value = mock_path

        # Call the main function
        main()

        # Verify ensure_dirs was called
        mock_ensure_dirs.assert_called_once()

        # Verify that to_parquet was called 4 times (for each data type)
        assert (
            mock_to_parquet.call_count == 4
        ), f"Expected 4 calls to to_parquet, got {mock_to_parquet.call_count}"

        # Check that the correct file paths were used
        call_args = [call[0][0] for call in mock_to_parquet.call_args_list]
        expected_files = [
            "/test/project/data/raw/customers.parquet",
            "/test/project/data/raw/merchants.parquet",
            "/test/project/data/raw/transactions.parquet",
            "/test/project/data/raw/login_attempts.parquet",
        ]

        for expected_file in expected_files:
            assert any(
                expected_file in call_arg for call_arg in call_args
            ), f"Expected file {expected_file} not found in calls: {call_args}"


class TestDataIntegrity:
    """Test data consistency and integrity across related tables."""

    def test_data_relationship_integrity(self):
        """Test that generated data maintains referential integrity."""
        # Generate complete dataset
        customers = generate_customers(start_id=1000, num_customers=5)
        merchants = generate_merchants(start_id=2000, num_merchants=3)
        transactions = generate_transactions(customers, merchants, avg_txs_per_cust=2.0)
        login_attempts = generate_login_attempts(transactions)

        # Test customer-transaction relationships
        customer_ids_customers = set(customers["CustomerID"])
        customer_ids_transactions = set(transactions["CustomerID"])
        assert customer_ids_transactions.issubset(
            customer_ids_customers
        ), "All transaction customer IDs must exist in customers table"

        # Test merchant-transaction relationships
        merchant_ids_merchants = set(merchants["MerchantID"])
        merchant_ids_transactions = set(transactions["MerchantID"])
        assert merchant_ids_transactions.issubset(
            merchant_ids_merchants
        ), "All transaction merchant IDs must exist in merchants table"

        # Test customer-login relationships
        customer_ids_logins = set(login_attempts["CustomerID"])
        assert customer_ids_logins.issubset(
            customer_ids_customers
        ), "All login attempt customer IDs must exist in customers table"

        # Test data type consistency for CustomerID across tables
        assert (
            customers["CustomerID"].dtype == transactions["CustomerID"].dtype
        ), "CustomerID data type should be consistent between customers and transactions"
        assert (
            customers["CustomerID"].dtype == login_attempts["CustomerID"].dtype
        ), "CustomerID data type should be consistent between customers and login_attempts"

        # Test that ingestion_date is consistent across all tables
        ingestion_dates = [
            customers["ingestion_date"].iloc[0],
            merchants["ingestion_date"].iloc[0],
            transactions["ingestion_date"].iloc[0],
            login_attempts["ingestion_date"].iloc[0],
        ]

        # All ingestion dates should be very close (within a few seconds)
        for i in range(1, len(ingestion_dates)):
            time_diff = abs((ingestion_dates[i] - ingestion_dates[0]).total_seconds())
            assert (
                time_diff < 10
            ), f"Ingestion dates should be close, but differ by {time_diff} seconds"


if __name__ == "__main__":
    # Run the tests when this file is executed directly
    pytest.main([__file__, "-v"])
