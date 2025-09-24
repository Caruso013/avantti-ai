#!/bin/bash
# Script de inicialização para EasyPanel

echo "🚀 Iniciando Avantti AI - Eliane V4..."

# Define PYTHONPATH para incluir o diretório atual
export PYTHONPATH="${PYTHONPATH}:/app"

# Verifica se existe .env, se não, cria um básico
if [ ! -f "/app/.env" ]; then
    echo "📝 Criando arquivo .env básico..."
    cp /app/.env.example /app/.env
fi

# Instala dependências se necessário
echo "📦 Verificando dependências..."
pip install -r requirements.txt

# Inicia a aplicação
echo "🏃 Iniciando servidor..."
cd /app && python main.py