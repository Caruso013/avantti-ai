# 🎯 Guia de Fine-Tuning - Evex Imóveis AI

Este guia explica como fazer **fine-tuning** do modelo GPT-4o-mini usando conversas reais da Eliane.

## 📚 O que é Fine-Tuning?

Fine-tuning é o processo de **treinar um modelo de IA existente** com seus próprios dados para:

✅ **Melhorar a qualidade das respostas**  
✅ **Manter consistência de tom e estilo**  
✅ **Reduzir "alucinações" (respostas inventadas)**  
✅ **Especializar o modelo no seu domínio** (imóveis, SDR, qualificação)  
✅ **Reduzir custos** (modelos fine-tunados são mais eficientes)

---

## 🚀 Processo Completo (3 Etapas)

### **Etapa 1: Preparar os Dados de Treinamento**

O primeiro passo é **converter conversas reais do Supabase** em formato JSONL.

```bash
cd /c/Users/Caruso/Desktop/Avantti-Ai
python fine_tuning/prepare_training_data.py
```

**O que esse script faz:**
1. Busca conversas do banco de dados Supabase
2. Agrupa por número de telefone (cria sessões completas)
3. Converte para formato JSONL aceito pela OpenAI
4. Valida qualidade dos dados
5. Salva em `fine_tuning/training_data.jsonl`

**Saída esperada:**
```
🚀 Iniciando preparação de dados para fine-tuning...

📥 Buscando 200 conversas do Supabase...
   ✅ 1.243 mensagens encontradas

📞 Agrupando por telefone...
   ✅ 87 conversas únicas

🔄 Convertendo para formato JSONL...
   ✅ 87 exemplos criados

📊 Validando formato dos dados...

📈 Estatísticas:
   - Total de exemplos: 87
   - Total de mensagens: 1.243
   - Média de mensagens/exemplo: 14.3
   - Tokens estimados: ~45.000
   - Custo estimado de treinamento: ~$0.36

✅ 87 exemplos salvos em: fine_tuning/training_data.jsonl

✨ Preparação concluída!
   Próximo passo: execute 'python fine_tuning/upload_and_train.py'
```

---

### **Etapa 2: Fazer Upload e Iniciar Treinamento**

Agora vamos **enviar os dados para OpenAI** e criar o job de fine-tuning.

```bash
python fine_tuning/upload_and_train.py
```

**O que esse script faz:**
1. Faz upload do arquivo `training_data.jsonl` para OpenAI
2. Cria um job de fine-tuning com modelo base `gpt-4o-mini-2024-07-18`
3. Define um **suffix** (nome customizado do modelo): `evex-eliane`
4. Retorna o **Job ID** para monitoramento

**Saída esperada:**
```
🚀 Iniciando processo de fine-tuning...

📤 Fazendo upload de: fine_tuning/training_data.jsonl
   ✅ Upload concluído! File ID: file-abc123xyz

🎯 Criando job de fine-tuning...
   Modelo base: gpt-4o-mini-2024-07-18
   Suffix: evex-eliane
   ✅ Job criado! Job ID: ftjob-abc123

📊 Status: validating_files

💾 Informações salvas em: fine_tuning/fine_tuning_jobs.json

============================================================
✨ FINE-TUNING INICIADO COM SUCESSO!
============================================================

📝 Informações importantes:
   Job ID: ftjob-abc123
   File ID: file-abc123xyz
   Status atual: validating_files

⏳ O treinamento pode levar de 10 minutos a algumas horas.

📊 Para monitorar o progresso:
   python fine_tuning/monitor_training.py ftjob-abc123

🌐 Ou acesse o dashboard:
   https://platform.openai.com/finetune/ftjob-abc123
```

---

### **Etapa 3: Monitorar o Treinamento**

Você pode **acompanhar o progresso** em tempo real.

#### **Opção 1: Consulta única (status atual)**
```bash
python fine_tuning/monitor_training.py ftjob-abc123
```

#### **Opção 2: Monitoramento contínuo (atualiza a cada 30s)**
```bash
python fine_tuning/monitor_training.py ftjob-abc123 --watch
```

**Saída durante o treinamento:**
```
============================================================
📊 STATUS DO FINE-TUNING
============================================================

🆔 Job ID: ftjob-abc123
📝 Status: running
🤖 Modelo base: gpt-4o-mini-2024-07-18
✨ Modelo final: Ainda não disponível

📈 Progresso:
   Tokens treinados: 32.450

🕐 Criado em: 1733789234

📝 Últimos eventos:
------------------------------------------------------------
ℹ️ [14:23:45] Fine-tuning job started
ℹ️ [14:24:12] Training progress: 25%
ℹ️ [14:25:34] Training progress: 50%
ℹ️ [14:26:45] Training progress: 75%

⏳ Próxima atualização em 30 segundos...
```

**Saída quando concluído:**
```
============================================================
📊 STATUS DO FINE-TUNING
============================================================

🆔 Job ID: ftjob-abc123
📝 Status: succeeded
🤖 Modelo base: gpt-4o-mini-2024-07-18
✨ Modelo final: ft:gpt-4o-mini-2024-07-18:avantti:evex-eliane:abc123

📈 Progresso:
   Tokens treinados: 45.230

🕐 Criado em: 1733789234
✅ Finalizado em: 1733791456
⏱️  Duração: 37 minutos

============================================================
✨ FINE-TUNING CONCLUÍDO COM SUCESSO!
============================================================

🎉 Seu modelo está pronto!
   ID do modelo: ft:gpt-4o-mini-2024-07-18:avantti:evex-eliane:abc123

📝 Para usar no código, substitua:
   model='gpt-4o-mini'
   por
   model='ft:gpt-4o-mini-2024-07-18:avantti:evex-eliane:abc123'
```

---

## 🔧 Como Usar o Modelo Fine-Tunado

Após o treinamento, você receberá um **model ID** (ex: `ft:gpt-4o-mini-2024-07-18:avantti:evex-eliane:abc123`).

### **Atualizar o código para usar o novo modelo:**

**Arquivo:** `src/services/openai_service.py`

**Antes:**
```python
"model": "gpt-4o-mini"
```

**Depois:**
```python
"model": "ft:gpt-4o-mini-2024-07-18:avantti:evex-eliane:abc123"
```

**Locais para atualizar:**
1. `src/services/openai_service.py` (linha ~417)
2. `tools/notificar_novo_lead_tool.py` (linha ~17)
3. `tools/crm_tool.py` (linha ~13)

---

## 💰 Custos de Fine-Tuning

### **GPT-4o-mini (2024-07-18)**
- **Treinamento:** $3.00 por 1M tokens (~$0.003 por 1K tokens)
- **Uso (input):** $0.30 por 1M tokens (~$0.0003 por 1K tokens)
- **Uso (output):** $1.20 por 1M tokens (~$0.0012 por 1K tokens)

### **Exemplo com 50.000 tokens de treinamento:**
- Custo de treinamento: **$0.15**
- Custo de uso: **50% mais barato que GPT-4o-mini base**

---

## 📊 Boas Práticas

### **1. Qualidade dos Dados**
✅ Use **conversas reais** (não inventadas)  
✅ Mínimo de **50 exemplos** (idealmente 100-500)  
✅ Exemplos devem ter **3+ trocas** (user ↔ assistant)  
✅ Remover conversas com **erros ou respostas ruins**

### **2. Formato dos Dados**
✅ Cada linha = 1 conversação completa (formato JSONL)  
✅ Sempre começar com `system` prompt  
✅ Alternar entre `user` e `assistant`  
✅ Não incluir mensagens vazias

### **3. Monitoramento**
✅ Acompanhar métricas de treinamento  
✅ Testar o modelo antes de colocar em produção  
✅ Comparar respostas com modelo base

---

## 🧪 Testando o Modelo

Depois de treinar, **teste o modelo** antes de colocar em produção:

```python
# Teste local (sem afetar produção)
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

response = client.chat.completions.create(
    model="ft:gpt-4o-mini-2024-07-18:avantti:evex-eliane:abc123",
    messages=[
        {"role": "system", "content": "Você é Eliane, SDR da Evex Imóveis..."},
        {"role": "user", "content": "Olá, tenho interesse em apartamentos"}
    ]
)

print(response.choices[0].message.content)
```

---

## 🔄 Re-Treinamento

Se quiser **retreinar com mais dados**:

1. Execute novamente `prepare_training_data.py` (aumentando o `limit`)
2. Execute novamente `upload_and_train.py` (use um suffix diferente, ex: `evex-eliane-v2`)
3. Você terá **dois modelos** (pode comparar qual funciona melhor)

---

## 📚 Recursos Adicionais

- [Documentação oficial OpenAI Fine-Tuning](https://platform.openai.com/docs/guides/fine-tuning)
- [Preços de Fine-Tuning](https://openai.com/pricing)
- [Boas práticas de preparação de dados](https://platform.openai.com/docs/guides/fine-tuning/preparing-your-dataset)

---

## ⚠️ Troubleshooting

### **Erro: "Not enough examples"**
- Você precisa de **no mínimo 10 exemplos** (idealmente 50+)
- Execute `prepare_training_data.py` com `limit=500`

### **Erro: "Invalid format"**
- Verifique se o arquivo JSONL está correto
- Execute novamente `prepare_training_data.py`

### **Modelo não melhora as respostas**
- Pode ser que os dados não sejam representativos
- Certifique-se de usar **conversas reais e de qualidade**
- Tente treinar com **mais exemplos**

---

## 📞 Suporte

Se tiver dúvidas, consulte:
1. Logs do script (`monitor_training.py`)
2. Dashboard da OpenAI: https://platform.openai.com/finetune
3. Documentação oficial: https://platform.openai.com/docs

---

**Última atualização:** Outubro 2025  
**Versão:** 1.0.0
