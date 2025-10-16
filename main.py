#!/usr/bin/env python3
"""
Avantti AI - Eliane V4 - Ponto de entrada principal
Alternativa ao app.py para resolver problemas de import em produção
"""

import os
import sys

# Garante que o diretório atual está no PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Adiciona também o diretório raiz do projeto
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"[MAIN] PYTHONPATH: {sys.path}")
print(f"[MAIN] Current dir: {current_dir}")
print(f"[MAIN] Project root: {project_root}")

# Agora importa o app
try:
    from app import app
    print("[MAIN] App importado com sucesso")
except ImportError as e:
    print(f"[MAIN] Erro ao importar app: {e}")
    sys.exit(1)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    print(f"[MAIN] Iniciando Avantti AI - Eliane V4 na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=False)