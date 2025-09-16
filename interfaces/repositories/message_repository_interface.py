from abc import ABC, abstractmethod
from datetime import datetime


class IMessageRepository(ABC):
    @abstractmethod
    def all(self) -> list:
        """Retrieve all messages."""
        pass

    @abstractmethod
    def get_latest_customer_messages(
        self, phone: int | None = None, limit: int = 20
    ) -> list:
        """Retrieve the latest message for a given phone number."""
        pass

    @abstractmethod
    def get_abandoned_conversation_numbers(
        self,
        until_time: datetime,
    ) -> list:
        """Retrieve all the latest messages."""
        pass

    @abstractmethod
    def create(self, phone: str, role: str, content: str | list) -> dict:
        """Create a new message."""
        pass
