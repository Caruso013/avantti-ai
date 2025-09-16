from abc import ABC, abstractmethod


class IAI(ABC):

    @abstractmethod
    def create_message(self, thread_id: str, message: str) -> dict:
        pass

    @abstractmethod
    def list_messages(self, thread_id: str) -> dict:
        pass

    @abstractmethod
    def create_run(self, thread_id: str) -> dict:
        pass

    @abstractmethod
    def retrieve_run(self, thread_id: str, run_id: str) -> dict:
        pass

    @abstractmethod
    def function_call_output(
        function_call_id: str,
        call_id: str,
        call_name: str,
        output: str,
        arguments: dict,
        model: str,
    ) -> tuple[list, dict]:
        pass

    @abstractmethod
    def list_input_items(self, response_id: str) -> dict: ...

    @abstractmethod
    def transcribe_audio(self, audio_bytes: str) -> str:
        pass

    @abstractmethod
    def create_thread(self, messages: list | None) -> dict:
        pass

    @abstractmethod
    def create_model_response(
        self,
        model: str,
        input: str | list,
        tools: list = [],
        instructions: str | None = None,
    ) -> dict:
        pass
