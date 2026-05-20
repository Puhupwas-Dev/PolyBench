# PolyBench – Test Suite

Internal test directory for the PolyBench evaluation harness.  
All tests are run locally and are not intended for public consumption.

## Test Files

- `polybench_evaluation.py` – Unit tests for the main evaluation module
- `repo_utils.py` – Test helpers for repository operations
- `run_evaluation.py` – Integration tests for the evaluation runner
- `scoring.py` – Tests for scoring and metrics computation

## Running Tests Locally

From the project root:

```bash
pytest test/ -v
Or run a specific test file:

bash
pytest test/test_scoring.py -v
Notes
Tests expect the benchmark/ directory to be present (downloaded separately).

Some tests require Docker to be installed and running.

Internet access may be needed for cloning repositories during tests.
