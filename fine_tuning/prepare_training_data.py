"""
Script para preparar dados de treinamento para fine-tuning do GPT-4o-mini

Este script converte conversas reais do Supabase em formato JSONL para fine-tuning.
"""

import json
import os
from datetime import datetime
from dotenv import load_dotenv
import sys

# Adicionar path do projeto
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from clients.supabase_client import SupabaseClient

load_dotenv()

class TrainingDataPreparer:
    def __init__(self):
        self.supabase = SupabaseClient()
        
        # System prompt atual da Eliane
        self.system_prompt = """# 1. Identidade
- **Nome:** Eliane
- **Função:** SDR (pré-vendas) da **Evex Imóveis**
- **Estilo de comunicação:**
- Tom formal-casual
- Simpática e humana (evitar parecer robô)
- Não envie mensagens com emojis!
- Frases curtas, objetivas
- Gatilhos de venda sutis e palavras-chave de conversão

# 2. Contexto da Empresa
- **Evex Imóveis:** imobiliária especializada em empreendimentos residenciais
- **Fonte dos leads:** anúncios Meta/Facebook
- **Canal:** WhatsApp/SMS (Z-API)

# 3. Fluxo de Qualificação CONTEXTUAL
REGRA FUNDAMENTAL: SEMPRE ANALISE O CONTEXTO ANTES DE RESPONDER

⚠️ RESTRIÇÃO CRÍTICA: NUNCA INVENTE INFORMAÇÕES!

Objetivo: Qualificar leads e registrar dados completos (nome + telefone + interesse) para vendedores."""
    
    def buscar_conversas_supabase(self, limit=100):
        """Busca conversas do banco de dados"""
        try:
            response = self.supabase.client.table('conversations')\
                .select('*')\
                .order('created_at', desc=False)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            print(f"❌ Erro ao buscar conversas: {e}")
            return []
    
    def agrupar_por_telefone(self, conversas):
        """Agrupa conversas por número de telefone"""
        grupos = {}
        
        for msg in conversas:
            phone = msg.get('phone', 'unknown')
            if phone not in grupos:
                grupos[phone] = []
            grupos[phone].append(msg)
        
        return grupos
    
    def converter_para_formato_openai(self, conversas_agrupadas):
        """Converte conversas agrupadas em formato JSONL para fine-tuning"""
        exemplos = []
        
        for phone, mensagens in conversas_agrupadas.items():
            # Pular conversas muito curtas (menos de 3 mensagens)
            if len(mensagens) < 3:
                continue
            
            # Criar exemplo de treinamento
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            for msg in mensagens:
                role = msg.get('role', 'user')
                text = msg.get('text', '').strip()
                
                if text:  # Só adicionar se tiver texto
                    if role in ['user', 'assistant']:
                        messages.append({
                            "role": role,
                            "content": text
                        })
            
            # Só adicionar se tiver pelo menos 1 user e 1 assistant
            if len(messages) > 2:
                exemplos.append({
                    "messages": messages
                })
        
        return exemplos
    
    def salvar_jsonl(self, exemplos, output_file='training_data.jsonl'):
        """Salva exemplos em arquivo JSONL"""
        output_path = os.path.join(os.path.dirname(__file__), output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for exemplo in exemplos:
                f.write(json.dumps(exemplo, ensure_ascii=False) + '\n')
        
        print(f"✅ {len(exemplos)} exemplos salvos em: {output_path}")
        return output_path
    
    def validar_formato(self, exemplos):
        """Valida se os exemplos estão no formato correto"""
        print("\n📊 Validando formato dos dados...")
        
        total_messages = 0
        total_tokens_estimate = 0
        
        for i, exemplo in enumerate(exemplos):
            messages = exemplo.get('messages', [])
            
            # Contar mensagens
            total_messages += len(messages)
            
            # Estimar tokens (aproximadamente 4 chars = 1 token)
            for msg in messages:
                content = msg.get('content', '')
                total_tokens_estimate += len(content) // 4
            
            # Validar estrutura
            if not messages:
                print(f"⚠️  Exemplo {i+1}: Sem mensagens")
                continue
            
            # Verificar se tem system prompt
            if messages[0].get('role') != 'system':
                print(f"⚠️  Exemplo {i+1}: Sem system prompt")
            
            # Verificar alternância user/assistant
            roles = [msg.get('role') for msg in messages[1:]]
            if not all(role in ['user', 'assistant'] for role in roles):
                print(f"⚠️  Exemplo {i+1}: Roles inválidos")
        
        print(f"\n📈 Estatísticas:")
        print(f"   - Total de exemplos: {len(exemplos)}")
        print(f"   - Total de mensagens: {total_messages}")
        print(f"   - Média de mensagens/exemplo: {total_messages/len(exemplos):.1f}")
        print(f"   - Tokens estimados: ~{total_tokens_estimate:,}")
        print(f"   - Custo estimado de treinamento: ~${total_tokens_estimate * 0.008 / 1000:.2f}")
        
        return True
    
    def executar(self, limit=100, output_file='training_data.jsonl'):
        """Executa todo o pipeline de preparação"""
        print("🚀 Iniciando preparação de dados para fine-tuning...\n")
        
        # 1. Buscar conversas
        print(f"📥 Buscando {limit} conversas do Supabase...")
        conversas = self.buscar_conversas_supabase(limit)
        print(f"   ✅ {len(conversas)} mensagens encontradas")
        
        # 2. Agrupar por telefone
        print("\n📞 Agrupando por telefone...")
        grupos = self.agrupar_por_telefone(conversas)
        print(f"   ✅ {len(grupos)} conversas únicas")
        
        # 3. Converter para formato OpenAI
        print("\n🔄 Convertendo para formato JSONL...")
        exemplos = self.converter_para_formato_openai(grupos)
        print(f"   ✅ {len(exemplos)} exemplos criados")
        
        # 4. Validar formato
        self.validar_formato(exemplos)
        
        # 5. Salvar arquivo
        print("\n💾 Salvando arquivo JSONL...")
        output_path = self.salvar_jsonl(exemplos, output_file)
        
        print("\n✨ Preparação concluída!")
        print(f"   Arquivo: {output_path}")
        print(f"\n   Próximo passo: execute 'python fine_tuning/upload_and_train.py'")
        
        return output_path

def main():
    """Função principal"""
    preparer = TrainingDataPreparer()
    
    # Você pode ajustar o limite de conversas aqui
    preparer.executar(limit=200, output_file='training_data.jsonl')

if __name__ == "__main__":
    main()
