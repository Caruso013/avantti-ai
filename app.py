from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Versão simplificada - sem Container complexo
print("=== AVANTTI AI - VERSÃO SIMPLIFICADA ===")

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
    """Endpoint para receber mensagens - versão simplificada"""
    payload: dict = request.get_json(silent=True) or {}
    
    print(f"[MENSAGEM RECEBIDA] {payload}")
    
    # Por enquanto, só retorna sucesso
    return jsonify({
        "status": "received", 
        "message": "Mensagem recebida com sucesso",
        "data": payload
    }), 200


if __name__ == "__main__":
    import os
    print("=== FLASK v2.0 - FORÇANDO REBUILD ===")
    print(f"PORT environment: {os.getenv('PORT', 'NOT_SET')}")
    
    debug_mode = False  # Força production mode
    port = 5000  # Porta 5000 - direto sem nginx
    
    print(f"Starting Flask app on host=0.0.0.0, port={port} [REBUILD FORCED]")
    try:
        app.run(host="0.0.0.0", port=port, debug=debug_mode)
    except Exception as e:
        print(f"ERRO AO INICIAR FLASK: {e}")
        import traceback
        traceback.print_exc()
