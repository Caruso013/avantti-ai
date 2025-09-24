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
from src.services.whisper_service import WhisperService
from src.services.lead_data_service import LeadDataService

# Import ZAPIClient with multiple fallback strategies for different environments
try:
    # Method 1: Direct import from clients package
    from clients.zapi_client import ZAPIClient
except ImportError:
    try:
        # Method 2: Import via sys.path manipulation
        clients_path = os.path.join(root_dir, 'clients')
        if clients_path not in sys.path:
            sys.path.insert(0, clients_path)
        from zapi_client import ZAPIClient
    except ImportError:
        # Method 3: Import from clients package directly
        import clients
        ZAPIClient = clients.ZAPIClient

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.supabase_service = SupabaseService()
        self.zapi_client = ZAPIClient()  # CORRIGIDO - usar cliente que funciona
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
            
            # Salva mensagem recebida (sem emojis)
            self.supabase_service.salvar_mensagem(
                phone, self._remover_emojis(message), 'user'
            )
            
            # Salva respostas da IA (sem emojis)
            for msg in mensagens_resposta:
                self.supabase_service.salvar_mensagem(
                    phone, self._remover_emojis(msg), 'assistant'
                )
            
            # Envia resposta usando ZAPIClient com delay
            thread = threading.Thread(
                target=self._enviar_mensagens_com_delay,
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
                    target=self._enviar_mensagens_com_delay,
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
    
    def _enviar_mensagens_com_delay(self, phone, mensagens):
        """Envia mensagens com delay de 10s usando ZAPIClient"""
        try:
            import time
            
            # Delay inicial de 10 segundos
            time.sleep(10)
            
            # Envia cada mensagem (ZAPIClient já quebra e filtra emojis automaticamente)
            for mensagem in mensagens:
                # Remove emojis manualmente também por garantia
                mensagem_limpa = self._remover_emojis(mensagem)
                self.zapi_client.send_message(phone, mensagem_limpa)
                
        except Exception as e:
            logger.error(f"Erro ao enviar mensagens com delay: {e}")
    
    def _remover_emojis(self, texto):
        """Remove emojis do texto usando uma abordagem mais robusta"""
        import re
        
        # Remove emojis usando múltiplos padrões
        # Padrão 1: Emojis padrão
        texto = re.sub(r'[\U0001F600-\U0001F64F]', '', texto)  # emoticons
        texto = re.sub(r'[\U0001F300-\U0001F5FF]', '', texto)  # symbols & pictographs
        texto = re.sub(r'[\U0001F680-\U0001F6FF]', '', texto)  # transport & map symbols
        texto = re.sub(r'[\U0001F1E0-\U0001F1FF]', '', texto)  # flags (iOS)
        texto = re.sub(r'[\U00002702-\U000027B0]', '', texto)
        texto = re.sub(r'[\U000024C2-\U0001F251]', '', texto)
        texto = re.sub(r'[\U0001F900-\U0001F9FF]', '', texto)  # Supplemental Symbols and Pictographs
        texto = re.sub(r'[\U0001FA70-\U0001FAFF]', '', texto)  # Symbols and Pictographs Extended-A
        
        # Padrão 2: Remove símbolos específicos que podem passar
        symbols_to_remove = ['😊', '😀', '😁', '😂', '🤣', '😃', '😄', '😅', '😆', '😉', '😊', 
                            '😋', '😎', '😍', '😘', '🥰', '😗', '😙', '😚', '🤪', '😜', '😝',
                            '🤑', '🤗', '🤭', '🤫', '🤔', '🤐', '🤨', '😐', '😑', '😶', '😏',
                            '😒', '🙄', '😬', '🤥', '😔', '😪', '🤤', '😴', '😷', '🤒', '🤕',
                            '🤢', '🤮', '🤧', '🥵', '🥶', '🥴', '😵', '🤯', '🤠', '🥳', '😎',
                            '🧐', '😕', '😟', '🙁', '☹️', '😮', '😯', '😲', '😳', '🥺', '😦',
                            '😧', '😨', '😰', '😥', '😢', '😭', '😱', '😖', '😣', '😞', '😓',
                            '😩', '😫', '🥱', '😤', '😡', '😠', '🤬', '😈', '👿', '💀', '☠️',
                            '💩', '🤡', '👹', '👺', '👻', '👽', '👾', '🤖', '🎃', '😺', '😸',
                            '🏢', '💰', '📍', '📞', '📌', '❌', '✅', '⚠️', '📝', '💬', '🚀',
                            '🎯', '🔥', '👨‍💻', '🏡', '💪', '🙌', '👏', '🎉', '💸', '💵', '💴',
                            '📈', '📊', '🏠', '🏗️', '🌟', '⭐', '💯', '👍', '👎', '❤️', '💙',
                            '💚', '🎁', '🎊', '🔔', '🔕', '📢', '📣', '📺', '📻', '📷', '📹',
                            '🎵', '🎶', '🟢', '🟡', '🔴', '🟠', '⚡', '💡', '🔒', '🔓', '🔑',
                            '🔐', '👥', '🔄', '▶️', '🧪', '🧹', '📱', '🤖']
        
        for symbol in symbols_to_remove:
            texto = texto.replace(symbol, '')
        
        # Remove espaços extras e limpa
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto