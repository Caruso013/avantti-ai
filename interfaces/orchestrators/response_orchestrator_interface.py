from abc import ABC, abstractmethod


class IResponseOrchestrator(ABC):
    @property
    @abstractmethod
    def model(self) -> str: ...

    @property
    @abstractmethod
    def instructions(self) -> str: ...

    @property
    @abstractmethod
    def tools(self) -> list: ...

    @property
    @abstractmethod
    def system_prompt(self) -> dict: ...

    @abstractmethod
    def execute(self, context: list, phone: str) -> list[dict]: ...
