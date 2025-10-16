#!/bin/bash
# Script de entrada para garantir que o Python encontre os módulos

cd /app
echo "Diretório atual: $(pwd)"
echo "Conteúdo do diretório:"
ls -la

# Define PYTHONPATH
export PYTHONPATH="/app:$PYTHONPATH"
echo "PYTHONPATH: $PYTHONPATH"

# Executa o main.py
exec python main.py