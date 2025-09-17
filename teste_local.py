#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste local para simular o recebimento e processamento de mensagens
"""

import os
import requests
import json
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

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
                    "content": "Você é Sofia, SDR da Avantti AI - empresa especializada em soluções de Inteligência Artificial. Sua missão é qualificar leads interessados em chatbots, automação de atendimento e assistentes virtuais. Seja consultiva, descubra necessidades reais e ofereça soluções personalizadas. Use metodologia BANT (Budget, Authority, Need, Timeline) para qualificar leads."
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
        import traceback
        traceback.print_exc()
        return False

def simular_webhook():
    """Simula o payload que seria recebido do webhook"""
    # Payload similar ao que apareceu no seu log
    payload = {
        'isStatusReply': False,
        'chatLid': '37680435998802@lid',
        'connectedPhone': '554196260255',
        'waitingMessage': False,
        'isEdit': False,
        'isGroup': False,
        'isNewsletter': False,
        'instanceId': '3E6CCAC06181F057FAF2FEB82DDB19DD',
        'messageId': 'TESTE_LOCAL_123',
        'phone': '5511991965237',  # Seu número do log
        'fromMe': False,
        'momment': 1758129901000,
        'status': 'RECEIVED',
        'chatName': 'Teste Local',
        'senderPhoto': None,
        'senderName': 'Teste Local',
        'broadcast': False,
        'participantLid': None,
        'forwarded': False,
        'type': 'ReceivedCallback',
        'fromApi': False,
        'text': {'message': 'teste local'}
    }
    
    return payload

def processar_mensagem_completa():
    """Processa uma mensagem completa como faria o servidor"""
    print("=" * 60)
    print("TESTE LOCAL - PROCESSAMENTO COMPLETO DE MENSAGEM")
    print("=" * 60)
    
    # 1. Simular recebimento do webhook
    payload = simular_webhook()
    print(f"[MENSAGEM RECEBIDA] {payload}")
    
    # 2. Extrair dados
    texto_obj = payload.get('text', {})
    mensagem_texto = texto_obj.get('message', '') if isinstance(texto_obj, dict) else str(texto_obj)
    numero_remetente = payload.get('phone', '')
    
    # 3. Validações
    if not mensagem_texto or not numero_remetente:
        print(f"[AVISO] Mensagem inválida - Texto: '{mensagem_texto}' | Número: '{numero_remetente}'")
        return
    
    if payload.get('fromMe', False):
        print("[AVISO] Mensagem enviada pelo bot - ignorando")
        return
    
    print(f"[PROCESSANDO] '{mensagem_texto}' de {numero_remetente}")
    
    # 4. Gerar resposta da IA
    resposta_ia = gerar_resposta_openai(mensagem_texto)
    print(f"[IA RESPOSTA] {resposta_ia}")
    
    # 5. Enviar resposta via Z-API
    sucesso_envio = enviar_mensagem_zapi(numero_remetente, resposta_ia)
    
    # 6. Resultado final
    print("\n" + "=" * 60)
    if sucesso_envio:
        print("[RESULTADO] MENSAGEM PROCESSADA E ENVIADA COM SUCESSO!")
        print("Verifique seu WhatsApp para confirmar o recebimento.")
    else:
        print("[RESULTADO] MENSAGEM PROCESSADA MAS FALHA NO ENVIO")
    print("=" * 60)

if __name__ == "__main__":
    processar_mensagem_completa()