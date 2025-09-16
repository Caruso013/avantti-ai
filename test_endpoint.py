import requests
import json

# Teste do health check
print("=== TESTE HEALTH CHECK ===")
try:
    response = requests.get("http://127.0.0.1:8000/", timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Erro: {e}")

print("\n=== TESTE ENDPOINT MESSAGE_RECEIVE ===")
# Teste do endpoint principal
url = "http://127.0.0.1:8000/message_receive"
data = {
    "phone": "5511999999999",
    "message": "Oi, gostaria de saber mais sobre IA para minha empresa"
}

try:
    response = requests.post(url, json=data, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Erro: {e}")