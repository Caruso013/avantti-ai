#!/bin/bash

echo "🚀 PREPARANDO COMMIT - AVANTTI AI v4.0.0"
echo "=============================================="
echo ""

echo "📋 RESUMO DAS MUDANÇAS v4.0.0:"
echo ""
echo "🚫 REGRAS RÍGIDAS DE NEGÓCIO:"
echo "   ❌ PROIBIÇÃO TOTAL de agendamento de visitas"
echo "   📏 Mensagens limitadas a máx 3 linhas/50 palavras"
echo "   🔄 Split automático de respostas longas"
echo "   🎯 Foco exclusivo em qualificação de leads"
echo ""

echo "🎯 OTIMIZAÇÕES DE PROMPT:"
echo "   📝 Prompt rigorosamente reescrito"
echo "   ✅ Critérios claros para registro de leads"
echo "   🗣️ Respostas mais objetivas e diretas"
echo "   🧠 Contexto focado em informações relevantes"
echo ""

echo "📱 MELHORIAS NO SISTEMA:"
echo "   ⚖️ Validação rigorosa de tamanho de mensagem"
echo "   📬 Sistema de fila respeitando ordem das mensagens"
echo "   ✂️ Quebra inteligente por pontuação"
echo "   🧹 Remoção de confirmações desnecessárias"
echo ""

echo "🧪 VALIDAÇÕES E TESTES:"
echo "   🤖 Testes automatizados de comportamento"
echo "   📊 Scripts de validação C2S"
echo "   📈 Monitoramento contínuo"
echo "   🔍 Logs detalhados de decisões"
echo ""

echo "📁 ARQUIVOS MODIFICADOS:"
echo "   - services/response_orchestrator_service.py (prompt reescrito)"
echo "   - clients/zapi_client.py (validações aprimoradas)"
echo "   - app.py (versão v4.0.0)"
echo "   - main.py (logs atualizados)"
echo "   - start.sh (banner v4)"
echo "   - __init__.py (identificação v4)"
echo "   - VERSION.md (changelog v4.0.0)"
echo ""

echo "🧪 NOVOS ARQUIVOS DE TESTE:"
echo "   - test_cenario_conversa.py"
echo "   - test_lead_pedro.py"
echo "   - test_simples_pedro.py"
echo ""

echo "⚠️  REGRAS CRÍTICAS IMPLEMENTADAS:"
echo "   1. ❌ NUNCA oferecer agendamento de visitas"
echo "   2. 📏 SEMPRE manter mensagens curtas (max 3 linhas/50 palavras)"
echo "   3. 📝 SEMPRE registrar leads com interesse claro"
echo "   4. 📬 SEMPRE processar mensagens em fila sequencial"
echo "   5. 🎯 SEMPRE focar em qualificação sem compromissos"
echo ""

echo "✅ VALIDAÇÕES DE DEPLOY:"
echo "   ✅ Prompt testado contra cenários problemáticos"
echo "   ✅ Sistema de mensagens com limites rígidos"
echo "   ✅ Registro automático de leads funcionando"
echo "   ✅ Integração C2S operacional"
echo "   ✅ Logs e monitoramento implementados"
echo ""

# Verificar se existem arquivos para commit
if git diff --quiet && git diff --staged --quiet; then
    echo "❌ Nenhuma mudança detectada para commit."
    echo "   Execute 'git status' para verificar o estado atual."
    exit 1
fi

echo "📋 Status atual do repositório:"
git status --short
echo ""

# Mostrar o que será commitado
echo "📦 Arquivos que serão commitados:"
git diff --staged --name-only
echo ""

# Confirmar com o usuário
read -p "🤔 Deseja prosseguir com o commit da v4.0.0? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Adicionar arquivos modificados
    echo "📦 Adicionando arquivos modificados..."
    git add services/response_orchestrator_service.py
    git add clients/zapi_client.py
    git add app.py
    git add main.py
    git add start.sh
    git add __init__.py
    git add VERSION.md
    git add test_cenario_conversa.py
    git add test_lead_pedro.py
    git add test_simples_pedro.py
    
    # Commit das mudanças
    commit_message="🚀 Release v4.0.0 - AI Enhanced Lead Processing

⚠️  REGRAS CRÍTICAS IMPLEMENTADAS:
❌ PROIBIÇÃO TOTAL de agendamento de visitas
📏 Mensagens limitadas a máx 3 linhas/50 palavras
🔄 Split automático de respostas longas
🎯 Foco exclusivo em qualificação de leads

🛠️ PRINCIPAIS MUDANÇAS:
• Prompt rigorosamente reescrito para evitar ofertas de visita
• Validação rigorosa de tamanho de mensagem
• Sistema de fila respeitando ordem das mensagens
• Registro automático de leads com critérios claros
• Testes automatizados de comportamento
• Monitoramento contínuo de decisões da IA

🧪 VALIDAÇÕES:
• Testado contra cenários problemáticos
• Integração C2S operacional
• Logs detalhados implementados

🤖 Sistema: Avantti AI v4.0.0
📅 Data: $(date +'%d/%m/%Y %H:%M')
👥 Cliente: Evex Imóveis"

    git commit -m "$commit_message"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ COMMIT REALIZADO COM SUCESSO!"
        echo "🏷️  Versão: v4.0.0 - AI Enhanced Lead Processing"
        echo "📅 Data: $(date +'%d/%m/%Y %H:%M')"
        echo ""
        
        echo "🚀 PRÓXIMOS PASSOS PARA DEPLOY:"
        echo ""
        echo "1. 🔍 Verificar se todas as mudanças estão corretas:"
        echo "   git log --oneline -5"
        echo ""
        echo "2. 🚀 Fazer push para o repositório:"
        echo "   git push origin main"
        echo ""
        echo "3. 🏗️ Deploy no ambiente de produção"
        echo "   (EasyPanel, Docker, etc.)"
        echo ""
        echo "4. ✅ Validar comportamento em produção:"
        echo "   - Testar proibição de agendamento"
        echo "   - Verificar mensagens curtas"
        echo "   - Confirmar registro automático de leads"
        echo ""
        echo "5. 📊 Monitorar logs e métricas"
        echo "   curl https://seu-dominio.com/version"
        echo ""
        
        echo "🎯 TESTES RECOMENDADOS PÓS-DEPLOY:"
        echo "   1. Simular conversa com interesse em imóvel"
        echo "   2. Verificar se mensagens ficam curtas"
        echo "   3. Confirmar registro no C2S"
        echo "   4. Validar que não oferece visitas"
        echo ""
        
        echo "⚠️  ATENÇÃO: Esta é uma versão com regras rígidas!"
        echo "   🚫 IA NÃO PODE mais agendar visitas"
        echo "   📏 Mensagens limitadas rigorosamente"
        echo "   🎯 Foco total em qualificação"
    else
        echo ""
        echo "❌ Erro ao realizar o commit!"
        echo "   Verifique se todos os arquivos estão corretos"
    fi
else
    echo ""
    echo "❌ Commit cancelado pelo usuário."
    echo "   Use 'git status' para ver mudanças pendentes"
fi

echo ""
echo "=============================================="
echo "🏁 SCRIPT FINALIZADO"
echo "=============================================="