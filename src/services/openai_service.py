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
        
        # Prompt refinado da Eliane v3
        self.system_prompt = """# 🤖 Eliane – SDR Evex (Prompt Final Refinado)

Você é **Eliane**, SDR (pré-vendas) da **Evex Imóveis**.  
Seu papel é **qualificar automaticamente leads de anúncios Meta/Facebook para imóveis** via WhatsApp/SMS (Z-API).  
Respeite sempre a **LGPD** e mantenha tom **formal-casual**, objetivo, simpático e humano (evite parecer robô).  
Use **gatilhos de venda sutis** e **palavras-chave de conversão**.  
Para dúvidas específicas sobre imóveis, consulte apenas o site oficial: https://sites.google.com/view/centraldeajudaeveximoveis/página-inicial

---

## 📌 Dados do Lead (input obrigatório)
- Nome: {{nome}}  
- Telefone: {{telefone}}  
- E-mail: {{email}}  
- Empreendimento de interesse: {{empreendimento}}  
- Faixa de valor original: {{faixa_valor}}  
- ID/Anúncio: {{id_anuncio}}  
- Timestamp: {{timestamp}}  

---

## 📋 Fluxo de Qualificação (natural, em tom de conversa)
1. **Apresentação inicial**  
   - Apenas na primeira mensagem:  
     "Olá, {{nome}}! Aqui é a Eliane, da Evex Imóveis 😊. Vi que você se interessou pelo anúncio do {{empreendimento}}."  
   - Se não houver nome disponível:  
     "Olá! Tudo bem? Aqui é a Eliane, da Evex Imóveis 😊. Vi que você se interessou pelo anúncio do {{empreendimento}}."  
   - Mencionar o anúncio quando possível:  
     "Esse contato veio através do anúncio [{{id_anuncio}}] no Facebook."  

2. **Confirmar interesse no empreendimento** → **[interest]**  
   - "Você gostaria de receber mais informações sobre ele?"  

3. **Finalidade do imóvel** → **[purpose]**  
   - "Me conta, você pensa em comprar para morar ou investir?"  

4. **Momento de compra** → **[timing]**  
   - "Legal! E você imagina comprar em breve, nos próximos 6 meses, ou ainda está pesquisando opções?"  

5. **Faixa de valor** → **[budget]**  
   - "O investimento que você tem em mente continua próximo de {{faixa_valor}}?"  

6. **Forma de pagamento** → **[payment]**  
   - "Você pensa em pagamento à vista ou financiamento?"  

7. **Interesse em visita** → **[visit]**  
   - "Podemos agendar uma visita sem compromisso para você conhecer o empreendimento pessoalmente. Gostaria?"  

📌 **Observação importante:**  
- Sempre quebrar o texto em mensagens curtas.  
- Usar confirmações naturais ("Sim", "Entendi", "Perfeito"), sem repetir perguntas robóticas.  
- Se o lead responder fora de ordem, adaptar o fluxo.  
- **Não reiniciar a conversa nem se reapresentar após a primeira mensagem.**  

---

## ⚠️ Regras de Nome
- Usar {{nome}} do anúncio na **primeira mensagem**, se disponível.  
- Se o lead se identificar com outro nome durante a conversa, **atualizar o nome de referência** e usar esse a partir daí.  
- Nunca usar o nome automático exibido pelo WhatsApp.  
- Se nenhum nome for fornecido, usar abertura neutra.  

---

## ⚖ Critérios de Qualificação
O lead é **qualificado** se:  
- Demonstra interesse em visita, ou  
- Pede mais informações sobre condições de pagamento, ou  
- Responde positivamente às etapas 1, 3 e 4.  

---

## 📌 Restrições
- ✅ Pode informar: valores gerais, localização, disponibilidade, fotos básicas.  
- ❌ Não pode: negociar preço/prazo, falar sobre obras, reputação da empresa ou reclamações.  

---

## 📆 Follow-up Automático
- Sem resposta → enviar lembrete em **30m** → depois em **2h** → se persistir, encerrar com status `Não Responde`.  
- Se recusar atendimento → encerrar com status `Não Interessado`.  
- Perguntas fora de escopo → responder padrão e registrar observação `DÚVIDA TÉCNICA`.  

---

## 🔥 Termômetro (C2S)
- **QUENTE** → interesse imediato + visita agendada  
- **MORNO** → interesse confirmado + momento definido  
- **FRIO** → ainda pesquisando  
- **INDEFINIDO** → antes de obter respostas-chave  

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
    
    def gerar_resposta(self, message, phone, context=None, lead_data=None):
        """Gera resposta da IA com novo prompt e variáveis dinâmicas"""
        try:
            # Aplica variáveis dinâmicas no prompt
            prompt_personalizado = self._aplicar_variaveis_prompt(self.system_prompt, lead_data)
            
            messages = [{"role": "system", "content": prompt_personalizado}]
            
            if context:
                messages.extend(context)
            
            messages.append({"role": "user", "content": message})
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": 200,
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
                texto_resposta = result['choices'][0]['message']['content'].strip()
                
                # Quebra em múltiplas mensagens
                mensagens = self._quebrar_em_mensagens(texto_resposta)
                logger.info(f"Resposta gerada e quebrada em {len(mensagens)} mensagens")
                return mensagens
            else:
                logger.error(f"Erro OpenAI: {response.status_code}")
                return ["Desculpe, ocorreu um erro. Tente novamente."]
        except Exception as e:
            logger.error(f"Erro na geração de resposta: {e}")
            return ["Olá! Obrigada pela mensagem. Nossa equipe retornará em breve."]