from abc import ABC, abstractmethod
from typing import Dict, Any


class NotifierInterface(ABC):
    """Interface base para todos os notificadores"""

    @abstractmethod
    def send_notification(self, error_data: Dict[str, Any]) -> bool:
        """
        Enviar notificação de erro

        Args:
            error_data: Dados do erro formatados

        Returns:
            bool: True se enviou com sucesso, False caso contrário
        """
        pass
