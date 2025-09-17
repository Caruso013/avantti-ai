from flask import Flask, request, jsonify
import os
import requests
import json
import threading
import time
from queue import Queue
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Versão simplificada - com filas em memória
print("=== AVANTTI AI - VERSÃO COM FILAS ===")

# Sistema de filas em memória
message_queues = {}  # {phone: Queue}
processing_lock = threading.Lock()

def get_queue_for_phone(phone):
    """Obtém ou cria uma fila para um telefone específico"""
    if phone not in message_queues:
        message_queues[phone] = Queue()
    return message_queues[phone]

def process_message_queue(phone):
    """Processa mensagens da fila de um telefone específico"""
    queue = get_queue_for_phone(phone)
    
    while not queue.empty():
        try:
            message_data = queue.get()
            mensagem_texto = message_data['message']
            
            print(f"[FILA] Processando: '{mensagem_texto}' de {phone}")
            
            # Salva mensagem do cliente
            salvar_mensagem_supabase(phone, mensagem_texto, is_customer=True)
            
            # Busca contexto da conversa
            contexto = buscar_contexto_conversa(phone)
            
            # Gera resposta da IA com contexto
            resposta_ia = gerar_resposta_openai(mensagem_texto, phone, contexto)
            
            # Salva resposta da IA
            salvar_mensagem_supabase(phone, resposta_ia, is_customer=False)
            
            # Envia resposta via Z-API
            enviar_mensagem_zapi(phone, resposta_ia)
            
            queue.task_done()
            
            # Pequena pausa entre mensagens para evitar spam
            time.sleep(1)
            
        except Exception as e:
            print(f"[ERRO] Processamento da fila: {e}")
            queue.task_done()

def start_queue_processor(phone):
    """Inicia processador de fila em thread separada"""
    with processing_lock:
        # Verifica se já está processando
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

def get_supabase_client():
    """Retorna headers para requisições Supabase"""
    return {
        'apikey': os.getenv('SUPABASE_KEY'),
        'Authorization': f"Bearer {os.getenv('SUPABASE_KEY')}",
        'Content-Type': 'application/json'
    }

def buscar_contexto_conversa(telefone):
    """Busca mensagens anteriores do telefone no Supabase"""
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        headers = get_supabase_client()
        
        # Busca as últimas 10 mensagens do telefone
        url = f"{supabase_url}/rest/v1/messages"
        params = {
            'phone': f'eq.{telefone}',
            'order': 'created_at.desc',
            'limit': '10'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            mensagens = response.json()
            # Converte para formato de contexto do OpenAI (ordem cronológica)
            contexto = []
            for msg in reversed(mensagens):  # Reverte para ordem cronológica
                role = "user" if msg['direction'] == 'inbound' else "assistant"
                contexto.append({
                    "role": role,
                    "content": msg['content']
                })
            return contexto
        else:
            print(f"[ERRO] Erro ao buscar contexto: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"[ERRO] Erro ao buscar contexto: {e}")
        return []

def salvar_mensagem_supabase(telefone, conteudo, direcao, message_id=None):
    """Salva mensagem no Supabase"""
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        headers = get_supabase_client()
        
        # Busca ou cria customer
        customer_id = obter_ou_criar_customer(telefone)
        
        # Busca ou cria thread
        thread_id = obter_ou_criar_thread(customer_id)
        
        # Salva a mensagem
        url = f"{supabase_url}/rest/v1/messages"
        data = {
            'thread_id': thread_id,
            'phone': telefone,
            'content': conteudo,
            'direction': direcao,  # 'inbound' ou 'outbound'
            'message_type': 'text',
            'processed_at': datetime.now().isoformat(),
            'metadata': {'message_id': message_id} if message_id else {}
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            print(f"[SUPABASE] Mensagem salva: {direcao} - {telefone}")
            return True
        else:
            print(f"[ERRO] Erro ao salvar mensagem: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro ao salvar mensagem: {e}")
        return False

def obter_ou_criar_customer(telefone):
    """Busca ou cria customer no Supabase"""
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        headers = get_supabase_client()
        
        # Busca customer existente
        url = f"{supabase_url}/rest/v1/customers"
        params = {'phone': f'eq.{telefone}'}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            customers = response.json()
            if customers:
                return customers[0]['id']
            
            # Se não existe, cria novo
            data = {'phone': telefone}
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                return response.json()[0]['id']
        
        return None
        
    except Exception as e:
        print(f"[ERRO] Erro ao obter/criar customer: {e}")
        return None

def obter_ou_criar_thread(customer_id):
    """Busca ou cria thread no Supabase"""
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        headers = get_supabase_client()
        
        # Busca thread existente
        url = f"{supabase_url}/rest/v1/threads"
        params = {'customer_id': f'eq.{customer_id}', 'status': 'eq.active'}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            threads = response.json()
            if threads:
                return threads[0]['id']
            
            # Se não existe, cria nova
            data = {'customer_id': customer_id}
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 201:
                return response.json()[0]['id']
        
        return None
        
    except Exception as e:
        print(f"[ERRO] Erro ao obter/criar thread: {e}")
        return None

def processar_novo_lead(argumentos_json, telefone):
    """Processa function call de novo lead"""
    try:
        args = json.loads(argumentos_json)
        
        # Salva lead no Supabase
        supabase_url = os.getenv('SUPABASE_URL')
        headers = get_supabase_client()
        
        url = f"{supabase_url}/rest/v1/leads"
        data = {
            'lead_name': args.get('nome_lead', 'Lead WhatsApp'),
            'phone': telefone,
            'motivation': f"Interesse: {args.get('interesse', '')} | Finalidade: {args.get('finalidade', '')} | Timing: {args.get('timing', '')}",
            'status': 'new_lead',
            'source': 'whatsapp_eliane',
            'metadata': args
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            print(f"[LEAD] Novo lead salvo: {args.get('nome_lead')} - {telefone}")
            return True
        else:
            print(f"[ERRO] Erro ao salvar lead: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro ao processar lead: {e}")
        return False

def gerar_resposta_openai(mensagem, telefone):
    """Gera resposta usando OpenAI com contexto e function calls"""
    try:
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            print("[ERRO] OPENAI_API_KEY não encontrada")
            return "Desculpe, serviço temporariamente indisponível."
        
        print(f"[IA] Gerando resposta para: '{mensagem}' do telefone: {telefone}")
        
        # Busca contexto da conversa
        contexto = buscar_contexto_conversa(telefone)
        print(f"[CONTEXTO] Encontradas {len(contexto)} mensagens anteriores")
        
        headers = {
            'Authorization': f'Bearer {openai_key}',
            'Content-Type': 'application/json'
        }
        
        # Monta mensagens com contexto
        messages = [
            {
                "role": "system", 
                "content": """Você é a Eliane, SDR da Evex Imóveis, especializada em empreendimentos residenciais. 

Seu objetivo é qualificar leads que vieram de anúncios do Facebook interessados em imóveis. Siga este fluxo:

1. Se for a primeira mensagem, apresente-se: "Olá! Aqui é a Eliane, da Evex Imóveis. Vi que você se interessou pelo nosso anúncio."

2. Confirme o interesse: "Você gostaria de receber mais informações sobre o empreendimento?"

3. Descubra a finalidade: "Me conta, você pensa em comprar para morar ou investir?"

4. Identifique o timing: "Legal! E você imagina comprar em breve, nos próximos 6 meses, ou ainda está pesquisando opções?"

5. Fale sobre valores: "O investimento que você tem em mente está em qual faixa de valor?"

6. Forme de pagamento: "Você pensa em pagamento à vista ou financiamento?"

7. Agende visita: "Podemos agendar uma visita sem compromisso para você conhecer o empreendimento pessoalmente. Gostaria?"

IMPORTANTE: Se o lead demonstrar interesse real (quer visitar, pergunta sobre preços, quer mais informações), use a função 'notificar_novo_lead' para avisar nosso time de vendas.

Seja sempre simpática, humana, use frases curtas e objetivas. Tom formal-casual."""
            }
        ]
        
        # Adiciona contexto histórico
        messages.extend(contexto)
        
        # Adiciona mensagem atual
        messages.append({
            "role": "user", 
            "content": mensagem
        })
        
        # Define function calls disponíveis
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "notificar_novo_lead",
                    "description": "Notifica o time de vendas quando um lead demonstra interesse real em imóveis",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "nome_lead": {
                                "type": "string",
                                "description": "Nome do lead interessado"
                            },
                            "telefone": {
                                "type": "string", 
                                "description": "Telefone do lead"
                            },
                            "interesse": {
                                "type": "string",
                                "description": "Tipo de interesse (ex: visita, mais informações, valores)"
                            },
                            "finalidade": {
                                "type": "string",
                                "description": "Finalidade do imóvel: morar ou investir"
                            },
                            "timing": {
                                "type": "string",
                                "description": "Prazo para compra (ex: próximos 6 meses, pesquisando)"
                            }
                        },
                        "required": ["nome_lead", "telefone", "interesse"]
                    }
                }
            }
        ]
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": 150,
            "temperature": 0.7,
            "tools": tools,
            "tool_choice": "auto"
        }
        
        print("[API] Fazendo requisição para OpenAI...")
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"[STATUS] OpenAI Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Verifica se há function calls
            choice = result['choices'][0]
            message = choice['message']
            
            if message.get('tool_calls'):
                # Processa function calls
                for tool_call in message['tool_calls']:
                    if tool_call['function']['name'] == 'notificar_novo_lead':
                        processar_novo_lead(tool_call['function']['arguments'], telefone)
                
                # Retorna mensagem de confirmação sobre o contato
                return "Perfeito! Registrei seu interesse. Nossa equipe comercial entrará em contato em breve para apresentar as melhores opções para você. Enquanto isso, posso esclarecer alguma dúvida?"
            
            # Se não há function calls, retorna resposta normal
            if message.get('content'):
                resposta = message['content'].strip()
                print(f"[SUCESSO] Resposta gerada: '{resposta}'")
                return resposta
            else:
                return "Olá! Como posso ajudar você com informações sobre nossos empreendimentos?"
                
        else:
            print(f"[ERRO] OpenAI: {response.status_code} - {response.text}")
            return "Desculpe, ocorreu um erro. Tente novamente em alguns instantes."
            
    except Exception as e:
        print(f"[ERRO] Erro ao gerar resposta: {e}")
        import traceback
        traceback.print_exc()
        return "Desculpe, ocorreu um erro. Tente novamente em alguns instantes."

def enviar_mensagem_zapi(numero, mensagem):
    """Envia mensagem via Z-API"""
    try:
        base_url = os.getenv('ZAPI_BASE_URL')
        instance_id = os.getenv('ZAPI_INSTANCE_ID')
        token = os.getenv('ZAPI_INSTANCE_TOKEN')
        client_token = os.getenv('ZAPI_CLIENT_TOKEN')
        
        if not all([base_url, instance_id, token]):
            print("[ERRO] Configurações Z-API não encontradas")
            print(f"Base URL: {base_url}")
            print(f"Instance ID: {instance_id}")
            print(f"Token: {'OK' if token else 'Não encontrado'}")
            print(f"Client Token: {'OK' if client_token else 'Não encontrado'}")
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
        
        print(f"[API] Enviando para: {url}")
        print(f"[HEADERS] Headers: {headers}")
        print(f"[DATA] Data: {data}")
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        print(f"[STATUS] Response Status: {response.status_code}")
        print(f"[RESPONSE] Response Text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"[DEBUG] Z-API Response JSON completo: {result}")
            
            # Verifica se houve erro na resposta
            if 'error' in result:
                print(f"[ERRO] Erro na resposta Z-API: {result}")
                return False
            elif 'id' in result:
                message_id = result.get('id')
                zaap_id = result.get('zaapId', 'N/A')
                print(f"[SUCESSO] Mensagem enviada com sucesso!")
                print(f"[SUCESSO] Message ID: {message_id}")
                print(f"[SUCESSO] Zaap ID: {zaap_id}")
                print(f"[SUCESSO] Para número: {numero}")
                return True
            else:
                print(f"[AVISO] Resposta sem erro mas sem ID: {result}")
                return True  # Assumir sucesso se não há erro explícito
        else:
            print(f"[ERRO] Erro ao enviar: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro Z-API: {e}")
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
    """Endpoint para receber mensagens - com sistema de filas"""
    payload: dict = request.get_json(silent=True) or {}
    
    print(f"[MENSAGEM RECEBIDA] {payload}")
    
    try:
        # Extrai dados da mensagem do Z-API
        texto_obj = payload.get('text', {})
        mensagem_texto = texto_obj.get('message', '') if isinstance(texto_obj, dict) else str(texto_obj)
        numero_remetente = payload.get('phone', '')
        
        # Verifica se é uma mensagem válida
        if not mensagem_texto or not numero_remetente:
            print(f"[AVISO] Mensagem inválida - Texto: '{mensagem_texto}' | Número: '{numero_remetente}'")
            return jsonify({"status": "ignored", "reason": "missing_data"}), 200
        
        # Ignora mensagens do próprio bot
        if payload.get('fromMe', False):
            print("[AVISO] Mensagem enviada pelo bot - ignorando")
            return jsonify({"status": "ignored", "reason": "from_bot"}), 200
        
        print(f"[FILA] Adicionando mensagem '{mensagem_texto}' de {numero_remetente}")
        
        # Adiciona mensagem à fila específica do telefone
        queue = get_queue_for_phone(numero_remetente)
        queue.put({
            'message': mensagem_texto,
            'timestamp': datetime.now().isoformat(),
            'phone': numero_remetente
        })
        
        # Inicia processador de fila se não estiver rodando
        start_queue_processor(numero_remetente)
        
        return jsonify({
            "status": "queued",
            "message": "Mensagem adicionada à fila de processamento"
        }), 200
            
    except Exception as e:
        print(f"[ERRO] Processamento: {e}")
        return jsonify({
            "status": "error", 
            "message": f"Erro: {str(e)}"
        }), 500


if __name__ == "__main__":
    print("[STARTUP] === AVANTTI AI - VERSÃO FINAL v4 === ")
    print("[STARTUP] NOVO BUILD - CACHE QUEBRADO!")
    print(f"[CONFIG] PORT environment: {os.getenv('PORT', 'DEFAULT_5000')}")
    
    port = int(os.getenv('PORT', 5000))
    
    print(f"[SERVIDOR] STARTING on host=0.0.0.0, port={port}")
    print("[REDE] ACEITA CONEXÕES EXTERNAS!")
    
    try:
        app.run(host="0.0.0.0", port=port, debug=False)
    except Exception as e:
        print(f"[ERRO] ERRO: {e}")
        import traceback
        traceback.print_exc()
