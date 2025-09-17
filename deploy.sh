#!/bin/bash
# Script para preparar e fazer commit para deploy

echo "🚀 Preparando deploy para EasyPanel..."

# Add todos os arquivos
git add .

# Commit
git commit -m "feat: deploy limpo com arquivo único

- Dockerfile único e otimizado
- app.py limpo com todas as funcionalidades
- requirements.txt simplificado
- Sistema de filas e contexto funcionando"

# Push
git push origin main

echo "✅ Deploy preparado! Agora configure no EasyPanel:"
echo "1. Repository: $(git remote get-url origin)"
echo "2. Branch: main" 
echo "3. Dockerfile: Dockerfile"
echo "4. Port: 5000"
echo ""
echo "📖 Consulte DEPLOY_EASYPANEL.md para instruções detalhadas"