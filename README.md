# PolyBench – Internal Multi‑Language Benchmark Reference

Personal reference for a multi‑language repository‑level software engineering benchmark.  
Contains 2,110 curated issues across **Java, JavaScript, TypeScript, and Python**.  
Includes stratified subsets (500 and 382 issues) for rapid experimentation.

> *Cloned from a public source and adapted for personal evaluation workflows.*

---

## Datasets (Local Reference)

- Full dataset: 2,110 instances  
- Sampled dataset (PB500): 500 instances (125 per language, 40‑40‑20 split across Bug Fix / Feature / Refactoring)  
- Verified dataset (PBv): 382 instances with curated annotations

All dataset references are stored locally – not published.

---

## Evaluation Harness (Internal Use)

Main script: `src/poly_bench_evaluation/run_evaluation.py`

### Key parameters

| Parameter | Description |
|-----------|-------------|
| `--dataset-path` | Path to local dataset |
| `--predictions-path` | Model‑generated `.jsonl` predictions (must have `instance_id` and `model_patch`) |
| `--result-path` | Output directory for instance‑level results |
| `--num-threads` | Default 1. For 16‑core CPU / 64GB RAM, use 10‑12 |
| `--evaluate-gold` | Evaluates gold patches (ignores `predictions-path`) |
| `--repo-path` | Directory to store base repositories |
| `--delete-image` | Delete instance‑level Docker images after run (saves space) |
| `--skip-existing` | Skip already‑evaluated instances |
| `--metrics-only` | Compute only file retrieval metrics (no pass rate) |
| `--node-metrics` | Include node retrieval metrics (slower) |

---

## Docker Images

Pre‑built instance‑level Docker images are pulled from a public registry automatically.  
If needed manually:

```sh
docker pull ghcr.io/timesler/swe-polybench.eval.x86_64.<instance_id>:v1.1
Example:

sh
docker pull ghcr.io/timesler/swe-polybench.eval.x86_64.google__gson-2337:v1.1
Setup & Run (Local)
Python 3.11+ recommended (conda environment optional)

bash
git clone <local-reference>
cd PolyBench
pip install -r requirements.txt
pip install -e .
Evaluate gold patches
bash
python3 src/poly_bench_evaluation/run_evaluation.py \
  --dataset-path <local_path_or_HF_ref> \
  --result-path ./eval_logs \
  --num-threads 9 \
  --repo-path ~/repos \
  --delete-image \
  --evaluate-gold
Evaluate model‑generated patches
bash
python3 src/poly_bench_evaluation/run_evaluation.py \
  --dataset-path <local_path_or_HF_ref> \
  --result-path ./eval_logs \
  --num-threads 9 \
  --repo-path ~/repos \
  --delete-image \
  --predictions-path ./model_generated_predictions.jsonl \
  --skip-existing
Outputs
Instance‑level results (passing/failing tests) saved in --result-path

Combined summary written to ./result.json

Test run logs stored in ./run_logs_{language}

Troubleshooting (Container conflicts)
If you see container conflicts after interrupting a run:

bash
docker rm -f $(docker ps -a -q)
⚠️ This removes all running containers – use with care.
