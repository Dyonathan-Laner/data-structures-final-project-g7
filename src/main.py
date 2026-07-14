"""Main driver execution script for benchmarking BST operations.

This script parses a trace file, executes the operations on the BST tree,
measures the latency of each operation in nanoseconds, and outputs the search
results and overall statistics (total time, p50, and p99 latency).
"""

import argparse
import os
import sys
import time

# Ensure the parent directory is in the system path to allow importing from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.arvore import MeuBST


def process_trace(trace_path: str, output_path: str) -> None:
    """Reads a trace file, runs operations on MeuBST, and writes search results and statistics.

    Args:
        trace_path (str): Path to the input trace file.
        output_path (str): Path to the output results file.
    """
    bst = MeuBST()
    latencies = []
    search_results = []
    
    try:
        with open(trace_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Erro: Arquivo de trace não encontrado em '{trace_path}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao ler o arquivo de trace: {e}", file=sys.stderr)
        sys.exit(1)

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            continue

        try:
            parts = stripped.split()
            if len(parts) != 2:
                raise ValueError("Formato de linha inválido. Esperado '<OPERAÇÃO> <CHAVE>'")

            op, key_str = parts[0], parts[1]
            key = int(key_str)

            if op == 'I':
                start = time.perf_counter_ns()
                bst.insert(key)
                end = time.perf_counter_ns()
                latencies.append(end - start)

            elif op == 'D':
                start = time.perf_counter_ns()
                bst.delete(key)
                end = time.perf_counter_ns()
                latencies.append(end - start)

            elif op == 'S':
                start = time.perf_counter_ns()
                found = bst.search(key)
                end = time.perf_counter_ns()
                latencies.append(end - start)
                
                status = "FOUND" if found else "NOT_FOUND"
                search_results.append((key, status))

            else:
                raise ValueError(f"Operação desconhecida '{op}'")

        except (ValueError, IndexError) as e:
            # Basic error handling: report to stderr but continue execution
            print(f"Aviso: Linha {line_num} com formato inesperado '{stripped}'. Erro: {e}", file=sys.stderr)
            continue

    if not latencies:
        print("Erro: Nenhuma operação válida pôde ser processada do trace.", file=sys.stderr)
        sys.exit(1)

    # Compute statistics
    total_time = sum(latencies)
    sorted_latencies = sorted(latencies)
    n = len(sorted_latencies)
    p50 = sorted_latencies[int(n * 0.50)]
    p99 = sorted_latencies[min(int(n * 0.99), n - 1)]

    # Write output to the destination file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for key, status in search_results:
                f.write(f"{key} {status}\n")

            f.write("\n")
            f.write("=== Estatísticas do Benchmark ===\n")
            f.write(f"Tempo Total (ns): {total_time}\n")
            f.write(f"Percentil p50 (ns): {p50}\n")
            f.write(f"Percentil p99 (ns): {p99}\n")
            f.write(f"Total de operações processadas: {len(latencies)}\n")
    except Exception as e:
        print(f"Erro ao salvar arquivo de saída: {e}", file=sys.stderr)
        sys.exit(1)

    print("Benchmark concluído com sucesso!")
    print(f"Resultados salvos em: {output_path}")
    print(f"Tempo Total: {total_time} ns")
    print(f"p50: {p50} ns")
    print(f"p99: {p99} ns")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Driver de execução e benchmark para MeuBST usando traces.")
    parser.add_argument("trace_path", type=str, help="Caminho para o arquivo .trace de entrada")
    parser.add_argument("output_path", type=str, help="Caminho para o arquivo de saída gerado")
    
    args = parser.parse_args()
    process_trace(args.trace_path, args.output_path)
