import requests
import time
import logging
import os
from typing import List

logger = logging.getLogger(__name__)

class ZAPIService:
    def __init__(self):
        self.instance = os.getenv('ZAPI_INSTANCE')
        self.token = os.getenv('ZAPI_TOKEN')
        self.base_url = f"https://api.z-api.io/instances/{self.instance}/token/{self.token}"
    
    def enviar_typing_indicator(self, phone):
        """Envia indicador de digitando"""
        try:
            url = f"{self.base_url}/chats/{phone}/typing"
            data = {
                "action": "on"
            }
            
            response = requests.post(url, json=data, timeout=10)
            
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
            url = f"{self.base_url}/chats/{phone}/typing"
            data = {
                "action": "off"
            }
            
            response = requests.post(url, json=data, timeout=10)
            
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
        """Envia mensagem simples pelo Z-API"""
        try:
            url = f"{self.base_url}/send-text"
            
            # Formato correto para Z-API
            data = {
                "phone": phone,
                "message": message,
                "delayTyping": 3
            }
            
            # Headers necessários
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=15)
            
            if response.status_code == 200:
                logger.info(f"Mensagem enviada para {phone}")
                return True
            else:
                logger.error(f"Erro ao enviar mensagem: {response.status_code}")
                logger.error(f"Response: {response.text}")
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
    
    def enviar_resposta_com_efeito_natural(self, phone, mensagens: List[str], delay_inicial=15):
        """
        Envia resposta com delay inicial de 15s e efeitos naturais
        
        Args:
            phone: Número do telefone  
            mensagens: Lista de mensagens para enviar
            delay_inicial: Delay antes da primeira mensagem (padrão 15s)
        """
        try:
            # Delay inicial de 15 segundos
            logger.info(f"Aguardando {delay_inicial}s antes de responder...")
            time.sleep(delay_inicial)
            
            # Envia mensagens com efeito natural
            return self.enviar_mensagens_com_delay(phone, mensagens)
            
        except Exception as e:
            logger.error(f"Erro na resposta com efeito natural: {e}")
            return False