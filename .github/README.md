# CI/CD Documentation

## Overview

This project uses GitHub Actions for Continuous Integration (CI) with comprehensive testing, code quality checks, and security scanning.

## Workflows

### 1. CI Workflow (`.github/workflows/ci.yml`)

Triggered on:
- Push to `main`, `develop`, or `feat/*` branches
- Pull requests to `main` or `develop`
- Manual dispatch

**Jobs:**

#### Test Suite
- Runs all Python tests using the custom test runner
- Sets up PostgreSQL service for database tests
- Creates test data directories
- Uploads test results as artifacts

#### Airflow DAG Validation
- Validates all Airflow DAG syntax
- Checks for import errors
- Ensures DAGs can be parsed correctly

#### dbt Model Validation
- Validates dbt project configuration
- Runs `dbt debug`, `dbt parse`, and `dbt compile`
- Ensures all models are syntactically correct

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

### `.flake8`
Flake8 linting configuration with Black compatibility.

### `.github/dependabot.yml`
Automated dependency updates for:
- Python packages
- Docker images
- GitHub Actions

## Local Development

### Install Pre-commit Hooks
```bash
pip install pre-commit
pre-commit install
```

### Run Code Quality Checks
```bash
# Format code
black .
isort .

# Lint code
flake8 .
mypy .

# Security scan
bandit -r .
safety check
```

### Run Tests
```bash
# Run all tests
python run_all_tests.py --verbose

# Run specific test
PYTHONPATH=. pytest tests/test_specific.py -v
```

## CI Status Badges

Add these to your main README.md:

```markdown
[![CI](https://github.com/karimtarek4/fraud-pipeline-patrol/actions/workflows/ci.yml/badge.svg)](https://github.com/karimtarek4/fraud-pipeline-patrol/actions/workflows/ci.yml)
[![Pre-commit](https://github.com/karimtarek4/fraud-pipeline-patrol/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/karimtarek4/fraud-pipeline-patrol/actions/workflows/pre-commit.yml)
```

## Troubleshooting

### Common Issues

1. **Test failures**: Check test logs in GitHub Actions artifacts
2. **DAG validation errors**: Ensure all Airflow dependencies are installed
3. **dbt compilation errors**: Verify dbt project configuration
4. **Code quality failures**: Run pre-commit hooks locally before pushing

### Environment Variables

The CI pipeline uses these environment variables:
- `PYTHONPATH`: Set to workspace root
- `POSTGRES_*`: Database connection details for tests
- `AIRFLOW_HOME`: Airflow configuration directory

### Debugging CI

1. Check the Actions tab in your GitHub repository
2. Review job logs for specific error messages
3. Download artifacts for detailed test results
4. Run commands locally to reproduce issues
