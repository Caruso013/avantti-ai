"""
Script de teste local para validar function calling do OpenAI

Este script testa:
1. Import do OpenAIService
2. Simulação de mensagem que deve acionar registrar_lead
3. Validação se a função é chamada corretamente
4. Verificação se o lead é registrado no C2S

Execute: python test_openai_function_calling.py
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

print("="*80)
print("🧪 TESTE DE FUNCTION CALLING - OPENAI")
print("="*80)

# Teste 1: Verificar variáveis de ambiente
print("\n📋 Teste 1: Verificando variáveis de ambiente...")
required_vars = {
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    'CONTACT2SALE_JWT_TOKEN': os.getenv('CONTACT2SALE_JWT_TOKEN'),
    'CONTACT2SALE_COMPANY_ID': os.getenv('CONTACT2SALE_COMPANY_ID'),
    'CONTACT2SALE_SELLER_ID': os.getenv('CONTACT2SALE_SELLER_ID')
}

missing_vars = []
for var_name, var_value in required_vars.items():
    if var_value:
        if 'TOKEN' in var_name or 'KEY' in var_name:
            print(f"   ✅ {var_name}: {'*' * 10} (configurado)")
        else:
            print(f"   ✅ {var_name}: {var_value}")
    else:
        print(f"   ❌ {var_name}: NÃO CONFIGURADO")
        missing_vars.append(var_name)

if missing_vars:
    print(f"\n❌ ERRO: Variáveis faltando no .env:")
    for var in missing_vars:
        print(f"   - {var}")
    sys.exit(1)

# Teste 2: Import do OpenAIService
print("\n📦 Teste 2: Importando OpenAIService...")
try:
    # Adicionar src ao path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    from services.openai_service import OpenAIService
    print("   ✅ Import bem-sucedido!")
except Exception as e:
    print(f"   ❌ Erro no import: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Teste 3: Instanciar o serviço
print("\n🔧 Teste 3: Instanciando OpenAIService...")
try:
    openai_service = OpenAIService()
    print("   ✅ Serviço instanciado com sucesso!")
except Exception as e:
    print(f"   ❌ Erro ao instanciar: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Teste 4: Simular mensagem que deve acionar function calling
print("\n📝 Teste 4: Testando detecção de function calling...")
print("   ATENÇÃO: Este teste vai CRIAR UM LEAD REAL no Contact2Sale!")
print("   Pressione Enter para continuar ou Ctrl+C para cancelar...")

try:
    input()
except KeyboardInterrupt:
    print("\n\n⏹️  Teste cancelado pelo usuário.")
    sys.exit(0)

# Cenários de teste
test_cases = [
    {
        "name": "Lead com nome completo e interesse",
        "message": "Oi, meu nome é João Silva, quero informações sobre apartamentos para investir",
        "phone": "5541999999991",
        "should_register": True
    },
    {
        "name": "Lead com nome e interesse em investimento",
        "message": "Me chamo Maria Santos, tenho R$ 300 mil para investir em imóveis",
        "phone": "5541999999992",
        "should_register": True
    },
    {
        "name": "Lead apenas perguntando (NÃO deve registrar)",
        "message": "Quanto custa?",
        "phone": "5541999999993",
        "should_register": False
    }
]

print(f"\n   Total de casos de teste: {len(test_cases)}")
print("   " + "-"*70)

for i, test_case in enumerate(test_cases, 1):
    print(f"\n   📌 Caso {i}: {test_case['name']}")
    print(f"      Mensagem: '{test_case['message']}'")
    print(f"      Telefone: {test_case['phone']}")
    print(f"      Deve registrar: {'SIM' if test_case['should_register'] else 'NÃO'}")
    
    try:
        # Simular contexto vazio (primeira mensagem)
        context = []
        
        # Lead data básico
        lead_data = {
            'telefone': test_case['phone'],
            'empreendimento': 'Teste',
            'nome': ''
        }
        
        print(f"\n      🤖 Enviando para OpenAI...")
        
        # Gerar resposta
        response = openai_service.gerar_resposta(
            message=test_case['message'],
            phone=test_case['phone'],
            context=context,
            lead_data=lead_data,
            supabase_service=None  # Não precisa para teste
        )
        
        print(f"      ✅ Resposta gerada!")
        print(f"\n      💬 Resposta da IA:")
        print(f"      {response}")
        
        if test_case['should_register']:
            print(f"\n      ✨ Se function calling funcionou, o lead foi registrado no C2S!")
        else:
            print(f"\n      ✨ Neste caso, NÃO deve ter registrado lead.")
        
        print("      " + "-"*70)
        
    except Exception as e:
        print(f"\n      ❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        print("      " + "-"*70)
        continue

print("\n" + "="*80)
print("✅ TESTES CONCLUÍDOS!")
print("="*80)

print("\n📌 PRÓXIMOS PASSOS:")
print("   1. Verifique no dashboard do Contact2Sale se os leads foram criados")
print("   2. Deve ter 2 leads: 'João Silva' e 'Maria Santos'")
print("   3. NÃO deve ter lead apenas com telefone 5541999999993")
print("   4. Delete os leads de teste")
print("   5. Se tudo ok, faça o deploy!")

print("\n⚠️  IMPORTANTE:")
print("   Se os leads NÃO foram criados, verifique:")
print("   - Logs do OpenAI (deve aparecer: '🎯 Function call detectado')")
print("   - Token do Contact2Sale (pode ter expirado)")
print("   - Company ID e Seller ID estão corretos")
