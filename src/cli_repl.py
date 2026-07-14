import os
import sys

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
    print("  c                    - Limpa a árvore")
    print("  load <caminho>       - Carrega e executa um arquivo .trace (ex: load data/traces/wiki_100k_shuffle.trace)")
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
            
        elif cmd == "load":
            if not args:
                print("Erro: informe o caminho do arquivo .trace. Ex: load data/traces/my_trace.trace")
                continue
            path = args[0]
            if not os.path.exists(path):
                print(f"Erro: arquivo '{path}' não encontrado.")
                continue
            print(f"Carregando e executando trace de '{path}'...")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except Exception as e:
                print(f"Erro ao ler arquivo: {e}")
                continue
            
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
                        tree.insert(key)
                        n_ins += 1
                    elif op == 'D':
                        tree.delete(key)
                        n_del += 1
                    elif op == 'S':
                        tree.search(key)
                        n_srch += 1
                except ValueError:
                    continue
            print(f"Sucesso! Operações executadas: {n_ins} inserções, {n_del} remoções, {n_srch} buscas.")
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
                
        else:
            print(f"Comando '{cmd}' desconhecido. Digite 'h' ou 'ajuda' para ver comandos.")


if __name__ == '__main__':
    main()
