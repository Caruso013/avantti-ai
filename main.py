#!/usr/bin/env python3
"""
Avantti AI - Eliane V4 - Ponto de entrada principal
Alternativa ao app.py para resolver problemas de import em produção
"""

import os
import sys

# Garante que o diretório atual está no PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(current_dir)  # O diretório atual É a raiz do projeto

# Adiciona os caminhos necessários ao sys.path
paths_to_add = [project_root, current_dir]
for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

print(f"[MAIN] PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
print(f"[MAIN] sys.path: {sys.path}")
print(f"[MAIN] Current dir: {current_dir}")
print(f"[MAIN] Project root: {project_root}")
print(f"[MAIN] Working directory: {os.getcwd()}")

# Verifica se os módulos existem antes de importar
try:
    import clients
    print("[MAIN] Módulo 'clients' encontrado")
except ImportError as e:
    print(f"[MAIN] ERRO: Módulo 'clients' não encontrado: {e}")
    print("[MAIN] Verificando estrutura de arquivos...")
    if os.path.exists(os.path.join(project_root, 'clients')):
        print("[MAIN] Diretório clients existe")
        files = os.listdir(os.path.join(project_root, 'clients'))
        print(f"[MAIN] Arquivos em clients: {files}")
    else:
        print("[MAIN] Diretório clients NÃO existe")

# Agora importa o app
try:
    from app import app
    print("[MAIN] App importado com sucesso")
except ImportError as e:
    print(f"[MAIN] Erro ao importar app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    print(f"[MAIN] Iniciando Avantti AI - Eliane V4 na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=False)