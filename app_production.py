from flask import Flask, request, jsonify
import os
import requests
import json
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Versão para produção
print("=== AVANTTI AI - PRODUCTION ===")

# Configurações do Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY')

def buscar_contexto_conversa(phone):
    """Busca o histórico de conversa de um cliente no Supabase"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Busca mensagens do cliente ordenadas por data
        url = f"{SUPABASE_URL}/rest/v1/messages"
        params = {
            'customer_phone': f'eq.{phone}',
            'order': 'created_at.asc',
            'limit': '20'  # Últimas 20 mensagens
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            mensagens = response.json()
            contexto = []
            
            for msg in mensagens:
                role = "user" if msg['is_customer'] else "assistant"
                contexto.append({
                    "role": role,
                    "content": msg['content']
                })
            
            return contexto
        else:
            print(f"[ERRO] Buscar contexto: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"[ERRO] Buscar contexto: {e}")
        return []

def salvar_mensagem_supabase(phone, content, is_customer=True):
    """Salva mensagem no Supabase"""
    try:
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Primeiro, busca ou cria o cliente
        customer_url = f"{SUPABASE_URL}/rest/v1/customers"
        customer_params = {
            'phone': f'eq.{phone}'
        }
        
        customer_response = requests.get(customer_url, headers=headers, params=customer_params)
        
        if customer_response.status_code == 200:
            customers = customer_response.json()
            
            if not customers:
                # Cria novo cliente
                customer_data = {
                    'phone': phone,
                    'name': phone  # Usar phone como nome inicialmente
                }
                
                create_response = requests.post(customer_url, headers=headers, json=customer_data)
                if create_response.status_code != 201:
                    print(f"[ERRO] Criar cliente: {create_response.status_code}")
                    return False
        
        # Salva a mensagem
        message_data = {
            'customer_phone': phone,
            'content': content,
            'is_customer': is_customer
        }
        
        message_url = f"{SUPABASE_URL}/rest/v1/messages"
        message_response = requests.post(message_url, headers=headers, json=message_data)
        
        if message_response.status_code == 201:
            print(f"[SUCESSO] Mensagem salva: {content[:30]}...")
            return True
        else:
            print(f"[ERRO] Salvar mensagem: {message_response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERRO] Salvar mensagem: {e}")
        return False

def processar_novo_lead(phone):
    """Processa um novo lead qualificado e notifica equipe"""
    try:
        # Salva o lead na base
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        
        lead_data = {
            'customer_phone': phone,
            'status': 'qualified',
            'source': 'whatsapp_ai'
        }
        
        lead_url = f"{SUPABASE_URL}/rest/v1/leads"
        lead_response = requests.post(lead_url, headers=headers, json=lead_data)
        
        if lead_response.status_code == 201:
            print(f"[SUCESSO] Lead criado: {phone}")
            
            # Notifica o lead sobre contato da equipe
            mensagem_lead = "Perfeito! Nossa equipe de vendas entrará em contato com você em breve para agendar a visita e tirar todas as suas dúvidas. Obrigada pelo interesse!"
            enviar_mensagem_zapi(phone, mensagem_lead)
            
            return True
        else:
            print(f"[ERRO] Criar lead: {lead_response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERRO] Processar lead: {e}")
        return False

def gerar_resposta_openai(mensagem, phone=None, contexto=None):
    """Gera resposta usando OpenAI com contexto e function calls"""
    try:
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            print("[ERRO] OPENAI_API_KEY não encontrada")
            return "Desculpe, serviço temporariamente indisponível."
        
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

Quando o lead demonstrar interesse real (responder sobre finalidade, timing, valores), use a function call 'processar_novo_lead' para notificar a equipe.

Seja sempre simpática, humana, use frases curtas e objetivas. Tom formal-casual."""
            }
        ]
        
        # Adiciona contexto se disponível
        if contexto:
            messages.extend(contexto)
        
        # Adiciona mensagem atual
        messages.append({
            "role": "user", 
            "content": mensagem
        })
        
        # Function call para processar lead
        functions = [
            {
                "name": "processar_novo_lead",
                "description": "Chama quando o lead está qualificado e interessado",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "motivo": {
                            "type": "string",
                            "description": "Motivo da qualificação"
                        }
                    },
                    "required": ["motivo"]
                }
            }
        ]
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "functions": functions,
            "function_call": "auto",
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
            choice = result['choices'][0]
            message = choice['message']
            
            # Verifica se há function call
            if 'function_call' in message:
                function_call = message['function_call']
                if function_call['name'] == 'processar_novo_lead' and phone:
                    print(f"[FUNCTION] Processando novo lead: {phone}")
                    processar_novo_lead(phone)
                
                # Gera resposta padrão após function call
                resposta = "Perfeito! Nossa equipe de vendas entrará em contato com você em breve. Obrigada pelo interesse!"
            else:
                resposta = message['content'].strip()
            
            print(f"[IA] Resposta gerada para: {mensagem[:30]}...")
            return resposta
        else:
            print(f"[ERRO] OpenAI: {response.status_code}")
            return "Desculpe, ocorreu um erro. Tente novamente em alguns instantes."
            
    except Exception as e:
        print(f"[ERRO] Erro ao gerar resposta: {e}")
        return "Olá! Obrigado pela mensagem. Nossa equipe retornará em breve."

def enviar_mensagem_zapi(numero, mensagem):
    """Envia mensagem via Z-API"""
    try:
        base_url = os.getenv('ZAPI_BASE_URL')
        instance_id = os.getenv('ZAPI_INSTANCE_ID')
        token = os.getenv('ZAPI_INSTANCE_TOKEN')
        client_token = os.getenv('ZAPI_CLIENT_TOKEN')
        
        if not all([base_url, instance_id, token]):
            print("[ERRO] Configurações Z-API não encontradas")
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
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            # Verifica se houve erro na resposta
            if 'error' in result:
                print(f"[ERRO] Z-API: {result['error']}")
                return False
            elif 'id' in result:
                message_id = result.get('id')
                print(f"[SUCESSO] Mensagem enviada - ID: {message_id}")
                return True
            else:
                print(f"[AVISO] Resposta sem ID: {result}")
                return True  # Assumir sucesso se não há erro explícito
        else:
            print(f"[ERRO] Z-API HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERRO] Z-API Exception: {e}")
        return False

@app.route("/", methods=["GET"])
def health_check():
    """Endpoint para verificar se o servidor está funcionando"""
    return jsonify({
        "status": "ok",
        "message": "Avantti AI está funcionando!",
        "version": "production"
    }), 200


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "service": "avantti-ai",
        "version": "production"
    }), 200


@app.route("/ping", methods=["GET"])
def ping():
    """Endpoint simples de ping"""
    return "pong"


@app.route("/message_receive", methods=["POST"])
def message_receive() -> tuple:
    """Endpoint para receber mensagens - com IA integrada"""
    payload: dict = request.get_json(silent=True) or {}
    
    try:
        # Extrai dados da mensagem do Z-API
        texto_obj = payload.get('text', {})
        mensagem_texto = texto_obj.get('message', '') if isinstance(texto_obj, dict) else str(texto_obj)
        numero_remetente = payload.get('phone', '')
        
        # Verifica se é uma mensagem válida
        if not mensagem_texto or not numero_remetente:
            return jsonify({"status": "ignored", "reason": "missing_data"}), 200
        
        # Ignora mensagens do próprio bot
        if payload.get('fromMe', False):
            return jsonify({"status": "ignored", "reason": "from_bot"}), 200
        
        print(f"[PROCESSANDO] '{mensagem_texto}' de {numero_remetente}")
        
        # Salva mensagem do cliente
        salvar_mensagem_supabase(numero_remetente, mensagem_texto, is_customer=True)
        
        # Busca contexto da conversa
        contexto = buscar_contexto_conversa(numero_remetente)
        
        # Gera resposta da IA com contexto
        resposta_ia = gerar_resposta_openai(mensagem_texto, numero_remetente, contexto)
        
        # Salva resposta da IA
        salvar_mensagem_supabase(numero_remetente, resposta_ia, is_customer=False)
        
        # Envia resposta via Z-API
        sucesso_envio = enviar_mensagem_zapi(numero_remetente, resposta_ia)
        
        if sucesso_envio:
            return jsonify({
                "status": "processed",
                "message": "Mensagem processada e resposta enviada"
            }), 200
        else:
            return jsonify({
                "status": "generated_only",
                "message": "IA gerou resposta mas falha no envio"
            }), 200
            
    except Exception as e:
        print(f"[ERRO] Processamento: {e}")
        return jsonify({
            "status": "error", 
            "message": f"Erro: {str(e)}"
        }), 500


if __name__ == "__main__":
    print("[STARTUP] === AVANTTI AI - PRODUCTION === ")
    
    port = int(os.getenv('PORT', 5000))
    
    print(f"[SERVIDOR] Starting on host=0.0.0.0, port={port}")
    
    try:
        # Em produção, usar Gunicorn. Em desenvolvimento, Flask
        if os.getenv('FLASK_ENV') == 'production':
            # Gunicorn será usado pelo Dockerfile
            app.run(host="0.0.0.0", port=port, debug=False)
        else:
            # Desenvolvimento
            app.run(host="0.0.0.0", port=port, debug=True)
    except Exception as e:
        print(f"[ERRO] STARTUP: {e}")
        import traceback
        traceback.print_exc()