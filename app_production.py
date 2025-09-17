from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Versão para produção
print("=== AVANTTI AI - PRODUCTION ===")

def gerar_resposta_openai(mensagem):
    """Gera resposta usando OpenAI"""
    try:
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            print("[ERRO] OPENAI_API_KEY não encontrada")
            return "Desculpe, serviço temporariamente indisponível."
        
        headers = {
            'Authorization': f'Bearer {openai_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system", 
                    "content": "Você é um assistente da Avantti AI, uma empresa de soluções em inteligência artificial. Seja educado, prestativo e profissional."
                },
                {
                    "role": "user", 
                    "content": mensagem
                }
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            resposta = result['choices'][0]['message']['content'].strip()
            print(f"[IA] Resposta gerada para: {mensagem[:30]}...")
            return resposta
        else:
            print(f"[ERRO] OpenAI: {response.status_code}")
            return "Desculpe, ocorreu um erro. Tente novamente em alguns instantes."
            
    except Exception as e:
        print(f"[ERRO] Erro ao gerar resposta: {e}")
        return "Olá! Obrigado pela mensagem. Nossa equipe retornará em breve."

def enviar_mensagem_zapi(numero, mensagem):
    """Envia mensagem via Z-API"""
    try:
        base_url = os.getenv('ZAPI_BASE_URL')
        instance_id = os.getenv('ZAPI_INSTANCE_ID')
        token = os.getenv('ZAPI_INSTANCE_TOKEN')
        client_token = os.getenv('ZAPI_CLIENT_TOKEN')
        
        if not all([base_url, instance_id, token]):
            print("[ERRO] Configurações Z-API não encontradas")
            return False
        
        # URL correta baseada na documentação Z-API
        url = f"{base_url}/instances/{instance_id}/token/{token}/send-text"
        
        # Headers com client-token
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Adiciona client-token se disponível
        if client_token:
            headers['Client-Token'] = client_token
        
        data = {
            "phone": numero,
            "message": mensagem
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            # Verifica se houve erro na resposta
            if 'error' in result:
                print(f"[ERRO] Z-API: {result['error']}")
                return False
            elif 'id' in result:
                message_id = result.get('id')
                print(f"[SUCESSO] Mensagem enviada - ID: {message_id}")
                return True
            else:
                print(f"[AVISO] Resposta sem ID: {result}")
                return True  # Assumir sucesso se não há erro explícito
        else:
            print(f"[ERRO] Z-API HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERRO] Z-API Exception: {e}")
        return False

@app.route("/", methods=["GET"])
def health_check():
    """Endpoint para verificar se o servidor está funcionando"""
    return jsonify({
        "status": "ok",
        "message": "Avantti AI está funcionando!",
        "version": "production"
    }), 200


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "service": "avantti-ai",
        "version": "production"
    }), 200


@app.route("/ping", methods=["GET"])
def ping():
    """Endpoint simples de ping"""
    return "pong"


@app.route("/message_receive", methods=["POST"])
def message_receive() -> tuple:
    """Endpoint para receber mensagens - com IA integrada"""
    payload: dict = request.get_json(silent=True) or {}
    
    try:
        # Extrai dados da mensagem do Z-API
        texto_obj = payload.get('text', {})
        mensagem_texto = texto_obj.get('message', '') if isinstance(texto_obj, dict) else str(texto_obj)
        numero_remetente = payload.get('phone', '')
        
        # Verifica se é uma mensagem válida
        if not mensagem_texto or not numero_remetente:
            return jsonify({"status": "ignored", "reason": "missing_data"}), 200
        
        # Ignora mensagens do próprio bot
        if payload.get('fromMe', False):
            return jsonify({"status": "ignored", "reason": "from_bot"}), 200
        
        print(f"[PROCESSANDO] '{mensagem_texto}' de {numero_remetente}")
        
        # Gera resposta da IA
        resposta_ia = gerar_resposta_openai(mensagem_texto)
        
        # Envia resposta via Z-API
        sucesso_envio = enviar_mensagem_zapi(numero_remetente, resposta_ia)
        
        if sucesso_envio:
            return jsonify({
                "status": "processed",
                "message": "Mensagem processada e resposta enviada"
            }), 200
        else:
            return jsonify({
                "status": "generated_only",
                "message": "IA gerou resposta mas falha no envio"
            }), 200
            
    except Exception as e:
        print(f"[ERRO] Processamento: {e}")
        return jsonify({
            "status": "error", 
            "message": f"Erro: {str(e)}"
        }), 500


if __name__ == "__main__":
    print("[STARTUP] === AVANTTI AI - PRODUCTION === ")
    
    port = int(os.getenv('PORT', 5000))
    
    print(f"[SERVIDOR] Starting on host=0.0.0.0, port={port}")
    
    try:
        # Em produção, usar Gunicorn. Em desenvolvimento, Flask
        if os.getenv('FLASK_ENV') == 'production':
            # Gunicorn será usado pelo Dockerfile
            app.run(host="0.0.0.0", port=port, debug=False)
        else:
            # Desenvolvimento
            app.run(host="0.0.0.0", port=port, debug=True)
    except Exception as e:
        print(f"[ERRO] STARTUP: {e}")
        import traceback
        traceback.print_exc()