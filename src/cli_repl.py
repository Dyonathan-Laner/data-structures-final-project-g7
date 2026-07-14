import os
import sys
import subprocess

# Garante que o diretório raiz e o diretório src estejam no path para importações
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.tree.avl_tree import AVLTree


def print_tree(node, prefix="", is_left=None):
    """Exibe a árvore AVL de forma hierárquica e horizontal no terminal."""
    if node is None:
        return
    
    if node.right is not None:
        print_tree(node.right, prefix + ("│   " if is_left is True else "    "), False)
    
    if is_left is None:
        marker = "─── "
    elif is_left:
        marker = "└── "
    else:
        marker = "┌── "
        
    print(prefix + marker + f"{node.key} [altura={node.height}, tamanho={node.size}, agregado={node.aggregate}]")
    
    if node.left is not None:
        print_tree(node.left, prefix + ("│   " if is_left is False else "    "), True)


def exibir_ajuda():
    print("\nComandos disponíveis:")
    print("  i <chave>            - Insere uma chave na árvore (ex: i 15)")
    print("  d <chave>            - Deleta uma chave da árvore (ex: d 15)")
    print("  s <chave>            - Busca uma chave na árvore (ex: s 15)")
    print("  r <chave>            - Retorna o rank da chave (quantidade de elementos menores) (ex: r 15)")
    print("  sel <índice>         - Seleciona a chave na posição (índice ordenado, 0-indexed) (ex: sel 2)")
    print("  ra <início> <fim>    - Retorna a quantidade de elementos no intervalo [início, fim] (ex: ra 10 30)")
    print("  p                    - Imprime a árvore AVL graficamente")
    print("  io                   - Imprime as chaves em ordem crescente (inorder)")
    print("  altura, alt          - Exibe a altura e tamanho da árvore ativa (ex: alt)")
    print("  c                    - Limpa a árvore")
    print("  load <caminho>       - Carrega e insere um trace silenciosamente na árvore (ex: load data/traces/wiki_100k_shuffle.trace)")
    print("  run <trace> <out>    - Executa um trace medindo tempos e gerando estatísticas (ex: run data/traces/wiki_100k_shuffle.trace data/output.out)")
    print("  gen <ops> <out_pref> [order] - Gera chaves sintéticas e arquivo .trace (ex: gen 1000 data/teste shuffle)")
    print("  verify <exp> <cand>  - Compara a saída candidata com o gabarito .expected (ex: verify data/teste.expected data/output.out)")
    print("  bench [synthetic]    - Executa os cenários do benchmark consolidado (ex: bench)")
    print("  wizard               - Abre o assistente interativo de benchmark rápido passo a passo")
    print("  h, ajuda             - Mostra este menu de ajuda")
    print("  q, sair              - Sai do REPL")


def main():
    # Garante suporte a caracteres Unicode no terminal
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
        sys.stdin.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

    print("====================================================")
    print("       REPL Interativo - Árvore AVL Aumentada       ")
    print("====================================================")
    exibir_ajuda()
    
    tree = AVLTree()
    
    while True:
        try:
            user_input = input("\navl_tree> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSaindo...")
            break
            
        if not user_input:
            continue
            
        parts = user_input.split()
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd in ("q", "sair"):
            print("Saindo...")
            break
            
        elif cmd in ("h", "ajuda"):
            exibir_ajuda()
            
        elif cmd == "p":
            if tree.root is None:
                print("Árvore está vazia.")
            else:
                print("\nEstrutura atual da árvore:")
                print_tree(tree.root)
                
        elif cmd == "io":
            chaves = tree.inorder()
            print(f"Chaves em ordem: {chaves} (Total: {len(chaves)})")
            
        elif cmd == "c":
            tree = AVLTree()
            print("Árvore limpa com sucesso.")
            
        elif cmd in ("altura", "alt"):
            if tree.root is None:
                print("Árvore está vazia (altura = 0, tamanho = 0).")
            else:
                print(f"Altura da árvore ativa: {tree.root.height}")
                print(f"Total de chaves guardadas (tamanho): {tree.root.size}")
            
        elif cmd == "load":
            if not args:
                print("Erro: informe o caminho do arquivo .trace. Ex: load data/traces/my_trace.trace")
                continue
            path = args[0]
            if not os.path.exists(path):
                print(f"Erro: arquivo '{path}' não encontrado.")
                continue
            print(f"Carregando e executando trace de '{path}' na árvore ativa...")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except Exception as e:
                print(f"Erro ao ler arquivo: {e}")
                continue
            
            import time
            from src.main import format_time
            
            latencies = []
            n_ins = n_del = n_srch = 0
            for line_num, line in enumerate(lines, 1):
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                try:
                    parts = stripped.split()
                    if len(parts) != 2:
                        continue
                    op, key_str = parts[0], parts[1]
                    key = int(key_str)
                    
                    if op == 'I':
                        start = time.perf_counter_ns()
                        tree.insert(key)
                        end = time.perf_counter_ns()
                        latencies.append(end - start)
                        n_ins += 1
                    elif op == 'D':
                        start = time.perf_counter_ns()
                        tree.delete(key)
                        end = time.perf_counter_ns()
                        latencies.append(end - start)
                        n_del += 1
                    elif op == 'S':
                        start = time.perf_counter_ns()
                        tree.search(key)
                        end = time.perf_counter_ns()
                        latencies.append(end - start)
                        n_srch += 1
                except ValueError:
                    continue
            print(f"Sucesso! Operações executadas: {n_ins} inserções, {n_del} remoções, {n_srch} buscas.")
            if latencies:
                total_time = sum(latencies)
                sorted_latencies = sorted(latencies)
                n_lat = len(sorted_latencies)
                p50 = sorted_latencies[int(n_lat * 0.50)]
                p99 = sorted_latencies[min(int(n_lat * 0.99), n_lat - 1)]
                print(f"Tempo Total de execução: {format_time(total_time)}")
                print(f"p50: {format_time(p50)}")
                print(f"p99: {format_time(p99)}")
            if tree.root:
                print(f"Estado atual da árvore: tamanho={tree.root.size}, altura={tree.root.height}")
            else:
                print("Árvore está vazia.")
            
        elif cmd == "i":
            if not args:
                print("Erro: insira uma chave para inserção. Ex: i 10")
                continue
            try:
                chave = int(args[0])
                tree.insert(chave)
                print(f"Chave {chave} inserida.")
            except ValueError:
                print("Erro: a chave deve ser um número inteiro.")
                
        elif cmd == "d":
            if not args:
                print("Erro: insira uma chave para remoção. Ex: d 10")
                continue
            try:
                chave = int(args[0])
                if not tree.search(chave):
                    print(f"Chave {chave} não encontrada para remoção.")
                else:
                    tree.delete(chave)
                    print(f"Chave {chave} removida.")
            except ValueError:
                print("Erro: a chave deve ser um número inteiro.")
                
        elif cmd == "s":
            if not args:
                print("Erro: insira uma chave para busca. Ex: s 10")
                continue
            try:
                chave = int(args[0])
                encontrada = tree.search(chave)
                if encontrada:
                    print(f"Chave {chave} ENCONTRADA.")
                else:
                    print(f"Chave {chave} NÃO ENCONTRADA.")
            except ValueError:
                print("Erro: a chave deve ser um número inteiro.")
                
        elif cmd == "r":
            if not args:
                print("Erro: insira uma chave para calcular o rank. Ex: r 10")
                continue
            try:
                chave = int(args[0])
                pos = tree.rank(chave)
                print(f"Rank da chave {chave} (elementos menores): {pos}")
            except ValueError:
                print("Erro: a chave deve ser um número inteiro.")
                
        elif cmd == "sel":
            if not args:
                print("Erro: insira um índice para seleção. Ex: sel 2")
                continue
            try:
                indice = int(args[0])
                chave = tree.select(indice)
                if chave is None:
                    print(f"Índice {indice} fora de alcance.")
                else:
                    print(f"Chave no índice {indice}: {chave}")
            except ValueError:
                print("Erro: o índice deve ser um número inteiro.")
                
        elif cmd == "ra":
            if len(args) < 2:
                print("Erro: informe os limites de início e fim. Ex: ra 10 30")
                continue
            try:
                inicio = int(args[0])
                fim = int(args[1])
                contagem = tree.range_agg(inicio, fim)
                print(f"Quantidade de elementos no intervalo [{inicio}, {fim}]: {contagem}")
            except ValueError:
                print("Erro: os limites devem ser números inteiros.")
                
        elif cmd == "run":
            if len(args) < 2:
                print("Erro: informe o caminho do trace e o arquivo de saída. Ex: run data/traces/my.trace data/output.out")
                continue
            trace_path, output_path = args[0], args[1]
            if not os.path.exists(trace_path):
                print(f"Erro: arquivo '{trace_path}' não encontrado.")
                continue
            print(f"Executando trace '{trace_path}'...")
            try:
                from src.main import process_trace
                process_trace(trace_path, output_path)
            except Exception as e:
                print(f"Erro durante execução: {e}")
                
        elif cmd == "gen":
            if len(args) < 2:
                print("Erro: informe o número de operações e o prefixo de saída. Ex: gen 1000 data/meu_teste [shuffle/sorted]")
                continue
            ops = args[0]
            out_prefix = args[1]
            order = args[2] if len(args) > 2 else "shuffle"
            
            cmd_gen = [
                sys.executable, "gen_workload_1.py", "generate",
                "--out", out_prefix,
                "--ops", ops,
                "--synthetic", ops,
                "--insert-order", order,
                "--seed", "42"
            ]
            print(f"Gerando workload com {ops} operações e ordem '{order}'...")
            try:
                subprocess.run(cmd_gen, check=True)
            except Exception as e:
                print(f"Erro ao gerar workload: {e}")
                
        elif cmd == "verify":
            if len(args) < 2:
                print("Erro: informe o arquivo gabarito (.expected) e o arquivo de saída (.out). Ex: verify data/meu.expected data/output.out")
                continue
            expected = args[0]
            candidate = args[1]
            cmd_verify = [
                sys.executable, "gen_workload_1.py", "verify",
                "--expected", expected,
                "--candidate", candidate
            ]
            print("Verificando corretude do resultado...")
            try:
                subprocess.run(cmd_verify, check=True)
            except Exception as e:
                print(f"Erro na verificação: {e}")
                
        elif cmd == "bench":
            use_synthetic = len(args) > 0 and args[0].lower() in ("synthetic", "--use-synthetic", "true")
            cmd_bench = [sys.executable, "benchmark_manager.py"]
            if use_synthetic:
                cmd_bench.append("--use-synthetic")
                print("Executando benchmark consolidado utilizando chaves sintéticas...")
            else:
                print("Executando benchmark consolidado completo (SOSD)...")
            try:
                subprocess.run(cmd_bench, check=True)
            except Exception as e:
                print(f"Erro ao rodar benchmark: {e}")
                
        elif cmd == "wizard":
            print("\n--- Assistente Interativo de Benchmark Rápido ---")
            while True:
                try:
                    val = input("Digite a quantidade de operações/chaves desejada: ").strip()
                    if not val:
                        continue
                    num_keys = int(val)
                    if num_keys <= 0:
                        print("Digite um número maior que 0.")
                        continue
                    break
                except ValueError:
                    print("Entrada inválida. Digite um número inteiro.")
            
            print("Escolha a ordem de inserção:")
            print("1) Embaralhado (shuffle)")
            print("2) Ordenado (sorted)")
            while True:
                choice = input("Opção (1 ou 2): ").strip()
                if choice == '1':
                    order = 'shuffle'
                    break
                elif choice == '2':
                    order = 'sorted'
                    break
                else:
                    print("Opção inválida. Digite 1 ou 2.")
            
            os.makedirs(os.path.join("data", "quick_run"), exist_ok=True)
            trace_prefix = os.path.join("data", "quick_run", f"quick_{num_keys}_{order}")
            trace_path = f"{trace_prefix}.trace"
            expected_path = f"{trace_prefix}.expected"
            output_path = os.path.join("data", "quick_run", f"output_{num_keys}_{order}.out")
            
            print(f"\n[1/3] Gerando trace com {num_keys} chaves...")
            cmd_gen = [
                sys.executable, "gen_workload_1.py", "generate",
                "--out", trace_prefix,
                "--ops", str(num_keys),
                "--synthetic", str(num_keys),
                "--insert-order", order,
                "--seed", "42"
            ]
            try:
                subprocess.run(cmd_gen, check=True)
                
                print(f"\n[2/3] Executando benchmark na árvore AVL ativa...")
                tree = AVLTree()  # Limpa a árvore ativa para iniciar o benchmark do zero
                
                import time
                from src.main import format_time
                
                try:
                    with open(trace_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                except Exception as e:
                    print(f"Erro ao ler trace gerado: {e}")
                    continue
                
                latencies = []
                search_results = []
                
                for line_num, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if not stripped or stripped.startswith('#'):
                        continue
                    try:
                        parts = stripped.split()
                        if len(parts) != 2:
                            continue
                        op, key_str = parts[0], parts[1]
                        key = int(key_str)
                        
                        if op == 'I':
                            start = time.perf_counter_ns()
                            tree.insert(key)
                            end = time.perf_counter_ns()
                            latencies.append(end - start)
                        elif op == 'D':
                            start = time.perf_counter_ns()
                            tree.delete(key)
                            end = time.perf_counter_ns()
                            latencies.append(end - start)
                        elif op == 'S':
                            start = time.perf_counter_ns()
                            found = tree.search(key)
                            end = time.perf_counter_ns()
                            latencies.append(end - start)
                            status = "FOUND" if found else "NOT_FOUND"
                            search_results.append((key, status))
                    except ValueError:
                        continue
                
                if not latencies:
                    print("Erro: Nenhuma operação válida pôde ser processada do trace.")
                    continue
                
                # Calcular estatísticas
                total_time = sum(latencies)
                sorted_latencies = sorted(latencies)
                n_lat = len(sorted_latencies)
                p50 = sorted_latencies[int(n_lat * 0.50)]
                p99 = sorted_latencies[min(int(n_lat * 0.99), n_lat - 1)]
                final_height = tree._height(tree.root)
                final_size = tree._size(tree.root)
                
                # Salvar saída no arquivo de destino
                try:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        for k, status in search_results:
                            f.write(f"{k} {status}\n")
                        f.write("\n")
                        f.write("=== Estatísticas do Benchmark ===\n")
                        f.write(f"Tempo Total (ns): {total_time}\n")
                        f.write(f"Tempo Total formatado: {format_time(total_time)}\n")
                        f.write(f"Percentil p50 (ns): {p50}\n")
                        f.write(f"Percentil p50 formatado: {format_time(p50)}\n")
                        f.write(f"Percentil p99 (ns): {p99}\n")
                        f.write(f"Percentil p99 formatado: {format_time(p99)}\n")
                        f.write(f"Total de operações processadas: {len(latencies)}\n")
                        f.write(f"Altura final da árvore: {final_height}\n")
                        f.write(f"Chaves vivas ao final: {final_size}\n")
                except Exception as e:
                    print(f"Erro ao salvar arquivo de saída: {e}")
                    continue
                
                print("Benchmark concluído com sucesso!")
                print(f"Resultados salvos em: {output_path}")
                print(f"Tempo Total: {format_time(total_time)}")
                print(f"p50: {format_time(p50)}")
                print(f"p99: {format_time(p99)}")
                print(f"Altura final da árvore: {final_height}")
                print(f"Chaves vivas ao final (salvas na memória do console): {final_size}")
                
                print(f"\n[3/3] Verificando corretude do resultado...")
                cmd_verify = [
                    sys.executable, "gen_workload_1.py", "verify",
                    "--expected", expected_path,
                    "--candidate", output_path
                ]
                subprocess.run(cmd_verify, check=True)
            except Exception as e:
                print(f"Erro durante execução do assistente: {e}")
                
        else:
            print(f"Comando '{cmd}' desconhecido. Digite 'h' ou 'ajuda' para ver comandos.")


if __name__ == '__main__':
    main()
