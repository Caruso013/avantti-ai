"""
Script de teste local para validar integração com Contact2Sale

Este script testa:
1. Import do Contact2SaleClient
2. Instanciação com variáveis de ambiente
3. Criação de lead com dados de teste
4. Validação da resposta

Execute: python test_contact2sale_integration.py
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

print("="*80)
print("🧪 TESTE DE INTEGRAÇÃO - CONTACT2SALE")
print("="*80)

# Teste 1: Verificar variáveis de ambiente
print("\n📋 Teste 1: Verificando variáveis de ambiente...")
required_vars = {
    'CONTACT2SALE_JWT_TOKEN': os.getenv('CONTACT2SALE_JWT_TOKEN'),
    'CONTACT2SALE_COMPANY_ID': os.getenv('CONTACT2SALE_COMPANY_ID'),
    'CONTACT2SALE_SELLER_ID': os.getenv('CONTACT2SALE_SELLER_ID')
}

missing_vars = []
for var_name, var_value in required_vars.items():
    if var_value:
        print(f"   ✅ {var_name}: {'*' * 10} (configurado)")
    else:
        print(f"   ❌ {var_name}: NÃO CONFIGURADO")
        missing_vars.append(var_name)

if missing_vars:
    print(f"\n❌ ERRO: Variáveis faltando no .env:")
    for var in missing_vars:
        print(f"   - {var}")
    print("\n💡 Adicione essas variáveis no arquivo .env")
    sys.exit(1)

# Teste 2: Import do Contact2SaleClient
print("\n📦 Teste 2: Importando Contact2SaleClient...")
try:
    from clients.contact2sale_client import Contact2SaleClient, LeadData
    print("   ✅ Import bem-sucedido!")
except Exception as e:
    print(f"   ❌ Erro no import: {e}")
    sys.exit(1)

# Teste 3: Instanciar o cliente
print("\n🔧 Teste 3: Instanciando Contact2SaleClient...")
try:
    c2s_client = Contact2SaleClient(
        jwt_token=os.getenv('CONTACT2SALE_JWT_TOKEN'),
        company_id=os.getenv('CONTACT2SALE_COMPANY_ID'),
        seller_id=os.getenv('CONTACT2SALE_SELLER_ID')
    )
    print("   ✅ Cliente instanciado com sucesso!")
except Exception as e:
    print(f"   ❌ Erro ao instanciar: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Teste 4: Criar lead de teste
print("\n📝 Teste 4: Criando lead de teste...")
print("   ATENÇÃO: Este teste vai CRIAR UM LEAD REAL no Contact2Sale!")
print("   Pressione Enter para continuar ou Ctrl+C para cancelar...")

try:
    input()
except KeyboardInterrupt:
    print("\n\n⏹️  Teste cancelado pelo usuário.")
    sys.exit(0)

lead_teste = LeadData(
    name="TESTE - João Silva (IA Bot)",
    phone="5541999999999",
    email="teste.ia.bot@example.com",
    source="WhatsApp Bot - Avantti AI (TESTE)",
    observation="=== TESTE DE INTEGRAÇÃO ===\nData: 2025-10-10\nLead criado automaticamente pelo script de teste.\nPode ser deletado."
)

print(f"\n   Dados do lead de teste:")
print(f"   - Nome: {lead_teste.name}")
print(f"   - Telefone: {lead_teste.phone}")
print(f"   - Email: {lead_teste.email}")
print(f"   - Fonte: {lead_teste.source}")

try:
    response = c2s_client.create_lead(lead_teste)
    
    if response:
        print("\n   ✅ Lead criado com SUCESSO!")
        print(f"\n   📊 Resposta do Contact2Sale:")
        print(f"   {response}")
        
        # Verificar se tem ID no response
        if isinstance(response, dict) and 'id' in response:
            print(f"\n   🆔 ID do lead: {response['id']}")
        
        print("\n   ✨ INTEGRAÇÃO FUNCIONANDO PERFEITAMENTE!")
        print("\n   📌 PRÓXIMO PASSO:")
        print("      1. Acesse o dashboard do Contact2Sale")
        print("      2. Verifique se o lead 'TESTE - João Silva (IA Bot)' apareceu")
        print("      3. Se aparecer, delete-o (é apenas um teste)")
        print("      4. Se tudo ok, faça o deploy: git push origin final-clean")
        
    else:
        print("\n   ⚠️  Lead criado, mas resposta vazia")
        print("      Verifique no dashboard do Contact2Sale se o lead foi criado")
        
except Exception as e:
    print(f"\n   ❌ Erro ao criar lead: {e}")
    import traceback
    print("\n   Stack trace completo:")
    traceback.print_exc()
    
    print("\n   🔍 POSSÍVEIS CAUSAS:")
    print("      1. JWT Token inválido ou expirado")
    print("      2. Company ID ou Seller ID incorretos")
    print("      3. API do Contact2Sale fora do ar")
    print("      4. Formato do payload incompatível")
    
    sys.exit(1)

print("\n" + "="*80)
print("✅ TESTE CONCLUÍDO!")
print("="*80)
