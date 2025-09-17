import requests
import time
import json

# URL do webhook local
webhook_url = "http://localhost:5000/message_receive"

def test_health():
    """Testa se o servidor está funcionando"""
    try:
        response = requests.get("http://localhost:5000/health", timeout=3)
        if response.status_code == 200:
            print("✅ Servidor está funcionando!")
            return True
        else:
            print(f"❌ Servidor retornou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Servidor não está rodando: {e}")
        return False

def test_single_message():
    """Testa uma única mensagem"""
    print("\n🧪 TESTE DE MENSAGEM ÚNICA")
    print("-" * 30)
    
    message = {
        "text": {"message": "Oi, tenho interesse no apartamento"},
        "phone": "5511999999999",
        "fromMe": False
    }
    
    try:
        response = requests.post(webhook_url, json=message, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {result.get('status')}")
            print(f"📝 Mensagem: {result.get('message')}")
            return True
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_multiple_messages():
    """Testa múltiplas mensagens rápidas"""
    print("\n🧪 TESTE DE MÚLTIPLAS MENSAGENS")
    print("-" * 30)
    
    messages = [
        "Oi",
        "Tenho interesse no apartamento", 
        "Gostaria de mais informações",
        "Qual o valor?"
    ]
    
    phone = "5511999999999"
    
    for i, msg in enumerate(messages, 1):
        print(f"📤 Enviando mensagem {i}: '{msg}'")
        
        message = {
            "text": {"message": msg},
            "phone": phone,
            "fromMe": False
        }
        
        try:
            response = requests.post(webhook_url, json=message, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {result.get('status')}")
            else:
                print(f"   ❌ Erro: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # Pausa pequena entre mensagens
        time.sleep(0.3)
    
    print("\n⏳ Aguardando processamento...")
    time.sleep(5)

if __name__ == "__main__":
    print("🚀 TESTE DO SISTEMA DE FILAS - AVANTTI AI")
    print("=" * 50)
    
    # Testa se servidor está funcionando
    if not test_health():
        print("\n❌ Servidor não está rodando. Execute: python app.py")
        exit(1)
    
    # Testa mensagem única
    if test_single_message():
        time.sleep(2)
        
        # Testa múltiplas mensagens
        test_multiple_messages()
    
    print("\n✅ Teste concluído!")
    print("🔍 Verifique os logs do servidor para ver o processamento das filas.")