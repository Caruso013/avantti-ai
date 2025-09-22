#!/bin/bash
# Script para commit da versão 3.0.0

echo "🚀 PREPARANDO COMMIT - AVANTTI AI v3.0.0"
echo "=========================================="

# Verifica se está em um repositório git
if [ ! -d ".git" ]; then
    echo "❌ Este diretório não é um repositório git"
    echo "💡 Inicializando repositório..."
    git init
    echo "✅ Repositório inicializado"
fi

echo ""
echo "📋 ARQUIVOS MODIFICADOS/CRIADOS:"
echo "--------------------------------"

# Lista arquivos novos e modificados
echo "🆕 Novos arquivos:"
echo "   - services/lead_distributor_service.py"
echo "   - services/contact2sale_service.py"
echo "   - clients/contact2sale_client.py"
echo "   - config/contact2sale_config.py"
echo "   - tools/notificar_novo_lead_tool.py"
echo "   - interfaces/clients/__init__.py"
echo "   - VERSION.md"
echo "   - test_*.py (scripts de teste)"

echo ""
echo "🔄 Arquivos modificados:"
echo "   - app.py (banner de inicialização + endpoint /version)"
echo "   - services/response_orchestrator_service.py (prompt sem visitas)"
echo "   - clients/zapi_client.py (quebra de mensagens)"
echo "   - container/tools.py (nova tool registrada)"
echo "   - .env (novas configurações Contact2Sale)"

echo ""
echo "🏷️ DETALHES DA VERSÃO:"
echo "----------------------"
echo "Versão: 3.0.0"
echo "Codinome: Contact2Sale Distribution"
echo "Cliente: Evex Imóveis"
echo "Data: $(date '+%d/%m/%Y %H:%M:%S')"

echo ""
echo "✨ PRINCIPAIS FUNCIONALIDADES:"
echo "-----------------------------"
echo "✅ Sistema de distribuição automática entre 11 equipes"
echo "✅ Integração completa Contact2Sale"
echo "✅ Quebra automática de mensagens WhatsApp"
echo "✅ Remoção de agendamento de visitas"
echo "✅ Banner de inicialização informativo"
echo "✅ Endpoint de versão (/version)"
echo "✅ Estatísticas de distribuição"
echo "✅ Testes automatizados"

echo ""
echo "🔧 CONFIGURAÇÕES NECESSÁRIAS:"
echo "-----------------------------"
echo "C2S_JWT_TOKEN=seu_token_aqui"
echo "C2S_COMPANY_ID=c9433557c1656dea3004165b6bcb7e2a"
echo "C2S_USE_TEAM_DISTRIBUTION=true"
echo "C2S_DISTRIBUTION_METHOD=round_robin"

echo ""
read -p "🤔 Deseja prosseguir com o commit? (y/N): " confirm

if [[ $confirm =~ ^[Yy]$ ]]; then
    echo ""
    echo "📦 Adicionando arquivos ao staging..."
    
    # Adiciona arquivos específicos
    git add app.py
    git add services/
    git add clients/
    git add config/
    git add tools/
    git add interfaces/
    git add container/
    git add .env
    git add VERSION.md
    git add test_*.py
    git add README.md 2>/dev/null || echo "README.md não encontrado"
    
    echo "✅ Arquivos adicionados ao staging"
    
    echo ""
    echo "💾 Fazendo commit..."
    
    commit_message="🚀 Release v3.0.0 - Contact2Sale Distribution

🌟 Principais novidades:
• Sistema de distribuição automática entre 11 equipes Evex Imóveis
• Integração completa Contact2Sale com criação/busca de leads
• Quebra automática de mensagens WhatsApp por ponto/interrogação
• Remoção de agendamento de visitas do prompt
• Banner de inicialização com status das configurações
• Endpoint /version para monitoramento
• Sistema de estatísticas de distribuição de leads

🏢 Cliente: Evex Imóveis
🤖 Sistema: Avantti AI v3.0.0
📅 Data: $(date '+%d/%m/%Y %H:%M:%S')

📋 Arquivos principais:
• services/lead_distributor_service.py - Distribuição de leads
• services/contact2sale_service.py - Integração CRM
• clients/contact2sale_client.py - Cliente HTTP API
• tools/notificar_novo_lead_tool.py - Tool atualizada
• app.py - Banner e endpoint versão
• clients/zapi_client.py - Quebra de mensagens

🔧 Configurações:
• C2S_JWT_TOKEN, C2S_COMPANY_ID configurados
• C2S_USE_TEAM_DISTRIBUTION=true
• C2S_DISTRIBUTION_METHOD=round_robin

✅ Testado e validado com scripts automatizados"

    git commit -m "$commit_message"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 COMMIT REALIZADO COM SUCESSO!"
        echo "================================"
        echo ""
        echo "📋 PRÓXIMOS PASSOS:"
        echo "1. Fazer push para o repositório remoto"
        echo "2. Deploy no EasyPanel"
        echo "3. Verificar logs de inicialização"
        echo "4. Testar distribuição de leads"
        echo "5. Monitorar endpoint /version"
        echo ""
        echo "🔗 Comando para push:"
        echo "git push origin main"
        echo ""
        echo "📊 Para ver o status:"
        echo "curl https://seu-dominio.com/version"
        echo ""
        echo "🎯 O banner será exibido nos logs do EasyPanel na inicialização!"
    else
        echo "❌ Erro no commit. Verifique os arquivos e tente novamente."
    fi
else
    echo ""
    echo "🛑 Commit cancelado pelo usuário"
    echo "💡 Execute novamente quando estiver pronto"
fi

echo ""
echo "📝 Para ver o histórico:"
echo "git log --oneline -10"
echo ""
echo "🔍 Para ver as mudanças:"
echo "git status"
echo "git diff --cached"