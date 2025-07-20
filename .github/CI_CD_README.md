# CI/CD Documentation

## Overview

This project uses GitHub Actions for Continuous Integration (CI) with comprehensive testing, code quality checks, and security scanning.

## Workflows

### 1. CI Workflow (`.github/workflows/ci.yml`)

Triggered on:
- Push to `main` or `feat/*` branches
- Pull requests to `main` 
- Manual dispatch

**Jobs:**

#### Test Suite
- Runs all Python tests using the custom test runner

#### Airflow DAG Validation
- Validates all Airflow DAG syntax
- Checks for import errors
- Ensures DAGs can be parsed correctly

#### dbt Model Validation
- Validates dbt project configuration
- Runs `dbt debug`, `dbt parse`, and `dbt compile`
- Ensures data quality for all 

#### Code Quality Checks
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting and style checks

#### Security Scan
- **Bandit**: Security vulnerability scanning
- **Safety**: Known vulnerability checks in dependencies
- Uploads security reports as artifacts

#### Docker Build Test
- Tests Docker image build process
- Validates the container can run Python

### 2. Pre-commit Workflow (`.github/workflows/pre-commit.yml`)

Runs pre-commit hooks on push/PR to ensure code quality.

## Configuration Files

### `.pre-commit-config.yaml`
Pre-commit hooks for local development:
- Code formatting (Black, isort)
- Linting (flake8, mypy)
- Security scanning (Bandit)
- Basic file checks

### `pyproject.toml`
Tool configurations for:
- Black code formatter
- isort import sorter
- pytest test runner
- mypy type checker

### Environment Variables

The CI pipeline uses these environment variables:
- `PYTHONPATH`: Set to workspace root
- `POSTGRES_*`: Database connection details for tests
- `AIRFLOW_HOME`: Airflow configuration directory