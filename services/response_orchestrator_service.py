import re
import asyncio
import json
from interfaces.orchestrators.response_orchestrator_interface import (
    IResponseOrchestrator,
)
from utils.logger import logger, to_json_dump
from interfaces.clients.chat_interface import IChat
from interfaces.repositories.message_repository_interface import IMessageRepository
from container.agents import AgentContainer
from container.tools import ToolContainer
from interfaces.clients.ai_interface import IAI


class ResponseOrchestratorService(IResponseOrchestrator):
    model: str = "gpt-5-mini-2025-08-07"
    instructions: str = ""

    system_prompt: dict = {
        "role": "system",
        "content": """# 1. Identidade
        - **Nome:** Eliane
        - **Função:** SDR (pré-vendas) da **Evex Imóveis**
        - **Estilo de comunicação:**
        - Tom formal-casual
        - Simpática e humana (evitar parecer robô)
        - Frases curtas, objetivas
        - Gatilhos de venda sutis e palavras-chave de conversão

        # 2. Contexto da Empresa
        - **Evex Imóveis:** imobiliária especializada em empreendimentos residenciais
        - **Fonte dos leads:** anúncios Meta/Facebook
        - **Canal:** WhatsApp/SMS (Z-API)
        - **Site oficial:** https://www.eveximoveis.com.br (usar apenas para consultas específicas, se o lead pedir)

        # 3. Fluxo de Qualificação
        1. **Apresentação inicial**  
        - Apenas na primeira mensagem:  
          "Olá, {{nome}}! Aqui é a Eliane, da Evex Imóveis 😊. Vi que você se interessou pelo anúncio do {{empreendimento}}."  
        - Se não houver nome disponível:  
          "Olá! Tudo bem? Aqui é a Eliane, da Evex Imóveis 😊. Vi que você se interessou pelo anúncio do {{empreendimento}}."  
        - Sempre que possível, mencionar o anúncio: "Esse contato veio através do anúncio [{{id_anuncio}}] no Facebook."

        2. **Confirmar interesse no empreendimento** → [interest]  
           - "Você gostaria de receber mais informações sobre ele?"

        3. **Finalidade do imóvel** → [purpose]  
           - "Me conta, você pensa em comprar para morar ou investir?"

        4. **Momento de compra** → [timing]  
           - "Legal! E você imagina comprar em breve, nos próximos 6 meses, ou ainda está pesquisando opções?"

        5. **Faixa de valor** → [budget]  
           - "O investimento que você tem em mente continua próximo de {{faixa_valor}}?"

        6. **Forma de pagamento** → [payment]  
           - "Você pensa em pagamento à vista ou financiamento?"

        📌 Observações:
        - Nunca reiniciar a conversa nem se reapresentar após a primeira mensagem.
        - Adaptar o fluxo caso o lead responda fora de ordem.
        - Sempre quebrar o texto em mensagens curtas.
        - Usar confirmações naturais ("Sim", "Perfeito", "Entendi").        # 4. Regras de Nome
        - Usar {{nome}} do anúncio na primeira mensagem, se disponível.
        - Se o lead se apresentar com outro nome, atualizar e usar esse.
        - Nunca usar o nome automático do WhatsApp.
        - Se não houver nome, usar abertura neutra.

        # 5. Critérios de Qualificação
        Lead é qualificado se:
        - Demonstra interesse real no empreendimento, ou
        - Pede informações sobre condições de pagamento, ou
        - Responde positivamente às etapas 1, 3 e 4, ou
        - Fornece informações detalhadas sobre orçamento e timing.

        # 6. Restrições
        - ✅ Pode informar: valores gerais, localização, disponibilidade, fotos básicas.
        - ❌ Não pode: negociar preço/prazo, falar sobre obras, reputação da empresa ou reclamações.

        # 7. Follow-up Automático
        - Sem resposta → lembrete em 30m → depois em 2h → se persistir, encerrar com status "Não Responde".
        - Se recusar atendimento → encerrar com status "Não Interessado".
        - Perguntas fora de escopo → responder padrão e registrar observação "DÚVIDA TÉCNICA".

        # 8. Termômetro (C2S)
        - **QUENTE** → interesse imediato + orçamento definido + timing próximo
        - **MORNO** → interesse confirmado + momento definido
        - **FRIO** → ainda pesquisando
        - **INDEFINIDO** → antes de obter respostas-chave

        # 9. Formato de Saída
        Sempre responder em JSON único (uma linha), conforme:

        {
          "reply": "Mensagem curta ao lead (máx 180 caracteres, formal-casual, clara, empática, com quebras de texto naturais)",
          "c2s": {
            "observations": "=== QUALIFICAÇÃO IA - ELIANE ===\\nData:[ISO]\\nNome:[{{nome}}]\\nTelefone:[{{telefone}}]\\nE-mail:[{{email}}]\\nEmpreendimento:[{{empreendimento}}]\\nAnúncio:[{{id_anuncio}}]\\nFaixa original:[{{faixa_valor}}]\\nFinalidade:[...]\\nMomento:[...]\\nFaixa confirmada:[...]\\nPagamento:[...]\\nObservações adicionais:[...]",
            "status": "Novo Lead - Qualificado por IA" | "Não Responde" | "Não Interessado"
          },
        "schedule": {
          "followup": "none|30m|2h",
          "reason": "no_response|awaiting_docs|other"
        }
    }
"""
    }
    tools: list = [
        {
            "type": "function",
            "name": "notificar_novo_lead",
            "description": "Avisa o time sobre a chegada de um novo lead com os parâmetros obrigatórios.",
            "parameters": {
                "type": "object",
                "required": ["nome", "telefone", "projeto", "preco_medio"],
                "properties": {
                    "nome": {"type": "string", "description": "Nome do Lead"},
                    "telefone": {
                        "type": "string",
                        "description": "Telefone do Lead",
                    },
                    "projeto": {
                        "type": "string",
                        "description": "Nome do projeto de interesse do Lead",
                    },
                    "preco_medio": {
                        "type": "number",
                        "description": "Faixa de preço médio que o Lead está considerando",
                    },
                },
                "additionalProperties": False,
            },
            "strict": True,
        }
    ]

    def __init__(
        self,
        agent_container: AgentContainer,
        tool_container: ToolContainer,
        chat_client: IChat,
        message_repository: IMessageRepository,
        ai_client: IAI,
    ) -> None:
        self.agent_container = agent_container
        self.tool_container = tool_container
        self.chat = chat_client
        self.message_repository = message_repository
        self.ai = ai_client

        self._resolve_agents()

    def _resolve_agents(self) -> None:
        agents_formatted = [
            f'{agent.name}{"." if "palavra-chave" in agent.name else ":"} responda apenas com "{agent.id}"'
            for agent in self.agent_container.all()
        ]

        agents_formatted_sorted = sorted(
            agents_formatted, key=lambda x: int(re.search(r"#(\d+)", x).group(1))
        )

        self.instructions = self.instructions.replace(
            "[[AGENTES]]", ",\n".join(agents_formatted_sorted)
        )

    def _insert_system_input(self, input: list) -> list:
        if not any(msg.get("role") == "system" for msg in input):
            input.insert(0, self.system_prompt)

        return input

    def _extract_all_outputs_in_text(
        self, output: list[dict], separator: str = " "
    ) -> str:
        texts = [
            content.get("text")
            for message in output
            for content in message.get("content", [])
            if "text" in content
        ]

        return separator.join(texts)

    def _extract_agent_id(self, output: list, all_outputs_in_text: str) -> list[str]:
        pattern = r"#\d+"
        return re.findall(pattern, all_outputs_in_text)

    def _is_agent_trigger(
        self, output: list, all_outputs_in_text: str
    ) -> tuple[bool, list[str]]:
        if not all_outputs_in_text:
            return False, []

        pattern = r"#\d+"
        return (
            bool(re.search(pattern, all_outputs_in_text)),
            self._extract_agent_id(output, all_outputs_in_text),
        )

    async def _handle_agents(
        self, phone: str, context: list, agent_ids: list[str]
    ) -> list[dict]:
        tasks = [
            asyncio.create_task(
                self.agent_container.get(agent_id).execute(phone=phone, context=context)
            )
            for agent_id in agent_ids
        ]

        logger.info(
            f"[RESPONSE ORCHESTRATOR SERVICE] Agente(s) acionado(s): {agent_ids}"
        )

        # Aguarda todas as tasks e pega os resultados
        results = await asyncio.gather(*tasks)

        return results or []

    def _is_tool_trigger(self, response: dict) -> tuple[bool, list]:
        tools = [
            item
            for item in response.get("output", [])
            if item.get("type") == "function_call" and item.get("status") == "completed"
        ]

        if tools:
            return True, tools

        return False, []

    async def _handle_tools(self, phone: str, tools: list[dict]) -> list[dict]:
        tasks = [
            asyncio.create_task(
                self.tool_container.get(tool.get("name").strip()).execute(
                    function_call_id=tool.get("id"),
                    call_id=tool.get("call_id"),
                    call_name=tool.get("name"),
                    arguments={
                        **json.loads(tool.get("arguments", "{}")),
                        "phone": phone,
                    },
                )
            )
            for tool in tools
            if tool.get("name")
        ]

        # Aguarda todas as tasks e pega os resultados
        results = await asyncio.gather(*tasks)

        # Extrai todos os dicionários de cada lista devolvida por cada tool para uma única lista de dicionários
        return [item for sublist in results for item in sublist]

    async def execute(self, context: list, phone: str) -> list[dict]:
        context = self._insert_system_input(context)

        response = self.ai.create_model_response(
            model=self.model,
            input=context,
            tools=self.tools,
            instructions=self.instructions,
        )

        logger.info(
            f"[RESPONSE ORCHESTRATOR SERVICE] Resposta gerada pelo orquestrador da IA: {to_json_dump(response)}"
        )

        full_output: list = []

        all_outputs_in_text: str = self._extract_all_outputs_in_text(
            response.get("output", [])
        )

        is_agent_trigger, agent_ids = self._is_agent_trigger(
            output=response.get("output", []), all_outputs_in_text=all_outputs_in_text
        )

        is_tool_trigger, tools = self._is_tool_trigger(response=response)

        if is_agent_trigger:
            agent_outputs: list[dict] = await self._handle_agents(
                phone=phone,
                context=context,
                agent_ids=agent_ids,
            )

            full_output.extend(agent_outputs)

        elif is_tool_trigger:
            tool_outputs: list[dict] = await self._handle_tools(
                phone=phone, tools=tools
            )

            full_output.extend(tool_outputs)

        else:
            full_output.append(
                {
                    "role": "assistant",
                    "content": self._extract_all_outputs_in_text(
                        output=response.get("output", []), separator=". "
                    ).strip(),
                }
            )

        return full_output
