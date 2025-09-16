from abc import ABC, abstractmethod


class ICache(ABC):

    @abstractmethod
    def get_queue(self, queue_key: str):
        pass

    @abstractmethod
    def add_to_queue(
        self, queue_key: str, key: str, value: str, append: bool = False
    ) -> int:
        pass

    @abstractmethod
    def delete_queue(self, queue_key: str, keys_to_delete: list[str]):
        pass
