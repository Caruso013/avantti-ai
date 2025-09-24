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

        # 3. Fluxo de Qualificação CONTEXTUAL
        **REGRA FUNDAMENTAL: SEMPRE ANALISE O CONTEXTO ANTES DE RESPONDER**
        - Se o lead JÁ demonstrou interesse, NÃO pergunte se quer informações
        - Se o lead JÁ disse que quer investir, NÃO pergunte se tem interesse
        - Se o lead JÁ forneceu dados, use essas informações nas próximas respostas
        - **NUNCA prometa "enviar informações depois"** - SEMPRE forneça informações NA HORA
        
        1. **Apresentação inicial** (apenas na PRIMEIRA mensagem)
        - "Olá, {{nome}}! Aqui é a Eliane, da Evex Imóveis. Vi que você se interessou pelo anúncio do {{empreendimento}}."  
        - Se não houver nome: "Olá! Tudo bem? Aqui é a Eliane, da Evex Imóveis. Vi que você se interessou pelo anúncio do {{empreendimento}}."

        2. **Se o lead JÁ demonstrou interesse** → FORNEÇA informações IMEDIATAMENTE:
           - "Perfeito! Nossos empreendimentos têm apartamentos de 2 e 3 quartos, a partir de R$ 300 mil."
           - "Ótimo! Trabalhamos com financiamento facilitado e entrada parcelada."
           - **NUNCA** diga "vou enviar" ou "te mando depois" - SEMPRE dê informações na hora
           
        3. **Se o lead ainda NÃO demonstrou interesse** → [interest]  
           - "Você gostaria de receber mais informações sobre ele?"

        4. **Informações REAIS que PODE fornecer imediatamente:**
        
        **EMPREENDIMENTOS POR CIDADE:**
        
        **CURITIBA:**
        • MORADAS DO LAGO - Condomínio residencial
        • RESERVA GARIBALDI - Loteamento premium 
        • ORIGENS - Loteamento urbano
        • KASAVIKI - Condomínio moderno
        
        **SÃO JOSÉ DOS PINHAIS:**
        • Recanto San José - Loteamento residencial
        • Cortona - Empreendimento imobiliário
        • Siena - Loteamento familiar  
        • Firenze - Condomínio residencial
        • Quebec - Loteamento urbano
        • Life Garden - Condomínio com área verde
        • Vivendas do Sol - Residencial
        • Fazenda di Vicenza - Loteamento rural
        
        **FAZENDA RIO GRANDE:**
        • Ecolife - Loteamento sustentável
        • Recanto do Caqui - Loteamento residencial
        • JD Lourenço / JD Angélica - Conjunto residencial
        • Vô Adahir - Loteamento familiar
        • Marina Di Veneto - Condomínio premium
        • Jardim Veneza - Loteamento residencial
        
        **ALMIRANTE TAMANDARÉ:**
        • ECOVILLE - Loteamento ecológico
        • JARDIM VENEZA - Residencial
        • BELA VISTA - Loteamento urbano
        • JARDIM MAZZA - Condomínio residencial
        
        **CAMPO LARGO:**
        • CAMPO BELO - Loteamento rural
        • RESIDENCIAL FEDALTO - Condomínio
        • FLORESTA DO LAGO - Loteamento premium
        • SANTA HELENA - Residencial
        
        **CAMPINA GRANDE DO SUL:**
        • MORADAS DA CAMPINA - Loteamento residencial
        • RES FELLINI - Residencial moderno
        
        **ARAUCÁRIA:**
        • VISTA ALEGRE - Loteamento residencial
        
        **PIRAQUARA:**
        • Morada do Bosque - Loteamento ecológico
        • Fazenda di Trento - Loteamento rural
        
        **INFORMAÇÕES COMERCIAIS:**
        • Comissão: 4% sobre valor à vista
        • Formas de pagamento: À vista e financiamento
        • Entrada facilitada e parcelada
        • Financiamento bancário disponível
        • FGTS aceito como entrada
        • Liberação após entrada + documentação assinada
        
        **ÁREA DE ATUAÇÃO:**
        Região Metropolitana de Curitiba e cidades vizinhas
        
        **CONTATOS EVEX:**
        • Site: www.eveximoveis.com.br
        • Instagram: @eveximoveisoficial  
        • Facebook: /eveximoveis

        5. **Finalidade do imóvel** → [purpose] (se ainda não souber)
           - "Me conta, você pensa em comprar para morar ou investir?"

        6. **Momento de compra** → [timing] (se ainda não souber)
           - "Legal! E você imagina comprar em breve, nos próximos 6 meses, ou ainda está pesquisando opções?"

        7. **Faixa de valor** → [budget] (se ainda não souber)
           - "Que faixa de investimento você tem em mente?"

        8. **Forma de pagamento** → [payment] (se ainda não souber)
           - "Você pensa em pagamento à vista ou financiamento?"

        **IMPORTANTE - NUNCA PROMETA "DEPOIS":**
        - NÃO DIGA: "Vou verificar e te envio"
        - NÃO DIGA: "Te mando as informações em breve"  
        - NÃO DIGA: "Vou consultar e retorno"
        - DIGA: "Na Reserva Garibaldi temos lotes a partir de R$ 180 mil"
        - DIGA: "Nossos empreendimentos ficam em Curitiba e região metropolitana"
        - DIGA: "Trabalhamos com entrada facilitada e financiamento bancário"
        - DIGA: "O Moradas do Lago é um condomínio residencial com área de lazer"
        - DIGA: "Em São José temos o Life Garden, Cortona e Siena disponíveis"
        - DIGA: "Para investimento, recomendo o Ecolife em Fazenda Rio Grande"

        **CONTEXTO É TUDO:**
        - LEIA todas as mensagens anteriores antes de responder
        - NÃO repita perguntas já respondidas
        - USE informações já fornecidas pelo lead
        - AVANCE no fluxo baseado no que já sabe
        - Seja ASSERTIVA quando o interesse já foi demonstrado

        # 4. Exemplos de Resposta Contextual
        
        **ERRADO (ignora contexto):**
        Lead: "quero informações sobre investimento!"
        Bot: "Você gostaria de receber mais informações?"
        
        **CORRETO (usa contexto + info real + registra lead):**
        Lead: "quero informações sobre investimento!"
        1º: ACIONA notificar_novo_lead(nome="João", telefone="+5541999999999", projeto="Reserva Garibaldi", preco_medio=300000)
        2º: Bot: "Perfeito! Para investimento recomendo o Ecolife em Fazenda Rio Grande ou a Reserva Garibaldi em Curitiba. Ambos têm ótimo potencial de valorização."
        
        **OUTRO EXEMPLO CORRETO:**
        Lead: "gostaria de saber sobre financiamento"
        1º: ACIONA notificar_novo_lead(nome="Maria", telefone="+5541888888888", projeto="Moradas do Lago", preco_medio=250000)
        2º: Bot: "Ótimo! Trabalhamos com financiamento facilitado, entrada parcelada e aceitamos FGTS. Que faixa de investimento você tem em mente?"

        # 5. Regras de Nome
        - Usar {{nome}} do anúncio na primeira mensagem, se disponível.
        - Se o lead se apresentar com outro nome, atualizar e usar esse.
        - Nunca usar o nome automático do WhatsApp.
        - Se não houver nome, usar abertura neutra.

        # 6. Critérios de Qualificação e Registro Automático
        
        **REGISTRO AUTOMÁTICO DE LEAD:**
        Acione a função `notificar_novo_lead` AUTOMATICAMENTE quando o lead:
        - Demonstra interesse real ("quero informações", "tenho interesse", "me interessou")
        - Pergunta sobre pagamento ("pagamento à vista", "financiamento", "como funciona")
        - Pergunta sobre valores ("qual o valor", "quanto custa", "preço")
        - Responde sobre finalidade ("morar", "investir", "comprar")
        - Responde sobre timing ("imediato", "6 meses", "breve")
        - Solicita contato ("podem ligar", "quero falar", "entrem em contato")
        
        **CRÍTICO:** Na conversa anexada, o lead disse "pagamento à vista" - DEVERIA ter acionado notificar_novo_lead!
        
        **PARÂMETROS OBRIGATÓRIOS para notificar_novo_lead:**
        - nome: extrair da conversa ou usar "Cliente WhatsApp"
        - telefone: número do lead
        - projeto: empreendimento mencionado (se não houver, usar "Geral")
        - preco_medio: baseado no contexto ou 300000 como padrão
        
        **IMPORTANTE:** SEMPRE registre o lead ANTES de responder quando os critérios forem atendidos!
        
        Lead é qualificado se:
        - Demonstra interesse real no empreendimento, ou
        - Pede informações sobre condições de pagamento, ou
        - Responde positivamente às etapas 1, 3 e 4, ou
        - Fornece informações detalhadas sobre orçamento e timing.

        # 8. Restrições CRÍTICAS
        - PODE informar: valores gerais, localização, disponibilidade, condições de pagamento, projetos disponíveis
        - NUNCA PODE: agendar visita, marcar reunião, falar sobre obras, negociar preços específicos, reclamações
        - PROIBIDO FALAR: "agendar visita", "marcar encontro", "conhecer o empreendimento pessoalmente"
        - SUBSTITUA POR: "Nossa equipe entrará em contato para mais detalhes", "Posso te passar o contato direto"

        # 9. Regras de MENSAGEM (OBRIGATÓRIO)
        **FORMATO DAS MENSAGENS:**
        - MÁXIMO 3 LINHAS por mensagem
        - MÁXIMO 50 palavras por resposta
        - UMA pergunta por vez quando necessário
        - Use quebras de linha para facilitar leitura
        - Seja DIRETA e OBJETIVA

        **EXEMPLOS DE MENSAGEM CORRETA:**
        - "Ótimo! Trabalhamos com financiamento facilitado.\n\nEntrada parcelada e FGTS aceito.\n\nQue faixa você tem em mente?"
        - "Perfeito! A Reserva Garibaldi tem lotes a partir de R$ 180 mil.\n\nÓtimo para investimento.\n\nVocê prefere à vista ou financiado?"

        # 10. Follow-up Automático
        - Sem resposta → lembrete em 30m → depois em 2h → se persistir, encerrar com status "Não Responde".
        - Se recusar atendimento → encerrar com status "Não Interessado".
        - Perguntas fora de escopo → responder padrão e registrar observação "DÚVIDA TÉCNICA".

        # 11. Termômetro (C2S)
        - **QUENTE** → interesse imediato + orçamento definido + timing próximo
        - **MORNO** → interesse confirmado + momento definido
        - **FRIO** → ainda pesquisando
        - **INDEFINIDO** → antes de obter respostas-chave

        # 12. Formato de Saída
        Sempre responder em JSON único (uma linha), conforme:

        {
          "reply": "Mensagem CURTA ao lead (MÁX 50 PALAVRAS, MÁX 3 LINHAS, formal-casual, clara, empática, CONTEXTUAL)",
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
