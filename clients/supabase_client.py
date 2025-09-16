from supabase import create_client
import os
from utils.logger import logger, to_json_dump
from interfaces.clients.database_interface import IDatabase
from interfaces.clients.ai_interface import IAI


class SupabaseClient(IDatabase):

    def __init__(self, ai_client: IAI):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        self._supabase = create_client(url, key)
        self.ai = ai_client

    def get_thread_id(self, phone: str) -> str:
        try:
            logger.info(f"[SUPABASE] Pegando Thread para o número {phone}")

            customers = (
                self._supabase.table("customers")
                .select("*, threads(id, customer_id)")
                .eq("phone", phone)
                .limit(1)
                .execute()
            )

            if not customers.data:
                new_customer = self.create_customer(phone)
                thread_id = new_customer["threads"]["id"]

                logger.info(f"[SUPABASE] Thread id para o número {phone}: {thread_id}")

                return thread_id

            customer = customers.data[0]
            if not customer["threads"]:
                thread_id = self.ai.create_thread()
                self.create_thread(customer["id"], thread_id)
                logger.info(f"[SUPABASE] Thread id para o número {phone}: {thread_id}")
                return thread_id

            thread_id = customer["threads"][0]["id"]
            logger.info(f"[SUPABASE] Thread id para o número {phone}: {thread_id}")

            return thread_id
        except Exception as e:
            logger.exception(
                f"[SUPABASE] ❌ Erro ao obter o thread id: \n{to_json_dump(e)}"
            )
            raise e

    def create_customer(self, phone: str) -> dict:
        try:
            logger.info(f"[SUPABASE] Criando customer para o número {phone}")

            thread_id = self.ai.create_thread()

            customer: dict = (
                self._supabase.table("customers").insert({"phone": phone}).execute()
            ).data[0]

            (
                self._supabase.table("threads")
                .insert({"id": thread_id, "customer_id": customer["id"]})
                .execute()
            )

            customer["threads"] = {"id": thread_id}

            logger.info(f"[SUPABASE] Customer criado. id {customer['id']}")

            return customer
        except Exception as e:
            logger.exception(
                f"[SUPABASE] ❌ Erro ao criar o cliente {phone}: \n{to_json_dump(e)}"
            )
            raise e

    def create_thread(self, customer_id: str, thread_id: str) -> bool:
        try:
            logger.info(
                f"[SUPABASE] Criando thread para o customer id {customer_id}, thread id {thread_id}"
            )

            return (
                self._supabase.table("threads")
                .insert({"id": thread_id, "customer_id": customer_id})
                .execute()
            )
        except Exception as e:
            logger.exception(
                f"[SUPABASE] ❌ Erro ao atualizar o thread: \n{to_json_dump(e)}"
            )
            raise e

    def get_phone(self, thread_id: str) -> str:
        try:
            logger.info(
                f"[SUPABASE] Pegando o número de telefone para o thread id {thread_id}"
            )
            customers = (
                self._supabase.table("customers")
                .select("*, threads(id, customer_id)")
                .eq("threads.id", thread_id)
                .limit(1)
                .execute()
            )

            if not customers.data:
                return ""

            phone = customers.data[0]["phone"]

            logger.info(f"[SUPABASE] Telefone para o thread id {thread_id}: {phone}")

            return phone
        except Exception as e:
            logger.exception(
                f"[SUPABASE] ❌ Erro ao obter o thread id: \n{to_json_dump(e)}"
            )
            raise e

    def create_deal(self, deal_id: str, phone: str) -> dict:
        try:
            logger.info(
                f"[SUPABASE] Criando deal com o id {deal_id} e telefone {phone}"
            )

            customer = (
                self._supabase.table("customers")
                .select("*")
                .eq("phone", phone)
                .limit(1)
                .execute()
            )

            if not customer.data:
                customer = self.create_customer(phone)

            deal = (
                self._supabase.table("deals")
                .insert({"id": deal_id, "customer_id": customer.data[0]["id"]})
                .execute()
            )

            deal_data = deal.data[0]
            deal_data["customer"] = customer.data[0]

            logger.info(
                f"[SUPABASE] Deal criado com o id {deal_data['id']}, data: \n{to_json_dump(deal_data)}"
            )

            return deal_data
        except Exception as e:
            logger.exception(f"[SUPABASE] ❌ Erro ao criar o deal: \n{to_json_dump(e)}")
            raise e

    def get_deal_id(self, phone: str) -> str:
        try:
            logger.info(f"[SUPABASE] Pegando o deal id para o número {phone}")

            customer = (
                self._supabase.table("customers")
                .select("*")
                .eq("phone", phone)
                .limit(1)
                .execute()
            )

            print(customer.data[0]["id"])

            deal = (
                self._supabase.table("deals")
                .select("*")
                .eq("customer_id", customer.data[0]["id"])
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            if not deal.data:
                return ""

            deal_id = deal.data[0]["id"]

            logger.info(f"[SUPABASE] Deal id para o número {phone}: {deal_id}")

            return deal_id
        except Exception as e:
            logger.exception(f"[SUPABASE] ❌ Erro ao obter o deal: \n{to_json_dump(e)}")
            raise e

    def get_customer(self, phone: str) -> dict | None:
        try:
            logger.info(f"[SUPABASE] Pegando o customer id para o número {phone}")

            customer = (
                self._supabase.table("customers")
                .select("*")
                .eq("phone", phone)
                .limit(1)
                .execute()
            )

            if not customer.data:
                return None

            return customer.data[0]
        except Exception as e:
            logger.exception(f"[SUPABASE] ❌ Erro ao obter o deal: \n{to_json_dump(e)}")
            raise e

    def turn_off_auto_response(self, phone: str) -> bool:
        response = (
            self._supabase.table("customers")
            .update({"auto_response": False})
            .eq("phone", phone)
            .execute()
        )

        return response

    def save_lead(self, lead_data: dict) -> dict:
        """
        Salva um lead na tabela 'leads' do Supabase
        """
        try:
            logger.info(f"[SUPABASE] Salvando lead: {to_json_dump(lead_data)}")
            
            response = (
                self._supabase.table("leads")
                .insert(lead_data)
                .execute()
            )
            
            if response.data:
                saved_lead = response.data[0]
                logger.info(f"[SUPABASE] Lead salvo com sucesso: {to_json_dump(saved_lead)}")
                return saved_lead
            else:
                logger.error(f"[SUPABASE] ❌ Erro ao salvar lead: Nenhum dado retornado")
                return {}
                
        except Exception as e:
            logger.exception(f"[SUPABASE] ❌ Erro ao salvar lead: {to_json_dump(e)}")
            raise e

    def get_session(self):
        """
        Implementação da interface IDatabase
        Retorna None pois Supabase não usa SQLAlchemy sessions
        """
        return None

    def close(self) -> None:
        """
        Implementação da interface IDatabase
        Supabase não precisa fechar conexões explicitamente
        """
        logger.info("[SUPABASE] Fechando cliente (nenhuma ação necessária)")
        pass
