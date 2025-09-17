from flask import Flask, request, jsonify
import os
import requests
import json
import threading
import time
from queue import Queue
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
print("=== AVANTTI AI - ELIANE CLEAN ===")

# Sistema de filas
message_queues = {}
processing_lock = threading.Lock()

def get_supabase_headers():
    """Headers para Supabase"""
    return {
        'apikey': os.getenv('SUPABASE_KEY'),
        'Authorization': f"Bearer {os.getenv('SUPABASE_KEY')}",
        'Content-Type': 'application/json'
    }

def buscar_contexto_conversa(phone):
    """Busca histórico no Supabase"""
    try:
        headers = get_supabase_headers()
        url = f"{os.getenv('SUPABASE_URL')}/rest/v1/conversations"
        params = {
            'phone': f'eq.{phone}',
            'order': 'created_at.desc',
            'limit': '10'
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            mensagens = response.json()
            contexto = []
            for msg in reversed(mensagens):
                if msg.get('text'):
                    contexto.append({
                        "role": msg.get('role', 'user'),
                        "content": msg.get('text')
                    })
            return contexto
        return []
    except Exception as e:
        print(f"[ERRO] Contexto: {e}")
        return []

def salvar_mensagem_supabase(phone, message, role):
    """Salva mensagem no Supabase"""
    try:
        headers = get_supabase_headers()
        url = f"{os.getenv('SUPABASE_URL')}/rest/v1/conversations"
        data = {
            'phone': phone,
            'role': role,  # 'user' ou 'assistant'
            'text': message
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            print(f"[SUPABASE] Salvo: {role} - {phone}")
            return True
        return False
    except Exception as e:
        print(f"[ERRO] Salvar: {e}")
        return False

def gerar_resposta_openai(message, phone, context=None):
    """Gera resposta da IA"""
    try:
        headers = {
            'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
            'Content-Type': 'application/json'
        }
        
        messages = [{
            "role": "system",
            "content": """Você é a Eliane, SDR da Evex Imóveis.

Fluxo de qualificação:
1. Apresentação: "Olá! Aqui é a Eliane, da Evex Imóveis. Vi que você se interessou pelo nosso anúncio."
2. Interesse: "Você gostaria de receber mais informações sobre o empreendimento?"
3. Finalidade: "Me conta, você pensa em comprar para morar ou investir?"
4. Timing: "E você imagina comprar em breve, nos próximos 6 meses, ou ainda está pesquisando?"
5. Valores: "O investimento que você tem em mente está em qual faixa de valor?"
6. Pagamento: "Você pensa em pagamento à vista ou financiamento?"
7. Visita: "Podemos agendar uma visita sem compromisso. Gostaria?"

Seja simpática, humana, frases curtas."""
        }]
        
        if context:
            messages.extend(context)
        
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
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
            print(f"[ERRO] OpenAI: {response.status_code}")
            return "Desculpe, ocorreu um erro. Tente novamente."
    except Exception as e:
        print(f"[ERRO] IA: {e}")
        return "Olá! Obrigada pela mensagem. Nossa equipe retornará em breve."

def enviar_mensagem_zapi(phone, message):
    """Envia mensagem via Z-API"""
    try:
        url = f"{os.getenv('ZAPI_BASE_URL')}/instances/{os.getenv('ZAPI_INSTANCE_ID')}/token/{os.getenv('ZAPI_INSTANCE_TOKEN')}/send-text"
        
        headers = {'Content-Type': 'application/json'}
        if os.getenv('ZAPI_CLIENT_TOKEN'):
            headers['Client-Token'] = os.getenv('ZAPI_CLIENT_TOKEN')
        
        data = {"phone": phone, "message": message}
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if 'error' not in result:
                print(f"[ZAPI] Enviado: {phone}")
                return True
        
        print(f"[ERRO] ZAPI: {response.status_code}")
        return False
    except Exception as e:
        print(f"[ERRO] ZAPI: {e}")
        return False

def get_queue_for_phone(phone):
    """Obtém fila do telefone"""
    if phone not in message_queues:
        message_queues[phone] = Queue()
    return message_queues[phone]

def process_message_queue(phone):
    """Processa fila de mensagens"""
    queue = get_queue_for_phone(phone)
    
    while not queue.empty():
        try:
            message_data = queue.get()
            message = message_data['message']
            
            print(f"[FILA] Processando: '{message}' de {phone}")
            
            # Salva mensagem do cliente
            salvar_mensagem_supabase(phone, message, 'user')
            
            # Busca contexto
            context = buscar_contexto_conversa(phone)
            
            # Gera resposta
            ai_response = gerar_resposta_openai(message, phone, context)
            
            # Salva resposta
            salvar_mensagem_supabase(phone, ai_response, 'assistant')
            
            # Envia resposta
            enviar_mensagem_zapi(phone, ai_response)
            
            queue.task_done()
            time.sleep(1)
            
        except Exception as e:
            print(f"[ERRO] Processamento: {e}")
            queue.task_done()

def start_queue_processor(phone):
    """Inicia processador da fila"""
    with processing_lock:
        if hasattr(start_queue_processor, 'processing') and phone in start_queue_processor.processing:
            return
        
        if not hasattr(start_queue_processor, 'processing'):
            start_queue_processor.processing = set()
        
        start_queue_processor.processing.add(phone)
    
    def worker():
        try:
            process_message_queue(phone)
        finally:
            with processing_lock:
                start_queue_processor.processing.discard(phone)
    
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "Avantti AI - Eliane funcionando!"}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "avantti-ai-eliane"}), 200

@app.route("/message_receive", methods=["POST"])
def message_receive():
    """Endpoint principal"""
    try:
        payload = request.get_json(silent=True) or {}
        
        text_obj = payload.get('text', {})
        message = text_obj.get('message', '') if isinstance(text_obj, dict) else str(text_obj)
        phone = payload.get('phone', '')
        
        if not message or not phone:
            return jsonify({"status": "ignored", "reason": "missing_data"}), 200
        
        if payload.get('fromMe', False):
            return jsonify({"status": "ignored", "reason": "from_bot"}), 200
        
        print(f"[WEBHOOK] '{message}' de {phone}")
        
        # Adiciona à fila
        queue = get_queue_for_phone(phone)
        queue.put({
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'phone': phone
        })
        
        # Processa fila
        start_queue_processor(phone)
        
        return jsonify({"status": "queued", "message": "Processando..."}), 200
        
    except Exception as e:
        print(f"[ERRO] Webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    print(f"[STARTUP] Servidor na porta {os.getenv('PORT', 5000)}")
    app.run(host="0.0.0.0", port=int(os.getenv('PORT', 5000)), debug=False)
