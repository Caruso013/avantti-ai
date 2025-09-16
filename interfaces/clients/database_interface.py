from abc import ABC, abstractmethod
from sqlalchemy.orm import Session


class IDatabase(ABC):
    @abstractmethod
    def get_session(self) -> Session:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    # @abstractmethod
    # def get_thread_id(self) -> str | None:
    #     pass

    # @abstractmethod
    # def turn_off_auto_response(self, phone: str) -> bool:
    #     pass

    # @abstractmethod
    # def get_phone(self, thread_id: str) -> str:
    #     pass

    # @abstractmethod
    # def get_deal_id(self, phone: str) -> str:
    #     pass

    # @abstractmethod
    # def create_deal(self, deal_id: str, phone: str) -> bool:
    #     pass
