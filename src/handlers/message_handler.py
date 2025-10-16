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
from src.services.zapi_client_service import ZAPIClientService

logger = logging.getLogger(__name__)

class MessageHandler:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.supabase_service = SupabaseService()
        self.zapi_client = ZAPIClientService()  # CORRIGIDO - usar service interno
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
            logger.info(f"🔄 Contexto recuperado para {phone}: {len(context) if context else 0} mensagens")
            
            # Obtém dados do lead para personalização
            lead_data = self.lead_data_service.get_lead_data_for_prompt(phone)
            
            # Gera resposta da IA (retorna lista de mensagens)
            logger.info(f"📤 Enviando para IA: mensagem='{message[:50]}...', contexto={len(context) if context else 0} msgs")
            mensagens_resposta = self.openai_service.gerar_resposta(
                message, phone, context, lead_data, self.supabase_service
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
        """Processa mensagem de áudio recebida (baixa, transcreve e envia para IA)"""
        import tempfile
        import requests
        import os
        try:
            phone = data.get('phone')
            audio_url = data.get('message', {}).get('audioUrl', '')
            if not phone or not audio_url:
                logger.warning("Dados incompletos na mensagem de áudio")
                return
            logger.info(f"🎵 Processando áudio de {phone} - URL: {audio_url[:50]}...")

            # Baixa o arquivo de áudio para um arquivo temporário
            temp_audio_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                    logger.info(f"📥 Baixando áudio de {audio_url} para {temp_audio.name}")
                    resp = requests.get(audio_url, stream=True, timeout=20)
                    resp.raise_for_status()
                    
                    # Verifica tamanho do arquivo (máximo 25MB)
                    content_length = resp.headers.get('content-length')
                    if content_length and int(content_length) > 25 * 1024 * 1024:
                        logger.warning(f"Arquivo muito grande: {content_length} bytes")
                        self._enviar_mensagens_com_delay(phone, ["O áudio é muito grande. Tente um arquivo menor."])
                        return
                    
                    for chunk in resp.iter_content(chunk_size=8192):
                        temp_audio.write(chunk)
                    temp_audio_path = temp_audio.name
                    
                logger.info(f"✅ Áudio baixado com sucesso: {temp_audio_path}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao baixar áudio: {e}")
                self._enviar_mensagens_com_delay(phone, ["Não consegui baixar o áudio. Pode tentar novamente?"])
                return

            # Transcreve o áudio localmente
            try:
                logger.info(f"🎯 Iniciando transcrição do arquivo: {temp_audio_path}")
                texto_transcrito = self.whisper_service.transcribe_audio(temp_audio_path)
                logger.info(f"📝 Transcrição concluída: '{texto_transcrito[:100]}...'")
                
            except Exception as e:
                logger.error(f"❌ Erro ao transcrever áudio: {e}")
                self._enviar_mensagens_com_delay(phone, ["Não consegui transcrever o áudio. Pode tentar novamente?"])
                if temp_audio_path and os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                return

            # Remove arquivo temporário
            try:
                if temp_audio_path and os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                    logger.info(f"🗑️ Arquivo temporário removido: {temp_audio_path}")
            except Exception as e:
                logger.warning(f"Não foi possível remover arquivo temporário: {e}")

            # Processa o texto transcrito
            if texto_transcrito and texto_transcrito.strip():
                logger.info(f"🤖 Enviando texto transcrito para IA: '{texto_transcrito[:50]}...'")
                texto_data = {
                    'phone': phone,
                    'message': {'text': texto_transcrito}
                }
                self.processar_mensagem_texto(texto_data)
            else:
                logger.warning("Texto transcrito vazio ou None")
                mensagem_erro = ["Desculpe, não consegui entender o áudio. Pode escrever sua mensagem?"]
                self._enviar_mensagens_com_delay(phone, mensagem_erro)
                
        except Exception as e:
            logger.error(f"❌ Erro geral ao processar mensagem de áudio: {e}")
            try:
                if 'temp_audio_path' in locals() and temp_audio_path and os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
            except:
                pass
    
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
        """Envia mensagens com delay de 10s inicial e 3s entre mensagens"""
        try:
            import time
            
            # Delay inicial de 10 segundos
            time.sleep(10)
            
            # Envia mensagens com delay de 3s entre elas
            for i, mensagem in enumerate(mensagens):
                # Remove emojis manualmente por garantia
                mensagem_limpa = self._remover_emojis(mensagem)
                
                # Envia a mensagem
                self.zapi_client.send_message(phone, mensagem_limpa)
                
                # Delay de 3 segundos entre mensagens (exceto na última)
                if i < len(mensagens) - 1:
                    logger.info(f"⏳ Aguardando 3s antes da próxima mensagem...")
                    time.sleep(3)
                
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