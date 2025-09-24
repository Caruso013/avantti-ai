import logging
import threading
import os
import sys

# Garante que o diretório raiz está no path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.services.openai_service import OpenAIService
from src.services.supabase_service import SupabaseService
from src.services.zapi_service import ZAPIService
from src.services.whisper_service import WhisperService
from src.services.lead_data_service import LeadDataService

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.supabase_service = SupabaseService()
        self.zapi_service = ZAPIService()
        self.whisper_service = WhisperService()
        self.lead_data_service = LeadDataService()
    
    def processar_mensagem_texto(self, data):
        """Processa mensagem de texto recebida"""
        try:
            phone = data.get('phone')
            message = data.get('message', {}).get('text', '')
            
            if not phone or not message:
                logger.warning("Dados incompletos na mensagem")
                return
            
            logger.info(f"Processando mensagem de {phone}: {message[:50]}...")
            
            # Detecta nome na mensagem (se mencionado)
            self.lead_data_service.detectar_nome_na_mensagem(message, phone)
            
            # Busca contexto da conversa
            context = self.supabase_service.buscar_contexto_conversa(phone)
            
            # Obtém dados do lead para personalização
            lead_data = self.lead_data_service.get_lead_data_for_prompt(phone)
            
            # Gera resposta da IA (retorna lista de mensagens)
            mensagens_resposta = self.openai_service.gerar_resposta(
                message, phone, context, lead_data
            )
            
            # Salva mensagem recebida
            self.supabase_service.salvar_mensagem(
                phone, message, 'user'
            )
            
            # Salva respostas da IA
            for msg in mensagens_resposta:
                self.supabase_service.salvar_mensagem(
                    phone, msg, 'assistant'
                )
            
            # Envia resposta com efeito natural (delay de 10s + typing)
            thread = threading.Thread(
                target=self.zapi_service.enviar_resposta_com_efeito_natural,
                args=(phone, mensagens_resposta)
            )
            thread.daemon = True
            thread.start()
            
            logger.info(f"Resposta processada para {phone}")
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem de texto: {e}")
    
    def processar_mensagem_audio(self, data):
        """Processa mensagem de áudio recebida"""
        try:
            phone = data.get('phone')
            audio_url = data.get('message', {}).get('audioUrl', '')
            
            if not phone or not audio_url:
                logger.warning("Dados incompletos na mensagem de áudio")
                return
            
            logger.info(f"Processando áudio de {phone}")
            
            # Transcreve o áudio
            texto_transcrito = self.whisper_service.transcribe_audio(audio_url)
            
            if texto_transcrito:
                # Cria dados simulando mensagem de texto
                texto_data = {
                    'phone': phone,
                    'message': {'text': texto_transcrito}
                }
                
                # Processa como mensagem de texto
                self.processar_mensagem_texto(texto_data)
            else:
                # Envia mensagem de erro
                mensagem_erro = ["Desculpe, não consegui entender o áudio. Pode escrever sua mensagem?"]
                
                thread = threading.Thread(
                    target=self.zapi_service.enviar_resposta_com_efeito_natural,
                    args=(phone, mensagem_erro)
                )
                thread.daemon = True
                thread.start()
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem de áudio: {e}")
    
    def atualizar_prompt(self, novo_prompt):
        """Atualiza o prompt da IA"""
        try:
            self.openai_service.update_prompt(novo_prompt)
            logger.info("Prompt atualizado via handler")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar prompt: {e}")
            return False