#!/usr/bin/env python3
"""
Avantti AI - Eliane V4 - Ponto de entrada principal
Alternativa ao app.py para resolver problemas de import em produção
"""

import os
import sys

# Garante que o diretório atual está no PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Agora importa o app
from app import app

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    print(f"[MAIN] Iniciando Avantti AI - Eliane V4 na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=False)