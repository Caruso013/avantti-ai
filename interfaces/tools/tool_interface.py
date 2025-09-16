from abc import ABC, abstractmethod


class ITool(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def model(self) -> str: ...

    @abstractmethod
    async def execute(
        self, response_id: str, function_call_id: str, call_id: str, **kwargs
    ) -> list[dict]: ...
