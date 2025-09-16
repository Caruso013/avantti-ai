"""
CLIENTE PIPEDRIVE - DESABILITADO
Este cliente foi desabilitado conforme solicitação.
O sistema agora usa apenas Supabase como banco de dados.
"""

import os
import requests
from utils.logger import logger, to_json_dump


class PipeDriveClient:
    """
    Cliente Pipedrive desabilitado.
    Mantido para compatibilidade, mas não é mais utilizado.
    """
    
    def __init__(self):
        logger.warning("[PIPEDRIVE] Cliente Pipedrive está desabilitado")
        # Comentado para não tentar acessar variáveis inexistentes
        # self.__base_url = os.getenv("PIPE_DRIVE_BASE_URL")
        # self.__token = os.getenv("PIPE_DRIVE_TOKEN")
        # self.__owner_id = int(os.getenv("PIPE_DRIVE_OWNER_ID"))
        self.__headers = {
            "Content-Type": "application/json",
        }

    def create_deal(
        self, company_name: str, lead_name: str, phone: str, motivation: str
    ) -> dict:
        logger.warning("[PIPEDRIVE] create_deal chamado, mas Pipedrive está desabilitado")
        # Retorna um objeto mock para compatibilidade
        return {
            "id": None,
            "title": f"{company_name} | {lead_name}",
            "phone": phone,
            "status": "disabled",
            "message": "Pipedrive está desabilitado"
        }

    def __create_organization(self, company_name: str, motivation: str) -> dict:
        url = f"{self.__base_url}/organizations?api_token={self.__token}"

        payload = {
            "name": company_name,
            "owner_id": self.__owner_id,
            "visible_to": 3,
            "custom_fields": {
                "0a605b9668c110080cd956312ac51b11a7855621": motivation,
            },
        }

        logger.info(
            f"[PIPEDRIVE] Criando organização. payload: \n{to_json_dump(payload)}"
        )

        try:
            response = requests.post(url, json=payload, headers=self.__headers)
            response.raise_for_status()
            response_data: dict = response.json()

            logger.info(
                f"[PIPEDRIVE] Organização criada: \n{to_json_dump(response_data)}"
            )

            return response_data.get("data")
        except Exception as e:
            logger.exception(
                f"[PIPEDRIVE] ❌ Erro ao criar a empresa: \n{to_json_dump(e)}"
            )
            raise e

    def __create_person(self, lead_name: str, org_id: str, phone: str) -> dict:
        url = f"{self.__base_url}/persons?api_token={self.__token}"

        payload = {
            "name": lead_name,
            "owner_id": self.__owner_id,
            "org_id": org_id,
            "visible_to": 3,
            "phones": [
                {
                    "value": phone,
                }
            ],
        }

        logger.info("[PIPEDRIVE] Criando person. payload: \n{to_json_dump(payload)}")

        try:
            response = requests.post(url, json=payload, headers=self.__headers)
            response.raise_for_status()
            response_data = response.json()

            logger.info(f"[PIPEDRIVE] Person criada: \n{to_json_dump(response_data)}")

            return response_data.get("data")
        except Exception as e:
            logger.exception(f"[PIPEDRIVE] ❌ Erro ao criar person: {e}")
            raise e

    def move_deal_to_scheduled_meeting(self, deal_id: int) -> bool:
        url = f"{self.__base_url}/deals/{deal_id}?api_token={self.__token}"

        logger.info(f"[PIPEDRIVE] Movendo deal {deal_id}")

        try:
            response = requests.patch(url, json={"stage_id": 3}, headers=self.__headers)
            response.raise_for_status()
            response_data: dict = response.json()

            logger.info(f"[PIPEDRIVE] Deal movido: \n{to_json_dump(response_data)}")

            return True
        except Exception as e:
            logger.exception(f"[PIPEDRIVE] ❌ Erro ao mover deal: \n{to_json_dump(e)}")
            raise e

    def create_activity(
        self, deal_id: int, subject: str, due_date: str, due_time: str
    ) -> bool:
        url = f"{self.__base_url}/activities?api_token={self.__token}"

        payload = {
            "subject": subject,
            "deal_id": deal_id,
            "due_date": due_date,
            "due_time": due_time,
            "type": "meeting",
        }

        logger.info(
            f"[PIPEDRIVE] Criando atividade. payload: \n{to_json_dump(payload)}"
        )

        try:
            response = requests.post(url, json=payload, headers=self.__headers)
            response.raise_for_status()
            response_data: dict = response.json()

            logger.info(
                f"[PIPEDRIVE] Atividade criada: \n{to_json_dump(response_data)}"
            )

            return True
        except Exception as e:
            logger.exception(f"[PIPEDRIVE] ❌ Erro ao criar atividade: {e}")
            raise e
