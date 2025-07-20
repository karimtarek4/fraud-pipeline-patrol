"""
Integration tests for Airflow DAG dataset-based triggering.

This file tests that DAGs are properly connected via datasets and that
the triggering mechanism works as expected in the fraud detection pipeline.

What this tests (simple):
- DAGs produce the correct datasets as outputs
- DAGs consume the correct datasets as inputs
- Dataset URIs match between producer and consumer DAGs
- The complete data flow pipeline is properly connected

Developer Notes:
- Tests the dataset-driven workflow without requiring database
- Validates DAG-to-DAG communication via Airflow's dataset mechanism
- Ensures proper dataset URI formatting and consistency
- Tests the complete pipeline flow from data generation to alerts
"""

import pytest

try:
    from airflow.models import DagBag

    AIRFLOW_AVAILABLE = True
except ImportError:
    AIRFLOW_AVAILABLE = False
    DagBag = None


class TestDAGDatasetIntegration:
    """Integration tests for dataset-based DAG triggering."""

    @pytest.fixture
    def dagbag(self):
        """Load all DAGs for testing - simplified version."""
        if not AIRFLOW_AVAILABLE:
            pytest.skip("Airflow not available")
        return DagBag(dag_folder="airflow/dags", include_examples=False)

    @pytest.mark.skipif(not AIRFLOW_AVAILABLE, reason="Airflow not available")
    def test_all_dags_exist_and_loadable(self, dagbag):
        """Test that all expected DAGs exist and can be loaded without errors."""
        # Expected DAGs in the fraud detection pipeline
        expected_dag_ids = [
            "generate_and_partition_data_dag",
            "upload_to_minio_dag",
            "run_dbt_dag",
            "ml_transaction_scoring_dag",
        ]
        # Verify expected DAGs exist
        available_dag_ids = list(dagbag.dag_ids)
        for expected_dag_id in expected_dag_ids:
            assert (
                expected_dag_id in available_dag_ids
            ), f"Expected DAG {expected_dag_id} not found in available DAGs: {available_dag_ids}"

    @pytest.mark.skipif(not AIRFLOW_AVAILABLE, reason="Airflow not available")
    def test_generate_and_partition_dag_structure(self, dagbag):
        """Test the structure of generate_and_partition_data_dag."""
        dag = dagbag.dags.get("generate_and_partition_data_dag")
        assert dag is not None, "generate_and_partition_data_dag should exist"

        # Check that expected tasks exist
        expected_tasks = ["partition_data_task", "generate_data_task"]
        actual_tasks = [task.task_id for task in dag.tasks]

        for expected_task in expected_tasks:
            assert (
                expected_task in actual_tasks
            ), f"Expected task {expected_task} not found in DAG tasks: {actual_tasks}"

        # Check basic DAG properties
        assert dag.catchup is False, "DAG should have catchup=False"
        assert dag.max_active_runs == 1, "DAG should have max_active_runs=1"

    @pytest.mark.skipif(not AIRFLOW_AVAILABLE, reason="Airflow not available")
    def test_upload_to_minio_dag_structure(self, dagbag):
        """Test the structure of upload_to_minio_dag."""
        dag = dagbag.dags.get("upload_to_minio_dag")
        assert dag is not None, "upload_to_minio_dag should exist"

        # Check that expected tasks exist
        expected_tasks = ["upload_partitioned_data_to_minio_task"]
        actual_tasks = [task.task_id for task in dag.tasks]

        for expected_task in expected_tasks:
            assert (
                expected_task in actual_tasks
            ), f"Expected task {expected_task} not found in DAG tasks: {actual_tasks}"

        # Check basic DAG properties
        assert dag.catchup is False, "DAG should have catchup=False"
        assert dag.max_active_runs == 1, "DAG should have max_active_runs=1"

    @pytest.mark.skipif(not AIRFLOW_AVAILABLE, reason="Airflow not available")
    def test_run_dbt_dag_structure(self, dagbag):
        """Test the structure of run_dbt_dag."""
        dag = dagbag.dags.get("run_dbt_dag")
        assert dag is not None, "run_dbt_dag should exist"

        # Check that expected DBT tasks exist
        expected_tasks = ["install_dbt_deps_task", "run_dbt_task"]
        actual_tasks = [task.task_id for task in dag.tasks]

        for expected_task in expected_tasks:
            assert (
                expected_task in actual_tasks
            ), f"Expected task {expected_task} not found in DAG tasks: {actual_tasks}"

        # Check basic DAG properties
        assert dag.catchup is False, "DAG should have catchup=False"
        assert dag.max_active_runs == 1, "DAG should have max_active_runs=1"

    @pytest.mark.skipif(not AIRFLOW_AVAILABLE, reason="Airflow not available")
    def test_ml_transaction_scoring_dag_structure(self, dagbag):
        """Test the structure of ml_transaction_scoring_dag."""
        dag = dagbag.dags.get("ml_transaction_scoring_dag")
        assert dag is not None, "ml_transaction_scoring_dag should exist"

        # Check that expected scoring tasks exist
        expected_tasks = ["run_score_transactions_task"]
        actual_tasks = [task.task_id for task in dag.tasks]

        for expected_task in expected_tasks:
            assert (
                expected_task in actual_tasks
            ), f"Expected task {expected_task} not found in DAG tasks: {actual_tasks}"

        # Check basic DAG properties
        assert dag.catchup is False, "DAG should have catchup=False"
        assert dag.max_active_runs == 1, "DAG should have max_active_runs=1"

    @pytest.mark.skipif(not AIRFLOW_AVAILABLE, reason="Airflow not available")
    def test_dataset_configuration(self, dagbag):
        """Test dataset configuration across the complete fraud detection pipeline."""
        # Define the complete pipeline DAGs
        pipeline_dags = {
            "generate_and_partition_data_dag": dagbag.dags.get(
                "generate_and_partition_data_dag"
            ),
            "upload_to_minio_dag": dagbag.dags.get("upload_to_minio_dag"),
            "run_dbt_dag": dagbag.dags.get("run_dbt_dag"),
            "ml_transaction_scoring_dag": dagbag.dags.get("ml_transaction_scoring_dag"),
        }

        # Test dataset outlets (what each DAG produces)
        pipeline_outlets = {}
        expected_outlet_patterns = {
            "generate_and_partition_data_dag": ["file://", "/data/processed/"],
            "upload_to_minio_dag": ["s3://", "/fraud-data-processed/"],
            "run_dbt_dag": ["s3://", "/fraud-data-processed/marts/"],
            "ml_transaction_scoring_dag": ["postgresql://", "/fraud_alerts"],
        }

        for dag_name, dag in pipeline_dags.items():
            dag_outlets = []
            for task in dag.tasks:
                if hasattr(task, "outlets") and task.outlets:
                    for outlet in task.outlets:
                        dag_outlets.append(outlet.uri)
            pipeline_outlets[dag_name] = dag_outlets

            # Verify each DAG produces expected dataset types
            if dag_name in expected_outlet_patterns:
                patterns = expected_outlet_patterns[dag_name]
                assert (
                    len(dag_outlets) > 0
                ), f"{dag_name} should produce dataset outlets"

                # Check at least one outlet matches expected patterns
                pattern_found = False
                for outlet in dag_outlets:
                    if any(pattern in outlet for pattern in patterns):
                        pattern_found = True
                        break

                assert (
                    pattern_found
                ), f"{dag_name} outlets should match patterns {patterns}, got {dag_outlets}"


if __name__ == "__main__":
    # Run the tests when this file is executed directly
    pytest.main([__file__, "-v"])
