import os
import time
import io
import json
from openai import OpenAI, OpenAIError, NotGiven, NOT_GIVEN
from enums.openai_run_status_enum import OpenaiRunStatus
from utils.logger import logger, to_json_dump
from interfaces.clients.ai_interface import IAI
from openai.types.audio import Transcription


class OpenIAClient(IAI):
    MAX_AUDIO_TRANSCRIBE_MB = int(os.getenv("OPENAI_MAX_AUDIO_TRANSCRIBE_MB", "25"))

    def __init__(self):
        self.assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.max_output_tokens = int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "1000"))

    def create_thread(self, messages: list | NotGiven = NOT_GIVEN) -> dict:
        try:
            thread: dict = self.client.beta.threads.create(messages=messages).to_dict()

            logger.info(f"[OPENAI] Thread criada: {thread}")

            return thread
        except Exception as e:
            logger.exception(f"[OPENAI] ❌ Erro ao criar a thread: \n{to_json_dump(e)}")
            raise e

    def retrieve_thread(self, thread_id: str) -> dict:
        try:
            thread: dict = self.client.beta.threads.retrieve(thread_id).to_dict()

            logger.info(
                f"[OPENAI] Thread recuperada com o id {thread.get('id')} e status {thread.get('status')}"
            )

            return thread
        except Exception as e:
            logger.exception(f"[OPENAI] ❌ Erro ao obter a thread: \n{to_json_dump(e)}")
            raise e

    def create_message(self, thread_id: str, message: str) -> dict:
        logger.info(
            f"[OPENAI] Criando message para a thread_id: {thread_id}: message: {message}"
        )

        try:
            thread_message: dict = self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message,
            ).to_dict()

            logger.info(
                f"[OPENAI] Message criada com o id {thread_message.get('id')}, thread_id: {thread_id}"
            )

            return thread_message
        except Exception as e:
            logger.exception(f"[OPENAI] ❌ Erro ao criar message: \n{to_json_dump(e)}")
            raise e

    def list_messages(self, thread_id: str) -> dict:
        logger.info(f"[OPENAI] Listando messages com o thread id: {thread_id}")

        try:
            thread_messages: dict = self.client.beta.threads.messages.list(
                thread_id=thread_id
            ).to_dict()

            return thread_messages
        except Exception as e:
            logger.exception(
                f"[OPENAI] ❌ Erro ao listar as messages: \n{to_json_dump(e)}"
            )
            raise e

    def create_run(self, thread_id: str) -> dict:
        payload = {"assistant_id": self.assistant_id}

        logger.info(
            f"[OPENAI] Criando run com o thread_id: {thread_id}, payload: \n{to_json_dump(payload)}"
        )

        try:
            run: dict = self.client.beta.threads.runs.create(
                thread_id=thread_id, assistant_id=self.assistant_id
            ).to_dict()

            logger.info(
                f"[OPENAI] Run criada com o id {run.get('id')}, thread_id: {thread_id}"
            )

            return run
        except Exception as e:
            logger.exception(f"[OPENAI] ❌ Erro ao criar run: \n{to_json_dump(e)}")
            raise e

    def retrieve_run(self, thread_id: str, run_id: str) -> dict:
        logger.info(
            f"[OPENAI] Recuperando run com o thread id: {thread_id}, run id: {run_id}"
        )

        try:
            run: dict = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run_id
            ).to_dict()

            logger.info(
                f"[OPENAI] Run recuperada com o id {run.get('id')}, thread_id: {thread_id}"
            )

            return run
        except Exception as e:
            logger.exception(f"[OPENAI] ❌ Erro ao obter run: \n{to_json_dump(e)}")
            raise e

    def listening_run(self, thread_id: str, run_id: str) -> dict:
        while True:
            run = self.retrieve_run(thread_id, run_id)

            if run["status"] not in [
                OpenaiRunStatus.QUEUED.value,
                OpenaiRunStatus.IN_PROGRESS.value,
            ]:
                logger.info(
                    f"[OPENAI] Run com o id {run['id']} mudou o status para: {run['status']}"
                )
                return run

            time.sleep(3)

    def function_call_output(
        self,
        function_call_id: str,
        call_id: str,
        call_name: str,
        output: str,
        arguments: dict,
        model: str = "gpt-4.1-nano",
    ) -> tuple[list, dict]:
        logger.info(
            f"[OPENAI] Function call output. function_call_id: {function_call_id}, call_id: {call_id}, function_call_id: {function_call_id}, output: {output}"
        )

        try:
            input = [
                {
                    "type": "function_call",
                    "id": function_call_id,
                    "call_id": call_id,
                    "name": call_name,
                    "arguments": json.dumps(arguments),
                },
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": output,
                },
            ]

            response = self.client.responses.create(
                model=model,
                instructions="",
                input=input,
                temperature=0.5,
            )

            logger.info(
                f"[OPENAI] Resposta do Function call output com o function_call_id {function_call_id}, call_id: {call_id}: \n{to_json_dump(response.to_dict())}"
            )

            return (input, response.to_dict())
        except Exception as e:
            logger.exception(
                f"[OPENAI] ❌ Erro ao fazer o function call output: \n{to_json_dump(e)}"
            )
            raise e

    def list_input_items(self, response_id: str) -> dict:
        logger.info(f"[OPENAI] Listando input items com o response_id: {response_id}")

        try:
            response = self.client.responses.input_items.list(response_id=response_id)

            return response.to_dict()
        except OpenAIError as e:
            logger.exception(
                f"[OPENAI] ❌ Erro ao listar input items: \n{to_json_dump(e)}"
            )
            raise e

    def transcribe_audio(self, audio_bytes: str) -> str:
        try:
            logger.info("[OPENAI] Transcrevendo audio...")

            buf = io.BytesIO(audio_bytes)
            buf.name = "voice.ogg"
            buf.seek(0, io.SEEK_END)
            size = buf.tell()
            buf.seek(0)

            if size > (self.MAX_AUDIO_TRANSCRIBE_MB * 1024 * 1024):
                raise Exception(
                    f"[OPENAI] O tamanho do audio é maior que {self.MAX_AUDIO_TRANSCRIBE_MB}MB"
                )

            result: Transcription = self.client.audio.transcriptions.create(
                model="whisper-1", file=buf, language="pt"
            )

            logger.info(f"[OPENAI] Resultado da transcrição: \n{to_json_dump(result)}")

            return result.text
        except OpenAIError as e:
            logger.exception(
                f"[OPENAI] ❌ Erro ao transcrever audio: \n{to_json_dump(e)}"
            )
            raise e

    def create_model_response(
        self,
        model: str,
        input: str | list,
        tools: list = [],
        instructions: str | None = None,
    ) -> dict:
        try:
            logger.info(
                f"[OPENAI] Criando resposta: modelo: {model}, input: \n{to_json_dump(input)}"
            )

            response = self.client.responses.create(
                model=model,
                instructions=instructions,
                input=input,
                tools=tools,
                temperature=0.5,
                top_p=1.0,
                store=True,
            )

            return response.to_dict()
        except OpenAIError as e:
            logger.exception(
                f"[OPENAI] ❌ Erro ao criar resposta do modelo: \n{to_json_dump(e)}"
            )
            raise e
