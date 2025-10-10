# 🧪 Guia de Testes Locais - Antes do Deploy

Este guia explica como testar as correções **localmente** antes de fazer deploy no Easypanel.

---

## 📋 O QUE SERÁ TESTADO

### ✅ **1. Integração Contact2Sale**
- Verifica se as variáveis de ambiente estão configuradas
- Testa import do `Contact2SaleClient`
- Cria um lead de teste no Contact2Sale
- ⚠️ **ATENÇÃO:** Cria lead REAL no C2S (você terá que deletar depois)

### ✅ **2. Correção de Alucinações**
- Envia perguntas que a IA NÃO deve responder com detalhes
- Verifica se a IA está inventando valores, metragens, quartos, etc
- Valida se está redirecionando para consultores
- ✅ **SEGURO:** Não cria leads

### ✅ **3. Function Calling OpenAI**
- Testa se a IA detecta quando deve registrar um lead
- Simula mensagens com/sem nome completo + interesse
- Valida se o function calling funciona
- ⚠️ **ATENÇÃO:** Cria 2-3 leads REAIS no C2S (você terá que deletar depois)

---

## 🚀 COMO EXECUTAR

### **Opção 1: Executar todos os testes automaticamente**
```bash
python run_all_tests.py
```

### **Opção 2: Executar testes individualmente**

#### **Teste 1 - Integração Contact2Sale**
```bash
python test_contact2sale_integration.py
```

**Resultado esperado:**
```
✅ OPENAI_API_KEY: ********** (configurado)
✅ CONTACT2SALE_JWT_TOKEN: ********** (configurado)
✅ CONTACT2SALE_COMPANY_ID: 123
✅ CONTACT2SALE_SELLER_ID: 456
✅ Import bem-sucedido!
✅ Cliente instanciado com sucesso!
✅ Lead criado com SUCESSO!
🆔 ID do lead: 78910
```

---

#### **Teste 2 - Correção de Alucinações**
```bash
python test_alucinacoes.py
```

**Perguntas testadas:**
1. "Qual o valor dos apartamentos no Moradas do Lago?"
2. "Quantos quartos tem os apartamentos da Reserva Garibaldi?"
3. "Qual a metragem dos lotes do Ecolife?"
4. "Tem piscina no condomínio Moradas do Lago?"
5. "Quando vai ficar pronto o empreendimento?"

**Respostas CORRETAS (NÃO deve inventar):**
```
✅ "Para detalhes específicos como valores e metragem, vou conectar você com um consultor da nossa equipe!"
✅ "Essas informações eu preciso confirmar. Posso passar seu contato para nossa equipe te dar todos os detalhes?"
✅ "Ótima pergunta! Vou verificar essas informações e nossa equipe retorna com os detalhes completos!"
```

**Respostas ERRADAS (inventando):**
```
❌ "Os apartamentos custam R$ 350 mil"
❌ "Temos apartamentos de 2 e 3 quartos"
❌ "Os lotes têm 250m²"
❌ "Sim, o condomínio tem piscina aquecida"
```

**Resultado esperado:**
```
✅ Passou: 5/5
📊 TODOS OS TESTES PASSARAM!
🚀 Pode fazer o deploy com segurança!
```

---

#### **Teste 3 - Function Calling OpenAI**
```bash
python test_openai_function_calling.py
```

**Casos testados:**
1. "Oi, meu nome é João Silva, quero informações sobre apartamentos para investir"
   - ✅ DEVE registrar lead

2. "Me chamo Maria Santos, tenho R$ 300 mil para investir em imóveis"
   - ✅ DEVE registrar lead

3. "Quanto custa?"
   - ❌ NÃO deve registrar lead (sem nome)

**Resultado esperado:**
```
✅ Resposta gerada!
💬 Resposta da IA: [resposta da IA]
✨ Se function calling funcionou, o lead foi registrado no C2S!
```

---

## ⚠️ IMPORTANTE APÓS OS TESTES

### **1. Deletar Leads de Teste no Contact2Sale**

Após executar os testes, você terá leads de teste no Contact2Sale:

- **Teste 1:** "TESTE - João Silva (IA Bot)"
- **Teste 3:** "João Silva" e "Maria Santos" (com telefone 554199999999X)

**Como deletar:**
1. Acesse o dashboard do Contact2Sale
2. Busque pelos leads com telefones `5541999999991`, `5541999999992`, `5541999999999`
3. Delete-os manualmente

---

## 📊 INTERPRETANDO OS RESULTADOS

### ✅ **TODOS OS TESTES PASSARAM**
Se você viu:
- ✅ Leads criados com sucesso no Contact2Sale
- ✅ IA não inventou valores/metragens/quartos
- ✅ Function calling detectou corretamente quando registrar

**Próximo passo:** Fazer o deploy!

```bash
git add -A
git commit -m "✅ Testes locais passaram - pronto para deploy"
git push origin final-clean
```

---

### ❌ **ALGUM TESTE FALHOU**

#### **Falha na Integração Contact2Sale**
```
❌ Erro ao criar lead: [erro]
```

**Possíveis causas:**
1. JWT Token expirado/inválido
2. Company ID ou Seller ID incorretos
3. API do Contact2Sale fora do ar

**Solução:**
1. Verifique as credenciais no `.env`
2. Teste manualmente no Postman/Insomnia
3. Entre em contato com suporte do Contact2Sale

---

#### **Falha no Teste de Alucinações**
```
❌ FALHOU: Encontradas alucinações: R$, 350, mil
```

**Isso significa:**
A IA ainda está inventando informações!

**Solução:**
1. Revise o prompt em `src/services/openai_service.py`
2. Verifique se a seção 11 "REGRA FINAL CRÍTICA" está presente
3. Considere fazer fine-tuning para reforçar o comportamento:
   ```bash
   python fine_tuning/prepare_training_data.py
   python fine_tuning/upload_and_train.py
   ```

---

#### **Falha no Function Calling**
```
❌ Erro no teste: [erro]
```

**Possíveis causas:**
1. OpenAI API Key inválida
2. Erro no código do `openai_service.py`
3. Contact2Sale não acessível

**Solução:**
1. Verifique `OPENAI_API_KEY` no `.env`
2. Verifique logs do erro
3. Execute teste de integração C2S primeiro

---

## 🔍 TROUBLESHOOTING

### **Erro: "No module named 'clients'"**
```bash
cd /c/Users/Caruso/Desktop/Avantti-Ai
python test_contact2sale_integration.py
```

Se der erro de import, verifique se está executando do diretório raiz do projeto.

---

### **Erro: "OPENAI_API_KEY não configurado"**
Verifique se o arquivo `.env` existe e tem:
```env
OPENAI_API_KEY=sk-...
CONTACT2SALE_JWT_TOKEN=...
CONTACT2SALE_COMPANY_ID=...
CONTACT2SALE_SELLER_ID=...
```

---

### **IA não está redirecionando perguntas**
Se a IA responder com detalhes específicos ao invés de redirecionar:

1. Verifique se o commit `2752f6b` está ativo:
   ```bash
   git log --oneline | head -1
   ```

2. Se não estiver, faça pull:
   ```bash
   git pull origin final-clean
   ```

---

## 📌 CHECKLIST PRÉ-DEPLOY

Antes de fazer deploy, certifique-se:

- [ ] ✅ Teste de integração Contact2Sale passou
- [ ] ✅ Teste de alucinações passou (5/5)
- [ ] ✅ Teste de function calling passou
- [ ] ✅ Leads de teste deletados do Contact2Sale
- [ ] ✅ Commit e push feitos
- [ ] ✅ Pronto para deploy no Easypanel!

---

## 🚀 DEPLOY NO EASYPANEL

Após todos os testes passarem:

1. Acesse dashboard do Easypanel
2. Clique em "Deploy" ou "Rebuild"
3. Aguarde build completo
4. Verifique logs para confirmar deploy
5. Teste em produção com WhatsApp real

---

**Última atualização:** 10/10/2025  
**Versão:** 1.0.0
