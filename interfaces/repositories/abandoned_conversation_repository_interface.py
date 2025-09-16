from abc import ABC, abstractmethod


class IAbandonedConversationRepository(ABC):
    @abstractmethod
    def find(self, phone: str) -> dict | None:
        pass

    @abstractmethod
    def mark_as_abandoned_conversation(self, phone: str) -> bool:
        pass

    @abstractmethod
    def unmark_as_abandoned_conversation(self, phone: str) -> bool:
        pass

    @abstractmethod
    def is_abandoned_conversation(self, phone: str) -> bool:
        """
        Check if a conversation is marked as abandoned.
        Returns True if it is, False otherwise.
        """
        pass

    @abstractmethod
    def is_not_abandoned_conversation(self, phone: str) -> bool:
        """
        Check if a conversation is not marked as abandoned.
        Returns True if it is not, False otherwise.
        """
        pass
