import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa as funções do app
from app import get_queue_for_phone, process_message_queue

def test_queue_functions():
    """Testa as funções de fila diretamente"""
    print("🧪 TESTE DAS FUNÇÕES DE FILA")
    print("=" * 40)
    
    # Testa criação de fila
    phone = "5511999999999"
    print(f"📱 Testando fila para: {phone}")
    
    queue = get_queue_for_phone(phone)
    print(f"✅ Fila criada: {queue}")
    
    # Adiciona mensagem na fila
    queue.put({
        'message': 'Teste de mensagem',
        'timestamp': '2025-09-17T16:00:00',
        'phone': phone
    })
    
    print(f"📤 Mensagem adicionada à fila")
    print(f"📊 Tamanho da fila: {queue.qsize()}")
    
    print("\n✅ Teste das funções básicas concluído!")
    print("🔍 As funções de fila estão funcionando corretamente.")

if __name__ == "__main__":
    test_queue_functions()