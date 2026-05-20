# Import json module for JSON serialization/deserialization
import json
# Import tempfile module for creating temporary files/directories
import tempfile
# Import Path class from pathlib for object-oriented filesystem paths
from pathlib import Path

# Import pytest framework for test fixtures and assertions
import pytest

# Import PolyBenchOutput and PolyBenchRetrievalMetrics data classes from polybench_data module
from poly_bench_evaluation.polybench_data import PolyBenchOutput, PolyBenchRetrievalMetrics
# Import scoring functions from scoring module
from poly_bench_evaluation.scoring import (
    _get_all_instance_results,     # Internal function to collect all instance result files
    aggregate_logs,                # Function to aggregate logs from multiple instances
    instance_level_scoring,        # Function to score an individual instance
    store_instance_level_output,   # Function to save instance output to JSON
)


# Define a pytest fixture that returns a mock resolved instance (all tests passed)
@pytest.fixture
def mock_resolved_instance():
    # Return a PolyBenchOutput object configured as resolved
    return PolyBenchOutput(
        instance_id="resolved_test_instance",   # Unique identifier for the instance
        patch_applied=True,                     # Indicates patch was successfully applied
        generation=True,                        # Indicates the model generated a patch
        with_logs=True,                         # Indicates logs were captured
        all_f2p_passed=True,                    # All "file to patch" tests passed
        no_p2p_failed=True,                     # No "patch to patch" tests failed
        resolved=True,                          # Overall resolution status (true = successful)
        passed_tests=["test1"],                 # List of test names that passed
        failed_tests=[],                        # List of test names that failed (empty)
    )


# Define a fixture that returns mock retrieval metrics
@pytest.fixture
def mock_metrics():
    # Return a PolyBenchRetrievalMetrics object with sample metrics
    return PolyBenchRetrievalMetrics(
        instance_id="resolved_test_instance",           # Link to instance ID
        file_retrieval_metrics={"recall": 0.5, "precision": 0.5, "f1": 0.5},  # File-level metrics
        node_retrieval_metrics={"recall": 0.5, "precision": 0.5, "f1": 0.5},  # AST node-level metrics
        reference_nodes=[],      # List of reference AST nodes (empty)
        predicted_nodes=[],      # List of predicted AST nodes (empty)
    )


# Define a fixture that returns a mock unresolved instance (some tests failed)
@pytest.fixture
def mock_unresolved_instance():
    # Return a PolyBenchOutput object configured as unresolved (failed tests)
    return PolyBenchOutput(
        instance_id="unresolved_test_instance",    # Unique identifier
        patch_applied=True,                        # Patch was applied
        generation=True,                           # Model generated a patch
        with_logs=True,                            # Logs captured
        all_f2p_passed=True,                       # "file to patch" tests all passed
        no_p2p_failed=True,                        # No "patch to patch" test failures
        resolved=False,                            # Overall resolution is false (failed)
        passed_tests=[],                           # No passing tests
        failed_tests=["test1"],                    # One failing test
    )


def test_instance_level_scoring():
    """Test the instance_level_scoring function with various scenarios."""
    # Docstring describing the test

    # Test case for successful patch with all tests passing
    instance_id = "test1"                          # Dummy instance ID
    result = {"passed_tests": ["test1", "test2"], "failed_tests": []}  # Mock test result
    f2p = ["test1"]                                # List of "file to patch" test names
    p2p = ["test2"]                                # List of "patch to patch" test names
    output = instance_level_scoring(
        instance_id=instance_id,
        result=result,
        f2p=f2p,
        p2p=p2p,
        patch_applied=True,
        generation=True,
    )
    # Assert that the output indicates resolution
    assert output.resolved
    assert output.all_f2p_passed
    assert output.no_p2p_failed
    assert output.patch_applied
    assert output.generation

    # Test case for failed f2p test (one of the file-to-patch tests fails)
    result = {"passed_tests": ["test2"], "failed_tests": ["test1"]}  # test1 failed
    output = instance_level_scoring(
        instance_id=instance_id,
        result=result,
        f2p=f2p,
        p2p=p2p,
        patch_applied=True,
        generation=True,
    )
    # Should not be resolved because all_f2p_passed is false
    assert not output.resolved
    assert not output.all_f2p_passed
    assert output.no_p2p_failed                     # p2p still passes

    # Test case for failed p2p test (one of the patch-to-patch tests fails)
    result = {"passed_tests": ["test1"], "failed_tests": ["test2"]}  # test2 failed
    output = instance_level_scoring(
        instance_id=instance_id,
        result=result,
        f2p=f2p,
        p2p=p2p,
        patch_applied=True,
        generation=True,
    )
    # Should not be resolved because no_p2p_failed is false
    assert not output.resolved
    assert output.all_f2p_passed
    assert not output.no_p2p_failed

    # Test case for no result (empty dictionary) – indicates missing logs
    output = instance_level_scoring(
        instance_id=instance_id, result={}, f2p=f2p, p2p=p2p, patch_applied=False, generation=False
    )
    # Should not be resolved and flags set to false
    assert not output.resolved
    assert not output.with_logs
    assert not output.patch_applied
    assert not output.generation


def test_store_instance_level_output():
    """Test that instance output is correctly stored to a JSON file."""
    # Docstring

    # Create a temporary directory for storing output files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test data: a PolyBenchOutput instance for a successful instance
        instance_output = PolyBenchOutput(
            instance_id="test_instance",
            patch_applied=True,
            generation=True,
            with_logs=True,
            all_f2p_passed=True,
            no_p2p_failed=True,
            resolved=True,
            passed_tests=["test1", "test2"],
            failed_tests=[],
        )

        # Store the output in the temporary directory
        store_instance_level_output(instance_output, temp_dir)

        # Verify that the expected JSON file was created
        output_file = Path(temp_dir) / "test_instance_result.json"
        assert output_file.exists()

        # Read and verify the JSON content
        with open(output_file, "r") as f:
            stored_data = json.load(f)                    # Parse JSON into dict
            assert stored_data["instance_id"] == "test_instance"
            assert stored_data["patch_applied"]
            assert stored_data["generation"]
            assert stored_data["with_logs"]
            assert stored_data["resolved"]
            assert stored_data["passed_tests"] == ["test1", "test2"]
            assert stored_data["failed_tests"] == []


def test_get_all_instance_results_happy(mock_resolved_instance, mock_unresolved_instance):
    """Test that _get_all_instance_results collects all result files correctly."""
    # Docstring

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Store both resolved and unresolved instance outputs
        store_instance_level_output(mock_resolved_instance, temp_dir)
        store_instance_level_output(mock_unresolved_instance, temp_dir)

        # Call the function to get all instance result dictionaries
        all_results = _get_all_instance_results(temp_dir)

        # Should have collected two result entries
        assert len(all_results) == 2


def test_get_all_instance_results_wrong_path():
    """Test that _get_all_instance_results raises errors for invalid paths."""
    # Docstring

    # Non-existent path should raise FileNotFoundError
    non_existent_path = "/non/existent/path"
    with pytest.raises(FileNotFoundError):
        _get_all_instance_results(non_existent_path)

    # Passing None should raise TypeError
    with pytest.raises(TypeError):
        _get_all_instance_results(None)


def test_aggregate_logs(mock_resolved_instance, mock_unresolved_instance, mock_metrics):
    """Test that aggregate_logs correctly combines instance outputs and metrics."""
    # Docstring

    # Create a temporary directory for storing outputs
    with tempfile.TemporaryDirectory() as temp_dir:
        # Store resolved instance, unresolved instance, and metrics
        store_instance_level_output(mock_resolved_instance, temp_dir)
        store_instance_level_output(mock_unresolved_instance, temp_dir)
        store_instance_level_output(mock_metrics, temp_dir, suffix="_metrics")  # Note suffix

        # Get the project root (parent of the directory containing this test file)
        project_root = Path(__file__).parent.parent
        # Path to the dataset CSV (polybench_sampled_500.csv in datasets folder)
        csv_path = project_root / "datasets" / "polybench_sampled_500.csv"
        # Run aggregation
        aggregate_logs(temp_dir, dataset_path=csv_path, output_path=temp_dir)

        # Verify that the aggregated result file was created
        result_file = Path(temp_dir) / "result.json"
        assert result_file.exists()

        # Read and validate the aggregated data
        with open(result_file, "r") as f:
            data = json.load(f)
            # One resolved, one unresolved
            assert data["total_resolved"] == 1
            assert data["total_unresolved"] == 1
            # Both instances had patch_applied, with_logs, generation true
            assert len(data["patch_applied"]) == 2
            assert len(data["with_logs"]) == 2
            assert len(data["generation"]) == 2
            assert len(data["no_generation"]) == 0
            # Check file retrieval metrics (from mock_metrics)
            assert data["file_retrieval"] == [
                {
                    "file_recall": 0.5,
                    "file_precision": 0.5,
                    "file_f1": 0.5,
                    "instance_id": "resolved_test_instance",
                }
            ]
            # Check node retrieval metrics
            assert data["node_retrieval"] == [
                {
                    "node_recall": 0.5,
                    "node_precision": 0.5,
                    "node_f1": 0.5,
                    "instance_id": "resolved_test_instance",
                }
            ]


def test_aggregate_logs_empty_directory():
    """Test that aggregate_logs raises ValueError when no instance results are found."""
    # Docstring

    # Create an empty temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Expect ValueError because no instance result files exist
        with pytest.raises(ValueError):
            project_root = Path(__file__).parent.parent
            csv_path = project_root / "datasets" / "polybench_sampled_500.csv"
            aggregate_logs(temp_dir, dataset_path=csv_path)


def test_store_instance_level_output_type_error():
    """Test that store_instance_level_output raises TypeError for invalid input type."""
    # Docstring

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Passing a dictionary instead of a PolyBenchOutput/PolyBenchRetrievalMetrics should raise TypeError
        with pytest.raises(TypeError):
            store_instance_level_output({"invalid": "type"}, temp_dir)
