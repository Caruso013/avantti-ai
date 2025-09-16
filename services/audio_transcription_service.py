from interfaces.clients.chat_interface import IChat
from interfaces.clients.ai_interface import IAI
from utils.logger import logger, to_json_dump


class AudioTranscriptionService:
    def __init__(self, chat_client: IChat, ai_client: IAI):
        self.chat = chat_client
        self.ai = ai_client

    def transcribe(self, **kwargs: dict) -> str | None:
        if not self.chat.is_audio_message(**kwargs):
            return None

        try:
            audio_bytes = self.chat.get_audio_bytes(**kwargs)
            return self.ai.transcribe_audio(audio_bytes=audio_bytes)
        except Exception as e:
            logger.error(
                f"[AUDIO TRANSCRIPTION SERVICE] Falha ao transcrever o áudio: {to_json_dump(e)}"
            )
            return None
