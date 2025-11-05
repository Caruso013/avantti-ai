#!/bin/bash
# Script de entrada para garantir que o Python encontre os módulos

cd /app
echo "Diretório atual: $(pwd)"
echo "Conteúdo do diretório:"
ls -la

# Verifica se o diretório clients existe
if [ -d "clients" ]; then
    echo "Diretório clients encontrado"
    ls -la clients/
else
    echo "ERRO: Diretório clients NÃO encontrado!"
    exit 1
fi

# Define PYTHONPATH
export PYTHONPATH="/app"
echo "PYTHONPATH: $PYTHONPATH"

# Executa o main.py
exec python main.py