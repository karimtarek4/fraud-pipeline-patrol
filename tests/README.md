# Tests Documentation

This directory contains all tests for the Fraud Pipeline Patrol project. The test suite covers unit tests, script tests, and DAG validation tests to ensure the reliability and correctness of the fraud detection pipeline.

## 📋 Test Overview

| Test File | Type | Tests Count | Description |
|-----------|------|-------------|-------------|
| `test_postgres_helper.py` | Unit | 3 | Tests PostgreSQL connection helper functions |
| `test_actualdata_postgres_helper.py` | Unit | 3 | Tests ActualData PostgreSQL connection helper functions |
| `test_generate_synthetic_fraud_data.py` | Script | 7 | Tests synthetic fraud data generation logic |
| `test_dag_parsing_and_validation.py` | DAG | 25 | Tests Airflow DAG parsing and validation |
| `test_dag_structure_and_datasets.py` | DAG | 6 | Tests DAG structure and dataset configurations |

## 🧪 Test Categories

### Unit Tests
Tests for helper functions and utility modules that provide database connections and other core functionality.

### Script Tests
Tests for data generation and processing scripts that create synthetic fraud data and handle file operations.

### DAG Tests
Tests for Airflow DAG parsing, validation, structure, and dataset flow configurations in the fraud detection pipeline.


### Environment Setup:
```bash
# Install basic test dependencies
pip install pytest pandas psycopg2-binary

# For DAG tests, install Airflow
pip install apache-airflow
```


## 🚀 How to Run Tests

Use the provided test runner script that automatically detects the correct pytest environment:

```bash
# Run all tests with summary
python run_all_tests.py

# Run all tests verbosely
python run_all_tests.py -v

# Run all tests quietly
python run_all_tests.py -q

```
