import os
from interfaces.clients.chat_interface import IChat
from interfaces.clients.database_interface import IDatabase
from utils.logger import logger


class UnsupportedMediaHandlerService:
    def __init__(self, chat_client: IChat, database_client: IDatabase):
        self.chat = chat_client
        self.database = database_client

    def handle(self, message: dict) -> bool:
        phone = self.chat.get_phone(**message)

        if any(key in message for key in ["document", "video"]):
            self.chat.send_message(
                phone=os.getenv("PHONE_NUMBER_NOTIFICATION"),
                message=f"⚠️ Um lead enviou um arquivo não suportado. \nNome: {message['chatName']} \nTelefone: {phone}.",
            )

            logger.info(
                f"[UNSUPPORTED MEDIA HANDLER] Arquivo recebido não suportado. Telefone: {phone}"
            )
            return True
        return False
