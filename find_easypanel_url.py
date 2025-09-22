#!/usr/bin/env python3
"""
Script para encontrar a URL funcional do EasyPanel
"""

import requests

def test_easypanel_urls():
    """Testa URLs possíveis do EasyPanel"""
    
    possible_urls = [
        "https://avantti-ai.easypanel.app",
        "https://avantti-ai.easypanel.io",
        "https://avantti-avantti-ai.easypanel.app", 
        "https://avantti-avantti-ai.easypanel.io",
        "https://avantti-ai-production.easypanel.host",
        "https://avantti-ai.production.easypanel.host",
        "https://avantti-ai.easypanel.host"
    ]
    
    print("=== PROCURANDO URL FUNCIONAL DO EASYPANEL ===")
    print("Testando URLs baseadas no nome do projeto...")
    print("=" * 60)
    
    for url in possible_urls:
        try:
            print(f"\nTestando: {url}")
            response = requests.get(url, timeout=8)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"ENCONTRADO! URL funcional: {url}")
                print(f"Response: {response.text[:100]}...")
                
                # Testa webhook
                print(f"\nTestando webhook: {url}/message_receive")
                webhook_data = {
                    "phone": "5511999999999",
                    "text": {"message": "Teste webhook"},
                    "fromMe": False
                }
                
                webhook_response = requests.post(
                    f"{url}/message_receive",
                    json=webhook_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                print(f"Webhook Status: {webhook_response.status_code}")
                
                if webhook_response.status_code == 200:
                    print("WEBHOOK FUNCIONANDO!")
                    print(f"\nUSE ESTA URL NO Z-API: {url}/message_receive")
                    return url
                    
            elif response.status_code == 404:
                print("URL nao encontrada")
            else:
                print(f"Erro: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("Conexao recusada")
        except requests.exceptions.Timeout:
            print("Timeout")
        except Exception as e:
            print(f"Erro: {str(e)[:50]}...")
    
    print("\n" + "=" * 60)
    print("Nenhuma URL funcional encontrada.")
    print("Verifique no painel do EasyPanel a URL exata do seu app.")
    return None

if __name__ == "__main__":
    test_easypanel_urls()