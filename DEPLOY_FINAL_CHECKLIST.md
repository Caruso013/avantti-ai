# ✅ CHECKLIST FINAL PARA DEPLOY - Avantti AI

**Data:** 10/10/2025  
**Branch:** final-clean  
**Último Commit:** 7cff19d  
**Status:** 🚀 PRONTO PARA DEPLOY

---

## 📋 RESUMO DAS CORREÇÕES IMPLEMENTADAS

### ✅ **1. Correção de Alucinações da IA** (Commit: 2752f6b)
**Problema:** IA inventava valores, metragens, quartos, infraestrutura

**Solução:**
- Prompt reforçado com **Seção 11: REGRA FINAL CRÍTICA**
- Lista clara do que pode/não pode inventar
- Respostas padronizadas: *"Vou conectar você com um consultor"*

**Arquivo:** `src/services/openai_service.py`

---

### ✅ **2. Delay de 3s entre Mensagens** (Commit: 2752f6b)
**Problema:** Mensagens enviadas instantaneamente (parecendo robô)

**Solução:**
- 10 segundos antes da primeira mensagem (mantido)
- **3 segundos entre cada mensagem** (novo!)
- Log: `⏳ Aguardando 3s antes da próxima mensagem...`

**Arquivo:** `src/handlers/message_handler.py`

---

### ✅ **3. Correção Contact2Sale - Erro de Módulo** (Commit: 7cff19d)
**Problema:** `ModuleNotFoundError: No module named 'clients'`

**Solução:**
- Import movido para **dentro da função** `_registrar_lead_contact2sale()`
- Import dinâmico com `sys.path` ajustado
- Uso correto das variáveis `C2S_*` do `.env`

**Arquivo:** `src/services/openai_service.py`

---

## 🔧 VARIÁVEIS DE AMBIENTE NECESSÁRIAS

Verifique se o `.env` tem todas essas configurações:

```bash
# OBRIGATÓRIAS
OPENAI_API_KEY=sk-...                           # ✅ Configurado
SUPABASE_URL=https://...                        # ✅ Configurado
SUPABASE_KEY=eyJ...                             # ✅ Configurado
ZAPI_INSTANCE=3E6CCAC06181F057FAF2FEB82DDB19DD  # ✅ Configurado
ZAPI_TOKEN=6B9781EB4F5A6A745400BEC7            # ✅ Configurado

# CONTACT2SALE (para registro de leads)
C2S_JWT_TOKEN=de7e216687e31141bacda3732e68b469ea33c545ab902ce3c1       # ✅ Configurado
C2S_COMPANY_ID=c9433557c1656dea3004165b6bcb7e2a                        # ✅ Configurado
C2S_SELLER_ID=                                                          # ℹ️ Opcional (vazio)
C2S_DEFAULT_SOURCE=WhatsApp IA - Avantti                                # ✅ Configurado
```

---

## 🚀 COMO FAZER O DEPLOY NO EASYPANEL

### **1. Acessar Dashboard**
```
https://app.easypanel.io
```

### **2. Selecionar Projeto**
- Encontre o projeto `avantti-ai`
- Clique para abrir

### **3. Deploy**
```
1. Clique em "Deploy" ou "Rebuild"
2. Aguarde build completar (2-5 minutos)
3. Verifique logs para confirmar sucesso
4. Status deve ficar "Running"
```

### **4. Verificar Logs**
```
1. Clique em "Logs" ou "View Logs"
2. Procure por:
   ✅ "Server running on port 5000"
   ✅ "Supabase connected"
   ✅ "OpenAI service initialized"
   ❌ Não deve ter: "ModuleNotFoundError"
   ❌ Não deve ter: "No module named 'clients'"
```

---

## 🧪 TESTES OBRIGATÓRIOS APÓS DEPLOY

### **Teste 1: Verificar se App Iniciou Corretamente**
**No Easypanel:**
```
1. Ver logs
2. Verificar: "Server running on port 5000"
3. Status: "Running" (bolinha verde)
```

---

### **Teste 2: Verificar Alucinações (IA NÃO inventa)**

**Enviar no WhatsApp:**
```
"Qual o valor dos apartamentos no Moradas do Lago?"
"Quantos quartos tem?"
"Qual a metragem dos lotes?"
"Tem piscina no condomínio?"
```

**✅ Comportamento Esperado:**
```
"Para detalhes específicos como valores e metragem, 
vou conectar você com um consultor da nossa equipe!"
```

**❌ NÃO deve responder:**
```
❌ "Os apartamentos custam R$ 350 mil"
❌ "Temos apartamentos de 2 e 3 quartos"
❌ "Os lotes têm 250m²"
❌ "Sim, o condomínio tem piscina aquecida"
```

---

### **Teste 3: Verificar Delay de 3s**

**Enviar no WhatsApp:**
```
"Oi, tenho interesse nos empreendimentos de Curitiba"
```

**✅ Comportamento Esperado:**
```
⏱️ 10 segundos de espera (delay inicial)
📱 Primeira mensagem enviada
⏱️ 3 segundos de espera
📱 Segunda mensagem enviada (se houver)
⏱️ 3 segundos de espera
📱 Terceira mensagem enviada (se houver)
```

**Verificar nos logs do Easypanel:**
```bash
✅ Deve aparecer: "⏳ Aguardando 3s antes da próxima mensagem..."
```

---

### **Teste 4: Verificar Contact2Sale (Registro de Leads)**

**Enviar no WhatsApp:**
```
"Oi, meu nome é João Silva e tenho interesse em investir em imóveis"
```

**✅ Comportamento Esperado:**

1. **No WhatsApp:**
```
"Perfeito, vou notificar o time de vendas, logo entrarão em contato!"
```

2. **Nos logs do Easypanel:**
```bash
✅ "🎯 Function call detectado: registrar_lead"
✅ "📤 Enviando lead para Contact2Sale: João Silva - 5511999999999"
✅ "✅ Lead registrado no Contact2Sale"
```

3. **No Dashboard do Contact2Sale:**
```
- Acessar: https://app.contact2sale.com/leads
- Verificar lead: "João Silva"
- Telefone: 5511999999999
- Source: "WhatsApp Bot - Avantti AI"
- Status: "Novo Lead - Qualificado por IA"
```

**❌ NÃO deve acontecer:**
```
❌ "Erro ao registrar lead no Contact2Sale"
❌ "ModuleNotFoundError: No module named 'clients'"
❌ "C2S_JWT_TOKEN não configurado"
```

---

### **Teste 5: Verificar Apresentação Única**

**Enviar no WhatsApp (mesma conversa):**
```
Mensagem 1: "Oi"
Mensagem 2: "Ainda estou aqui"
Mensagem 3: "Você pode me ajudar?"
```

**✅ Comportamento Esperado:**
```
- Primeira mensagem: "Olá! Aqui é a Eliane, da Evex Imóveis..."
- Mensagens seguintes: NÃO se apresenta novamente
```

**Verificar nos logs:**
```bash
✅ "✨ Primeira apresentação" (primeira vez)
✅ "✅ Não precisa reapresentar" (mensagens seguintes)
```

---

## 📊 MONITORAMENTO CONTÍNUO

### **Logs Importantes para Monitorar:**

```bash
# SUCESSO
✅ "Server running on port 5000"
✅ "📝 Consolidando X mensagens"
✅ "✅ Não precisa reapresentar"
✅ "⏳ Aguardando 3s antes da próxima mensagem..."
✅ "🎯 Function call detectado: registrar_lead"
✅ "✅ Lead registrado no Contact2Sale"

# ERROS QUE NÃO DEVEM APARECER
❌ "ModuleNotFoundError: No module named 'clients'"
❌ "C2S_JWT_TOKEN não configurado"
❌ "Erro ao registrar lead no Contact2Sale"
❌ "name 'is_primeira_mensagem' is not defined"
```

---

## 🐛 TROUBLESHOOTING

### **Problema 1: App não inicia**
```bash
Erro: "ModuleNotFoundError: No module named 'clients'"

Solução:
1. Verificar se commit 7cff19d está ativo no Easypanel
2. Fazer rebuild forçado
3. Verificar se requirements.txt está correto
```

---

### **Problema 2: Leads não são registrados**
```bash
Erro: "C2S_JWT_TOKEN não configurado"

Solução:
1. Verificar variáveis de ambiente no Easypanel:
   - C2S_JWT_TOKEN
   - C2S_COMPANY_ID
   - C2S_SELLER_ID (opcional)
2. Rebuild após adicionar variáveis
```

---

### **Problema 3: IA continua inventando informações**
```bash
Solução:
1. Verificar se commit 2752f6b está ativo
2. Verificar logs: prompt deve ter "Seção 11: REGRA FINAL CRÍTICA"
3. Considerar fine-tuning (já implementado):
   python fine_tuning/prepare_training_data.py
   python fine_tuning/upload_and_train.py
```

---

### **Problema 4: Delay não funciona**
```bash
Sintoma: Mensagens enviadas instantaneamente

Solução:
1. Verificar logs: "⏳ Aguardando 3s antes da próxima mensagem..."
2. Se não aparece, verificar commit 2752f6b
3. Restart do container pode ser necessário
```

---

## 📝 COMMITS IMPORTANTES

| Commit | Descrição | Arquivos |
|--------|-----------|----------|
| **7cff19d** | Corrige erro 'No module named clients' | `openai_service.py` |
| **2752f6b** | Corrige alucinações + delay 3s | `openai_service.py`, `message_handler.py` |
| **919e85a** | Scripts de teste locais | `test_*.py`, `run_all_tests.py` |
| **ccae9cc** | Sistema de fine-tuning | `fine_tuning/*` |

---

## ✅ CHECKLIST FINAL

Antes de considerar o deploy concluído:

- [ ] Deploy feito no Easypanel (commit 7cff19d)
- [ ] Logs mostram "Server running on port 5000"
- [ ] Teste 1: App iniciou sem erros ✅
- [ ] Teste 2: IA NÃO inventa informações ✅
- [ ] Teste 3: Delay de 3s funciona ✅
- [ ] Teste 4: Contact2Sale registra leads ✅
- [ ] Teste 5: Apresentação única funciona ✅
- [ ] Dashboard Contact2Sale mostra leads de teste
- [ ] Leads de teste deletados do Contact2Sale
- [ ] Monitoramento configurado (logs)

---

## 🎯 PRÓXIMOS PASSOS (OPCIONAL)

### **1. Fine-Tuning (Recomendado)**
Para melhorar ainda mais a qualidade das respostas:

```bash
python fine_tuning/prepare_training_data.py
python fine_tuning/upload_and_train.py
python fine_tuning/monitor_training.py <job_id> --watch
```

**Documentação:** `fine_tuning/README.md`

---

### **2. Monitoramento Avançado**
- Configurar alertas no Easypanel
- Webhook para notificar erros críticos
- Dashboard de métricas (leads registrados, taxa de conversão)

---

### **3. Otimizações**
- Ajustar prompts com base em feedback real
- Adicionar mais empreendimentos na lista
- Melhorar lógica de qualificação

---

## 📞 SUPORTE

Se encontrar problemas:
1. Verificar logs do Easypanel primeiro
2. Consultar este checklist
3. Verificar documentação:
   - `CORRECAO_ALUCINACOES_DELAY.md`
   - `TESTES_LOCAIS.md`
   - `fine_tuning/README.md`

---

**Status:** 🟢 PRONTO PARA DEPLOY  
**Última atualização:** 10/10/2025 15:45  
**Responsável:** Caruso (Avantti AI)
