"""Main driver execution script for benchmarking BST operations.

This script parses a trace file, executes the operations on the chosen tree
(augmented AVL or naive unbalanced BST), measures the latency of each
operation in nanoseconds, and produces:

  * <output_path>            search results only ("<key> <FOUND|NOT_FOUND>"),
                             directly comparable with the oracle via
                             `gen_workload_1.py verify`;
  * <output_path>.stats.json machine-readable statistics (total time, mean,
                             p50/p99 overall and per operation type, final
                             tree height and size).
"""

import argparse
import json
import os
import sys
import time

# Ensure the parent directory is in the system path to allow importing from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tree.avl_tree import AVLTree
from src.tree.naive_bst import NaiveBST


def format_time(ns_val: float) -> str:
    """Format nanosecond values to user-friendly units (min, s, ms, µs, ns).

    Displays at most two units where the value is between 0.5 and 5000.
    However:
      - 'ns' is always displayed if the value is < 0.5 ns.
      - 'min' is always displayed if the value is > 5000 min.
    """
    units = [
        ("min", ns_val / 60_000_000_000, "{:.2f}"),
        ("s", ns_val / 1_000_000_000, "{:.2f}"),
        ("ms", ns_val / 1_000_000, "{:.2f}"),
        ("µs", ns_val / 1_000, "{:.2f}"),
        ("ns", ns_val, "{:.0f}")
    ]

    # Boundary checks:
    # 1. Extremely small value: if ns < 0.5
    if ns_val < 0.5:
        return f"{ns_val:.2f} ns"

    # 2. Extremely large value: if min > 5000
    val_min_check = ns_val / 60_000_000_000
    if val_min_check > 5000:
        return f"{val_min_check:.2f} min"

    valid = []
    for name, val, fmt in units:
        if 0.5 <= val <= 5000:
            valid.append((name, val, fmt))

    if valid:
        display_parts = [f"{fmt.format(val)} {name}" for name, val, fmt in valid[:2]]
        return " e ".join(display_parts)

    # Fallback in case of rounding/edge cases
    if ns_val >= 60_000_000_000:
        return f"{ns_val / 60_000_000_000:.2f} min"
    return f"{ns_val:.0f} ns"


def percentile(sorted_values: list[int], q: float) -> int:
    """Return the q-th percentile (0..1) of an already sorted list."""

    if not sorted_values:
        return 0

    idx = min(int(len(sorted_values) * q), len(sorted_values) - 1)
    return sorted_values[idx]


def tree_height_and_size(root) -> tuple[int, int]:
    """Compute height and size of a tree iteratively.

    Uses an explicit stack because the naive BST can degenerate into a
    chain of N nodes, which would exceed Python's recursion limit.
    """

    if root is None:
        return 0, 0

    height = 0
    size = 0
    stack = [(root, 1)]

    while stack:
        node, depth = stack.pop()
        size += 1
        if depth > height:
            height = depth
        if node.left is not None:
            stack.append((node.left, depth + 1))
        if node.right is not None:
            stack.append((node.right, depth + 1))

    return height, size


def summarize(latencies: list[int]) -> dict:
    """Return count/total/mean/p50/p99 statistics for a list of latencies."""

    if not latencies:
        return {"count": 0, "total_ns": 0, "mean_ns": 0, "p50_ns": 0, "p99_ns": 0}

    ordered = sorted(latencies)
    total = sum(ordered)

    return {
        "count": len(ordered),
        "total_ns": total,
        "mean_ns": total / len(ordered),
        "p50_ns": percentile(ordered, 0.50),
        "p99_ns": percentile(ordered, 0.99),
    }


def parse_trace(trace_path: str) -> list[tuple[str, int]]:
    """Parse the trace file into (operation, key) tuples.

    Parsing happens before execution so that string handling does not
    contaminate the latency measurements.
    """

    ops: list[tuple[str, int]] = []

    try:
        with open(trace_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue

                parts = stripped.split()
                if len(parts) != 2 or parts[0] not in ('I', 'D', 'S'):
                    print(f"Aviso: linha {line_num} com formato inesperado '{stripped}'.",
                          file=sys.stderr)
                    continue

                ops.append((parts[0], int(parts[1])))
    except FileNotFoundError:
        print(f"Erro: Arquivo de trace não encontrado em '{trace_path}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao ler o arquivo de trace: {e}", file=sys.stderr)
        sys.exit(1)

    return ops


def process_trace(trace_path: str, output_path: str, structure: str) -> None:
    """Runs the trace operations on the chosen tree and writes results and statistics.

    Args:
        trace_path (str): Path to the input trace file.
        output_path (str): Path to the output results file (search results only).
        structure (str): Which tree to benchmark ('avl' or 'naive').
    """
    tree = AVLTree() if structure == 'avl' else NaiveBST()

    ops = parse_trace(trace_path)
    if not ops:
        print("Erro: Nenhuma operação válida pôde ser processada do trace.", file=sys.stderr)
        sys.exit(1)

    latencies_by_op: dict[str, list[int]] = {'I': [], 'D': [], 'S': []}
    search_results: list[tuple[int, str]] = []

    insert = tree.insert
    delete = tree.delete
    search = tree.search
    clock = time.perf_counter_ns

    for op, key in ops:
        if op == 'I':
            start = clock()
            insert(key)
            end = clock()
            latencies_by_op['I'].append(end - start)

        elif op == 'D':
            start = clock()
            delete(key)
            end = clock()
            latencies_by_op['D'].append(end - start)

        else:  # 'S'
            start = clock()
            found = search(key)
            end = clock()
            latencies_by_op['S'].append(end - start)
            search_results.append((key, "FOUND" if found else "NOT_FOUND"))

    all_latencies = latencies_by_op['I'] + latencies_by_op['D'] + latencies_by_op['S']
    overall = summarize(all_latencies)
    final_height, final_size = tree_height_and_size(tree.root)

    stats = {
        "structure": structure,
        "trace": trace_path,
        "overall": overall,
        "per_op": {
            "insert": summarize(latencies_by_op['I']),
            "delete": summarize(latencies_by_op['D']),
            "search": summarize(latencies_by_op['S']),
        },
        "final_height": final_height,
        "final_size": final_size,
    }

    # Write search results (oracle-comparable) and the stats JSON
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for key, status in search_results:
                f.write(f"{key} {status}\n")

        with open(output_path + ".stats.json", 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar arquivos de saída: {e}", file=sys.stderr)
        sys.exit(1)

    print("Benchmark concluído com sucesso!")
    print(f"Estrutura: {structure}")
    print(f"Resultados salvos em: {output_path}")
    print(f"Estatísticas salvas em: {output_path}.stats.json")
    print(f"Tempo Total: {format_time(overall['total_ns'])}")
    print(f"p50 geral: {format_time(overall['p50_ns'])} | p99 geral: {format_time(overall['p99_ns'])}")
    for name, label in (("insert", "I"), ("delete", "D"), ("search", "S")):
        s = stats["per_op"][name]
        print(f"  {label}: n={s['count']} média={format_time(s['mean_ns'])} "
              f"p50={format_time(s['p50_ns'])} p99={format_time(s['p99_ns'])}")
    print(f"Altura final da árvore: {final_height}")
    print(f"Chaves vivas ao final: {final_size}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Driver de execução e benchmark para árvores de busca usando traces.")
    parser.add_argument("trace_path", type=str, help="Caminho para o arquivo .trace de entrada")
    parser.add_argument("output_path", type=str, help="Caminho para o arquivo de saída gerado")
    parser.add_argument("--structure", choices=["avl", "naive"], default="avl",
                        help="Estrutura a exercitar: 'avl' (aumentada) ou 'naive' (BST sem balanceamento)")

    args = parser.parse_args()
    process_trace(args.trace_path, args.output_path, args.structure)
