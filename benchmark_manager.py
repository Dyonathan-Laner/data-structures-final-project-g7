"""Automation script for generating workloads and executing benchmarks for AVL Tree.

This script manages:
1. Downloading the SOSD wiki dataset if not present.
2. Generating traces for various sizes (100k, 1M, 5M, 10M) and insert orders (sorted, shuffle).
3. Running the benchmark driver.
4. Parsing results, saving them as JSON per scenario, and writing a consolidated CSV summary.
"""

import argparse
import csv
import json
import os
import subprocess
import sys
import urllib.request

# Configuration Constants
WIKI_DATASET_URL = "https://zenodo.org/records/4728952/files/wiki_ts_200M_uint64?download=1"
DATASET_PATH = os.path.join("data", "wiki_ts_200M_uint64")
SEED = 7
THETA = 0.6
MIX = "55:15:30"  # 55% Insert, 15% Delete, 30% Search

SCENARIOS_N = {
    "100k": 100_000,
    "1M": 1_000_000,
    "5M": 5_000_000,
    "10M": 10_000_000
}
INSERT_ORDERS = ["sorted", "shuffle"]


def check_and_download_dataset() -> bool:
    """Verifica se o dataset wiki existe ou inicia o download caso não esteja presente.

    Returns:
        bool: True se o dataset real estiver disponível, False caso contrário.
    """
    if os.path.exists(DATASET_PATH):
        print(f"[Info] Dataset wiki encontrado em '{DATASET_PATH}'.")
        return True

    print(f"[Aviso] Dataset wiki real não foi encontrado em '{DATASET_PATH}'.")
    print(f"Iniciando download automático do Zenodo (~1.6 GB)...")
    print("Nota: Este download pode levar alguns minutos dependendo da sua velocidade de internet.")

    try:
        os.makedirs("data", exist_ok=True)
        
        # Download tracker
        last_reported_percent = -1
        def download_progress(count, block_size, total_size):
            nonlocal last_reported_percent
            downloaded = count * block_size
            if total_size > 0:
                percent = int(downloaded * 100 / total_size)
                # Log progress every 5%
                if percent % 5 == 0 and percent != last_reported_percent:
                    print(f"Progresso do download: {percent}% ({downloaded // (1024*1024)} MB / {total_size // (1024*1024)} MB)...")
                    last_reported_percent = percent
            else:
                if count % 5000 == 0:
                    print(f"Baixados: {downloaded // (1024*1024)} MB...")

        urllib.request.urlretrieve(WIKI_DATASET_URL, DATASET_PATH, download_progress)
        print("[Sucesso] Download do dataset concluído com sucesso!")
        return True
    except Exception as e:
        print(f"\n[Erro] Falha ao baixar o dataset: {e}", file=sys.stderr)
        return False


def run_workload_generator(n_name: str, n_val: int, order: str, use_synthetic: bool) -> tuple[str, str]:
    """Chama gen_workload_1.py para gerar os arquivos de trace e gabarito (.expected).

    Args:
        n_name (str): Nome do tamanho (ex: 100k, 1M).
        n_val (int): Valor numérico de N.
        order (str): Ordem de inserção (sorted ou shuffle).
        use_synthetic (bool): Se deve usar chaves sintéticas.

    Returns:
        tuple[str, str]: Caminhos para o trace gerado e para o arquivo de gabarito.
    """
    os.makedirs(os.path.join("data", "traces"), exist_ok=True)
    trace_prefix = os.path.join("data", "traces", f"wiki_{n_name}_{order}")
    
    cmd = [
        sys.executable, "gen_workload_1.py", "generate",
        "--out", trace_prefix,
        "--ops", str(n_val),
        "--seed", str(SEED),
        "--theta", str(THETA),
        "--mix", MIX,
        "--insert-order", order
    ]

    if use_synthetic:
        cmd.extend(["--synthetic", str(n_val)])
    else:
        # Optimizar limite de carregamento de chaves para evitar uso excessivo de RAM
        cmd.extend(["--keys", DATASET_PATH, "--max-load", str(n_val * 2)])

    print(f"Executando gerador de workloads para N={n_name}, ordem={order}...")
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    if result.stderr:
        sys.stderr.write(result.stderr)

    return f"{trace_prefix}.trace", f"{trace_prefix}.expected"


def run_benchmark_driver(trace_path: str, n_name: str, order: str) -> str:
    """Executa o script de benchmark em src/main.py passando o trace gerado.

    Args:
        trace_path (str): Caminho do arquivo .trace.
        n_name (str): Nome do tamanho (ex: 100k, 1M).
        order (str): Ordem de inserção.

    Returns:
        str: Caminho do arquivo de saída .out com as estatísticas.
    """
    os.makedirs(os.path.join("data", "outputs"), exist_ok=True)
    out_path = os.path.join("data", "outputs", f"results_n_{n_name}_{order}.out")
    
    cmd = [
        sys.executable, os.path.join("src", "main.py"),
        trace_path,
        out_path
    ]
    
    print(f"Executando benchmark para N={n_name}, ordem={order}...")
    subprocess.run(cmd, check=True)
    return out_path


def parse_benchmark_stats(out_path: str) -> tuple[int, int, int]:
    """Lê o arquivo de saída gerado pelo driver de benchmark e extrai as latências.

    Args:
        out_path (str): Caminho do arquivo de saída .out.

    Returns:
        tuple[int, int, int]: (TempoTotal, P50, P99) em nanossegundos.
    """
    tempo_total = 0
    p50 = 0
    p99 = 0
    
    with open(out_path, "r", encoding="utf-8") as f:
        for line in f:
            if "Tempo Total (ns):" in line:
                tempo_total = int(line.split(":")[1].strip())
            elif "Percentil p50 (ns):" in line:
                p50 = int(line.split(":")[1].strip())
            elif "Percentil p99 (ns):" in line:
                p99 = int(line.split(":")[1].strip())
                
    return tempo_total, p50, p99


def clean_temporary_trace_files(trace_path: str, expected_path: str) -> None:
    """Remove os arquivos de trace e expected gerados para economizar espaço em disco.

    Args:
        trace_path (str): Caminho do arquivo .trace.
        expected_path (str): Caminho do arquivo .expected.
    """
    try:
        if os.path.exists(trace_path):
            os.remove(trace_path)
        if os.path.exists(expected_path):
            os.remove(expected_path)
    except Exception as e:
        print(f"[Aviso] Não foi possível remover arquivos temporários: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Automatizador de benchmarks e estudo empírico para AVLTree.")
    parser.add_argument("--use-synthetic", action="store_true", 
                        help="Usa chaves sintéticas ao invés de baixar/usar o dataset wiki real do SOSD")
    parser.add_argument("--keep-traces", action="store_true",
                        help="Mantém os arquivos .trace e .expected em disco após a execução")
    args = parser.parse_args()

    # 1. Obter dataset
    use_synthetic = args.use_synthetic
    if not use_synthetic:
        success = check_and_download_dataset()
        if not success:
            print("[Aviso] Alternando automaticamente para chaves sintéticas como fallback...", file=sys.stderr)
            use_synthetic = True

    results = []

    # 2. Executar cenários
    for n_name, n_val in SCENARIOS_N.items():
        for order in INSERT_ORDERS:
            print("\n" + "="*60)
            print(f"Cenário: N = {n_name} ({n_val} operações) | Ordem = {order}")
            print("="*60)
            
            try:
                # Geração de workloads
                trace_path, expected_path = run_workload_generator(n_name, n_val, order, use_synthetic)
                
                # Execução de benchmark
                out_path = run_benchmark_driver(trace_path, n_name, order)
                
                # Coleta de estatísticas
                tempo_total, p50, p99 = parse_benchmark_stats(out_path)
                
                # Salvar no JSON do cenário
                scenario_result = {
                    "Tamanho": n_name,
                    "Ordem": order,
                    "TempoTotal": tempo_total,
                    "P50": p50,
                    "P99": p99
                }
                
                json_path = os.path.join("data", "outputs", f"results_n_{n_name}_{order}.json")
                with open(json_path, "w", encoding="utf-8") as jf:
                    json.dump(scenario_result, jf, indent=4)
                print(f"[Salvo] Resultados do cenário salvos em: {json_path}")
                
                results.append(scenario_result)
                
                # Limpeza de traces gigantes (para não estourar o disco)
                if not args.keep_traces:
                    clean_temporary_trace_files(trace_path, expected_path)
                    
            except Exception as e:
                print(f"[Erro] Falha ao executar o cenário N={n_name}, ordem={order}: {e}", file=sys.stderr)
                continue

    # 3. Gerar resumo consolidado em CSV
    csv_path = "benchmark_summary.csv"
    try:
        with open(csv_path, "w", newline="", encoding="utf-8") as cf:
            writer = csv.writer(cf)
            # Header
            writer.writerow(["Tamanho", "Ordem", "TempoTotal", "P50", "P99"])
            # Rows
            for res in results:
                writer.writerow([res["Tamanho"], res["Ordem"], res["TempoTotal"], res["P50"], res["P99"]])
        print(f"\n[Sucesso] Resumo geral do benchmark gravado em: {csv_path}")
    except Exception as e:
        print(f"[Erro] Falha ao escrever resumo CSV: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
