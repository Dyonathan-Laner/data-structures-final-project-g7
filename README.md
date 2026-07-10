# Balanced Augmented Tree

Final project for the Data Structures course.

## Overview

This project implements an augmented balanced binary search tree capable of efficiently supporting dynamic operations and order-statistics queries over large datasets.

The implementation is evaluated using real-world datasets from the SOSD (Search on Sorted Data) benchmark and includes an empirical performance analysis.

## Features

* Insert
* Delete
* Search
* Rank
* Select
* Range Aggregate

## Project Structure

```text
src/
├── tree/          # Tree implementation
├── workload/      # Workload reader and execution
├── benchmark/     # Benchmark utilities
└── utils/         # Shared utilities

tests/             # Unit tests
data/              # Input datasets and generated files
docs/              # Report, presentation and supporting documents
```

## Requirements

* Python 3.12+
* pip

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running

Run the application:

```bash
python src/main.py
```

## Testing

Run the tests:

```bash
pytest
```

## Team

* Dyonathan Bento Laner
* Gustavo Borges Arrussul Veiga
* Lucas Kaue Ribeiro Weber
