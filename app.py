from dotenv import load_dotenv
from flask import Flask, request, jsonify
from utils.logger import logger, to_json_dump

load_dotenv()
from container.container import Container

app = Flask(__name__)

# Container simplificado - apenas para health check funcionar
container = None
try:
    container = Container()
    logger.info("Container inicializado com sucesso")
except Exception as e:
    logger.error(f"Container falhou, mas mantendo Flask ativo: {e}")
    # Mantém container=None mas não crashea


@app.route("/", methods=["GET"])
def health_check():
    """Endpoint para verificar se o servidor está funcionando"""
    return jsonify({
        "status": "ok",
        "message": "Flask está rodando!",
        "container_ready": container is not None
    }), 200


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "service": "avantti-ai",
        "container_status": "loaded" if container else "failed"
    }), 200
    return jsonify({"status": "ok", "message": "Avantti AI API está funcionando!"})


@app.route("/health", methods=["GET"])
def health():
    """Endpoint alternativo de health check"""
    return jsonify({"status": "healthy", "service": "avantti-ai", "version": "1.0"})


@app.route("/ping", methods=["GET"])
def ping():
    """Endpoint simples de ping"""
    return "pong"


@app.route("/message_receive", methods=["POST"])
def message_receive() -> tuple:
    if container is None:
        logger.error("Container não inicializado")
        return jsonify({"status": "error", "message": "Sistema não inicializado"}), 500
    
    payload: dict = request.get_json(silent=True) or {}

    logger.info(
        f"[ENDPOINT RECEIVE MESSAGE] Requisição recebida: \n{to_json_dump(payload)}"
    )

    try:
        return container.controllers.process_incoming_message_controller.handle(
            **payload
        )

    except Exception as err:
        logger.exception(
            f"[ENDPOINT RECEIVE MESSAGE] Erro ao processar endpoint /receive_message: {err}"
        )

        return jsonify({"status": "error"}), 400


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
