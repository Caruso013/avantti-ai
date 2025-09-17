import requests
import time
import json

# URL do webhook local
webhook_url = "http://localhost:5000/message_receive"

# Dados de teste simulando mensagens do Z-API
test_messages = [
    {
        "text": {"message": "Oi"},
        "phone": "5511999999999",
        "fromMe": False
    },
    {
        "text": {"message": "Tenho interesse no apartamento"},
        "phone": "5511999999999", 
        "fromMe": False
    },
    {
        "text": {"message": "Gostaria de mais informações"},
        "phone": "5511999999999",
        "fromMe": False
    },
    {
        "text": {"message": "Qual o valor?"},
        "phone": "5511999999999",
        "fromMe": False
    }
]

def test_queue_system():
    """Testa o sistema de filas enviando mensagens rapidamente"""
    print("🧪 TESTE DO SISTEMA DE FILAS")
    print("=" * 40)
    
    for i, message in enumerate(test_messages, 1):
        print(f"📤 Enviando mensagem {i}: '{message['text']['message']}'")
        
        try:
            response = requests.post(
                webhook_url,
                json=message,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Resposta: {result.get('status')} - {result.get('message')}")
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão: {e}")
            break
        
        # Enviar mensagens rapidamente para testar fila
        time.sleep(0.5)  # 500ms entre mensagens
    
    print("\n⏳ Aguardando processamento das filas...")
    time.sleep(10)  # Aguarda processamento
    print("✅ Teste concluído!")

if __name__ == "__main__":
    print("⚠️  CERTIFIQUE-SE DE QUE O APP ESTÁ RODANDO EM: http://localhost:5000")
    input("Pressione ENTER para continuar...")
    test_queue_system()