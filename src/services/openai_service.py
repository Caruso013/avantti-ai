import os
import requests
import logging
import re
import json
from datetime import datetime
from .response_processor_service import response_processor

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Prompt refinado da Eliane v4.0.1 - Sem emojis e com contexto real
        self.system_prompt = """# 1. Identidade
- **Nome:** Eliane
- **Função:** SDR (pré-vendas) da **Evex Imóveis**
- **Estilo de comunicação:**
- Tom formal-casual
- Simpática e humana (evitar parecer robô)
- Não envie mensagens com emojis!
- Frases curtas, objetivas
- Gatilhos de venda sutis e palavras-chave de conversão

# 2. Contexto da Empresa
- **Evex Imóveis:** imobiliária especializada em empreendimentos residenciais
- **Fonte dos leads:** anúncios Meta/Facebook
- **Canal:** WhatsApp/SMS (Z-API)
- **Site oficial:** https://www.eveximoveis.com.br (usar apenas para consultas específicas, se o lead pedir)

# 3. Fluxo de Qualificação CONTEXTUAL
REGRA FUNDAMENTAL: SEMPRE ANALISE O CONTEXTO ANTES DE RESPONDER
- Se o lead JÁ demonstrou interesse, NÃO pergunte se quer informações
- Se o lead JÁ disse que quer investir, NÃO pergunte se tem interesse
- Se o lead JÁ forneceu dados, use essas informações nas próximas respostas
- **NUNCA prometa "enviar informações depois"** - SEMPRE forneça informações NA HORA

⚠️ RESTRIÇÃO CRÍTICA: NUNCA INVENTE INFORMAÇÕES!
- Use APENAS as informações listadas na seção 4
- Se não souber detalhes específicos, diga "Posso verificar isso para você"
- NÃO crie descrições detalhadas não listadas no prompt
- NÃO invente características dos empreendimentos

1. **Apresentação inicial** (apenas na PRIMEIRA mensagem OU após 12+ horas sem contato)
- **Primeira mensagem:** "Olá, {{nome}}! Aqui é a Eliane, da Evex Imóveis. Vi que você se interessou pelo anúncio do {{empreendimento}}."  
- **Sem nome:** "Olá! Tudo bem? Aqui é a Eliane, da Evex Imóveis. Vi que você se interessou pelo anúncio do {{empreendimento}}."
- **Reapresentação (12h+):** "Oi{{, {{nome}}}}! Aqui é a Eliane novamente, da Evex Imóveis. Como posso ajudar você hoje?"

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
• JARDIM VENEZA - Loteamento residencial
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
- ERRADO: "Vou verificar e te envio"
- ERRADO: "Te mando as informações em breve"  
- ERRADO: "Vou consultar e retorno"
- CORRETO: "Na Reserva Garibaldi temos lotes a partir de R$ 180 mil"
- CORRETO: "Nossos empreendimentos ficam em Curitiba e região metropolitana"
- CORRETO: "Trabalhamos com entrada facilitada e financiamento bancário"
- CORRETO: "O Moradas do Lago é um condomínio residencial"
- CORRETO: "Em São José temos o Life Garden, Cortona e Siena disponíveis"
- CORRETO: "Para investimento, recomendo o Ecolife em Fazenda Rio Grande"

**NUNCA INVENTE DETALHES:**
- ERRADO: "O Jardim Veneza tem ótima estrutura"
- ERRADO: "É um condomínio fechado com segurança"
- ERRADO: "Tem área de lazer completa"
- CORRETO: "O Jardim Veneza é um loteamento residencial em Almirante Tamandaré"
- CORRETO: "Esse empreendimento tem potencial interessante! Me conta, você busca para morar ou investir?"
- CORRETO: "Temos o Jardim Veneza disponível. Qual seria sua faixa de investimento?"

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

**CORRETO (usa contexto + info real):**
Lead: "quero informações sobre investimento!"
Bot: "Perfeito! Para investimento recomendo o Ecolife em Fazenda Rio Grande ou a Reserva Garibaldi em Curitiba. Ambos têm ótimo potencial de valorização."

# 5. Regras de Nome
- Usar {{nome}} do anúncio na primeira mensagem, se disponível.
- Se o lead se apresentar com outro nome, atualizar e usar esse.
- Nunca usar o nome automático do WhatsApp.
- Se não houver nome, usar abertura neutra.

# 6. Critérios de Qualificação e REGISTRO AUTOMÁTICO
Lead é qualificado se:
- Demonstra interesse real no empreendimento, ou
- Pede informações sobre condições de pagamento, ou
- Responde positivamente às etapas 1, 3 e 4, ou
- Fornece informações detalhadas sobre orçamento e timing.

🎯 **IMPORTANTE - MENSAGENS CONSOLIDADAS**: 
Se a mensagem contém múltiplas informações separadas por " | ", significa que o lead enviou várias mensagens seguidas. Analise TODAS as informações e responda de forma CONSOLIDADA, considerando TUDO que foi mencionado:

Exemplo:
Lead: "olá | meu nome é Pedro | tenho 45mil | quero casa para morar | tem alguma dica?"
Resposta: "Olá Pedro! Vi que você tem R$ 45 mil para investir em uma casa para morar. Com esse valor, posso sugerir excelentes opções! Me conta, você tem preferência por alguma região específica?"

🚨 NUNCA responda cada parte separadamente - SEMPRE consolide em UMA resposta completa.

🎯 **ATENÇÃO FUNCTION CALLING**: Quando um lead fornecer NOME + demonstrar INTERESSE genuíno, CHAME AUTOMATICAMENTE a função `registrar_lead` com os dados coletados:
- Nome completo do lead
- Telefone (sempre disponível)
- Email se fornecido
- Tipo de interesse (investimento/residencial/comercial)
- Orçamento mencionado
- Localização de interesse

🚨 EXEMPLOS PARA FUNCTION CALLING:
- Lead: "Oi, sou Pedro, quero informações sobre investimento" → REGISTRAR LEAD
- Lead: "Meu nome é Ana, estou procurando apartamento" → REGISTRAR LEAD  
- Lead: "Me chamo João, tenho R$ 300k para investir" → REGISTRAR LEAD
- Lead: "Sou Maria, quero saber sobre os empreendimentos" → REGISTRAR LEAD

# 7. Restrições RIGOROSAS
- ✅ Pode informar: APENAS o que está listado na seção 4 (lista de empreendimentos e informações comerciais básicas)
- ✅ Pode dizer: localização básica (cidade), tipo geral (loteamento/condomínio conforme listado)
- ❌ NÃO pode: inventar detalhes sobre estrutura, características específicas, amenidades
- ❌ NÃO pode: descrever "ótima estrutura", "área de lazer", "segurança" sem estar na lista
- ❌ NÃO pode: negociar preço/prazo, falar sobre obras, reputação da empresa
- ❌ NÃO pode: criar descrições detalhadas não fornecidas no prompt

🚨 SE NÃO SOUBER DETALHES ESPECÍFICOS: Use abordagem consultiva e desperte interesse:
- "Esse empreendimento tem potencial interessante! Me conta, você busca para morar ou investir?"
- "Ótima escolha de localização! Qual seria sua faixa de investimento?"
- "Esse é bem procurado no mercado! Você tem interesse em financiar ou à vista?"
- "Excelente oportunidade! Para morada própria ou investimento?"
- "Muito procurado por investidores! Que tipo de imóvel você busca?"
- "Localização privilegiada! Qual seria seu orçamento aproximado?"
- "Temos esse disponível! Me conta mais sobre o que você procura?"
- NUNCA apenas: "Posso verificar mais detalhes"

# 7.1. ESTRATÉGIA CONSULTIVA
SEMPRE direcione a conversa para qualificação quando não souber detalhes:
- Desperte interesse com frases positivas sobre o empreendimento: "tem potencial interessante", "ótima escolha", "bem procurado"
- Faça perguntas sobre finalidade (morar/investir)
- Pergunte sobre orçamento disponível
- Ofereça opções similares da lista
- Mantenha o lead engajado e interessado

# 7.2. FRASES PARA DESPERTAR INTERESSE
Use estas frases para tornar os empreendimentos mais atrativos:
- "Esse empreendimento tem potencial interessante!"
- "Ótima escolha de localização!"
- "Esse é bem procurado no mercado!"
- "Excelente oportunidade para investimento!"
- "Localização privilegiada!"
- "Muito procurado por investidores!"
- "Boa opção para quem busca valorização!"

# 8. Follow-up Automático
- Sem resposta → lembrete em 30m → depois em 2h → se persistir, encerrar com status "Não Responde".
- Se recusar atendimento → encerrar com status "Não Interessado".
- Perguntas fora de escopo → responder padrão e registrar observação "DÚVIDA TÉCNICA".

# 9. Termômetro (C2S)
- **QUENTE** → interesse imediato + orçamento definido + timing próximo
- **MORNO** → interesse confirmado + momento definido
- **FRIO** → ainda pesquisando
- **INDEFINIDO** → antes de obter respostas-chave

# 10. Formato de Saída
ATENÇÃO: RETORNE APENAS O TEXTO DA MENSAGEM, NÃO RETORNE JSON!

Se você quiser incluir dados estruturados, use o seguinte formato JSON interno:
{
  "reply": "Mensagem curta ao lead (máx 180 caracteres, formal-casual, clara, empática, com quebras de texto naturais, CONTEXTUAL)",
  "c2s": {
    "observations": "=== QUALIFICAÇÃO IA - ELIANE ===\\nData:[ISO]\\nNome:[{{nome}}]\\nTelefone:[{{telefone}}]\\nE-mail:[{{email}}]\\nEmpreendimento:[{{empreendimento}}]\\nAnúncio:[{{id_anuncio}}]\\nFaixa original:[{{faixa_valor}}]\\nFinalidade:[...]\\nMomento:[...]\\nFaixa confirmada:[...]\\nPagamento:[...]\\nObservações adicionais:[...]",
    "status": "Novo Lead - Qualificado por IA" | "Não Responde" | "Não Interessado"
  },
"schedule": {
  "followup": "none|30m|2h",
  "reason": "no_response|awaiting_docs|other"
}
}

IMPORTANTE: O cliente receberá APENAS o conteúdo do campo "reply". NUNCA envie o JSON completo.
Sempre responda de forma natural, empática e mantenha mensagens curtas (máx 180 caracteres cada)."""
    
    def update_prompt(self, new_prompt):
        """Atualiza o prompt do sistema"""
        self.system_prompt = new_prompt
        logger.info("Prompt atualizado")
    
    def _aplicar_variaveis_prompt(self, prompt, lead_data=None):
        """Aplica variáveis dinâmicas no prompt"""
        try:
            if not lead_data:
                # Valores padrão se não tiver dados do lead
                lead_data = {
                    'nome': '',
                    'telefone': '',
                    'email': '',
                    'empreendimento': 'nosso empreendimento',
                    'faixa_valor': 'sua faixa de interesse',
                    'id_anuncio': '',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Substitui variáveis no prompt
            prompt_personalizado = prompt
            for key, value in lead_data.items():
                prompt_personalizado = prompt_personalizado.replace(f'{{{{{key}}}}}', str(value))
            
            return prompt_personalizado
            
        except Exception as e:
            logger.error(f"Erro ao aplicar variáveis no prompt: {e}")
            return prompt
    
    def _quebrar_em_mensagens(self, texto):
        """Quebra texto em mensagens naturais baseado em pontos finais e perguntas"""
        # Remove espaços extras
        texto = re.sub(r'\s+', ' ', texto.strip())
        
        # Quebra em sentenças baseado em pontos finais e perguntas
        # Mantém pontuação que indica fim de frase
        sentences = re.split(r'([.!?]+\s+)', texto)
        
        mensagens = []
        mensagem_atual = ""
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i] if i < len(sentences) else ""
            punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
            
            frase_completa = sentence + punctuation
            
            # Se a mensagem atual + nova frase fica muito longa, envia a atual
            if len(mensagem_atual + frase_completa) > 200 and mensagem_atual:
                mensagens.append(mensagem_atual.strip())
                mensagem_atual = frase_completa
            else:
                mensagem_atual += frase_completa
        
        # Adiciona última mensagem se houver
        if mensagem_atual.strip():
            mensagens.append(mensagem_atual.strip())
        
        # Se não conseguiu quebrar, mantém original em uma mensagem
        if not mensagens:
            mensagens = [texto]
        
        logger.info(f"Texto quebrado em {len(mensagens)} mensagens")
        return mensagens
    
    def _verificar_reapresentacao(self, phone, supabase_service):
        """Verifica se precisa se reapresentar após 12 horas desde última APRESENTAÇÃO (não última mensagem)"""
        try:
            # Usa o SupabaseService para verificar quando foi a última apresentação
            info_apresentacao = supabase_service.verificar_ultima_apresentacao(phone)
            
            if info_apresentacao:
                precisa = info_apresentacao.get('precisa_reapresentar', False)
                
                if precisa:
                    if info_apresentacao.get('teve_apresentacao'):
                        logger.info(f"🔄 Reapresentação necessária para {phone} (última há {info_apresentacao.get('horas_desde', 0):.1f}h)")
                    else:
                        logger.info(f"✨ Primeira apresentação para {phone}")
                else:
                    logger.info(f"✅ Não precisa reapresentar para {phone} (última há {info_apresentacao.get('horas_desde', 0):.1f}h)")
                
                return precisa
            
            # Fallback: se não conseguiu verificar, não se apresenta
            logger.warning(f"⚠️ Não foi possível verificar apresentação para {phone} - não se apresentará")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar necessidade de reapresentação: {e}")
            return False
    
    def gerar_resposta(self, message, phone, context=None, lead_data=None, supabase_service=None):
        """Gera resposta da IA usando GPT-4o-mini configurado para o assistant asst_C4tLHrq74kxj8NUHEUkieU65"""
        try:
            # Verifica se precisa se reapresentar usando o SupabaseService
            if supabase_service:
                precisa_reapresentar = self._verificar_reapresentacao(phone, supabase_service)
            else:
                # Fallback: se não tem supabase_service, usa lógica antiga
                logger.warning("⚠️ SupabaseService não fornecido - usando lógica de apresentação simplificada")
                precisa_reapresentar = not context or len(context) == 0
            
            # Aplica variáveis dinâmicas no prompt
            prompt_personalizado = self._aplicar_variaveis_prompt(self.system_prompt, lead_data)
            
            # Adiciona instrução de apresentação APENAS se necessário
            if precisa_reapresentar:
                logger.info(f"🎤 Adicionando instrução de apresentação para {phone}")
                prompt_personalizado += "\n\n🎤 APRESENTAÇÃO OBRIGATÓRIA: Se apresente como Eliane da Evex Imóveis conforme as instruções de apresentação inicial. Esta é a primeira mensagem ou já passou 12+ horas desde a última apresentação.\n\nATENÇÃO CRÍTICA: Use APENAS as informações exatas da seção 4. NUNCA invente detalhes sobre empreendimentos. Se não souber algo específico, seja CONSULTIVA: desperte interesse, faça perguntas sobre finalidade e orçamento."
            else:
                logger.info(f"💬 Continuando conversa para {phone} (sem apresentação)")
                prompt_personalizado += "\n\n💬 CONTINUAÇÃO: NÃO se apresente novamente. Continue a conversa de forma natural e contextual, baseando-se no histórico.\n\nATENÇÃO CRÍTICA: Use APENAS as informações exatas da seção 4. NUNCA invente detalhes sobre empreendimentos. Se não souber algo específico, seja CONSULTIVA: desperte interesse, faça perguntas sobre finalidade e orçamento."

            # Payload para usar a API de chat completions com GPT-4o-mini
            messages = [
                {"role": "system", "content": prompt_personalizado}
            ]
            
            # Se houver contexto, adiciona mensagens anteriores NA ORDEM CRONOLÓGICA
            if context:
                logger.info(f"🔄 Adicionando contexto: {len(context)} mensagens anteriores")
                # Adiciona TODAS as mensagens do contexto em ordem cronológica
                for ctx in context[-10:]:  # Últimas 10 mensagens para mais contexto
                    role = "user" if ctx.get('sender') == 'user' else "assistant"
                    msg_content = ctx.get('message', '').strip()
                    if msg_content:  # Só adiciona se tiver conteúdo
                        messages.append({"role": role, "content": msg_content})
                        logger.debug(f"Contexto adicionado: {role} - {msg_content[:50]}...")
            
            # AGORA adiciona a mensagem atual por último
            messages.append({"role": "user", "content": message})
            
            logger.info(f"📝 Total de mensagens enviadas para IA: {len(messages)} (incluindo system prompt)")
            
            data = {
                "model": "gpt-4o-mini",  # Modelo configurado para o assistant
                "messages": messages,
                "max_tokens": 300,  # Aumentado para acomodar JSON
                "temperature": 0.7,
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "name": "registrar_lead",
                            "description": "Registra automaticamente um lead qualificado no Contact2Sale CRM quando coleta nome, telefone e demonstra interesse em investir em imóveis",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "nome": {
                                        "type": "string",
                                        "description": "Nome completo do lead"
                                    },
                                    "telefone": {
                                        "type": "string", 
                                        "description": "Telefone do lead (sempre disponível no contexto)"
                                    },
                                    "email": {
                                        "type": "string",
                                        "description": "Email do lead se fornecido"
                                    },
                                    "interesse": {
                                        "type": "string",
                                        "description": "Tipo de interesse: investimento, residencial, comercial"
                                    },
                                    "orcamento": {
                                        "type": "string",
                                        "description": "Faixa de orçamento mencionada pelo lead"
                                    },
                                    "localizacao": {
                                        "type": "string",
                                        "description": "Localização de interesse mencionada"
                                    }
                                },
                                "required": ["nome", "telefone"]
                            }
                        }
                    }
                ],
                "tool_choice": "auto"
            }

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=self.headers,
                json=data,
                timeout=15
            )

            if response.status_code == 200:
                result = response.json()
                choice = result.get('choices', [{}])[0]
                message = choice.get('message', {})
                
                # 🎯 VERIFICAR SE HOUVE FUNCTION CALL
                tool_calls = message.get('tool_calls')
                lead_registrado = False
                if tool_calls:
                    logger.info("🎯 Function call detectado - Processando registro de lead...")
                    for tool_call in tool_calls:
                        if tool_call.get('function', {}).get('name') == 'registrar_lead':
                            try:
                                # Extrair argumentos da function call
                                arguments = json.loads(tool_call.get('function', {}).get('arguments', '{}'))
                                arguments['telefone'] = phone  # Garantir que o telefone está correto
                                
                                # Registrar lead no Contact2Sale
                                success = self._registrar_lead_contact2sale(arguments)
                                if success:
                                    logger.info(f"✅ Lead registrado com sucesso: {arguments.get('nome', 'Sem nome')}")
                                    lead_registrado = True
                                else:
                                    logger.error(f"❌ Falha ao registrar lead: {arguments.get('nome', 'Sem nome')}")
                            except Exception as e:
                                logger.error(f"Erro ao processar function call: {e}")
                
                # Se registrou lead mas não tem texto de resposta, usa mensagem padrão
                texto_resposta = message.get('content')
                if texto_resposta:
                    texto_resposta = texto_resposta.strip()
                elif lead_registrado:
                    # Mensagem de sucesso quando lead foi registrado
                    texto_resposta = "Perfeito, vou notificar o time de vendas, logo entrarão em contato!"
                    logger.info("🎯 Lead registrado - usando mensagem de sucesso")
                else:
                    texto_resposta = ""
                
                if texto_resposta:
                    # 🔥 NOVO: PROCESSAMENTO COM RESPONSE PROCESSOR
                    logger.info("Processando resposta com Response Processor...")
                    contexto_processamento = {
                        'precisa_reapresentar': precisa_reapresentar,
                        'phone': phone,
                        'lead_data': lead_data
                    }
                    
                    # Delega todo o processamento para o Response Processor
                    mensagens_processadas = response_processor.processar_resposta(
                        texto_resposta, 
                        contexto_processamento
                    )
                    
                    logger.info(f"✅ Resposta processada com sucesso: {len(mensagens_processadas)} mensagens")
                    return mensagens_processadas
                else:
                    return ["Olá! Obrigada pela mensagem. Nossa equipe retornará em breve."]
            else:
                logger.error(f"Erro OpenAI API: {response.status_code} - {response.text}")
                return ["Desculpe, ocorreu um erro. Tente novamente."]
        except Exception as e:
            logger.error(f"Erro na geração de resposta: {e}")
            return ["Olá! Obrigada pela mensagem. Nossa equipe retornará em breve."]
    
    def get_processor_stats(self):
        """Retorna estatísticas do Response Processor"""
        return response_processor.get_stats()
    
    def _registrar_lead_contact2sale(self, lead_data):
        """
        Registra lead no Contact2Sale CRM usando function calling
        """
        try:
            # Importar o client do Contact2Sale com caminho absoluto
            import sys
            import os
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            if root_dir not in sys.path:
                sys.path.insert(0, root_dir)
            from clients.contact2sale_client import Contact2SaleClient
            
            # Instanciar client
            c2s_client = Contact2SaleClient()
            
            # Preparar dados do lead para o Contact2Sale
            lead_payload = {
                "name": lead_data.get('nome', ''),
                "phone": lead_data.get('telefone', ''),
                "email": lead_data.get('email', ''),
                "interest": lead_data.get('interesse', 'Investimento Imobiliário'),
                "budget": lead_data.get('orcamento', ''),
                "location": lead_data.get('localizacao', ''),
                "source": "WhatsApp Bot - Avantti AI",
                "status": "Novo Lead - Qualificado por IA",
                "notes": f"Lead qualificado automaticamente via function calling. Interesse: {lead_data.get('interesse', 'Investimento')}",
                "created_at": datetime.now().isoformat()
            }
            
            # Enviar para Contact2Sale
            resultado = c2s_client.create_lead(lead_payload)
            
            if resultado:
                logger.info(f"🎯 Lead registrado no Contact2Sale: {lead_data.get('nome')} - {lead_data.get('telefone')}")
                return True
            else:
                logger.error(f"❌ Falha ao registrar lead no Contact2Sale: {lead_data}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao registrar lead no Contact2Sale: {e}")
            return False
    
    def reset_processor_stats(self):
        """Reseta estatísticas do Response Processor"""
        response_processor.reset_stats()