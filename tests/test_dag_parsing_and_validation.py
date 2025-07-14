import os
import pytest
from airflow.models import DagBag

DAGS_PATH = os.path.join(os.path.dirname(__file__), "../airflow/dags")

def get_dag_files():
    return [f for f in os.listdir(DAGS_PATH) if f.endswith(".py") and not f.startswith("__")]

def get_dag_ids():
    return [dag_id for dag_id in DagBag(dag_folder=DAGS_PATH, include_examples=False).dags.keys()]

@pytest.fixture(scope="module")
def dagbag():
    return DagBag(dag_folder=DAGS_PATH, include_examples=False)

def test_no_import_errors(dagbag):
    assert dagbag.import_errors == {}, f"Import errors: {dagbag.import_errors}"

@pytest.mark.parametrize("dag_file", get_dag_files())
def test_dag_registered(dagbag, dag_file):
    dag_id = dag_file.replace(".py", "")
    assert dag_id in dagbag.dags, f"DAG '{dag_id}' not found in dagbag"


@pytest.mark.parametrize("dag_id", get_dag_ids())
def test_dag_has_tasks(dagbag, dag_id):
    dag = dagbag.dags[dag_id]
    assert len(dag.tasks) > 0, f"DAG '{dag_id}' has no tasks"


@pytest.mark.parametrize("dag_id", get_dag_ids())
def test_dag_catchup_false(dagbag, dag_id):
    dag = dagbag.dags[dag_id]
    assert hasattr(dag, 'catchup'), f"DAG '{dag_id}' missing 'catchup' attribute"
    assert dag.catchup is False, f"DAG '{dag_id}' should have catchup=False"


@pytest.mark.parametrize("dag_id", get_dag_ids())
def test_dag_no_cycles(dagbag, dag_id):
    dag = dagbag.dags[dag_id]
    try:
        dag.topological_sort()
    except Exception as e:
        pytest.fail(f"DAG '{dag_id}' has a cycle: {e}")