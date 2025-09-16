#!/usr/bin/env python3
"""
Teste de webhook Z-API para verificar se está funcionando corretamente
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_webhook_url(webhook_url):
    """Testa se o webhook está respondendo"""
    print(f"🧪 Testando webhook: {webhook_url}")
    
    # Payload de teste simulando Z-API
    test_payload = {
        "phone": "5511999999999",
        "isGroup": False,
        "status": "RECEIVED",
        "text": {
            "message": "Teste de webhook - Z-API funcionando!"
        },
        "timestamp": 1726502610,
        "messageId": "webhook_test_123"
    }
    
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(webhook_url, json=test_payload, headers=headers, timeout=30)
        
        print(f"📟 Status HTTP: {response.status_code}")
        print(f"📄 Resposta: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook funcionando corretamente!")
            return True
        else:
            print("❌ Webhook com problemas!")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar webhook: {e}")
        return False

def test_health_endpoint(base_url):
    """Testa o endpoint de saúde"""
    health_url = f"{base_url}/health"
    print(f"🏥 Testando health check: {health_url}")
    
    try:
        response = requests.get(health_url, timeout=10)
        print(f"📟 Status: {response.status_code}")
        print(f"📄 Resposta: {response.text}")
        
        if response.status_code == 200:
            print("✅ Aplicação funcionando!")
            return True
        else:
            print("❌ Aplicação com problemas!")
            return False
            
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False

def main():
    print("🚀 Teste de Webhook Z-API\n")
    
    # Solicita a URL do EasyPanel
    print("📝 Para configurar o webhook, preciso da URL do seu app no EasyPanel.")
    print("💡 Exemplo: https://meu-projeto.easypanel.host")
    
    app_url = input("\n🌐 Digite a URL do seu app no EasyPanel: ").strip()
    
    if not app_url:
        print("❌ URL é obrigatória!")
        return
    
    # Remove barra final se existir
    app_url = app_url.rstrip('/')
    
    # Testa health check primeiro
    print("\n" + "="*50)
    health_ok = test_health_endpoint(app_url)
    
    if not health_ok:
        print("\n⚠️ A aplicação não está respondendo.")
        print("📋 Verifique se o deploy foi concluído no EasyPanel.")
        return
    
    # Testa webhook
    print("\n" + "="*50)
    webhook_url = f"{app_url}/message_receive"
    webhook_ok = test_webhook_url(webhook_url)
    
    # Mostra configuração do webhook
    print("\n" + "="*50)
    print("📋 CONFIGURAÇÃO DO WEBHOOK Z-API:")
    print(f"🌐 URL: {webhook_url}")
    print("📡 Método: POST")
    print("📄 Content-Type: application/json")
    print("📨 Eventos: message (mensagens recebidas)")
    print("🔛 Status: Ativo")
    
    if webhook_ok:
        print("\n🎉 Webhook configurado e funcionando!")
        print("\n📱 Como testar:")
        print("1. Configure o webhook no painel Z-API com a URL acima")
        print("2. Envie uma mensagem para o número da sua instância Z-API")
        print("3. Verifique se recebe uma resposta do assistente AI")
    else:
        print("\n⚠️ Webhook com problemas. Verifique:")
        print("- Se o deploy foi concluído")
        print("- Se a URL está correta")
        print("- Se não há erros nos logs do EasyPanel")

if __name__ == "__main__":
    main()