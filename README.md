# Balanced Augmented Tree

Final project for the Data Structures course (Group 7).

## Overview

This project implements an augmented balanced binary search tree (AVL Tree) capable of efficiently supporting dynamic operations and order-statistics queries over large datasets. 

The implementation features custom range-aggregate queries based on count aggregation (specific to Group 7 requirements) and is evaluated using Wikipedia timestamps from the SOSD (Search on Sorted Data) benchmark.

## Features

* **Insert (`/insert`)**: Insert unique keys into the tree with automatic AVL rebalancing.
* **Delete (`/delete`)**: Remove keys from the tree with automatic AVL rebalancing.
* **Search (`/search`)**: Fast membership queries in $O(\log N)$ time.
* **Rank (`/rank`)**: Retrieve the number of keys smaller than a given target in $O(\log N)$ time.
* **Select (`/select`)**: Find the $i$-th smallest key in the tree in $O(\log N)$ time.
* **Range Aggregate (`/range_agg`)**: Perform range queries to count elements in a range $[start, end]$ in $O(\log N)$ time.
* **Graphical Print (`/print`)**: Visualize the tree structure, heights, and sub-tree sizes horizontally in the terminal.

## Project Structure

```text
src/
├── tree/            # Tree implementations
│   ├── avl_tree.py  # Augmented AVL Tree (core structure)
│   ├── naive_bst.py # Unbalanced BST (naive baseline for the empirical study)
│   └── node.py
├── cli_repl.py      # Unified interactive CLI REPL
└── main.py          # Benchmark driver (per-operation latency stats)

scripts/
└── generate_charts.py # Report figures from data/outputs (matplotlib)

data/                # Ignored directory for traces, inputs, and outputs
docs/                # Project final report PDF and documentation
tests/               # Unit tests for correctness validation
pyproject.toml       # Poetry dependency configuration
run.py               # Simple root-level CLI REPL entrypoint
benchmark_manager.py # Automated execution manager for SOSD wiki scenarios
gen_workload_1.py    # YCSB zipfian workload generator and verifier
```

## Requirements

* Python 3.12+
* Poetry

Install the dependencies:

```bash
poetry install
```

## Running the Application

### 1. Interactive Console (REPL)
The primary entry point of the project is the interactive CLI REPL. It allows you to run manual operations, execute custom workloads, or start the step-by-step benchmark assistant.

Run it using:
```bash
python run.py
```

Inside the console, type `/help` to see the complete command manual. All commands are strictly formatted with a `/` prefix (e.g., `/insert 15`, `/print`, `/wizard`).

### 2. Running Benchmarks with Real Wiki Data
Since Group 7 evaluates using Wikipedia timestamps, you must manually download the dataset first:
1. Download the SOSD `wiki_ts_200M_uint64` dataset from Zenodo:
   [https://zenodo.org/records/15240501/files/wiki_ts_200M_uint64?download=1](https://zenodo.org/records/15240501/files/wiki_ts_200M_uint64?download=1)
2. Place the file inside the `data/` directory (create it if missing) with the exact filename: `wiki_ts_200M_uint64` (without any file extension).
3. Run the consolidated benchmark runner:
   * Via interactive console: `/benchmark`
   * Or directly from your shell: `python benchmark_manager.py`

The runner executes two experiments (see `docs/relatorio_empirico.md`):

* **escala** — 1k to 10M operations, insert orders `sorted` and `shuffle`, on the augmented AVL and on a deliberately naive unbalanced BST baseline (capped at sizes where it remains tractable);
* **theta** — Zipfian skew sweep θ ∈ {0.0, 0.6, 0.99, 1.2} at N=1M.

Every run is automatically checked against the oracle (`gen_workload_1.py verify`). Results are written to `data/outputs/` (per-scenario JSON + consolidated `results_all.json`) and summarized in `benchmark_summary.csv`.

Useful flags: `--quick` (small smoke-test scenarios), `--experiment escala|theta`, `--keep-traces`, `--use-synthetic` (run without the real dataset).

4. Generate the report figures from the measured results:

```bash
python scripts/generate_charts.py
```

Figures are written to `docs/figures/` and referenced by `docs/relatorio_empirico.md`.

*Note: To run the benchmark using synthetic data instead of downloading the 1.6 GB dataset, run `python benchmark_manager.py --use-synthetic` or `/benchmark synthetic` inside the console.*

## Testing

Verify the correctness of all tree invariants (BST properties, AVL heights, duplicate management, select/rank metrics, and range aggregation):

```bash
pytest
```

## Deliverables (docs/)

* [`docs/relatorio_empirico.md`](docs/relatorio_empirico.md) — empirical study report (submission copy: `docs/relatorio_empirico.docx`): methodology, the five required experiments with measured data, interpretation, and the full measurement appendix.
* [`docs/justificativa_projeto.md`](docs/justificativa_projeto.md) — design justification: why AVL, the four invariants of the augmented tree, why they hold under rotation, `range_agg` correctness, and discarded alternatives with measured costs.
* [`docs/apresentacao.md`](docs/apresentacao.md) — 10-minute oral presentation script with anticipated examiner questions.
* [`docs/prompts/`](docs/prompts/README.md) — organized dump of the AI chat sessions used in the project (graded deliverable).
* `docs/figures/` — report figures, generated from `data/outputs/` by `scripts/generate_charts.py`.

## Team (Group 7)

* Dyonathan Bento Laner
* Gustavo Borges Arrussul Veiga
* Lucas Kaue Ribeiro Weber
