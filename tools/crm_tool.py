import os
import time
from threading import Thread
from interfaces.tools.tool_interface import ITool
from interfaces.clients.ai_interface import IAI
from interfaces.clients.database_interface import IDatabase
from interfaces.clients.chat_interface import IChat
from utils.logger import logger, to_json_dump


class CRMTool(ITool):
    name = "crm"
    model = "gpt-4o-mini"
    _function_call_input = "Perfeito! Registrei suas informações e nossa equipe comercial entrará em contato em breve para apresentar uma proposta personalizada. Enquanto isso, posso esclarecer alguma dúvida sobre nossas soluções de IA?"
    _seller_prompt = """Sua função é escrever uma mensagem que será enviada via WhatsApp. Sua resposta deve conter apenas o conteúdo que será enviado direto para o WhatsApp do usuário, personalizando as informações abaixo da mensagem modelo.

"
Olá, {first_name}! Tudo bem?

Aqui é o Pedro da Avantti AI 👋

Nossa IA Sofia me notificou sobre seu interesse em {ai_solution}, e acredito que posso te ajudar a implementar uma solução personalizada.

Quando seria um bom momento para uma demo de 15 minutos? Posso te mostrar exatamente como nossa IA funcionaria na {company}.
"

Informações do cliente:
Nome: {name}
Empresa: {company}
Necessidade: {motivation}

Importante: Sempre escreva uma mensagem natural e objetiva. Exemplo de uma boa mensagem:

"
Oi Carlos! Tudo bem?

Aqui é o Pedro da Avantti AI 👋

Nossa IA Sofia me notificou sobre seu interesse em chatbot para WhatsApp, e acredito que posso te ajudar a implementar uma solução personalizada.

Quando seria um bom momento para uma demo de 15 minutos? Posso te mostrar exatamente como nossa IA funcionaria na MegaStore.
"

Diretrizes:
- Use apenas o primeiro nome
- Adapte a necessidade para soar natural (não copie exatamente)
- Mencione a empresa quando relevante
- Sempre ofereça demo específica
- Tom consultivo e profissional"""

    def __init__(
        self,
        ai_client: IAI,
        database_client: IDatabase,
        chat_client: IChat,
    ):
        self.ai = ai_client
        self.database = database_client
        self.chat = chat_client

    def _save_lead_to_database(
        self, company_name: str, lead_name: str, phone: str, motivation: str
    ) -> dict:
        """
        Salva lead diretamente no Supabase ao invés de usar CRM externo
        """
        try:
            lead_data = {
                "company_name": company_name,
                "lead_name": lead_name,
                "phone": phone,
                "motivation": motivation,
                "status": "new_lead",
                "created_at": "now()",
                "source": "whatsapp_ai"
            }
            
            logger.info(f"[CRM TOOL] Salvando lead no banco: {to_json_dump(lead_data)}")
            
            # Salva no Supabase usando o cliente de database
            # Nota: Este método precisará ser implementado no SupabaseClient
            result = self.database.save_lead(lead_data)
            
            logger.info(f"[CRM TOOL] Lead salvo com sucesso: {to_json_dump(result)}")
            
            return {
                "id": result.get("id") if result else None,
                "title": f"{company_name} | {lead_name}",
                "phone": phone,
                "status": "saved_to_database",
                "message": "Lead salvo no Supabase"
            }
            
        except Exception as e:
            logger.exception(f"[CRM TOOL] ❌ Erro ao salvar lead: {str(e)}")
            # Retorna objeto de fallback para não quebrar o fluxo
            return {
                "id": None,
                "title": f"{company_name} | {lead_name}",
                "phone": phone,
                "status": "error",
                "message": f"Erro ao salvar: {str(e)}"
            }

    def _send_message_from_seller_to_customer(
        self, phone: str, lead_name: str, motivation: str, company_name: str = ""
    ) -> None:
        response = self.ai.create_model_response(
            model=self.model,
            input=[
                {
                    "role": "user",
                    "content": self._seller_prompt.format(
                        name=lead_name,
                        first_name=lead_name.split()[0] if lead_name else "Olá",
                        company=company_name or "sua empresa",
                        motivation=motivation,
                        ai_solution=motivation,
                    ),
                }
            ],
        )

        logger.info(
            f"[CRM TOOL] Resposta gerada pela IA que será enviada do vendedor para o telefone {phone}: {to_json_dump(response)}"
        )

        messages = [
            o.get("text", "")
            for message in response.get("output", [])
            if message.get("status", "") == "completed"
            for o in message.get("content", [])
            if o.get("type") == "output_text"
        ]
        message = ". ".join(messages).strip()

        seller_message_waiting_time_in_seconds = int(
            os.getenv("SELLER_MESSAGE_WAITING_TIME_IN_SECONDS", 180)
        )

        time.sleep(seller_message_waiting_time_in_seconds)
        self.chat.send_message(
            phone=phone,
            message=message,
        )

        logger.info(
            f"[CRM TOOL] Mensagem de vendedor enviada para o telefone {phone}: {message}"
        )

    def _function_call_output(
        self,
        function_call_id: str,
        call_id: str,
        call_name: str,
        output: str,
        arguments: dict,
    ) -> tuple[list, str, str]:
        fc_input, response = self.ai.function_call_output(
            function_call_id=function_call_id,
            call_id=call_id,
            call_name=call_name,
            output=output,
            arguments=arguments,
            model=self.model,
        )

        all_output = [
            content.get("text")
            for message in response.get("output", [])
            if message.get("status", "") == "completed"
            for content in message.get("content", [])
            if content.get("type") == "output_text"
        ]

        fc_msg_id = response["output"][0]["id"]
        all_output_in_text = ". ".join(all_output) or ""

        return (fc_input, fc_msg_id, all_output_in_text)

    async def execute(
        self,
        function_call_id: str,
        call_id: str,
        call_name: str,
        arguments: dict,
    ) -> list[dict]:
        phone: str = arguments.get("phone").strip()
        lead_name: str = arguments.get("lead_name").strip()
        motivation: str = arguments.get("motivation").strip()
        company_name: str = arguments.get("company_name", "").strip()

        logger.info(
            f"[CRM TOOL] Executando a ferramenta '{self.name}', telefone: {phone}, function_call_id: {function_call_id}, call_id: {call_id}, call_name: {call_name}, arguments: {to_json_dump(arguments)}"
        )

        # Salva lead no banco de dados (Supabase) ao invés de CRM externo
        lead_result = self._save_lead_to_database(
            company_name=company_name,
            lead_name=lead_name,
            phone=phone,
            motivation=motivation,
        )

        logger.info(f"[CRM TOOL] Resultado do salvamento: {to_json_dump(lead_result)}")

        fc_input, fc_msg_id, function_call_output = self._function_call_output(
            function_call_id=function_call_id,
            call_id=call_id,
            call_name=call_name,
            output=self._function_call_input,
            arguments=arguments,
        )

        logger.info(
            f"[CRM TOOL] Resposta da ferramenta '{self.name}' com o function_call_id: {function_call_id}, call_id: {call_id}, call_name: {call_name}: {to_json_dump(function_call_output)}"
        )

        # Inicia thread para enviar mensagem do vendedor (mantida funcionalidade)
        Thread(
            target=self._send_message_from_seller_to_customer,
            args=(phone, lead_name, motivation, company_name),
            daemon=False,
        ).start()

        return [
            *fc_input,
            {
                "id": fc_msg_id,
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "text": function_call_output,
                    }
                ],
            },
        ]
