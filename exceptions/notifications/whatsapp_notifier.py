import copy
import os
from typing import Dict, Any
from . import NotifierInterface
from interfaces.clients.chat_interface import IChat
from utils.logger import logger


class WhatsAppNotifier(NotifierInterface):
    """Notificador por WhatsApp para erros"""

    def __init__(self, container):
        self.phone: str = os.getenv("ERROR_NOTIFICATION_PHONE_NUMBER")
        self.chat: IChat = copy.deepcopy(container.clients.chat)

        self._configure_credentials()

    def _configure_credentials(self):
        instance = os.getenv("ERROR_NOTIFICATION_INSTANCE")
        instance_key = os.getenv("ERROR_NOTIFICATION_INSTANCE_KEY")

        self.chat.set_instance(instance, instance_key)

    def send_notification(self, error_data: Dict[str, Any]) -> bool:
        """Enviar mensagem WhatsApp com detalhes do erro"""
        try:
            if not self.phone:
                logger.warning(
                    "[WhatsAppNotifier] ⚠️ Nenhum número de notificação de erro configurado."
                )
                return False

            message = self._format_whatsapp_message(error_data)

            self.chat.send_message(phone=self.phone, message=message)

        except Exception as e:
            logger.warning(f"[WhatsAppNotifier] ❌ Erro ao enviar WhatsApp: {e}")
            return False

    def _format_whatsapp_message(self, error_data: Dict[str, Any]) -> str:
        """Formatar mensagem do WhatsApp"""
        return f"""🚨 *ERRO NA APLICAÇÃO*

        📍 *Serviço:* {error_data['service']}
        ⏰ *Timestamp:* {error_data['timestamp']}
        📁 *Arquivo:* {error_data['file']}
        🔧 *Função:* {error_data['function']}
        📝 *Linha:* {error_data['line']}
        ⚠️ *Tipo:* {error_data['error_type']}
        💬 *Mensagem:* {error_data['message']}

        *Stack Trace:*
        ```
        {error_data['traceback'][:500]}...
        ```"""
