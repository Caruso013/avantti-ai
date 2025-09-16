import requests
import os
import re
import time
import random
import base64
from utils.logger import logger, to_json_dump
from interfaces.clients.chat_interface import IChat


class EvolutionAPIClient(IChat):
    def __init__(self):
        self._base_url = os.getenv("EVOLUTION_BASE_URL")
        self._instance_name = os.getenv("EVOLUTION_INSTANCE_NAME")
        self._headers = {
            "Content-Type": "application/json",
            "apikey": os.getenv("EVOLUTION_INSTANCE_KEY"),
        }

    def __is_valid_request(self, **kwargs) -> bool:
        if not kwargs["apikey"] or kwargs["apikey"] != os.getenv(
            "EVOLUTION_INSTANCE_KEY"
        ):
            return False

        if not kwargs["instance"] or kwargs["instance"] != os.getenv(
            "EVOLUTION_INSTANCE_NAME"
        ):
            return False

        return True

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
            print("❌ Dados incompletos: O número de telefone é obrigatório.")
            return False

        # Trata o telefone
        cell_number_clean = cell_number.strip()

        # Remove caracteres não numéricos
        cell_number_clean = re.sub(r"[^0-9]", "", cell_number_clean)

        # Verifica tamanho mínimo (11 dígitos = DDD + Celular)
        if len(cell_number_clean) < 11:
            print(
                f"Telefone inválido. O número de celular deve conter no mínimo 11 dígitos (com DDD): {cell_number_clean}"
            )
            return False

        # Verifica tamanho máximo (13 dígitos = 11DDI + DDD + Celular)
        if len(cell_number_clean) > 13:
            print(
                f"Telefone inválido. O número de celular deve conter no máximo 13 dígitos (com DDI e DDD): {cell_number_clean}"
            )
            return False

        return True

    # Coloca o DDI se necessário
    def _resolve_phone(self, phone: str) -> str:
        # Coloca o número o prefixo 9 caso o número tenha 8 dígitos
        if len(phone[4:]) == 8:
            phone = f"{phone[:4]}9{phone[4:]}"

        # Adiciona o DDI 55 caso não tenha
        if not phone.startswith("55") and len(phone) == 11:
            return f"55{phone}"

        return phone

    def __resolve_message(self, message: str) -> str:
        # Padrão mais sofisticado que evita dividir enumerações e algumas abreviações comuns
        sentences = re.split(r"(?<!\d|\.)\.(?:\s+|$)", message)

        sentences = [s.strip() for s in sentences if s.strip()]

        # Adiciona ponto final onde apropriado
        for i in range(len(sentences) - 1):
            if not re.search(r"(?:^|\s)\d+\.$", sentences[i]) and not sentences[
                i
            ].endswith("."):
                sentences[i] += "."

        return sentences

    def set_instance(self, instance: str, instance_key: str) -> None:
        self._instance_id = instance
        self._headers["apikey"] = instance_key

    def is_valid_message(self, **kwargs) -> bool:
        return self.__is_valid_request(**kwargs)

    def is_audio_message(self, **kwargs) -> bool:
        return "audioMessage" in kwargs.get("data", {}).get("message", {})

    def is_image(self, **kwargs) -> bool:
        return False

    def is_file(self, **kwargs) -> bool:
        return False

    def get_message(self, **kwargs) -> str:
        if (
            "data" in kwargs
            and "message" in kwargs["data"]
            and "remoteJid" in kwargs["data"]["key"]
        ):
            return str(kwargs["data"]["message"]["conversation"])

        return "Olá, Tenho interesse e queria mais informações, por favor."

    def get_phone(self, **kwargs) -> str:
        phone = kwargs["data"]["key"]["remoteJid"].split("@")[0] or ""
        return self._resolve_phone(phone) or ""

    def _get_audio_url(self, **kwargs) -> str:
        return kwargs["data"]["message"]["audioMessage"]["url"]

    def get_audio_bytes(self, **kwargs) -> str:
        endpoint = (
            f"{self._base_url}/chat/getBase64FromMediaMessage/{self._instance_name}"
        )

        payload = {
            "message": {"key": {"id": kwargs["data"]["key"]["id"]}},
            "convertToMp4": False,
        }

        try:
            response = requests.post(url=endpoint, json=payload, headers=self._headers)
            response.raise_for_status()

            logger.info(
                f"[EVOLUTION] Recuperando audio da mensagem {kwargs['data']['key']['id']}"
            )

            return base64.b64decode(response.json().get("base64"))
        except Exception as e:
            logger.exception(
                f"[EVOLUTION] ❌ Falha ao obter audio: \n{to_json_dump(e)}"
            )
            raise e

    def get_image_url(self, **kwargs) -> str:
        return ""

    def get_image_caption(self, **kwargs) -> str:
        return ""

    def get_file_url(self, **kwargs) -> str:
        return ""

    def get_file_caption(self, **kwargs) -> str:
        return ""

    def _resolve_url(self) -> str:
        return f"{self._base_url}/message/sendText/{self._instance_name}"

    def send_message(self, phone: str, message: str) -> bool:
        if not self.__validate_message(message) or not self.__validate_cell_number(
            phone
        ):
            return False

        url: str = self._resolve_url()
        payload: dict = {"number": self._resolve_phone(phone), "delay": 3000}

        try:
            messages: str = self.__resolve_message(message)

            for message in messages:
                if not message:
                    continue

                payload["text"] = message
                response = requests.post(url, json=payload, headers=self._headers)

                logger.info(
                    f"[EVOLUTION] Enviando mensagem para o número {phone}: {message!r}"
                )

                response.raise_for_status()

                pause = random.randint(2, 3)
                time.sleep(pause)

            return True
        except Exception as e:
            logger.exception(
                f"[EVOLUTION] ❌ Falha ao enviar mensagem: \n{to_json_dump(e)}"
            )
            raise e
