import subprocess
import sys

def main():
    try:
        # Executa o REPL interativo unificado
        subprocess.run([sys.executable, "src/cli_repl.py"])
    except KeyboardInterrupt:
        print("\nSaindo...")

if __name__ == '__main__':
    main()
