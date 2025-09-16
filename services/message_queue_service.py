import os
from interfaces.clients.cache_interface import ICache
from interfaces.clients.chat_interface import IChat
from utils.logger import logger
from services.unsupported_media_handler_service import UnsupportedMediaHandlerService
from services.audio_transcription_service import AudioTranscriptionService
from interfaces.repositories.abandoned_conversation_repository_interface import (
    IAbandonedConversationRepository,
)


class MessageQueueService:

    def __init__(
        self,
        cache_client: ICache,
        chat_client: IChat,
        unsupported_media_handler: UnsupportedMediaHandlerService,
        audio_transcription_service: AudioTranscriptionService,
        abandoned_message_repository: IAbandonedConversationRepository,
    ) -> None:
        self.cache = cache_client
        self.chat = chat_client
        self.unsupported_media_handler = unsupported_media_handler
        self.audio_transcription_service = audio_transcription_service
        self.abandoned_message_repository = abandoned_message_repository

    def handle(self, **kwargs) -> None:
        phone: str = self.chat.get_phone(**kwargs) or ""
        kwargs["phone"] = phone

        if not self.chat.is_valid_message(**kwargs):
            return

        if self.unsupported_media_handler.handle(kwargs):
            return

        message = ""

        if self.chat.is_image(**kwargs):
            caption: str = self.chat.get_image_caption(**kwargs)
            url: str = self.chat.get_image_url(**kwargs)
            message = f"<image-url>{url}</image-url> {caption or ''}"

        elif self.chat.is_file(**kwargs):
            caption: str = self.chat.get_file_caption(**kwargs)
            url: str = self.chat.get_file_url(**kwargs)
            message = f"<file-url>{url}</file-url> {caption or ''}"

        else:
            transcribed_message = self.audio_transcription_service.transcribe(**kwargs)
            message = transcribed_message or self.chat.get_message(**kwargs)

        queue_key = os.getenv("QUEUE_KEY")
        self.cache.add_to_queue(
            queue_key=queue_key, key=phone, value=message, append=True
        )

        logger.info(
            f"[MESSAGE QUEUE SERVICE] Adicionado mensagem para o número {phone} na fila {queue_key}. Mensagem: {message!r}"
        )
