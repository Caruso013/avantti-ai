"""
Script de teste para comparar modelo base vs modelo fine-tunado

Este script permite testar e comparar respostas antes de colocar em produção.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ModelComparator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        self.system_prompt = """# 1. Identidade
- **Nome:** Eliane
- **Função:** SDR (pré-vendas) da **Evex Imóveis**
- **Estilo de comunicação:**
- Tom formal-casual
- Simpática e humana (evitar parecer robô)
- Não envie mensagens com emojis!
- Frases curtas, objetivas

# 2. Contexto da Empresa
- **Evex Imóveis:** imobiliária especializada em empreendimentos residenciais
- **Fonte dos leads:** anúncios Meta/Facebook
- **Canal:** WhatsApp/SMS (Z-API)

# 3. Objetivo
Qualificar leads e registrar dados completos (nome + telefone + interesse) para vendedores."""
    
    def testar_modelo(self, model_id, user_message):
        """Testa um modelo com uma mensagem"""
        try:
            response = self.client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ Erro: {e}"
    
    def comparar_modelos(self, base_model, fine_tuned_model, test_messages):
        """Compara respostas entre modelo base e fine-tunado"""
        print("="*80)
        print("🔬 COMPARAÇÃO DE MODELOS")
        print("="*80)
        print(f"\n📊 Modelo Base: {base_model}")
        print(f"✨ Modelo Fine-Tunado: {fine_tuned_model}")
        print("\n" + "="*80)
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n\n{'='*80}")
            print(f"🧪 TESTE #{i}")
            print("="*80)
            print(f"\n👤 Mensagem do usuário:")
            print(f"   {message}")
            
            # Testar modelo base
            print(f"\n🤖 Resposta do Modelo Base ({base_model}):")
            print("-" * 80)
            base_response = self.testar_modelo(base_model, message)
            print(base_response)
            
            # Testar modelo fine-tunado
            print(f"\n✨ Resposta do Modelo Fine-Tunado ({fine_tuned_model}):")
            print("-" * 80)
            fine_tuned_response = self.testar_modelo(fine_tuned_model, message)
            print(fine_tuned_response)
            
            print("\n" + "="*80)
            
            # Solicitar feedback do usuário
            print("\n❓ Qual resposta ficou melhor?")
            print("   1 = Modelo Base")
            print("   2 = Modelo Fine-Tunado")
            print("   3 = Empate")
            print("   Enter = Pular")
            
            try:
                escolha = input("\n   Sua escolha: ").strip()
                if escolha in ['1', '2', '3']:
                    feedback = {
                        '1': "📊 Modelo Base foi melhor",
                        '2': "✨ Modelo Fine-Tunado foi melhor",
                        '3': "🤝 Empate"
                    }
                    print(f"\n   ✅ {feedback[escolha]}")
            except:
                pass

def main():
    """Função principal"""
    print("\n🚀 Iniciando teste de modelos...\n")
    
    # Solicitar ID do modelo fine-tunado
    print("📝 Cole o ID do modelo fine-tunado (ou deixe em branco para pular):")
    fine_tuned_id = input("   Modelo: ").strip()
    
    if not fine_tuned_id:
        print("❌ Nenhum modelo fornecido. Encerrando.")
        return
    
    # Mensagens de teste
    test_messages = [
        "Olá, tenho interesse em apartamentos",
        "Quero saber mais sobre o empreendimento",
        "Qual o valor dos imóveis?",
        "Meu nome é João Silva e quero investir",
        "Tem apartamentos de 2 quartos disponíveis?",
        "Como funciona o financiamento?",
        "Posso agendar uma visita?",
        "Obrigado pela ajuda"
    ]
    
    comparator = ModelComparator()
    comparator.comparar_modelos(
        base_model="gpt-4o-mini",
        fine_tuned_model=fine_tuned_id,
        test_messages=test_messages
    )
    
    print("\n\n" + "="*80)
    print("✅ TESTE CONCLUÍDO!")
    print("="*80)
    print("\n📊 Análise os resultados acima para decidir qual modelo usar.")
    print("\n💡 Dicas:")
    print("   - Se o modelo fine-tunado foi melhor na maioria, use em produção")
    print("   - Se houve empate, considere retreinar com mais dados")
    print("   - Se o modelo base foi melhor, revise a qualidade dos dados de treino")

if __name__ == "__main__":
    main()
