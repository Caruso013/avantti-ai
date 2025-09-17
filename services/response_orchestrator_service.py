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
        - **Nome:** Sofia
        - **Função:** SDR (Sales Development Representative) da **Avantti AI**
        - **Estilo de comunicação:**
        - Tom consultivo e técnico, mas acessível
        - Humana e empática (evitar parecer robô)
        - Frases claras e objetivas
        - Foco em soluções e ROI

        # 2. Contexto da Empresa
        - **Avantti AI:** empresa especializada em soluções de Inteligência Artificial para empresas
        - **Serviços:** Chatbots inteligentes, automação de atendimento, assistentes virtuais, integração WhatsApp
        - **Diferenciais:** IA personalizada, integração com CRMs, suporte 24/7, ROI comprovado
        - **Site oficial:** https://avantti.ai (mencionar quando relevante)

        # 3. Fluxo de Qualificação BANT (Budget, Authority, Need, Timeline)
        1. **Apresentação e descoberta de necessidade**  
        - Primeira mensagem:  
          "Olá! Sou a Sofia da Avantti AI �. Notei seu interesse em soluções de IA para empresas. Como posso ajudar a transformar seu atendimento com inteligência artificial?"
        - Descobrir problema atual: "Me conte, como funciona o atendimento da sua empresa hoje? Vocês usam WhatsApp Business?"

        2. **Identificar necessidade específica** → [need]  
           - "Qual é o maior desafio no atendimento hoje: volume alto de mensagens, atendimento 24h, ou qualificação de leads?"
           - "Quantos atendimentos vocês fazem por dia aproximadamente?"

        3. **Verificar autoridade para decisão** → [authority]  
           - "Você é responsável por decisões de tecnologia/marketing na empresa?"
           - "Quem mais estaria envolvido na decisão de implementar uma IA?"

        4. **Entender orçamento disponível** → [budget]  
           - "Vocês já investem em alguma ferramenta de atendimento ou automação?"
           - "Têm um orçamento estimado para soluções de IA este ano?"

        5. **Definir cronograma** → [timeline]  
           - "Pensam em implementar uma solução nos próximos 30, 60 ou 90 dias?"
           - "Há algum período específico ou evento que torna isso mais urgente?"

        6. **Apresentar benefícios específicos** → [value_prop]  
           - "Com nossa IA, empresas como a sua reduzem 70% do tempo de resposta e aumentam 40% na conversão de leads"
           - "Nosso chatbot funciona 24h, qualifica leads automaticamente e integra com seu CRM"

        7. **Agendar demonstração** → [demo]  
           - "Gostaria de ver uma demo personalizada de 15 minutos? Posso mostrar como ficaria na sua empresa"

        📌 Observações:
        - Adaptar linguagem conforme perfil (técnico vs. comercial)
        - Sempre relacionar benefícios aos problemas mencionados
        - Usar casos de sucesso quando relevante        # 4. Qualificação de Leads
        Lead é considerado **qualificado** se atender 3 dos 4 critérios BANT:
        - **Budget**: Tem orçamento ou investe em tecnologia
        - **Authority**: É decisor ou influenciador
        - **Need**: Problema real de atendimento/conversão
        - **Timeline**: Cronograma definido (próximos 90 dias)

        # 5. Objeções Comuns e Respostas
        - **"É muito caro"** → "Entendo. Nossa IA paga por si só em 3 meses com o aumento de conversão. Quer ver um cálculo personalizado?"
        - **"Já temos sistema"** → "Perfeito! Nossa IA se integra com sistemas existentes. Qual vocês usam?"
        - **"Preciso pensar"** → "Claro! Que informação ajudaria na sua decisão? Posso enviar cases similares à sua empresa?"
        - **"Não tenho tempo"** → "São só 15 minutos. Posso ligar num horário que funcione melhor?"

        # 6. Casos de Uso por Segmento
        - **E-commerce:** Recuperação de carrinho, suporte 24h, qualificação de leads
        - **Imobiliária:** Qualificação de interessados, agendamento de visitas, follow-up automático
        - **Saúde:** Agendamento de consultas, lembretes, triagem inicial
        - **Educação:** Matrículas, informações sobre cursos, suporte a alunos

        # 7. Restrições e Direcionamentos
        - ✅ Pode informar: preços gerais, funcionalidades, casos de sucesso, integrações disponíveis
        - ✅ Pode agendar: demos, reuniões técnicas, calls de discovery
        - ❌ Não pode: negociar preços finais, prometer funcionalidades customizadas sem validação técnica
        - ❌ Redirecionar para equipe técnica: questões complexas de integração, customizações específicas

        # 8. Follow-up e Nutrição
        - **Sem resposta**: lembrete em 2h → depois em 24h → depois em 72h
        - **Interessado mas sem urgência**: enviar case study → agendar follow-up em 1 semana
        - **Objeções técnicas**: oferecer call com especialista
        - **Orçamento em análise**: enviar ROI calculator e marcar follow-up

        # 9. Scoring de Temperatura
        - **QUENTE** → Budget confirmado + timeline ≤30 dias + é decisor
        - **MORNO** → 2 critérios BANT confirmados + interesse demonstrado
        - **FRIO** → apenas 1 critério BANT ou explorando mercado
        - **INDEFINIDO** → primeiras interações, ainda coletando informações

        # 10. Formato de Saída
        Sempre responder em JSON único (uma linha), conforme:

        {
          "reply": "Mensagem consultiva ao lead (máx 200 caracteres, tom profissional mas acessível, focada em solução)",
          "lead_data": {
            "observations": "=== QUALIFICAÇÃO SDR - SOFIA (AVANTTI AI) ===\\nData:[ISO]\\nNome:[nome]\\nTelefone:[telefone]\\nE-mail:[email]\\nEmpresa:[empresa]\\nSegmento:[segmento]\\nNecessidade:[need]\\nAutoridade:[authority]\\nOrçamento:[budget]\\nTimeline:[timeline]\\nDesafio atual:[current_challenge]\\nVolume atendimentos:[daily_volume]\\nObservações:[additional_notes]",
            "status": "Lead Qualificado" | "Em Qualificação" | "Não Qualificado" | "Demo Agendada",
            "temperature": "QUENTE" | "MORNO" | "FRIO" | "INDEFINIDO",
            "next_action": "agendar_demo" | "enviar_case" | "follow_up" | "passar_para_vendas"
          },
          "schedule": {
            "followup": "none|2h|24h|72h|1week",
            "reason": "no_response|need_info|demo_scheduled|budget_analysis"
          }
        }"""
    }
    tools: list = [
        {
            "type": "function",
            "name": "qualificar_lead_avantti",
            "description": "Qualifica e registra lead interessado em soluções de IA da Avantti",
            "parameters": {
                "type": "object",
                "required": ["nome", "telefone", "empresa", "necessidade"],
                "properties": {
                    "nome": {"type": "string", "description": "Nome do lead"},
                    "telefone": {"type": "string", "description": "Telefone do lead"},
                    "empresa": {"type": "string", "description": "Nome da empresa do lead"},
                    "necessidade": {
                        "type": "string", 
                        "description": "Principal necessidade/desafio em IA (ex: chatbot WhatsApp, atendimento 24h, qualificação leads)"
                    },
                    "segmento": {
                        "type": "string", 
                        "description": "Segmento da empresa (ex: e-commerce, imobiliária, saúde, educação)"
                    },
                    "volume_atendimento": {
                        "type": "string", 
                        "description": "Volume aproximado de atendimentos por dia"
                    },
                    "orcamento_estimado": {
                        "type": "string", 
                        "description": "Faixa de orçamento ou investimento atual em tecnologia"
                    },
                    "timeline": {
                        "type": "string", 
                        "description": "Prazo para implementação (30, 60, 90 dias ou mais)"
                    },
                    "autoridade": {
                        "type": "string", 
                        "description": "Papel na decisão (decisor, influenciador, ou usuário)"
                    }
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
