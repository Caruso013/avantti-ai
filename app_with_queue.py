from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from container.container import Container
from exceptions.handler import setup_error_handler

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Versão com sistema de filas
print("=== AVANTTI AI - COM SISTEMA DE FILAS ===")

# Inicializa container e handlers
container = Container()
setup_error_handler(container)

@app.route("/", methods=["GET"])
def health_check():
    """Endpoint para verificar se o servidor está funcionando"""
    return jsonify({
        "status": "ok",
        "message": "Avantti AI está funcionando!",
        "version": "queue-enabled"
    }), 200

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "service": "avantti-ai",
        "version": "queue-enabled"
    }), 200

@app.route("/ping", methods=["GET"])
def ping():
    """Endpoint simples de ping"""
    return "pong"

@app.route("/message_receive", methods=["POST"])
def message_receive():
    """Endpoint para receber mensagens - usando sistema de filas"""
    try:
        payload = request.get_json(silent=True) or {}
        
        # Verifica se é uma mensagem válida
        if not payload:
            return jsonify({"status": "ignored", "reason": "no_payload"}), 200
        
        # Ignora mensagens do próprio bot
        if payload.get('fromMe', False):
            return jsonify({"status": "ignored", "reason": "from_bot"}), 200
        
        print(f"[WEBHOOK] Payload recebido: {payload}")
        
        # Usa o controller do container para processar a mensagem
        response, status_code = container.controllers.process_incoming_message.handle(**payload)
        
        return jsonify(response), status_code
        
    except Exception as e:
        print(f"[ERRO] Processamento: {e}")
        return jsonify({
            "status": "error", 
            "message": f"Erro: {str(e)}"
        }), 500

if __name__ == "__main__":
    print("[STARTUP] === AVANTTI AI - COM SISTEMA DE FILAS === ")
    
    port = int(os.getenv('PORT', 5000))
    
    print(f"[SERVIDOR] Starting on host=0.0.0.0, port={port}")
    print("[INFO] Para processar mensagens, execute também: python workers/queue_worker.py")
    
    try:
        app.run(host="0.0.0.0", port=port, debug=True)
    except Exception as e:
        print(f"[ERRO] STARTUP: {e}")
        import traceback
        traceback.print_exc()