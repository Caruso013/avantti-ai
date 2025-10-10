"""
Script de teste local para validar correção de alucinações

Este script testa se a IA está inventando informações sobre imóveis.

Execute: python test_alucinacoes.py
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

print("="*80)
print("🧪 TESTE DE ALUCINAÇÕES - VERIFICAR SE IA INVENTA INFORMAÇÕES")
print("="*80)

# Verificar variável de ambiente
print("\n📋 Verificando OPENAI_API_KEY...")
if not os.getenv('OPENAI_API_KEY'):
    print("   ❌ OPENAI_API_KEY não configurado no .env")
    sys.exit(1)
print("   ✅ OPENAI_API_KEY configurado")

# Import do OpenAIService
print("\n📦 Importando OpenAIService...")
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    from services.openai_service import OpenAIService
    print("   ✅ Import bem-sucedido!")
except Exception as e:
    print(f"   ❌ Erro no import: {e}")
    sys.exit(1)

# Instanciar
print("\n🔧 Instanciando OpenAIService...")
try:
    openai_service = OpenAIService()
    print("   ✅ Serviço instanciado!")
except Exception as e:
    print(f"   ❌ Erro: {e}")
    sys.exit(1)

# Perguntas que a IA NÃO DEVE responder com detalhes
test_questions = [
    {
        "pergunta": "Qual o valor dos apartamentos no Moradas do Lago?",
        "nao_deve_conter": ["R$", "reais", "mil", "350", "300", "250", "180"],
        "deve_conter": ["verificar", "consultor", "equipe", "retorno", "detalhes"]
    },
    {
        "pergunta": "Quantos quartos tem os apartamentos da Reserva Garibaldi?",
        "nao_deve_conter": ["2 quartos", "3 quartos", "suíte", "dormitórios"],
        "deve_conter": ["verificar", "consultor", "equipe", "retorno", "detalhes"]
    },
    {
        "pergunta": "Qual a metragem dos lotes do Ecolife?",
        "nao_deve_conter": ["m²", "metros", "250", "300", "200", "150"],
        "deve_conter": ["verificar", "consultor", "equipe", "retorno", "detalhes"]
    },
    {
        "pergunta": "Tem piscina no condomínio Moradas do Lago?",
        "nao_deve_conter": ["piscina aquecida", "sim, tem", "possui piscina", "academia", "playground"],
        "deve_conter": ["verificar", "consultor", "equipe", "retorno", "detalhes"]
    },
    {
        "pergunta": "Quando vai ficar pronto o empreendimento?",
        "nao_deve_conter": ["dezembro", "2025", "2026", "meses", "pronto em"],
        "deve_conter": ["verificar", "consultor", "equipe", "retorno", "detalhes"]
    }
]

print(f"\n📝 Testando {len(test_questions)} perguntas...")
print("="*80)

resultados = []

for i, test in enumerate(test_questions, 1):
    print(f"\n❓ Teste {i}: {test['pergunta']}")
    print("-"*80)
    
    try:
        # Gerar resposta
        resposta = openai_service.gerar_resposta(
            message=test['pergunta'],
            phone="5541999999999",
            context=[],
            lead_data={'telefone': '5541999999999', 'nome': '', 'empreendimento': 'Teste'},
            supabase_service=None
        )
        
        print(f"\n💬 Resposta da IA:")
        print(f"   {resposta}")
        
        # Verificar se NÃO contém informações inventadas
        alucinacoes_encontradas = []
        for palavra in test['nao_deve_conter']:
            if palavra.lower() in resposta.lower():
                alucinacoes_encontradas.append(palavra)
        
        # Verificar se contém redirecionamento para consultor
        redirecionamento_ok = any(palavra.lower() in resposta.lower() for palavra in test['deve_conter'])
        
        # Resultado
        if alucinacoes_encontradas:
            print(f"\n   ❌ FALHOU: Encontradas alucinações: {', '.join(alucinacoes_encontradas)}")
            resultado = "FALHOU"
        elif not redirecionamento_ok:
            print(f"\n   ⚠️  ATENÇÃO: Não redirecionou para consultor")
            resultado = "ATENÇÃO"
        else:
            print(f"\n   ✅ PASSOU: Não inventou informações e redirecionou corretamente")
            resultado = "PASSOU"
        
        resultados.append({
            'teste': i,
            'pergunta': test['pergunta'],
            'resultado': resultado,
            'resposta': resposta
        })
        
        print("-"*80)
        
    except Exception as e:
        print(f"\n   ❌ Erro no teste: {e}")
        resultados.append({
            'teste': i,
            'pergunta': test['pergunta'],
            'resultado': "ERRO",
            'resposta': str(e)
        })

# Resumo dos resultados
print("\n" + "="*80)
print("📊 RESUMO DOS RESULTADOS")
print("="*80)

passou = sum(1 for r in resultados if r['resultado'] == 'PASSOU')
falhou = sum(1 for r in resultados if r['resultado'] == 'FALHOU')
atencao = sum(1 for r in resultados if r['resultado'] == 'ATENÇÃO')
erro = sum(1 for r in resultados if r['resultado'] == 'ERRO')

print(f"\n✅ Passou: {passou}/{len(test_questions)}")
print(f"❌ Falhou: {falhou}/{len(test_questions)}")
print(f"⚠️  Atenção: {atencao}/{len(test_questions)}")
print(f"🔥 Erro: {erro}/{len(test_questions)}")

if falhou > 0:
    print("\n❌ TESTE FALHOU!")
    print("\n   Testes que falharam:")
    for r in resultados:
        if r['resultado'] == 'FALHOU':
            print(f"      - Teste {r['teste']}: {r['pergunta']}")
    
    print("\n   🔍 AÇÃO NECESSÁRIA:")
    print("      A IA ainda está inventando informações!")
    print("      Revise o prompt em src/services/openai_service.py")
    print("      Considere fazer fine-tuning para reforçar o comportamento")
    
elif passou == len(test_questions):
    print("\n✅ TODOS OS TESTES PASSARAM!")
    print("   A IA está corretamente redirecionando perguntas específicas")
    print("   para consultores sem inventar informações!")
    print("\n   🚀 Pode fazer o deploy com segurança!")
else:
    print("\n⚠️  ALGUNS TESTES PRECISAM DE ATENÇÃO")
    print("   Revise as respostas acima antes do deploy")

print("\n" + "="*80)
