from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Versão simplificada - sem Container complexo
print("=== AVANTTI AI - VERSÃO SIMPLIFICADA ===")

def gerar_resposta_openai(mensagem):
    """Gera resposta usando OpenAI"""
    try:
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
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
            return result['choices'][0]['message']['content'].strip()
        else:
            print(f"Erro OpenAI: {response.status_code} - {response.text}")
            return "Desculpe, ocorreu um erro. Tente novamente em alguns instantes."
            
    except Exception as e:
        print(f"Erro ao gerar resposta: {e}")
        return "Olá! Obrigado pela mensagem. Nossa equipe retornará em breve."

def enviar_mensagem_zapi(numero, mensagem):
    """Envia mensagem via Z-API"""
    try:
        base_url = os.getenv('ZAPI_BASE_URL')
        instance_id = os.getenv('ZAPI_INSTANCE_ID')
        token = os.getenv('ZAPI_INSTANCE_TOKEN')
        
        if not all([base_url, instance_id, token]):
            print("❌ Configurações Z-API não encontradas")
            return False
        
        url = f"{base_url}/v1/instances/{instance_id}/token/{token}/send-text"
        
        data = {
            "phone": numero,
            "message": mensagem
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Mensagem enviada para {numero}")
            return True
        else:
            print(f"❌ Erro ao enviar: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro Z-API: {e}")
        return False

@app.route("/", methods=["GET"])
def health_check():
    """Endpoint para verificar se o servidor está funcionando"""
    return jsonify({
        "status": "ok",
        "message": "Avantti AI está funcionando!",
        "version": "simplified"
    }), 200


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "service": "avantti-ai",
        "version": "simplified"
    }), 200


@app.route("/ping", methods=["GET"])
def ping():
    """Endpoint simples de ping"""
    return "pong"


@app.route("/message_receive", methods=["POST"])
def message_receive() -> tuple:
    """Endpoint para receber mensagens - com IA integrada"""
    payload: dict = request.get_json(silent=True) or {}
    
    print(f"🔔 [MENSAGEM RECEBIDA] {payload}")
    
    try:
        # Extrai dados da mensagem do Z-API
        # Z-API estrutura: {'text': {'message': 'conteúdo'}, 'phone': 'numero'}
        texto_obj = payload.get('text', {})
        mensagem_texto = texto_obj.get('message', '') if isinstance(texto_obj, dict) else str(texto_obj)
        numero_remetente = payload.get('phone', '')
        
        # Verifica se é uma mensagem válida
        if not mensagem_texto or not numero_remetente:
            print(f"⚠️ Mensagem inválida - Texto: '{mensagem_texto}' | Número: '{numero_remetente}'")
            return jsonify({"status": "ignored", "reason": "missing_data"}), 200
        
        # Ignora mensagens do próprio bot
        if payload.get('fromMe', False):
            print("⚠️ Mensagem enviada pelo bot - ignorando")
            return jsonify({"status": "ignored", "reason": "from_bot"}), 200
        
        print(f"📤 Processando: '{mensagem_texto}' de {numero_remetente}")
        
        # Gera resposta da IA
        resposta_ia = gerar_resposta_openai(mensagem_texto)
        print(f"🤖 IA gerou: {resposta_ia}")
        
        # Envia resposta via Z-API
        sucesso_envio = enviar_mensagem_zapi(numero_remetente, resposta_ia)
        
        if sucesso_envio:
            return jsonify({
                "status": "processed",
                "message": "Mensagem processada e resposta enviada",
                "ia_response": resposta_ia
            }), 200
        else:
            return jsonify({
                "status": "generated_only",
                "message": "IA gerou resposta mas falha no envio",
                "ia_response": resposta_ia
            }), 200
            
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        return jsonify({
            "status": "error", 
            "message": f"Erro: {str(e)}"
        }), 500


if __name__ == "__main__":
    print("🚀 === AVANTTI AI - VERSÃO FINAL v4 === 🚀")
    print("🔥 NOVO BUILD - CACHE QUEBRADO!")
    print(f"📡 PORT environment: {os.getenv('PORT', 'DEFAULT_5000')}")
    
    port = int(os.getenv('PORT', 5000))
    
    print(f"🌐 STARTING on host=0.0.0.0, port={port}")
    print("✅ ACEITA CONEXÕES EXTERNAS!")
    
    try:
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
