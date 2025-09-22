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
    def transcribe_audio(self, audio_url):
        """Transcreve áudio usando OpenAI Whisper"""
        try:
            logger.info(f"Iniciando transcrição de áudio: {audio_url[:50]}...")
            
            # Validação de URL
            if not audio_url or not audio_url.startswith(('http://', 'https://')):
                logger.warning("URL de áudio inválida")
                return None
            
            # Baixa o áudio com validação de tamanho
            response = requests.get(audio_url, timeout=30, stream=True)
            if response.status_code != 200:
                logger.error(f"Falha ao baixar áudio: {response.status_code}")
                return None
            
            # Verifica Content-Length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_size:
                logger.warning(f"Arquivo muito grande: {content_length} bytes")
                return None
            
            # Salva temporariamente com validação
            audio_data = b""
            for chunk in response.iter_content(chunk_size=8192):
                audio_data += chunk
                if len(audio_data) > self.max_size:
                    logger.warning(f"Arquivo excede limite de {self.max_size} bytes")
                    return None
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Transcreve com Whisper
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            
            with open(temp_file_path, 'rb') as audio_file:
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
            
            # Remove arquivo temporário
            os.unlink(temp_file_path)
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('text', '').strip()
                logger.info(f"Áudio transcrito com sucesso: {len(text)} caracteres")
                return text
            else:
                logger.error(f"Erro Whisper: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro na transcrição: {e}")
            return None