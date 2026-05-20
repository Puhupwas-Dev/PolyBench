# Import Path class from pathlib module for object-oriented filesystem paths
from pathlib import Path

# Import RepoManager class from poly_bench_evaluation.repo_utils module
from poly_bench_evaluation.repo_utils import RepoManager


def test_init():
    """Test RepoManager initialization."""
    # Docstring explaining this test verifies the constructor and attributes

    # Create a RepoManager instance with test name and path
    repo_manager = RepoManager("test_repo", "/path/to/repo")
    # Assert that the repo_name attribute matches the expected value
    assert repo_manager.repo_name == "test_repo"
    # Assert that the repo_path attribute is a Path object with the expected path
    assert repo_manager.repo_path == Path("/path/to/repo")
    # Assert that tmp_repo_dir is initially None (not yet created)
    assert repo_manager.tmp_repo_dir is None
    # Assert that base_repo_dir is initially None (not yet set)
    assert repo_manager.base_repo_dir is None

    # Clean up by calling internal _cleanup method (closes any open resources)
    repo_manager._cleanup()
