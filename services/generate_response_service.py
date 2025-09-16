import os
import re
import json
from interfaces.clients.chat_interface import IChat
from utils.logger import logger, to_json_dump
from interfaces.repositories.message_repository_interface import IMessageRepository
from interfaces.orchestrators.response_orchestrator_interface import (
    IResponseOrchestrator,
)


class GenerateResponseService:

    def __init__(
        self,
        chat_client: IChat,
        message_repository: IMessageRepository,
        response_orchestrator: IResponseOrchestrator,
    ) -> None:
        self.chat = chat_client
        self.message_repository = message_repository
        self.response_orchestrator = response_orchestrator

    def _resolve_output_content(self, outputs: list | dict) -> str:
        logger.info(
            f"[GENERATE RESPONSE SERVICE] Resolvendo o conteúdo da resposta: \n{to_json_dump(outputs)}"
        )

        return ". ".join(
            (
                output.get("content")
                if isinstance(output.get("content"), str)
                else output.get("content")[0]["text"]
            )
            for output in outputs
            if output.get("role", "") == "assistant"
        )

    def _prepare_context(self, context: list, user_input: str) -> list[dict]:
        # Faz a formatação correta do contexto caso não esteja vazio
        if context:
            context_resolved = []

            # Trata os casos do contexto simples do usuário e do assistente e das chamadas e saídas das tools
            for message in context[::-1]:
                role = message.get("role", "")
                content = message.get("content", "")

                if role in ["user", "assistant"]:
                    context_resolved.append({"role": role, "content": content})
                    continue

                context_resolved.append(content)

            context = context_resolved

        # Prepara o input de imagem caso exista
        image_url = re.search(r"<image-url>(.*?)</image-url>", user_input)
        if image_url:
            user_input = re.sub(r"<image-url>.*?</image-url>", "", user_input).strip()
            context.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": user_input,
                        },
                        {
                            "type": "input_image",
                            "image_url": image_url.group(1),
                        },
                    ],
                }
            )

            return context

        # Prepara o input de arquivo caso exista
        file_url = re.search(r"<file-url>(.*?)</file-url>", user_input)
        if file_url:
            user_input = re.sub(r"<file-url>.*?</file-url>", "", user_input).strip()
            context.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": user_input,
                        },
                        {
                            "type": "input_file",
                            "file_url": file_url.group(1),
                        },
                    ],
                }
            )

            return context

        # Caso não tenha imagem, apenas adiciona o input do usuário
        context.append(
            {
                "role": "user",
                "content": str(user_input),
            }
        ),

        return context

    def _save_messages_to_database(
        self, phone: str, input: dict, outputs: list[dict]
    ) -> None:
        logger.info(
            f"[GENERATE RESPONSE SERVICE] Salvando mensagens no banco de dados para o telefone: {phone} \nInput: {to_json_dump(input)} Output: \n{to_json_dump(outputs)}"
        )

        # Salva a nova mensagem do usuário
        content: str | list = input.get("content")
        if content and isinstance(content, list):
            input_text = next(
                (item["text"] for item in content if item.get("type") == "input_text"),
                "",
            )

            input_type = next(
                (
                    item["type"]
                    for item in content
                    if item.get("type") in ["input_image", "input_file"]
                ),
                None,
            )

            self.message_repository.create(
                phone=phone,
                role=input.get("role"),
                content=f"{input_text} (um {input_type} foi enviado anteriormente)",
            )

        else:
            self.message_repository.create(
                phone=phone,
                role=input.get("role"),
                content=content,
            )

        if not outputs:
            logger.warning(
                f"[GENERATE RESPONSE SERVICE] A resposta gerada está vazia para o telefone {phone}. Input: \n{to_json_dump(input)}"
            )
            return

        # Salva a resposta gerada pela IA
        for output in outputs:
            if output.get("type", "") in ["function_call", "function_call_output"]:
                self.message_repository.create(
                    phone=phone,
                    role=output.get("type"),
                    content=output,
                )
                continue

            self.message_repository.create(
                phone=phone,
                role=output.get("role"),
                content=output.get("content"),
            )

        logger.info(
            f"[GENERATE RESPONSE SERVICE] Mensagens salvas no banco de dados para o telefone: {phone}. Input: \n{to_json_dump(input)}, output: \n{to_json_dump(output)}"
        )

    async def execute(self, phone: str, message: str) -> None:
        messages: list = self.message_repository.get_latest_customer_messages(
            phone=phone, limit=int(os.getenv("CONTEXT_SIZE", 80))
        )

        context: list[dict] = self._prepare_context(
            context=messages or [],
            user_input=message,
        )

        logger.info(
            f"[GENERATE RESPONSE SERVICE] Gerando resposta para o número: {phone}"
        )

        try:
            full_output: list[dict] = await self.response_orchestrator.execute(
                context=context, phone=phone
            )

            resolved_output_content = self._resolve_output_content(full_output)

            self.chat.send_message(
                phone=phone,
                message=resolved_output_content,
            )

            self._save_messages_to_database(
                phone=phone,
                input=context[-1],
                outputs=full_output,
            )

            logger.info(
                f"[GENERATE RESPONSE SERVICE] Resposta final: \ninput: {to_json_dump(context[-1])} \noutput: {to_json_dump(resolved_output_content)}"
            )

        except Exception as e:
            logger.exception(
                f"[GENERATE RESPONSE SERVICE] ❌ Erro ao gerar resposta: \n{to_json_dump(e)}"
            )

            raise e
