import requests
import os
import re
import time
import random
from utils.logger import logger, to_json_dump
from interfaces.clients.chat_interface import IChat


class ZAPIClient(IChat):
    def __init__(self):
        self._base_url = os.getenv("ZAPI_BASE_URL")
        self._instance_id = os.getenv("ZAPI_INSTANCE_ID")
        self._instance_token = os.getenv("ZAPI_INSTANCE_TOKEN")
        self._client_token = os.getenv("ZAPI_CLIENT_TOKEN")
        self._headers = {"Content-Type": "application/json"}

    def __validate_message(self, message: str) -> bool:
        # Trata a mensagem
        message_clean = message.strip()

        # Verifica se a mensagem não está vazia
        if not message_clean:
            print("❌ Dados incompletos: A mensagem é obrigatória.")
            return False

        return True

    def __validate_cell_number(self, cell_number: str) -> bool:
        # Verifica se o celular não está vazio
        if not cell_number:
            logger.info(
                f"[Z-API] ❌ Dados incompletos: O número de telefone é obrigatório. {cell_number}"
            )
            return False

        # Trata o telefone
        cell_number_clean = cell_number.strip()

        # Remove caracteres não numéricos
        cell_number_clean = re.sub(r"[^0-9]", "", cell_number_clean)

        # Verifica tamanho mínimo (11 dígitos = DDD + Celular)
        if len(cell_number_clean) < 11:
            logger.info(
                f"[Z-API] Telefone inválido. O número de celular deve conter no mínimo 11 dígitos (com DDD): {cell_number_clean}"
            )
            return False

        # Verifica tamanho máximo (13 dígitos = 11DDI + DDD + Celular)
        if len(cell_number_clean) > 13:
            print(
                f"[Z-API] Telefone inválido. O número de celular deve conter no máximo 13 dígitos (com DDI e DDD): {cell_number_clean}"
            )
            return False

        return True

    def _resolve_phone(self, phone: str) -> str:
        # Coloca o número o prefixo 9 caso o número tenha 8 dígitos
        if len(phone[4:]) == 8:
            phone = f"{phone[:4]}9{phone[4:]}"

        # Adiciona o DDI 55 caso não tenha
        if not phone.startswith("55") and len(phone) == 11:
            return f"55{phone}"

        return phone

    def __resolve_message(self, message: str) -> list[str]:
        abrevs = [
            "Av",
            "R",
            "Rua",
            "Dr",
            "Dra",
            "Sr",
            "Sra",
            "Prof",
            "Rod",
            "Tv",
            "Est",
            "Sta",
            "Sto",
        ]

        # Protege abreviações comuns
        for ab in abrevs:
            message = re.sub(rf"\b{ab}\.", f"{ab}<<P>>", message)

        # Protege marcadores de lista (1. 2. 3. etc.)
        message = re.sub(r"(?<=\b\d)\.", "<<N>>", message)

        # Quebra sentenças reais (ponto final seguido de espaço ou fim de string)
        sentences = re.split(r"\.(?:\s+|$)", message)

        cleaned = []
        for s in sentences:
            s = s.strip().replace("<<P>>", ".").replace("<<N>>", ".")
            if s:
                cleaned.append(s if s.endswith(".") else s + ".")

        return cleaned

    def set_instance(self, instance: str, instance_key: str) -> None:
        self._instance_id = instance
        self._instance_token = instance_key

    def is_valid_message(self, **kwargs) -> bool:
        phone = self.get_phone(**kwargs)

        if not phone:
            return False

        return not kwargs["isGroup"] and kwargs["status"] == "RECEIVED"

    def is_image(self, **kwargs) -> bool:
        return "image" in kwargs and kwargs["image"].get("imageUrl") is not None

    def is_audio_message(self, **kwargs) -> bool:
        return "audio" in kwargs

    def is_file(self, **kwargs) -> bool:
        return (
            "document" in kwargs and kwargs["document"].get("documentUrl") is not None
        )

    def get_message(self, **kwargs) -> str:
        if "text" in kwargs:
            return str(kwargs["text"]["message"])

        return "Olá, Tenho interesse e queria mais informações, por favor."

    def get_phone(self, **kwargs) -> str:
        return self._resolve_phone(kwargs.get("phone", "")) or ""

    def _get_audio_url(self, **kwargs) -> str:
        try:
            url: str = kwargs["audio"]["audioUrl"]

            if not url:
                raise KeyError(
                    f"[Z-API] Erro ao recuperar url do audio: \n{to_json_dump(kwargs)}"
                )

            return kwargs["audio"]["audioUrl"]
        except KeyError as e:
            logger.error(e)
            raise e

    def get_audio_bytes(self, **kwargs) -> str:
        url = self._get_audio_url(**kwargs)
        return requests.get(url, timeout=15).content

    def get_image_url(self, **kwargs) -> str:
        return kwargs.get("image", {}).get("imageUrl", "")

    def get_image_caption(self, **kwargs) -> str:
        return kwargs.get("image", {}).get(
            "caption", "Responda o usuário conforme o contexto e a imagem enviada"
        )

    def get_file_url(self, **kwargs) -> str:
        return kwargs.get("document", {}).get("documentUrl", "")

    def get_file_caption(self, **kwargs) -> str:
        return kwargs.get("document", {}).get(
            "caption",
            "interprete o arquivo e responda o usuário conforme o contexto e o arquivo enviado",
        )

    def _resolve_url(self) -> str:
        return f"{self._base_url}/instances/{self._instance_id}/token/{self._instance_token}"

    def send_message(self, phone: str, message: str) -> bool:
        if not self.__validate_message(message) or not self.__validate_cell_number(
            phone
        ):
            logger.error(
                f"[Z-API] Dados incompletos: mensagem: {message}, telefone: {phone}"
            )
            return False

        url = self._resolve_url() + "/send-text"

        headers = {**self._headers, "Client-Token": self._client_token}

        payload = {"phone": self._resolve_phone(phone), "delayTyping": 3}

        try:
            messages = self.__resolve_message(message)

            for message in messages:
                if not message:
                    continue

                msg = message[:-1] if message.endswith(".") else message
                payload["message"] = msg
                response = requests.post(url, json=payload, headers=headers)

                logger.info(
                    f"[Z-API] Enviando mensagem para {phone}: {msg!r} payload:\n{to_json_dump(payload)} \nresponse:{to_json_dump(response.json())}"
                )

                response.raise_for_status()

                pause = random.randint(2, 3)
                time.sleep(pause)

            return True
        except Exception as e:
            logger.exception(
                f"[Z-API] ❌ Falha ao enviar mensagem: \n{to_json_dump(e)}"
            )
            raise e

    def send_button_list(self, phone: str, message: str, buttons: list) -> dict:
        url = self._resolve_url() + "/send-button-list"

        headers = {**self._headers, "Client-Token": self._client_token}

        payload = {
            "phone": self._resolve_phone(phone),
            "message": message,
            "buttonList": {
                "buttons": buttons,
            },
            "delayTyping": 3,
        }

        try:
            if not buttons:
                logger.error(f"[Z-API] Lista de botões vazia: {phone}")
                return

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            logger.info(
                f"[Z-API] Lista de botões enviada para {phone}: \n{to_json_dump(response.json())}"
            )

        except Exception as e:
            logger.exception(
                f"[Z-API] ❌ Falha ao enviar lista de botões: \n{to_json_dump(e)}"
            )
            raise e
