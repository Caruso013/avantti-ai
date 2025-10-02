import os
import requests
import logging
import re
from datetime import datetime

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

# 6. Critérios de Qualificação
Lead é qualificado se:
- Demonstra interesse real no empreendimento, ou
- Pede informações sobre condições de pagamento, ou
- Responde positivamente às etapas 1, 3 e 4, ou
- Fornece informações detalhadas sobre orçamento e timing.

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
    
    def _verificar_reapresentacao(self, context):
        """Verifica se precisa se reapresentar após 12 horas desde última interação"""
        try:
            if not context or len(context) == 0:
                return False
            
            # Pega a última mensagem do contexto
            ultima_mensagem = context[-1]
            
            # Verifica se tem timestamp
            if 'timestamp' not in ultima_mensagem:
                return False
            
            # Calcula diferença de tempo
            from datetime import datetime, timedelta
            
            # Parse do timestamp da última mensagem
            ultimo_timestamp = datetime.fromisoformat(ultima_mensagem['timestamp'].replace('Z', '+00:00'))
            agora = datetime.now(ultimo_timestamp.tzinfo) if ultimo_timestamp.tzinfo else datetime.now()
            
            # Verifica se passou mais de 12 horas
            diferenca = agora - ultimo_timestamp
            passou_12_horas = diferenca > timedelta(hours=12)
            
            if passou_12_horas:
                logger.info(f"Passou {diferenca.total_seconds()/3600:.1f} horas desde última interação - reapresentação necessária")
            
            return passou_12_horas
            
        except Exception as e:
            logger.error(f"Erro ao verificar necessidade de reapresentação: {e}")
            return False
    
    def gerar_resposta(self, message, phone, context=None, lead_data=None):
        """Gera resposta da IA usando GPT-4o-mini configurado para o assistant asst_C4tLHrq74kxj8NUHEUkieU65"""
        try:
            # Verifica se é a primeira interação (sem contexto ou contexto vazio)
            is_primeira_mensagem = not context or len(context) == 0
            
            # Verifica se precisa se reapresentar após 12 horas
            precisa_reapresentar = self._verificar_reapresentacao(context)
            
            # Aplica variáveis dinâmicas no prompt
            prompt_personalizado = self._aplicar_variaveis_prompt(self.system_prompt, lead_data)
            
            # Se é a primeira mensagem OU precisa se reapresentar, reforça a instrução de apresentação
            if is_primeira_mensagem or precisa_reapresentar:
                if precisa_reapresentar:
                    prompt_personalizado += "\n\nIMPORTANTE: Já passou mais de 12 horas desde a última interação com este lead. OBRIGATORIAMENTE se reapresente como Eliane da Evex Imóveis de forma calorosa, como se fosse um novo contato.\n\nATENÇÃO CRÍTICA: Use APENAS as informações exatas da seção 4. NUNCA invente detalhes sobre empreendimentos. Se não souber algo específico, seja CONSULTIVA: desperte interesse, faça perguntas sobre finalidade e orçamento."
                else:
                    prompt_personalizado += "\n\nIMPORTANTE: Esta é a PRIMEIRA mensagem para este lead. OBRIGATORIAMENTE se apresente como Eliane da Evex Imóveis conforme as instruções de apresentação inicial.\n\nATENÇÃO CRÍTICA: Use APENAS as informações exatas da seção 4. NUNCA invente detalhes sobre empreendimentos. Se não souber algo específico, seja CONSULTIVA: desperte interesse, faça perguntas sobre finalidade e orçamento."
            else:
                prompt_personalizado += "\n\nATENÇÃO CRÍTICA: Use APENAS as informações exatas da seção 4. NUNCA invente detalhes sobre empreendimentos. Se não souber algo específico, seja CONSULTIVA: desperte interesse, faça perguntas sobre finalidade e orçamento."

            # Payload para usar a API de chat completions com GPT-4o-mini
            messages = [
                {"role": "system", "content": prompt_personalizado},
                {"role": "user", "content": message}
            ]
            
            # Se houver contexto, adiciona mensagens anteriores
            if context:
                # Adiciona contexto antes da mensagem atual
                for ctx in context[-5:]:  # Últimas 5 mensagens
                    role = "user" if ctx.get('sender') == 'user' else "assistant"
                    messages.insert(-1, {"role": role, "content": ctx.get('message', '')})

            data = {
                "model": "gpt-4o-mini",  # Modelo configurado para o assistant
                "messages": messages,
                "max_tokens": 300,  # Aumentado para acomodar JSON
                "temperature": 0.7
            }

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=self.headers,
                json=data,
                timeout=15
            )

            if response.status_code == 200:
                result = response.json()
                texto_resposta = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                
                if texto_resposta:
                    # VERIFICAÇÃO CRÍTICA: Se contém JSON, extrai OBRIGATORIAMENTE
                    if '{ "reply"' in texto_resposta or '{"reply"' in texto_resposta:
                        logger.info("JSON detectado na resposta - extraindo reply...")
                        resposta_final = self._extrair_reply_do_json(texto_resposta)
                        
                        if resposta_final:
                            mensagens = self._quebrar_em_mensagens(resposta_final)
                            logger.info(f"✅ JSON extraído com sucesso: {resposta_final[:50]}...")
                            return mensagens
                        else:
                            # FALLBACK CRÍTICO: Tenta regex mais agressivo
                            logger.warning("Extração JSON falhou - tentando regex alternativo...")
                            fallback_reply = self._extrair_reply_fallback(texto_resposta)
                            if fallback_reply:
                                mensagens = self._quebrar_em_mensagens(fallback_reply)
                                logger.info(f"✅ Fallback extraído: {fallback_reply[:50]}...")
                                return mensagens
                            else:
                                # ÚLTIMO RECURSO: Resposta padrão
                                logger.error("❌ FALHA CRÍTICA: Não conseguiu extrair reply do JSON!")
                                return ["Olá! Obrigada pela mensagem. Nossa equipe retornará em breve."]
                    else:
                        # Resposta já está limpa (sem JSON)
                        mensagens = self._quebrar_em_mensagens(texto_resposta)
                        logger.info(f"Resposta direta (sem JSON) quebrada em {len(mensagens)} mensagens")
                        return mensagens
                else:
                    return ["Olá! Obrigada pela mensagem. Nossa equipe retornará em breve."]
            else:
                logger.error(f"Erro OpenAI API: {response.status_code} - {response.text}")
                return ["Desculpe, ocorreu um erro. Tente novamente."]
        except Exception as e:
            logger.error(f"Erro na geração de resposta: {e}")
            return ["Olá! Obrigada pela mensagem. Nossa equipe retornará em breve."]
    
    def _extrair_reply_do_json(self, texto_resposta):
        """Extrai o campo 'reply' do JSON retornado pela IA"""
        try:
            import json
            
            # Remove quebras de linha e espaços extras
            texto_limpo = re.sub(r'\s+', ' ', texto_resposta.strip())
            
            # Tenta encontrar JSON na resposta
            # Procura por padrões de JSON que começam com {
            start_pos = texto_limpo.find('{ "reply"')
            if start_pos == -1:
                start_pos = texto_limpo.find('{"reply"')
            
            if start_pos != -1:
                # Encontra o final do JSON balanceando chaves
                bracket_count = 0
                end_pos = start_pos
                
                for i, char in enumerate(texto_limpo[start_pos:], start_pos):
                    if char == '{':
                        bracket_count += 1
                    elif char == '}':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end_pos = i + 1
                            break
                
                json_text = texto_limpo[start_pos:end_pos]
                
                # Tenta fazer parse do JSON
                try:
                    json_obj = json.loads(json_text)
                    reply = json_obj.get('reply', '').strip()
                    
                    if reply:
                        logger.info(f"JSON extraído com sucesso: {reply[:50]}...")
                        return reply
                        
                except json.JSONDecodeError as je:
                    logger.warning(f"Erro ao fazer parse do JSON: {je}")
                    
            # Se não conseguiu extrair JSON, tenta extrair apenas o reply
            reply_match = re.search(r'"reply":\s*"([^"]+)"', texto_resposta)
            if reply_match:
                reply = reply_match.group(1).strip()
                logger.info(f"Reply extraído via regex: {reply[:50]}...")
                return reply
            
            logger.warning("Não foi possível extrair reply do JSON")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao extrair reply do JSON: {e}")
            return None
    
    def _extrair_reply_fallback(self, texto_resposta):
        """Fallback mais agressivo para extrair reply quando o JSON está malformado"""
        try:
            import re
            
            # Múltiplas tentativas de extração
            padroes = [
                r'"reply":\s*"([^"]+)"',  # Padrão básico
                r'"reply"\s*:\s*"([^"]+)"',  # Com espaços extras
                r'reply":\s*"([^"]+)"',  # Sem aspas inicial
                r'"reply":\s*\'([^\']+)\'',  # Com aspas simples
                r'"reply":\s*"([^"]*)"',  # Aceita string vazia
            ]
            
            for padrao in padroes:
                match = re.search(padrao, texto_resposta, re.IGNORECASE)
                if match:
                    reply = match.group(1).strip()
                    if reply:
                        logger.info(f"Fallback extraído via regex: {reply[:50]}...")
                        return reply
            
            # Se ainda não conseguiu, tenta extrair texto antes do primeiro "c2s"
            if '"c2s"' in texto_resposta:
                antes_c2s = texto_resposta.split('"c2s"')[0]
                # Procura por texto entre aspas no início
                match = re.search(r'"([^"]{10,})"', antes_c2s)
                if match:
                    possivel_reply = match.group(1).strip()
                    if not possivel_reply.startswith('{') and len(possivel_reply) > 5:
                        logger.info(f"Fallback extraído antes de c2s: {possivel_reply[:50]}...")
                        return possivel_reply
            
            logger.warning("Todos os fallbacks falharam")
            return None
            
        except Exception as e:
            logger.error(f"Erro no fallback de extração: {e}")
            return None