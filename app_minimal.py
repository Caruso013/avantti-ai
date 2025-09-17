#!/usr/bin/env python3
"""
Flask app MINIMAL - só para testar se o problema é o Container()
"""
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "Flask MINIMAL funcionando!",
        "port": os.getenv("PORT", "5000")
    }), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy", 
        "service": "avantti-ai-minimal"
    }), 200

if __name__ == "__main__":
    print("=== FLASK MINIMAL v2.0 - REBUILD FORCED ===")
    port = 5000
    print(f"Starting on 0.0.0.0:{port} [MINIMAL BUILD]")
    app.run(host="0.0.0.0", port=port, debug=False)