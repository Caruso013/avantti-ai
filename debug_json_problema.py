#!/usr/bin/env python3
"""
Teste de debugging para o problema específico do JSON sendo enviado.
Vamos simular exatamente o que está acontecendo.
"""

import os
import sys
import time

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def carregar_variaveis_env():
    """Carrega variáveis do .env"""
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("✅ Variáveis .env carregadas")

def testar_problema_real():
    """Testa com o JSON exato que está sendo enviado aos clientes"""
    print("\n🐛 TESTANDO PROBLEMA REAL - JSON SENDO ENVIADO")
    print("-" * 60)
    
    try:
        from src.services.openai_service import OpenAIService
        
        openai_service = OpenAIService()
        
        # JSON exato que está aparecendo no WhatsApp do cliente
        json_problematico = '''{ "reply": "Olá! Como posso te ajudar hoje?", "c2s": { "observations": "=== QUALIFICAÇÃO IA - ELIANE ===\\nData:[ISO]\\nNome:[]\\nTelefone:[]\\nE-mail:[]\\nEmpreendimento:[]\\nAnúncio:[]\\nFaixa original:[]\\nFinalidade:[]\\nMomento:[]\\nFaixa confirmada:[]\\nPagamento:[]\\nObservações adicionais:[]", "status": "Novo Lead - Qualificado por IA" }, "schedule": { "followup": "30m", "reason": "no_response" } }'''
        
        print(f"🔍 JSON problemático:\n{json_problematico[:100]}...")
        
        # Testa a extração
        resultado = openai_service._extrair_reply_do_json(json_problematico)
        
        print(f"\n📤 Resultado da extração: '{resultado}'")
        
        if resultado == "Olá! Como posso te ajudar hoje?":
            print("✅ Extração funcionou corretamente!")
            return True
        else:
            print("❌ Extração falhou!")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def testar_fluxo_completo_real():
    """Testa o fluxo completo simulando a situação real"""
    print("\n🔄 TESTANDO FLUXO COMPLETO COMO CLIENTE REAL")
    print("-" * 60)
    
    try:
        from src.handlers.message_handler import MessageHandler
        
        # Simula uma mensagem real de cliente
        handler = MessageHandler()
        
        # Dados que simulariam uma primeira mensagem
        data_entrada = {
            'phone': '5541999626255',  # Número do print
            'message': {'text': 'Ola'}  # Mensagem simples do cliente
        }
        
        print(f"📞 Telefone: {data_entrada['phone']}")
        print(f"💬 Mensagem: {data_entrada['message']['text']}")
        
        # Executa o processamento (isso vai até a OpenAI e volta)
        print("\n⏳ Processando mensagem...")
        inicio = time.time()
        
        # Chama o método que processa mensagem de texto
        handler.processar_mensagem_texto(data_entrada)
        
        tempo = time.time() - inicio
        print(f"⏱️  Tempo total: {tempo:.2f}s")
        print("✅ Processamento concluído")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no fluxo completo: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_step_by_step():
    """Debug passo a passo para entender onde está falhando"""
    print("\n🔧 DEBUG PASSO A PASSO")
    print("-" * 60)
    
    try:
        from src.services.openai_service import OpenAIService
        
        openai_service = OpenAIService()
        
        # Simula o que a OpenAI retornaria
        resposta_openai = '''{ "reply": "Olá! Como posso te ajudar hoje?", "c2s": { "observations": "=== QUALIFICAÇÃO IA - ELIANE ===\\nData:[ISO]\\nNome:[]\\nTelefone:[]\\nE-mail:[]\\nEmpreendimento:[]\\nAnúncio:[]\\nFaixa original:[]\\nFinalidade:[]\\nMomento:[]\\nFaixa confirmada:[]\\nPagamento:[]\\nObservações adicionais:[]", "status": "Novo Lead - Qualificado por IA" }, "schedule": { "followup": "30m", "reason": "no_response" } }'''
        
        print("📥 1. Resposta da OpenAI:")
        print(f"   {resposta_openai[:80]}...")
        
        print("\n🔍 2. Tentando extrair reply...")
        reply_extraido = openai_service._extrair_reply_do_json(resposta_openai)
        print(f"   Reply extraído: '{reply_extraido}'")
        
        if reply_extraido:
            print("\n✂️  3. Quebrando em mensagens...")
            mensagens = openai_service._quebrar_em_mensagens(reply_extraido)
            print(f"   Número de mensagens: {len(mensagens)}")
            for i, msg in enumerate(mensagens, 1):
                print(f"   {i}. {msg}")
            
            print("✅ O sistema DEVERIA funcionar corretamente!")
            
            # Vamos ver o que realmente acontece no gerar_resposta
            print("\n🎯 4. Testando gerar_resposta diretamente...")
            resultado_real = openai_service.gerar_resposta(
                message="Ola",
                phone="5541999626255",
                context=None,  # Primeira mensagem
                lead_data=None
            )
            
            print(f"   Resultado real: {resultado_real}")
            
            return True
        else:
            print("❌ Falha na extração!")
            return False
            
    except Exception as e:
        print(f"❌ Erro no debug: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal do debug"""
    print("=" * 70)
    print("🚨 DEBUG PROBLEMA JSON SENDO ENVIADO AOS CLIENTES")
    print("=" * 70)
    
    carregar_variaveis_env()
    
    testes = [
        ("🐛 Problema Real", testar_problema_real),
        ("🔧 Debug Step by Step", debug_step_by_step),
        ("🔄 Fluxo Completo", testar_fluxo_completo_real)
    ]
    
    for nome_teste, funcao_teste in testes:
        print(f"\n{'='*70}")
        print(f"▶️  EXECUTANDO: {nome_teste}")
        print("="*70)
        
        try:
            sucesso = funcao_teste()
            if sucesso:
                print(f"✅ {nome_teste} - PASSOU")
            else:
                print(f"❌ {nome_teste} - FALHOU")
        except Exception as e:
            print(f"❌ {nome_teste} - ERRO: {e}")

if __name__ == "__main__":
    main()