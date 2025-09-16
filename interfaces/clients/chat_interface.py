from abc import ABC, abstractmethod


class IChat(ABC):

    @abstractmethod
    def set_instance(self, instance: str, instance_key: str) -> None:
        pass

    @abstractmethod
    def send_message(self, phone: str, message: str) -> bool:
        pass

    @abstractmethod
    def get_message(self, **kwargs) -> str:
        pass

    @abstractmethod
    def get_phone(self, **kwargs) -> str:
        pass

    @abstractmethod
    def is_valid_message(self, **kwargs) -> bool:
        pass

    @abstractmethod
    def is_audio_message(self, **kwargs) -> bool:
        pass

    @abstractmethod
    def get_audio_bytes(self, **kwargs) -> str:
        pass

    @abstractmethod
    def is_image(self, **kwargs) -> bool:
        pass

    @abstractmethod
    def get_image_url(self, **kwargs) -> str:
        pass

    @abstractmethod
    def get_image_caption(self, **kwargs) -> str:
        pass

    @abstractmethod
    def is_file(self, **kwargs) -> bool:
        pass

    @abstractmethod
    def get_file_url(self, **kwargs) -> str:
        pass

    @abstractmethod
    def get_file_caption(self, **kwargs) -> str:
        pass
