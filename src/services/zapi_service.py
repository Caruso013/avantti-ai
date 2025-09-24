import requests
import time
import logging
import os
import re
from typing import List

logger = logging.getLogger(__name__)

class ZAPIService:
    def __init__(self):
        # Usando as variáveis corretas que funcionam no teste
        self.base_url = os.getenv('ZAPI_BASE_URL', 'https://api.z-api.io')
        self.instance_id = os.getenv('ZAPI_INSTANCE_ID')
        self.instance_token = os.getenv('ZAPI_INSTANCE_TOKEN') 
        self.client_token = os.getenv('ZAPI_CLIENT_TOKEN')
        
        # URL completa como no cliente que funciona
        self.api_url = f"{self.base_url}/instances/{self.instance_id}/token/{self.instance_token}"
    
    def _resolve_phone(self, phone: str) -> str:
        """Formata telefone como no cliente que funciona"""
        # Coloca o número o prefixo 9 caso o número tenha 8 dígitos
        if len(phone[4:]) == 8:
            phone = f"{phone[:4]}9{phone[4:]}"

        # Adiciona o DDI 55 caso não tenha
        if not phone.startswith("55") and len(phone) == 11:
            return f"55{phone}"

        return phone
    
    def enviar_typing_indicator(self, phone):
        """Envia indicador de digitando"""
        try:
            url = f"{self.api_url}/chats/{self._resolve_phone(phone)}/typing"
            data = {
                "action": "on"
            }
            
            headers = {
                "Content-Type": "application/json",
                "Client-Token": self.client_token
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Typing indicator enviado para {phone}")
                return True
            else:
                logger.error(f"Erro ao enviar typing: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erro no typing indicator: {e}")
            return False
    
    def parar_typing_indicator(self, phone):
        """Para o indicador de digitando"""
        try:
            url = f"{self.api_url}/chats/{self._resolve_phone(phone)}/typing"
            data = {
                "action": "off"
            }
            
            headers = {
                "Content-Type": "application/json",
                "Client-Token": self.client_token
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Typing indicator parado para {phone}")
                return True
            else:
                logger.error(f"Erro ao parar typing: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao parar typing: {e}")
            return False
    
    def enviar_mensagem(self, phone, message):
        """Envia mensagem simples pelo Z-API - FORMATO EXATO QUE FUNCIONA"""
        try:
            url = f"{self.api_url}/send-text"
            
            # Formato EXATO que funcionou no teste
            data = {
                "phone": self._resolve_phone(phone),
                "message": message,
                "delayTyping": 3
            }
            
            # Headers EXATOS que funcionaram
            headers = {
                "Content-Type": "application/json",
                "Client-Token": self.client_token
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=15)
            
            if response.status_code == 200:
                logger.info(f"Mensagem enviada para {phone}")
                logger.info(f"Response: {response.text}")
                return True
            else:
                logger.error(f"Erro ao enviar mensagem: {response.status_code}")
                logger.error(f"Response: {response.text}")
                logger.error(f"URL: {url}")
                logger.error(f"Data: {data}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return False
    
    def enviar_mensagens_com_delay(self, phone, mensagens: List[str], delay_entre_mensagens=3):
        """
        Envia múltiplas mensagens com typing indicator e delay
        
        Args:
            phone: Número do telefone
            mensagens: Lista de mensagens para enviar
            delay_entre_mensagens: Delay entre cada mensagem (padrão 3s)
        """
        try:
            for i, mensagem in enumerate(mensagens):
                # Envia typing indicator
                self.enviar_typing_indicator(phone)
                
                # Delay baseado no tamanho da mensagem (simula tempo de digitação)
                # Mínimo 2s, máximo 8s
                typing_delay = min(max(len(mensagem) / 20, 2), 8)
                time.sleep(typing_delay)
                
                # Para o typing e envia mensagem
                self.parar_typing_indicator(phone)
                self.enviar_mensagem(phone, mensagem)
                
                # Delay entre mensagens (exceto na última)
                if i < len(mensagens) - 1:
                    time.sleep(delay_entre_mensagens)
            
            logger.info(f"Enviadas {len(mensagens)} mensagens para {phone}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagens com delay: {e}")
            return False
    
    def enviar_resposta_com_efeito_natural(self, phone, mensagens: List[str], delay_inicial=10):
        """
        Envia resposta com delay inicial de 10s e efeitos naturais
        
        Args:
            phone: Número do telefone  
            mensagens: Lista de mensagens para enviar
            delay_inicial: Delay antes da primeira mensagem (padrão 10s)
        """
        try:
            # Delay inicial de 10 segundos
            logger.info(f"Aguardando {delay_inicial}s antes de responder...")
            time.sleep(delay_inicial)
            
            # Envia mensagens com efeito natural
            return self.enviar_mensagens_com_delay(phone, mensagens)
            
        except Exception as e:
            logger.error(f"Erro na resposta com efeito natural: {e}")
            return False