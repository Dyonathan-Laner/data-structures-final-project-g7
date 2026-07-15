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
├── tree/            # AVL Tree and Node implementation
│   ├── avl_tree.py
│   └── node.py
├── cli_repl.py      # Unified interactive CLI REPL
└── main.py          # Benchmark driver and time formatter

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
3. Run the consolidated benchmark runner (scenarios from 100k to 10M keys):
   * Via interactive console: `/benchmark`
   * Or directly from your shell: `python benchmark_manager.py`

*Note: To run the benchmark using synthetic data instead of downloading the 1.6 GB dataset, run `python benchmark_manager.py --use-synthetic` or `/benchmark synthetic` inside the console.*

## Testing

Verify the correctness of all tree invariants (BST properties, AVL heights, duplicate management, select/rank metrics, and range aggregation):

```bash
pytest
```

## Team (Group 7)

* Dyonathan Bento Laner
* Gustavo Borges Arrussul Veiga
* Lucas Kaue Ribeiro Weber
