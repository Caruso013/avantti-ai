#!/usr/bin/env python3
"""
Teste específico para Z-API
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clients.zapi_client import ZAPIClient

def test_zapi_connection():
    """Testa a conexão com a Z-API"""
    print("🧪 Testando conexão Z-API...")
    
    # Verifica as variáveis de ambiente
    base_url = os.getenv("ZAPI_BASE_URL")
    instance_id = os.getenv("ZAPI_INSTANCE_ID")
    instance_token = os.getenv("ZAPI_INSTANCE_TOKEN")
    client_token = os.getenv("ZAPI_CLIENT_TOKEN")
    
    print(f"📍 Base URL: {base_url}")
    print(f"📍 Instance ID: {instance_id}")
    print(f"📍 Instance Token: {instance_token[:10]}..." if instance_token else "❌ Token não encontrado")
    print(f"📍 Client Token: {client_token[:10]}..." if client_token else "❌ Client Token não encontrado")
    
    if not all([base_url, instance_id, instance_token, client_token]):
        print("❌ Configurações Z-API incompletas!")
        return False
    
    # Testa status da instância
    try:
        url = f"{base_url}/instances/{instance_id}/token/{instance_token}/status"
        headers = {
            "Content-Type": "application/json",
            "Client-Token": client_token
        }
        
        print(f"🔗 Testando: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"📟 Status HTTP: {response.status_code}")
        print(f"📄 Resposta: {response.text}")
        
        if response.status_code == 200:
            print("✅ Conexão Z-API OK!")
            return True
        else:
            print("❌ Erro na conexão Z-API!")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar Z-API: {e}")
        return False

def test_zapi_send_message():
    """Testa envio de mensagem via Z-API"""
    print("\n📱 Testando envio de mensagem...")
    
    # Número de teste (substitua pelo seu número)
    test_phone = "5511999999999"  # ALTERE PARA SEU NÚMERO
    test_message = "🤖 Teste do Avantti AI - Z-API funcionando!"
    
    print(f"📞 Enviando para: {test_phone}")
    print(f"💬 Mensagem: {test_message}")
    
    try:
        client = ZAPIClient()
        result = client.send_message(test_phone, test_message)
        
        if result:
            print("✅ Mensagem enviada com sucesso!")
            return True
        else:
            print("❌ Falha ao enviar mensagem!")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
        return False

def simulate_webhook_message():
    """Simula uma mensagem recebida via webhook"""
    print("\n🔗 Simulando webhook Z-API...")
    
    # Payload simulado da Z-API
    webhook_payload = {
        "phone": "5511999999999",  # Número que está enviando
        "isGroup": False,
        "status": "RECEIVED",
        "text": {
            "message": "Oi, quero saber mais sobre o produto!"
        },
        "timestamp": 1726502610,
        "messageId": "test_message_id"
    }
    
    try:
        # Testa endpoint local
        url = "http://localhost:5000/message_receive"
        headers = {"Content-Type": "application/json"}
        
        print(f"🔗 Enviando para: {url}")
        print(f"📄 Payload: {json.dumps(webhook_payload, indent=2)}")
        
        response = requests.post(url, json=webhook_payload, headers=headers, timeout=10)
        
        print(f"📟 Status: {response.status_code}")
        print(f"📄 Resposta: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook processado com sucesso!")
            return True
        else:
            print("❌ Erro no processamento do webhook!")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao simular webhook: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes Z-API\n")
    
    # Teste 1: Conexão
    connection_ok = test_zapi_connection()
    
    # Teste 2: Envio de mensagem (opcional)
    send_ok = False
    if connection_ok:
        print("\n" + "="*50)
        test_send = input("❓ Deseja testar envio de mensagem? (s/n): ").lower().strip()
        if test_send in ['s', 'sim', 'y', 'yes']:
            phone = input("📞 Digite seu número (formato: 5511999999999): ").strip()
            if phone:
                # Atualiza o número de teste
                global test_phone
                test_phone = phone
                send_ok = test_zapi_send_message()
    
    # Teste 3: Webhook simulado
    print("\n" + "="*50)
    webhook_ok = simulate_webhook_message()
    
    # Resumo
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES:")
    print(f"🔗 Conexão Z-API: {'✅ OK' if connection_ok else '❌ FALHA'}")
    print(f"📱 Envio mensagem: {'✅ OK' if send_ok else '❌ FALHA' if connection_ok else '⏭️ PULADO'}")
    print(f"🔗 Webhook simulado: {'✅ OK' if webhook_ok else '❌ FALHA'}")
    
    if connection_ok:
        print("\n🎉 Z-API configurada corretamente!")
        print("📝 Próximos passos:")
        print("   1. Configure o webhook no painel Z-API")
        print("   2. Use a URL: https://sua-app.easypanel.host/message_receive")
    else:
        print("\n⚠️ Verifique as configurações Z-API no arquivo .env")

if __name__ == "__main__":
    main()