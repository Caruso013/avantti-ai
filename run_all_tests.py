"""
Script principal para executar todos os testes locais antes do deploy

Execute: python run_all_tests.py
"""

import subprocess
import sys

print("="*80)
print("🧪 EXECUTANDO TODOS OS TESTES LOCAIS")
print("="*80)

testes = [
    {
        "nome": "1️⃣  Integração Contact2Sale",
        "arquivo": "test_contact2sale_integration.py",
        "descricao": "Testa se o Contact2SaleClient funciona corretamente"
    },
    {
        "nome": "2️⃣  Correção de Alucinações",
        "arquivo": "test_alucinacoes.py",
        "descricao": "Verifica se a IA NÃO inventa informações sobre imóveis"
    },
    {
        "nome": "3️⃣  Function Calling OpenAI",
        "arquivo": "test_openai_function_calling.py",
        "descricao": "Testa se o registrar_lead é chamado corretamente"
    }
]

print("\n📋 Testes disponíveis:\n")
for teste in testes:
    print(f"   {teste['nome']}")
    print(f"      {teste['descricao']}")
    print()

print("="*80)
print("\n⚠️  ATENÇÃO:")
print("   - Os testes 1 e 3 vão CRIAR LEADS REAIS no Contact2Sale")
print("   - Você precisará DELETAR os leads de teste manualmente")
print("   - O teste 2 (Alucinações) não cria leads")
print()
print("📌 RECOMENDAÇÃO:")
print("   Execute os testes na seguinte ordem:")
print("   1. Teste de Alucinações (seguro, não cria leads)")
print("   2. Integração Contact2Sale (cria 1 lead de teste)")
print("   3. Function Calling OpenAI (cria 2-3 leads de teste)")
print()
print("="*80)

print("\n❓ Deseja executar todos os testes automaticamente?")
print("   [1] Sim, executar todos")
print("   [2] Não, vou executar manualmente")
print("   [3] Executar apenas teste de Alucinações (seguro)")

try:
    escolha = input("\n   Sua escolha [1/2/3]: ").strip()
except KeyboardInterrupt:
    print("\n\n⏹️  Cancelado pelo usuário.")
    sys.exit(0)

if escolha == "1":
    print("\n🚀 Executando todos os testes...\n")
    print("="*80)
    
    for teste in testes:
        print(f"\n{'='*80}")
        print(f"▶️  Executando: {teste['nome']}")
        print(f"{'='*80}\n")
        
        try:
            result = subprocess.run(
                [sys.executable, teste['arquivo']],
                capture_output=False,
                text=True
            )
            
            if result.returncode != 0:
                print(f"\n⚠️  Teste '{teste['nome']}' falhou ou foi cancelado")
        except Exception as e:
            print(f"\n❌ Erro ao executar teste: {e}")
    
    print("\n" + "="*80)
    print("✅ TODOS OS TESTES EXECUTADOS!")
    print("="*80)

elif escolha == "3":
    print("\n🚀 Executando apenas teste de Alucinações...\n")
    print("="*80)
    
    try:
        subprocess.run([sys.executable, "test_alucinacoes.py"])
    except Exception as e:
        print(f"\n❌ Erro: {e}")

else:
    print("\n📝 Execute os testes manualmente:")
    print()
    for teste in testes:
        print(f"   python {teste['arquivo']}")
    print()
    print("="*80)

print("\n📌 APÓS OS TESTES:")
print("   1. Verifique os resultados acima")
print("   2. Se tudo OK, acesse o dashboard do Contact2Sale")
print("   3. Delete os leads de teste criados")
print("   4. Faça o commit e push:")
print("      git add -A")
print("      git commit -m '✅ Testes locais passaram - pronto para deploy'")
print("      git push origin final-clean")
print("   5. Deploy no Easypanel")
print()
