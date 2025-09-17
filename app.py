from dotenv import load_dotenv
from flask import Flask, request, jsonify
from utils.logger import logger, to_json_dump

load_dotenv()
from container.container import Container

app = Flask(__name__)

# Inicialização do container com tratamento de erro
try:
    container = Container()
    logger.info("Container inicializado com sucesso")
except Exception as e:
    logger.exception(f"Erro ao inicializar container: {e}")
    container = None


@app.route("/", methods=["GET"])
def health_check():
    """Endpoint para verificar se o servidor está funcionando"""
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
    print("=== INICIANDO APLICAÇÃO ===")
    print(f"PORT environment: {os.getenv('PORT', 'NOT_SET')}")
    
    debug_mode = False  # Força production mode
    port = 5001  # Porta 5001 para não conflitar com nginx:5000
    
    print(f"Starting Flask app on host=127.0.0.1, port={port}")
    try:
        app.run(host="127.0.0.1", port=port, debug=debug_mode)
    except Exception as e:
        print(f"ERRO AO INICIAR FLASK: {e}")
        import traceback
        traceback.print_exc()
