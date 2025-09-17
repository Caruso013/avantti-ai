#!/usr/bin/env python3
"""
Teste do fluxo completo: contexto + function calls + notificações
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_message_endpoint():
    """Testa o endpoint de mensagens com contexto"""
    
    # URL do endpoint local
    url = "http://localhost:5000/message_receive"
    
    # Simula uma mensagem do WhatsApp
    test_payload = {
        "phone": "5511999888777",
        "text": {
            "message": "Oi, vi o anúncio do apartamento no Facebook"
        },
        "fromMe": False
    }
    
    print("=== TESTE FLUXO COMPLETO ===")
    print(f"Enviando mensagem: {test_payload['text']['message']}")
    print(f"Telefone: {test_payload['phone']}")
    
    try:
        response = requests.post(url, json=test_payload, timeout=30)
        
        print(f"\nStatus HTTP: {response.status_code}")
        print(f"Resposta: {response.json()}")
        
        if response.status_code == 200:
            print("\n✅ SUCESSO: Mensagem processada")
        else:
            print("\n❌ ERRO: Falha no processamento")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Servidor não está rodando")
        print("Execute: python app.py")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")

def test_supabase_connection():
    """Testa conexão com Supabase"""
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ ERRO: Configurações do Supabase não encontradas")
        return False
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Testa conexão
        url = f"{supabase_url}/rest/v1/customers?limit=1"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("✅ SUCESSO: Conexão com Supabase OK")
            return True
        else:
            print(f"❌ ERRO: Supabase retornou {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERRO: Falha na conexão com Supabase: {e}")
        return False

def test_openai_connection():
    """Testa conexão com OpenAI"""
    
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_key:
        print("❌ ERRO: OPENAI_API_KEY não encontrada")
        return False
    
    headers = {
        'Authorization': f'Bearer {openai_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "teste"}],
        "max_tokens": 5
    }
    
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ SUCESSO: Conexão com OpenAI OK")
            return True
        else:
            print(f"❌ ERRO: OpenAI retornou {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ ERRO: Falha na conexão com OpenAI: {e}")
        return False

if __name__ == "__main__":
    print("=== TESTE DE CONFIGURAÇÕES ===")
    
    # Testa conexões
    supabase_ok = test_supabase_connection()
    openai_ok = test_openai_connection()
    
    if supabase_ok and openai_ok:
        print("\n=== TESTANDO ENDPOINT ===")
        test_message_endpoint()
    else:
        print("\n❌ Verifique as configurações antes de testar o endpoint")