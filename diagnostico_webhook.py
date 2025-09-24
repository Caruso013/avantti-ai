#!/usr/bin/env python3
"""
Script para verificar e configurar webhook no Z-API
"""
import os
import requests
import json
from dotenv import load_dotenv

# Carrega variáveis
load_dotenv()

def verificar_webhook():
    """Verifica configuração atual do webhook"""
    
    # Dados do Z-API
    instance = os.getenv('ZAPI_INSTANCE')
    token = os.getenv('ZAPI_TOKEN')
    
    if not instance or not token:
        print("❌ ERRO: ZAPI_INSTANCE ou ZAPI_TOKEN não configurados")
        return
    
    print("🔍 VERIFICANDO WEBHOOK Z-API...")
    print(f"Instance: {instance}")
    print(f"Token: {token[:20]}...")
    print("")
    
    # URL da API
    url = f"https://api.z-api.io/instances/{instance}/token/{token}/webhook"
    
    try:
        # Faz requisição
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ WEBHOOK CONFIGURADO:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verifica se está apontando para o endpoint correto
            webhook_url = data.get('value', '')
            if '/message_receive' in webhook_url:
                print("✅ Webhook apontando para /message_receive")
            else:
                print("⚠️  Webhook NÃO está apontando para /message_receive")
                print(f"Atual: {webhook_url}")
                print("Esperado: deve conter '/message_receive'")
        else:
            print(f"❌ ERRO na requisição: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ ERRO na requisição: {e}")

def configurar_webhook():
    """Configura webhook para o endpoint correto"""
    
    # Dados do Z-API
    instance = os.getenv('ZAPI_INSTANCE')
    token = os.getenv('ZAPI_TOKEN')
    
    if not instance or not token:
        print("❌ ERRO: ZAPI_INSTANCE ou ZAPI_TOKEN não configurados")
        return
    
    # URL do webhook (baseado nas imagens do EasyPanel)
    webhook_url = "https://avantti-avantti-ai-kb4vlo.easypanel.host/message_receive"
    
    print("🔧 CONFIGURANDO WEBHOOK...")
    print(f"URL: {webhook_url}")
    print("")
    
    # URL da API
    url = f"https://api.z-api.io/instances/{instance}/token/{token}/webhook"
    
    # Dados do webhook
    payload = {
        "value": webhook_url,
        "enabled": True,
        "webhookByEvents": False
    }
    
    try:
        # Faz requisição POST
        response = requests.post(url, json=payload)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ WEBHOOK CONFIGURADO COM SUCESSO!")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ ERRO ao configurar: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ ERRO na requisição: {e}")

def testar_webhook():
    """Testa se o webhook está recebendo mensagens"""
    
    print("🧪 TESTE DE WEBHOOK...")
    print("Envie uma mensagem de teste para o WhatsApp e verifique os logs")
    print("")
    
    # Simula uma requisição de webhook
    webhook_url = "http://127.0.0.1:5001/message_receive"
    
    test_payload = {
        "phone": "5511999999999",
        "fromMe": False,
        "message": {
            "conversation": "Teste de webhook"
        }
    }
    
    try:
        response = requests.post(webhook_url, json=test_payload)
        print(f"Teste local - Status: {response.status_code}")
        print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"❌ ERRO no teste local: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("🔍 DIAGNÓSTICO WEBHOOK Z-API - AVANTTI AI V4")
    print("=" * 50)
    print("")
    
    # Menu
    print("Escolha uma opção:")
    print("1. Verificar webhook atual")
    print("2. Configurar webhook")
    print("3. Teste local")
    print("4. Fazer tudo")
    print("")
    
    opcao = input("Digite a opção (1-4): ").strip()
    
    if opcao == "1":
        verificar_webhook()
    elif opcao == "2":
        configurar_webhook()
    elif opcao == "3":
        testar_webhook()
    elif opcao == "4":
        verificar_webhook()
        print("\n" + "="*50 + "\n")
        configurar_webhook()
        print("\n" + "="*50 + "\n")
        testar_webhook()
    else:
        print("❌ Opção inválida")
    
    print("\n" + "=" * 50)
    print("🏁 DIAGNÓSTICO FINALIZADO")
    print("=" * 50)