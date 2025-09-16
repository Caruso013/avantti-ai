import os
from typing import List
from interfaces.notifier_interface import NotifierInterface
from exceptions.notifications.whatsapp_notifier import WhatsAppNotifier


class NotifierFactory:
    """Factory para criar lista de notificadores baseado na configuração"""

    _notifier_classes = {
        "whatsapp": WhatsAppNotifier,
    }

    @classmethod
    def create_notifiers(cls, container) -> List[NotifierInterface]:
        """
        Criar lista de notificadores baseado no .env

        Returns:
            List[NotifierInterface]: Lista de notificadores ativos
        """
        notifiers = []

        # Verificar se notificações estão habilitadas
        if not cls._is_notifications_enabled():
            return notifiers

        # Obter lista de notificadores do .env
        notifier_names = cls._get_enabled_notifiers()

        # Criar instâncias dos notificadores
        for name in notifier_names:
            if name in cls._notifier_classes:
                try:
                    notifier = cls._notifier_classes[name](container)
                    notifiers.append(notifier)
                    print(f"✅ Notificador {name} ativado")
                except Exception as e:
                    print(f"❌ Erro ao criar notificador {name}: {e}")
            else:
                print(f"⚠️  Notificador desconhecido: {name}")

        return notifiers

    @classmethod
    def _is_notifications_enabled(cls) -> bool:
        """Verificar se notificações estão habilitadas"""
        enabled = os.getenv("ERROR_NOTIFICATION_ENABLED", "false").lower()
        return enabled in ["true", "1", "yes", "on"]

    @classmethod
    def _get_enabled_notifiers(cls) -> List[str]:
        """Obter lista de notificadores habilitados"""
        notifiers_str = os.getenv("ERROR_NOTIFIERS", "")
        if not notifiers_str:
            return []

        return [name.strip() for name in notifiers_str.split(",") if name.strip()]
