# 🔧 CORREÇÕES CRÍTICAS - Alucinações da IA + Delay entre Mensagens

**Data:** 10/10/2025  
**Commit:** 2752f6b  
**Branch:** final-clean  
**Status:** ✅ Concluído - AGUARDANDO DEPLOY

---

## 🚨 PROBLEMA 1: IA Inventando Informações sobre Imóveis

### **Relatado pelo Cliente:**
> "O cliente está falando que está passando informações que não existem dos imóveis"

### **Comportamento Identificado:**
A IA estava **inventando detalhes** que não estão documentados:
- ❌ Valores específicos (ex: "apartamento de R$ 350 mil")
- ❌ Metragens (ex: "lotes de 250m²", "apartamentos de 80m²")
- ❌ Quartos/suítes (ex: "3 quartos sendo 1 suíte")
- ❌ Infraestrutura (ex: "tem piscina aquecida", "academia completa")
- ❌ Localização exata (ex: "fica na Rua X, próximo ao Shopping Y")
- ❌ Prazo de entrega (ex: "entrega em dezembro de 2025")
- ❌ Características de acabamento (ex: "porcelanato", "armários planejados")

### **Causa Raiz:**
O prompt não tinha instruções **suficientemente rígidas** sobre o que a IA pode/não pode dizer. A IA estava usando "conhecimento geral" sobre imóveis para "completar" informações.

---

## ✅ SOLUÇÃO 1: Prompt Reforçado com Regras Rígidas

### **Alterações no Prompt (openai_service.py):**

#### **1. Seção "⚠️ RESTRIÇÃO CRÍTICA" Expandida:**
```
⚠️ RESTRIÇÃO CRÍTICA: NUNCA INVENTE INFORMAÇÕES!
- Use APENAS as informações listadas na seção 4
- Se não souber detalhes específicos, diga EXATAMENTE: "Vou verificar essa informação com nossa equipe e te retorno"
- NÃO crie descrições detalhadas não listadas no prompt
- NÃO invente características dos empreendimentos
- NÃO invente valores, metragens, número de quartos, localização exata
- NÃO invente datas de entrega, fase de construção, ou status do empreendimento
- NÃO invente características de infraestrutura (piscina, academia, playground, etc)
- NÃO invente detalhes de acabamento, planta, área útil, área total
- SE O LEAD PERGUNTAR algo não listado: "Vou verificar essa informação com nossa equipe e te retorno"
```

#### **2. Nova Seção "IMPORTANTE - O QUE PODE E NÃO PODE FAZER":**
```
✅ CORRETO (informações gerais da seção 4):
- "Na Reserva Garibaldi temos lotes disponíveis"
- "Nossos empreendimentos ficam em Curitiba e região metropolitana"
- "Trabalhamos com entrada facilitada e financiamento bancário"
- "O Moradas do Lago é um condomínio residencial"
- "Aceitamos FGTS como entrada"

❌ PROIBIDO INVENTAR (informações NÃO listadas na seção 4):
- NUNCA invente valores específicos
- NUNCA invente metragens
- NUNCA invente quartos/suítes
- NUNCA invente infraestrutura
- NUNCA invente localização exata
- NUNCA invente prazo de entrega
- NUNCA invente status da obra
- NUNCA invente características de acabamento

🔄 QUANDO NÃO SOUBER:
- "Vou verificar essa informação com nossa equipe e te retorno"
- "Para detalhes específicos de metragem/valor, posso conectar você com um consultor"
- "Essa informação eu preciso confirmar, posso passar seu contato para nossa equipe?"
```

#### **3. Nova Seção Final "11. REGRA FINAL CRÍTICA":**
```
# 11. ⚠️ REGRA FINAL CRÍTICA - NÃO INVENTE NADA!

🚨 ATENÇÃO MÁXIMA: Esta é a regra MAIS IMPORTANTE de todas!

VOCÊ SÓ PODE FORNECER:
1. Nomes dos empreendimentos listados na seção 4
2. Cidades onde ficam (conforme listado)
3. Tipo básico: "loteamento" ou "condomínio" (conforme listado)
4. Informações comerciais gerais: comissão 4%, entrada facilitada, financiamento, FGTS

VOCÊ NUNCA PODE INVENTAR:
❌ Valores, metragens, quartos, infraestrutura, localização exata, prazo, status, acabamentos

SE O LEAD PERGUNTAR QUALQUER COISA NÃO LISTADA:
✅ "Para detalhes específicos como valores e metragem, vou conectar você com um consultor da nossa equipe!"
✅ "Essas informações eu preciso confirmar. Posso passar seu contato para nossa equipe te dar todos os detalhes?"
✅ "Ótima pergunta! Vou verificar essas informações e nossa equipe retorna com os detalhes completos!"

MANTENHA-SE NO SEU PAPEL: Você é SDR (pré-vendas), seu trabalho é QUALIFICAR o lead (coletar nome, interesse, orçamento, finalidade) e PASSAR PARA VENDEDORES. Não tente vender diretamente com detalhes técnicos.
```

---

## 🚨 PROBLEMA 2: Falta de Delay entre Mensagens

### **Relatado pelo Cliente:**
> "também preciso ajeitar a questão de uma mensagem que ai manda para outra ponha um delay de 3 segundos"

### **Comportamento Anterior:**
Quando a IA enviava múltiplas mensagens (ex: quebra de texto), elas eram enviadas **imediatamente uma após a outra**, sem intervalo, parecendo muito robotizado.

### **Comportamento Esperado:**
- ✅ Delay de **10 segundos** antes da primeira mensagem (já existia)
- ✅ Delay de **3 segundos entre cada mensagem** (estava faltando)

---

## ✅ SOLUÇÃO 2: Loop com Delay de 3s

### **Alteração no Código (message_handler.py):**

**Antes:**
```python
def _enviar_mensagens_com_delay(self, phone, mensagens):
    """Envia mensagens com delay de 10s usando ZAPIClient"""
    try:
        import time
        
        # Delay inicial de 10 segundos
        time.sleep(10)
        
        # Envia cada mensagem
        for mensagem in mensagens:
            mensagem_limpa = self._remover_emojis(mensagem)
            self.zapi_client.send_message(phone, mensagem_limpa)
            # ❌ SEM DELAY entre mensagens
            
    except Exception as e:
        logger.error(f"Erro ao enviar mensagens com delay: {e}")
```

**Depois:**
```python
def _enviar_mensagens_com_delay(self, phone, mensagens):
    """Envia mensagens com delay de 10s inicial e 3s entre mensagens"""
    try:
        import time
        
        # Delay inicial de 10 segundos
        time.sleep(10)
        
        # Envia mensagens com delay de 3s entre elas
        for i, mensagem in enumerate(mensagens):
            # Remove emojis manualmente por garantia
            mensagem_limpa = self._remover_emojis(mensagem)
            
            # Envia a mensagem
            self.zapi_client.send_message(phone, mensagem_limpa)
            
            # ✅ Delay de 3 segundos entre mensagens (exceto na última)
            if i < len(mensagens) - 1:
                logger.info(f"⏳ Aguardando 3s antes da próxima mensagem...")
                time.sleep(3)
            
    except Exception as e:
        logger.error(f"Erro ao enviar mensagens com delay: {e}")
```

### **Comportamento Novo:**
1. **Primeira mensagem:** 10s de delay inicial
2. **Segunda mensagem:** +3s de delay (total 13s desde início)
3. **Terceira mensagem:** +3s de delay (total 16s desde início)
4. **Quarta mensagem:** +3s de delay (total 19s desde início)

Isso simula uma conversa **mais natural e humana**.

---

## 📝 Resumo das Mudanças

### **Arquivos Modificados:**
1. ✅ `src/services/openai_service.py` - Prompt com regras muito mais rígidas
2. ✅ `src/handlers/message_handler.py` - Loop com delay de 3s entre mensagens

### **Linhas Adicionadas:**
- **openai_service.py:** +56 linhas de instruções sobre não inventar
- **message_handler.py:** +4 linhas para implementar delay de 3s

---

## 🚀 PRÓXIMOS PASSOS

### **1. DEPLOY OBRIGATÓRIO NO EASYPANEL**
```bash
# No Easypanel:
1. Acessar dashboard
2. Clicar em "Deploy" ou "Rebuild"
3. Aguardar build completo
4. Verificar logs para confirmar deploy
```

### **2. TESTES OBRIGATÓRIOS**

#### **Teste 1: Verificar Alucinações**
**Enviar no WhatsApp:**
```
"Qual o valor dos apartamentos no Moradas do Lago?"
"Quantos quartos tem os imóveis da Reserva Garibaldi?"
"Qual a metragem dos lotes do Ecolife?"
"Tem piscina no condomínio?"
```

**Comportamento Esperado:**
```
✅ "Para detalhes específicos como valores e metragem, vou conectar você com um consultor da nossa equipe!"
✅ "Essas informações eu preciso confirmar. Posso passar seu contato para nossa equipe?"
✅ "Ótima pergunta! Vou verificar e nossa equipe retorna com os detalhes!"

❌ NÃO deve responder: "Os apartamentos custam R$ 350 mil"
❌ NÃO deve responder: "Temos apartamentos de 2 e 3 quartos"
❌ NÃO deve responder: "Os lotes têm 250m²"
❌ NÃO deve responder: "Sim, o condomínio tem piscina aquecida"
```

#### **Teste 2: Verificar Delay de 3s**
**Enviar no WhatsApp:**
```
"Oi, tenho interesse nos empreendimentos de Curitiba"
```

**Comportamento Esperado:**
1. ⏱️ **10 segundos** de espera (delay inicial)
2. 📱 **Primeira mensagem** enviada
3. ⏱️ **3 segundos** de espera
4. 📱 **Segunda mensagem** enviada (se houver)
5. ⏱️ **3 segundos** de espera
6. 📱 **Terceira mensagem** enviada (se houver)

**Verificar nos logs do Easypanel:**
```
✅ Deve aparecer: "⏳ Aguardando 3s antes da próxima mensagem..."
```

### **3. MONITORAR LOGS**
```bash
# Verificar se as mensagens estão sendo enviadas corretamente:
✅ "⏳ Aguardando 3s antes da próxima mensagem..."
✅ "Enviadas X mensagens para [telefone]"

# Verificar se NÃO há erros:
❌ Não deve ter: "Erro ao enviar mensagens com delay"
```

---

## 📊 IMPACTO ESPERADO

### **Redução de Alucinações:**
- ✅ IA não vai mais inventar valores, metragens, quartos
- ✅ IA vai redirecionar perguntas específicas para vendedores
- ✅ IA vai focar em QUALIFICAÇÃO, não em venda técnica

### **Melhoria na Naturalidade:**
- ✅ Conversas mais humanas (delay de 3s entre mensagens)
- ✅ Menos aparência de robô
- ✅ Melhor experiência do usuário

### **Qualificação Mantida:**
- ✅ IA continua qualificando leads (nome, interesse, orçamento)
- ✅ IA continua registrando no Contact2Sale
- ✅ IA continua apresentando-se apenas 1x a cada 12h

---

## ⚠️ OBSERVAÇÕES IMPORTANTES

### **Se Ainda Houver Alucinações:**
Se após o deploy a IA continuar inventando informações:

1. **Verificar se o deploy foi feito** (checar commit no Easypanel)
2. **Verificar logs** para confirmar que o novo prompt está sendo usado
3. **Considerar fine-tuning** (já implementado em `fine_tuning/`) para reforçar comportamento
4. **Coletar exemplos** das alucinações para análise

### **Se o Delay Não Funcionar:**
Se as mensagens continuarem sem delay:

1. **Verificar logs:** `"⏳ Aguardando 3s antes da próxima mensagem..."`
2. **Verificar se está usando** `_enviar_mensagens_com_delay()`
3. **Verificar threading:** Pode estar usando thread antiga

---

## 📞 SUPORTE

Se houver problemas após o deploy:
1. Verificar logs do Easypanel: `/api/logs` ou dashboard
2. Buscar por erros: `"Erro ao enviar mensagens com delay"`
3. Verificar se commit 2752f6b está ativo
4. Reiniciar container se necessário

---

**Status:** ✅ Código pronto e commitado (2752f6b)  
**Próximo passo:** Deploy no Easypanel + Testes  
**Última atualização:** 10/10/2025
