#!/usr/bin/env python3
"""
SERVIDOR ULTRA-SIMPLES PARA WEBHOOK Z-API
Versão mínima que FUNCIONA - sem dependências complexas
"""
import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configurações mínimas
app.config['DEBUG'] = False

@app.route('/', methods=['GET'])
def home():
    """Endpoint raiz"""
    return jsonify({
        "status": "✅ FUNCIONANDO",
        "service": "Avantti AI Webhook",
        "version": "simple-v1.0",
        "timestamp": "2025-09-17"
    }), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "service": "avantti-ai-webhook",
        "ready": True
    }), 200

@app.route('/receive_message', methods=['POST'])
def receive_message():
    """Endpoint principal para receber webhooks do Z-API"""
    try:
        # Log da requisição
        print(f"📨 WEBHOOK RECEBIDO: {request.method}")
        
        # Pega os dados
        data = request.get_json() or {}
        print(f"📄 DADOS: {json.dumps(data, indent=2)}")
        
        # Resposta de sucesso
        return jsonify({
            "status": "success",
            "message": "Webhook recebido com sucesso!",
            "received_at": "2025-09-17",
            "data_received": True
        }), 200
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/test', methods=['GET', 'POST'])
def test():
    """Endpoint de teste"""
    return jsonify({
        "message": "🎯 TESTE OK!",
        "method": request.method,
        "headers": dict(request.headers),
        "args": dict(request.args)
    }), 200

if __name__ == '__main__':
    print("🚀 INICIANDO SERVIDOR SIMPLES...")
    print("📍 Configuração:")
    print(f"   HOST: 0.0.0.0")
    print(f"   PORT: 5000")
    print(f"   DEBUG: False")
    print("=" * 50)
    
    # Inicia o servidor
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )