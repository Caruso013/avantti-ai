#!/bin/bash
# Script para preparar e fazer commit para deploy

echo "🚀 Preparando deploy para EasyPanel..."

# Add todos os arquivos
git add .

# Commit
git commit -m "feat: preparar deploy para produção no EasyPanel

- Dockerfile.production otimizado com Gunicorn
- app_production.py com logs de produção  
- docker-compose.yml configurado
- Documentação completa de deploy
- Configurações de segurança implementadas"

# Push
git push origin main

echo "✅ Deploy preparado! Agora configure no EasyPanel:"
echo "1. Repository: $(git remote get-url origin)"
echo "2. Branch: main" 
echo "3. Dockerfile: Dockerfile.production"
echo "4. Port: 5000"
echo ""
echo "📖 Consulte DEPLOY_EASYPANEL.md para instruções detalhadas"