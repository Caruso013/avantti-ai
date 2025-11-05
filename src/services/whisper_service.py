import os
import requests
import tempfile
import logging
from functools import wraps
import time

logger = logging.getLogger(__name__)

def log_performance(func):
    """Decorator para log de performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"{func.__name__} executado em {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} falhou após {duration:.2f}s: {e}")
            raise
    return wrapper

class WhisperService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.max_size = int(os.getenv('OPENAI_MAX_AUDIO_TRANSCRIBE_MB', 25)) * 1024 * 1024
    
    @log_performance
    def transcribe_audio(self, audio_path):
        """Transcreve áudio usando OpenAI Whisper"""
        try:
            logger.info(f"Iniciando transcrição de áudio: {audio_path}")
            
            # Verifica se o arquivo existe
            if not os.path.exists(audio_path):
                logger.error(f"Arquivo de áudio não encontrado: {audio_path}")
                return None
            
            # Verifica tamanho do arquivo
            file_size = os.path.getsize(audio_path)
            if file_size > self.max_size:
                logger.warning(f"Arquivo muito grande: {file_size} bytes")
                return None
            
            # Transcreve com Whisper
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            with open(audio_path, 'rb') as audio_file:
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
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('text', '').strip()
                logger.info(f"Áudio transcrito com sucesso: {len(text)} caracteres")
                return text
            else:
                logger.error(f"Erro Whisper: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Erro na transcrição: {e}")
            return None