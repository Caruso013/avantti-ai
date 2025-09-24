#!/usr/bin/env python3
"""
Testa conectividade com o domínio público
"""
import requests
import json

def testar_dominio():
    """Testa se o domínio público está funcionando"""
    
    base_url = "https://avantti-avantti-ai-kb4vlo.easypanel.host"
    
    print("🌐 TESTANDO CONECTIVIDADE DO DOMÍNIO")
    print(f"URL: {base_url}")
    print("")
    
    # Testa endpoints
    endpoints = [
        "/",
        "/health", 
        "/version",
        "/message_receive"
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"🔍 Testando: {url}")
        
        try:
            if endpoint == "/message_receive":
                # POST para webhook
                test_data = {
                    "phone": "5511999999999",
                    "fromMe": False,
                    "message": {"conversation": "teste"}
                }
                response = requests.post(url, json=test_data, timeout=10)
            else:
                # GET para outros
                response = requests.get(url, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Resposta: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                except:
                    print(f"   Resposta: {response.text[:200]}...")
            else:
                print(f"   Erro: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print("   ❌ TIMEOUT - Aplicação pode não estar rodando")
        except requests.exceptions.ConnectionError:
            print("   ❌ CONEXÃO FALHOU - Domínio não está acessível")
        except Exception as e:
            print(f"   ❌ ERRO: {e}")
        
        print("")

def configurar_webhook_manual():
    """Configura webhook manualmente via curl"""
    
    instance = "3E6CCAC06181F057FAF2FEB82DDB19DD"
    token = "6B9781EB4F5A6A745400BEC7"
    webhook_url = "https://avantti-avantti-ai-kb4vlo.easypanel.host/message_receive"
    
    curl_command = f'''curl -X POST "https://api.z-api.io/instances/{instance}/token/{token}/webhook" \\
-H "Content-Type: application/json" \\
-d '{{"value": "{webhook_url}", "enabled": true, "webhookByEvents": false}}'
'''
    
    print("🔧 COMANDO CURL PARA CONFIGURAR WEBHOOK:")
    print("")
    print(curl_command)
    print("")

if __name__ == "__main__":
    print("=" * 60)
    print("🌐 TESTE DE CONECTIVIDADE - AVANTTI AI V4")
    print("=" * 60)
    print("")
    
    testar_dominio()
    
    print("=" * 60)
    configurar_webhook_manual()
    print("=" * 60)