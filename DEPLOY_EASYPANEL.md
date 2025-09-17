# 🚀 Deploy Avantti AI no EasyPanel

## 📋 Pré-requisitos

1. Conta no EasyPanel
2. Repositório Git com o código
3. Variáveis de ambiente configuradas

## 🔧 Arquivos para Deploy

### Arquivos criados para produção:
- `Dockerfile.production` - Dockerfile otimizado
- `docker-compose.yml` - Configuração Docker Compose  
- `app_production.py` - Versão otimizada da aplicação
- `.env.example` - Exemplo de variáveis de ambiente

## 🌐 Passos para Deploy no EasyPanel

### 1. Preparar Repositório

```bash
# Commit todos os arquivos novos
git add .
git commit -m "feat: preparar para deploy em produção"
git push origin main
```

### 2. Configurar no EasyPanel

1. **Login no EasyPanel**
   - Acesse seu painel EasyPanel

2. **Criar Nova Aplicação**
   - Clique em "New Project" ou "Add Application"
   - Escolha "Docker" como tipo

3. **Configurar Source**
   - **Repository**: Cole a URL do seu repositório GitHub
   - **Branch**: `main`
   - **Dockerfile**: `Dockerfile.production`

4. **Configurar Variáveis de Ambiente**
   No painel de Environment Variables, adicione:

   ```env
   # Aplicação
   APP_ENV=production
   PORT=5000
   FLASK_ENV=production

   # OpenAI
   OPENAI_API_KEY=sua_openai_api_key_aqui
   OPENAI_ASSISTANT_ID=seu_assistant_id_aqui

   # Z-API
   ZAPI_BASE_URL=https://api.z-api.io
   ZAPI_INSTANCE_ID=seu_instance_id_aqui
   ZAPI_INSTANCE_TOKEN=seu_instance_token_aqui
   ZAPI_CLIENT_TOKEN=seu_client_token_aqui

   # Supabase
   SUPABASE_URL=https://seu_projeto.supabase.co
   SUPABASE_KEY=sua_supabase_key_aqui
   ```

5. **Configurar Porta**
   - **Port**: `5000`
   - **Protocol**: `HTTP`

6. **Deploy**
   - Clique em "Deploy" ou "Create"

### 3. Configurar Webhook da Z-API

1. **Obter URL da Aplicação**
   - Após deploy, copie a URL da aplicação (ex: `https://sua-app.easypanel.app`)

2. **Configurar Webhook Z-API**
   - URL do Webhook: `https://sua-app.easypanel.app/message_receive`
   - Events: `message`
   - Status: `enabled`

## 🔍 Verificação de Funcionamento

### 1. Health Check
```bash
curl https://sua-app.easypanel.app/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "service": "avantti-ai", 
  "version": "production"
}
```

### 2. Teste de Endpoint
```bash
curl https://sua-app.easypanel.app/ping
```

Resposta esperada: `pong`

### 3. Logs da Aplicação
- No painel EasyPanel, verifique os logs para confirmar:
  - `[STARTUP] === AVANTTI AI - PRODUCTION ===`
  - `[SERVIDOR] Starting on host=0.0.0.0, port=5000`

## 🐛 Troubleshooting

### Problemas Comuns:

1. **Build Failed**
   - Verifique se `requirements.txt` está atualizado
   - Confirme que `Dockerfile.production` está no repositório

2. **Container não inicia**
   - Verifique logs no EasyPanel
   - Confirme variáveis de ambiente

3. **Webhook não funciona**
   - Teste URL manualmente: `https://sua-app.easypanel.app/message_receive`
   - Verifique configuração webhook Z-API

4. **OpenAI não responde**
   - Verifique `OPENAI_API_KEY` nas variáveis de ambiente
   - Confirme saldo da conta OpenAI

## 📊 Monitoramento

### Logs Importantes:
```
[PROCESSANDO] 'mensagem' de 5511999999999
[IA] Resposta gerada para: mensagem...
[SUCESSO] Mensagem enviada - ID: ABC123
```

### Endpoints de Status:
- `/health` - Status da aplicação
- `/ping` - Teste de conectividade
- `/` - Informações gerais

## 🔄 Atualizações

Para atualizar a aplicação:

1. **Commit mudanças**:
   ```bash
   git add .
   git commit -m "feat: nova funcionalidade"
   git push origin main
   ```

2. **Redesploy no EasyPanel**:
   - No painel, clique em "Redeploy" ou "Update"

## ✅ Checklist Final

- [ ] Dockerfile.production configurado
- [ ] Variáveis de ambiente definidas no EasyPanel
- [ ] Aplicação buildou com sucesso
- [ ] Health check responde corretamente
- [ ] Webhook Z-API configurado
- [ ] Teste de mensagem funcionando

## 🎯 URLs Importantes

Substitua `sua-app.easypanel.app` pela URL real:

- **Health Check**: `https://sua-app.easypanel.app/health`
- **Webhook Endpoint**: `https://sua-app.easypanel.app/message_receive`
- **Ping Test**: `https://sua-app.easypanel.app/ping`