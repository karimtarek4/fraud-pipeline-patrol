"""
Unit tests for DAG parsing and validation.

This file tests that all Airflow DAGs:
1. Parse without import errors
2. Have valid structure and configuration
3. Meet basic validation requirements
"""
import os

import pytest
from airflow.models import DagBag

DAGS_PATH = os.path.join(os.path.dirname(__file__), "../airflow/dags")


def get_dag_files():
    """Get list of DAG Python files."""
    return [
        f for f in os.listdir(DAGS_PATH) if f.endswith(".py") and not f.startswith("__")
    ]


def get_dag_ids():
    """Get list of DAG IDs from DagBag."""
    return [
        dag_id
        for dag_id in DagBag(dag_folder=DAGS_PATH, include_examples=False).dags.keys()
    ]


@pytest.fixture(scope="module")
def dagbag():
    """Create DagBag fixture for testing."""
    return DagBag(dag_folder=DAGS_PATH, include_examples=False)


def test_no_import_errors(dagbag):
    """Test that DAGs import without errors."""
    assert dagbag.import_errors == {}, f"Import errors: {dagbag.import_errors}"


@pytest.mark.parametrize("dag_file", get_dag_files())
def test_dag_registered(dagbag, dag_file):
    """Test that DAG file is properly registered in DagBag."""
    dag_id = dag_file.replace(".py", "")
    assert dag_id in dagbag.dags, f"DAG '{dag_id}' not found in dagbag"


@pytest.mark.parametrize("dag_id", get_dag_ids())
def test_dag_has_tasks(dagbag, dag_id):
    """Test that DAG has at least one task."""
    dag = dagbag.dags[dag_id]
    assert len(dag.tasks) > 0, f"DAG '{dag_id}' has no tasks"


@pytest.mark.parametrize("dag_id", get_dag_ids())
def test_dag_catchup_false(dagbag, dag_id):
    """Test that DAG has catchup set to False."""
    dag = dagbag.dags[dag_id]
    assert hasattr(dag, "catchup"), f"DAG '{dag_id}' missing 'catchup' attribute"
    assert dag.catchup is False, f"DAG '{dag_id}' should have catchup=False"


@pytest.mark.parametrize("dag_id", get_dag_ids())
def test_dag_no_cycles(dagbag, dag_id):
    """Test that DAG has no circular dependencies."""
    dag = dagbag.dags[dag_id]
    try:
        dag.topological_sort()
    except Exception as e:
        pytest.fail(f"DAG '{dag_id}' has a cycle: {e}")
