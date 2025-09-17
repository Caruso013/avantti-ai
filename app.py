from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Versão simplificada - sem Container complexo
print("=== AVANTTI AI - VERSÃO SIMPLIFICADA ===")

def gerar_resposta_openai(mensagem):
    """Gera resposta usando OpenAI"""
    try:
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            print("[ERRO] OPENAI_API_KEY não encontrada")
            return "Desculpe, serviço temporariamente indisponível."
        
        print(f"[IA] Gerando resposta para: '{mensagem}'")
        
        headers = {
            'Authorization': f'Bearer {openai_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
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

Seja sempre simpática, humana, use frases curtas e objetivas. Tom formal-casual."""
                },
                {
                    "role": "user", 
                    "content": mensagem
                }
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }
        
        print("[API] Fazendo requisição para OpenAI...")
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=10
        )
        
        print(f"[STATUS] OpenAI Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            resposta = result['choices'][0]['message']['content'].strip()
            print(f"[SUCESSO] Resposta gerada: '{resposta}'")
            return resposta
        else:
            print(f"[ERRO] OpenAI: {response.status_code} - {response.text}")
            return "Desculpe, ocorreu um erro. Tente novamente em alguns instantes."
            
    except Exception as e:
        print(f"[ERRO] Erro ao gerar resposta: {e}")
        import traceback
        traceback.print_exc()
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
    """Endpoint para receber mensagens - com IA integrada"""
    payload: dict = request.get_json(silent=True) or {}
    
    print(f"[MENSAGEM RECEBIDA] {payload}")
    
    try:
        # Extrai dados da mensagem do Z-API
        # Z-API estrutura: {'text': {'message': 'conteúdo'}, 'phone': 'numero'}
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
        
        print(f"[PROCESSANDO] '{mensagem_texto}' de {numero_remetente}")
        
        # Gera resposta da IA
        resposta_ia = gerar_resposta_openai(mensagem_texto)
        print(f"[IA RESPOSTA] {resposta_ia}")
        
        # Envia resposta via Z-API
        sucesso_envio = enviar_mensagem_zapi(numero_remetente, resposta_ia)
        
        if sucesso_envio:
            return jsonify({
                "status": "processed",
                "message": "Mensagem processada e resposta enviada",
                "ia_response": resposta_ia
            }), 200
        else:
            return jsonify({
                "status": "generated_only",
                "message": "IA gerou resposta mas falha no envio",
                "ia_response": resposta_ia
            }), 200
            
    except Exception as e:
        print(f"[ERRO] Erro no processamento: {e}")
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
