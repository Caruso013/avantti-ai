from flask import Flask, request, jsonify
import os
import requests
import json
import threading
import time
from queue import Queue
from datetime import datetime
from dotenv import load_dotenv
import tempfile
import base64

load_dotenv()
app = Flask(__name__)
print("=== AVANTTI AI - ELIANE V2 ===")

# Sistema de filas melhorado
message_queues = {}
processing_lock = threading.Lock()
active_processors = set()

def get_supabase_headers():
    """Headers para Supabase"""
    return {
        'apikey': os.getenv('SUPABASE_KEY'),
        'Authorization': f"Bearer {os.getenv('SUPABASE_KEY')}",
        'Content-Type': 'application/json'
    }

def transcribe_audio_whisper(audio_url):
    """Transcreve áudio usando OpenAI Whisper"""
    try:
        print(f"[WHISPER] Transcrevendo áudio: {audio_url}")
        
        # Baixa o áudio
        response = requests.get(audio_url, timeout=30)
        if response.status_code != 200:
            print(f"[ERRO] Falha ao baixar áudio: {response.status_code}")
            return None
        
        # Salva temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        
        # Transcreve com Whisper
        headers = {
            'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}'
        }
        
        with open(temp_file_path, 'rb') as audio_file:
            files = {
                'file': audio_file,
                'model': (None, 'whisper-1'),
                'language': (None, 'pt')
            }
            
            response = requests.post(
                'https://api.openai.com/v1/audio/transcriptions',
                headers=headers,
                files=files,
                timeout=30
            )
        
        # Remove arquivo temporário
        os.unlink(temp_file_path)
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('text', '').strip()
            print(f"[WHISPER] Transcrito: '{text}'")
            return text
        else:
            print(f"[ERRO] Whisper: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[ERRO] Transcrição: {e}")
        return None

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
            print(f"[CONTEXTO] {len(contexto)} mensagens para {phone}")
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
        print(f"[ERRO] Supabase: {response.status_code}")
        return False
    except Exception as e:
        print(f"[ERRO] Salvar: {e}")
        return False

def gerar_resposta_openai(message, phone, context=None):
    """Gera resposta da IA com novo prompt"""
    try:
        headers = {
            'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
            'Content-Type': 'application/json'
        }
        
        system_prompt = """Você é **Eliane**, SDR (pré-vendas) da **Evex Imóveis**.
Seu papel é **qualificar automaticamente leads de anúncios Meta/Facebook para imóveis** via WhatsApp.
Respeite sempre a **LGPD** e mantenha tom **formal-casual**, objetivo, simpático e humano (evite parecer robô).
Use **gatilhos de venda sutis** e **palavras-chave de conversão**.

## 📋 Fluxo de Qualificação (natural, em tom de conversa)
1. **Apresentação inicial** (apenas na primeira mensagem):
   "Olá! Aqui é a Eliane, da Evex Imóveis 😊. Vi que você se interessou pelo nosso anúncio."

2. **Confirmar interesse no empreendimento**:
   "Você gostaria de receber mais informações sobre ele?"

3. **Finalidade do imóvel**:
   "Me conta, você pensa em comprar para morar ou investir?"

4. **Momento de compra**:
   "Legal! E você imagina comprar em breve, nos próximos 6 meses, ou ainda está pesquisando opções?"

5. **Faixa de valor**:
   "O investimento que você tem em mente está em qual faixa de valor?"

6. **Forma de pagamento**:
   "Você pensa em pagamento à vista ou financiamento?"

7. **Interesse em visita**:
   "Podemos agendar uma visita sem compromisso para você conhecer o empreendimento pessoalmente. Gostaria?"

📌 **Observações importantes**:
- Sempre quebrar o texto em mensagens curtas
- Usar confirmações naturais ("Sim", "Entendi", "Perfeito")
- Se o lead responder fora de ordem, adaptar o fluxo
- **Não reiniciar a conversa nem se reapresentar após a primeira mensagem**

## ⚠️ Restrições
- ✅ Pode informar: valores gerais, localização, disponibilidade
- ❌ Não pode: negociar preço/prazo, falar sobre obras, reputação da empresa

Seja sempre simpática, humana e use frases curtas e objetivas."""

        messages = [{"role": "system", "content": system_prompt}]
        
        if context:
            messages.extend(context)
        
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": 200,
            "temperature": 0.7
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=15
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
        response = requests.post(url, json=data, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if 'error' not in result:
                print(f"[ZAPI] Enviado: {phone}")
                return True
        
        print(f"[ERRO] ZAPI: {response.status_code} - {response.text}")
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
    """Processa fila de mensagens com melhor debug"""
    queue = get_queue_for_phone(phone)
    
    print(f"[FILA] Iniciando processamento para {phone} - {queue.qsize()} mensagens")
    
    while not queue.empty():
        try:
            message_data = queue.get(timeout=5)
            message_text = message_data.get('message', '')
            message_type = message_data.get('type', 'text')
            
            print(f"[FILA] Processando {message_type}: '{message_text}' de {phone}")
            
            if message_text:
                # Salva mensagem do cliente
                salvar_mensagem_supabase(phone, message_text, 'user')
                
                # Busca contexto
                context = buscar_contexto_conversa(phone)
                
                # Gera resposta
                ai_response = gerar_resposta_openai(message_text, phone, context)
                
                if ai_response:
                    # Salva resposta
                    salvar_mensagem_supabase(phone, ai_response, 'assistant')
                    
                    # Envia resposta
                    enviar_mensagem_zapi(phone, ai_response)
            
            queue.task_done()
            time.sleep(1)  # Evita spam
            
        except Exception as e:
            print(f"[ERRO] Processamento: {e}")
            try:
                queue.task_done()
            except:
                pass
    
    print(f"[FILA] Processamento concluído para {phone}")

def start_queue_processor(phone):
    """Inicia processador da fila com melhor controle"""
    global active_processors
    
    with processing_lock:
        if phone in active_processors:
            print(f"[FILA] Processador já ativo para {phone}")
            return
        
        active_processors.add(phone)
        print(f"[FILA] Iniciando processador para {phone}")
    
    def worker():
        try:
            process_message_queue(phone)
        except Exception as e:
            print(f"[ERRO] Worker: {e}")
        finally:
            with processing_lock:
                active_processors.discard(phone)
                print(f"[FILA] Processador finalizado para {phone}")
    
    thread = threading.Thread(target=worker, name=f"queue-{phone}")
    thread.daemon = True
    thread.start()

def extract_message_content(payload):
    """Extrai conteúdo da mensagem dependendo do tipo"""
    try:
        # Mensagem de texto
        if payload.get('text'):
            text_obj = payload.get('text', {})
            if isinstance(text_obj, dict):
                return text_obj.get('message', ''), 'text'
            return str(text_obj), 'text'
        
        # Mensagem de áudio
        elif payload.get('audio'):
            audio_obj = payload.get('audio', {})
            if isinstance(audio_obj, dict):
                audio_url = audio_obj.get('audioUrl') or audio_obj.get('url')
                if audio_url:
                    # Transcreve o áudio
                    transcribed_text = transcribe_audio_whisper(audio_url)
                    if transcribed_text:
                        return transcribed_text, 'audio'
                    else:
                        return "Desculpe, não consegui entender o áudio. Pode digitar?", 'audio_error'
        
        # Mensagem de imagem com caption
        elif payload.get('image'):
            image_obj = payload.get('image', {})
            if isinstance(image_obj, dict):
                caption = image_obj.get('caption', '').strip()
                if caption:
                    return f"[Imagem] {caption}", 'image'
                else:
                    return "[Imagem recebida] Como posso ajudar?", 'image'
        
        # Mensagem de vídeo com caption  
        elif payload.get('video'):
            video_obj = payload.get('video', {})
            if isinstance(video_obj, dict):
                caption = video_obj.get('caption', '').strip()
                if caption:
                    return f"[Vídeo] {caption}", 'video'
                else:
                    return "[Vídeo recebido] Como posso ajudar?", 'video'
        
        return None, 'unknown'
        
    except Exception as e:
        print(f"[ERRO] Extração de conteúdo: {e}")
        return None, 'error'

@app.route("/", methods=["GET"])
def health_check():
    active_count = len(active_processors)
    queue_count = sum(q.qsize() for q in message_queues.values())
    return jsonify({
        "status": "ok", 
        "message": "Avantti AI - Eliane V2 funcionando!",
        "active_processors": active_count,
        "queued_messages": queue_count
    }), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "avantti-ai-eliane-v2"}), 200

@app.route("/message_receive", methods=["POST"])
def message_receive():
    """Endpoint principal com suporte a áudio"""
    try:
        payload = request.get_json(silent=True) or {}
        phone = payload.get('phone', '')
        
        if not phone:
            return jsonify({"status": "ignored", "reason": "missing_phone"}), 200
        
        if payload.get('fromMe', False):
            return jsonify({"status": "ignored", "reason": "from_bot"}), 200
        
        # Extrai conteúdo baseado no tipo
        message_text, message_type = extract_message_content(payload)
        
        if not message_text:
            return jsonify({"status": "ignored", "reason": "no_content"}), 200
        
        print(f"[WEBHOOK] {message_type.upper()}: '{message_text}' de {phone}")
        
        # Adiciona à fila
        queue = get_queue_for_phone(phone)
        queue.put({
            'message': message_text,
            'type': message_type,
            'timestamp': datetime.now().isoformat(),
            'phone': phone,
            'payload': payload
        })
        
        # Inicia processador
        start_queue_processor(phone)
        
        return jsonify({
            "status": "queued", 
            "message": "Processando...",
            "type": message_type
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    print(f"[STARTUP] Servidor na porta {os.getenv('PORT', 5000)}")
    app.run(host="0.0.0.0", port=int(os.getenv('PORT', 5000)), debug=False)
