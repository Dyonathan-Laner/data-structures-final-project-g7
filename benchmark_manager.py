"""Automation script for generating workloads and executing benchmarks (Group 7).

Group 7 parameters: dataset=wiki, theta=0.6, mix=55:15:30 (I:D:S),
range_agg=count, insert order=sorted, seed=7.

Experiments (per section 7 of the assignment):
  escala  - operation count N over 4+ orders of magnitude (1k .. 10M), for
            insert orders sorted (group assignment, pathological for naive
            BSTs) and shuffle, on the augmented AVL and on the naive
            unbalanced BST baseline (capped where it would take hours).
  theta   - Zipfian skew sweep theta in {0.0, 0.6, 0.99, 1.2} at N=1M.

Every run is checked against the oracle (gen_workload_1.py verify); the
result is recorded in each scenario JSON and in the consolidated CSV.
"""

import argparse
import csv
import json
import os
import platform
import subprocess
import sys
from datetime import datetime

# Group 7 configuration
DATASET_PATH = os.path.join("data", "wiki_ts_200M_uint64")
SEED = 7
THETA = 0.6
MIX = "55:15:30"  # 55% Insert, 15% Delete, 30% Search

SCENARIOS_N = {
    "1k": 1_000,
    "10k": 10_000,
    "100k": 100_000,
    "1M": 1_000_000,
    "5M": 5_000_000,
    "10M": 10_000_000,
}
QUICK_SCENARIOS_N = {
    "1k": 1_000,
    "10k": 10_000,
}
INSERT_ORDERS = ["sorted", "shuffle"]
THETA_SWEEP = [0.0, 0.6, 0.99, 1.2]
THETA_SWEEP_N = ("1M", 1_000_000)

# The naive BST costs O(depth) per operation. Under sorted insertion the
# depth equals the number of live keys, so the total cost is quadratic --
# beyond these caps a single scenario would take hours.
NAIVE_MAX_OPS = {
    "sorted": 10_000,
    "shuffle": 1_000_000,
}

OUT_DIR = os.path.join("data", "outputs")
TRACE_DIR = os.path.join("data", "traces")


def check_dataset() -> bool:
    """Verifica se o dataset wiki existe na pasta local data/."""
    if os.path.exists(DATASET_PATH):
        print(f"[Info] Dataset wiki encontrado em '{DATASET_PATH}'.")
        return True

    print(f"\n[Erro] Dataset wiki real não foi encontrado em '{DATASET_PATH}'.", file=sys.stderr)
    print("--------------------------------------------------------------------------------", file=sys.stderr)
    print("Para executar o benchmark com os dados reais do Grupo 7, faça o seguinte:", file=sys.stderr)
    print("1. Baixe o dataset manualmente pelo seu navegador usando este link:", file=sys.stderr)
    print("   https://zenodo.org/records/15240501/files/wiki_ts_200M_uint64?download=1", file=sys.stderr)
    print("2. Crie uma pasta chamada 'data' (se não existir) na raiz do projeto.", file=sys.stderr)
    print("3. Salve o arquivo dentro dela com o nome exato 'wiki_ts_200M_uint64' (sem extensão).", file=sys.stderr)
    print("4. Execute o benchmark novamente.", file=sys.stderr)
    print("--------------------------------------------------------------------------------\n", file=sys.stderr)
    return False


def write_run_info() -> None:
    """Grava informações da máquina e do ambiente, exigidas na metodologia do relatório."""
    info = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "platform": platform.platform(),
        "python": sys.version,
        "seed": SEED,
        "theta_grupo": THETA,
        "mix": MIX,
        "dataset": DATASET_PATH,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "run_info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=4)
    print(f"[Info] Ambiente registrado em {os.path.join(OUT_DIR, 'run_info.json')}")


def run_workload_generator(name: str, ops: int, order: str, theta: float,
                           use_synthetic: bool) -> tuple[str, str]:
    """Chama gen_workload_1.py para gerar os arquivos de trace e gabarito (.expected)."""
    os.makedirs(TRACE_DIR, exist_ok=True)
    trace_prefix = os.path.join(TRACE_DIR, name)

    cmd = [
        sys.executable, "gen_workload_1.py", "generate",
        "--out", trace_prefix,
        "--ops", str(ops),
        "--seed", str(SEED),
        "--theta", str(theta),
        "--mix", MIX,
        "--insert-order", order,
    ]

    if use_synthetic:
        cmd.extend(["--synthetic", str(ops)])
    else:
        # Limita o carregamento de chaves para evitar uso excessivo de RAM
        cmd.extend(["--keys", DATASET_PATH, "--max-load", str(ops * 2)])

    print(f"[Gen] trace {name} (ops={ops}, ordem={order}, theta={theta})...")
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    if result.stderr:
        sys.stderr.write(result.stderr)

    return f"{trace_prefix}.trace", f"{trace_prefix}.expected"


def run_benchmark_driver(trace_path: str, name: str, structure: str) -> str:
    """Executa o driver src/main.py sobre o trace com a estrutura escolhida."""
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"{name}_{structure}.out")

    cmd = [
        sys.executable, os.path.join("src", "main.py"),
        trace_path,
        out_path,
        "--structure", structure,
    ]

    print(f"[Run] {name} ({structure})...")
    subprocess.run(cmd, check=True)
    return out_path


def verify_with_oracle(expected_path: str, candidate_path: str) -> bool:
    """Confere a saída com o gabarito usando o subcomando verify do gerador."""
    cmd = [
        sys.executable, "gen_workload_1.py", "verify",
        "--expected", expected_path,
        "--candidate", candidate_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = (result.stdout or "") + (result.stderr or "")
    print(output.strip())
    return result.returncode == 0


def load_driver_stats(out_path: str) -> dict:
    """Lê o arquivo .stats.json produzido pelo driver."""
    with open(out_path + ".stats.json", "r", encoding="utf-8") as f:
        return json.load(f)


def clean_temporary_trace_files(*paths: str) -> None:
    """Remove arquivos de trace/gabarito para economizar disco (regeneráveis via seed)."""
    for path in paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError as e:
            print(f"[Aviso] Não foi possível remover '{path}': {e}", file=sys.stderr)


def execute_scenario(name: str, ops: int, order: str, theta: float, structures: list[str],
                     experiment: str, use_synthetic: bool, keep_traces: bool,
                     results: list[dict]) -> None:
    """Gera o trace uma vez e o executa em cada estrutura, verificando com o oráculo."""
    print("\n" + "=" * 60)
    print(f"Cenário [{experiment}]: {name} | ops={ops} | ordem={order} | theta={theta}")
    print("=" * 60)

    try:
        trace_path, expected_path = run_workload_generator(name, ops, order, theta, use_synthetic)
    except subprocess.CalledProcessError as e:
        print(f"[Erro] Falha na geração do trace {name}: {e}", file=sys.stderr)
        return

    for structure in structures:
        try:
            out_path = run_benchmark_driver(trace_path, name, structure)
            oracle_ok = verify_with_oracle(expected_path, out_path)
            stats = load_driver_stats(out_path)

            row = {
                "experiment": experiment,
                "scenario": name,
                "structure": structure,
                "ops": ops,
                "order": order,
                "theta": theta,
                "oracle": "OK" if oracle_ok else "FAIL",
                "stats": stats,
            }
            results.append(row)

            json_path = os.path.join(OUT_DIR, f"{name}_{structure}.json")
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(row, jf, indent=4)
            print(f"[Salvo] {json_path} (oráculo: {row['oracle']})")

        except Exception as e:
            print(f"[Erro] Falha no cenário {name} ({structure}): {e}", file=sys.stderr)

    if not keep_traces:
        clean_temporary_trace_files(trace_path, expected_path)


def scenarios_escala(scenarios_n: dict[str, int]) -> list[tuple]:
    """Grade do experimento de escala: N x ordem x estruturas cabíveis."""
    grid = []
    for n_name, n_val in scenarios_n.items():
        for order in INSERT_ORDERS:
            structures = ["avl"]
            if n_val <= NAIVE_MAX_OPS[order]:
                structures.append("naive")
            name = f"wiki_{n_name}_{order}"
            grid.append((name, n_val, order, THETA, structures))
    return grid


def scenarios_theta() -> list[tuple]:
    """Grade da varredura de theta em N fixo, nas duas ordens de inserção."""
    n_name, n_val = THETA_SWEEP_N
    grid = []
    for theta in THETA_SWEEP:
        for order in INSERT_ORDERS:
            theta_tag = str(theta).replace(".", "_")
            name = f"wiki_{n_name}_{order}_theta{theta_tag}"
            grid.append((name, n_val, order, theta, ["avl"]))
    return grid


def write_summary_csv(results: list[dict]) -> None:
    """Grava o resumo consolidado com métricas por operação em CSV."""
    csv_path = "benchmark_summary.csv"
    fields = [
        "experiment", "scenario", "structure", "ops", "order", "theta", "oracle",
        "total_ns", "mean_ns", "p50_ns", "p99_ns",
        "insert_mean_ns", "insert_p50_ns", "insert_p99_ns",
        "delete_mean_ns", "delete_p50_ns", "delete_p99_ns",
        "search_mean_ns", "search_p50_ns", "search_p99_ns",
        "final_height", "final_size",
    ]
    try:
        with open(csv_path, "w", newline="", encoding="utf-8") as cf:
            writer = csv.writer(cf)
            writer.writerow(fields)
            for res in results:
                stats = res["stats"]
                row = [
                    res["experiment"], res["scenario"], res["structure"], res["ops"],
                    res["order"], res["theta"], res["oracle"],
                    stats["overall"]["total_ns"], stats["overall"]["mean_ns"],
                    stats["overall"]["p50_ns"], stats["overall"]["p99_ns"],
                ]
                for op in ("insert", "delete", "search"):
                    row.extend([
                        stats["per_op"][op]["mean_ns"],
                        stats["per_op"][op]["p50_ns"],
                        stats["per_op"][op]["p99_ns"],
                    ])
                row.extend([stats["final_height"], stats["final_size"]])
                writer.writerow(row)
        print(f"\n[Sucesso] Resumo geral do benchmark gravado em: {csv_path}")
    except Exception as e:
        print(f"[Erro] Falha ao escrever resumo CSV: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Automatizador de benchmarks e estudo empírico (Grupo 7).")
    parser.add_argument("--use-synthetic", action="store_true",
                        help="Usa chaves sintéticas ao invés do dataset wiki real do SOSD")
    parser.add_argument("--keep-traces", action="store_true",
                        help="Mantém os arquivos .trace e .expected em disco após a execução")
    parser.add_argument("--experiment", choices=["escala", "theta", "all"], default="all",
                        help="Qual experimento executar (padrão: todos)")
    parser.add_argument("--quick", action="store_true",
                        help="Executa apenas cenários pequenos (teste rápido do pipeline)")
    args = parser.parse_args()

    if not args.use_synthetic and not check_dataset():
        print("[Erro] O benchmark real não pode continuar sem o dataset da Wikipédia.", file=sys.stderr)
        sys.exit(1)

    write_run_info()

    scenarios_n = QUICK_SCENARIOS_N if args.quick else SCENARIOS_N

    grid: list[tuple] = []
    if args.experiment in ("escala", "all"):
        grid.extend([(*s, "escala") for s in scenarios_escala(scenarios_n)])
    if args.experiment in ("theta", "all") and not args.quick:
        grid.extend([(*s, "theta") for s in scenarios_theta()])

    results: list[dict] = []
    for name, ops, order, theta, structures, experiment in grid:
        execute_scenario(name, ops, order, theta, structures, experiment,
                         args.use_synthetic, args.keep_traces, results)

    if results:
        write_summary_csv(results)
        with open(os.path.join(OUT_DIR, "results_all.json"), "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
        print(f"[Sucesso] Resultados consolidados em: {os.path.join(OUT_DIR, 'results_all.json')}")

    failures = [r for r in results if r["oracle"] != "OK"]
    if failures:
        print(f"\n[ATENÇÃO] {len(failures)} cenário(s) DIVERGIRAM do oráculo:", file=sys.stderr)
        for r in failures:
            print(f"  - {r['scenario']} ({r['structure']})", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
