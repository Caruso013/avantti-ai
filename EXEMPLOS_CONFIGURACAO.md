# 🎯 CONFIGURAÇÕES DE EXEMPLO PARA DESENVOLVIMENTO

## Cenário 1: Desenvolvimento Local Básico

```bash
# .env para desenvolvimento local
APP_ENV=local
APP_PORT=8000

# OpenAI (OBRIGATÓRIO - configure com suas chaves)
OPENAI_API_KEY=sk-proj-ABC123...  # Sua chave aqui
OPENAI_ASSISTANT_ID=asst_123...   # Seu assistente aqui
OPENAI_MAX_OUTPUT_TOKENS=1000

# Supabase (OBRIGATÓRIO)
SUPABASE_URL=https://abc123.supabase.co
SUPABASE_KEY=eyJhbGc...

# Redis Local (via Docker)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Z-API (configure com sua conta)
ZAPI_BASE_URL=https://api.z-api.io
ZAPI_INSTANCE_ID=sua-instancia
ZAPI_INSTANCE_TOKEN=seu-token
ZAPI_CLIENT_TOKEN=seu-client-token

# Configurações básicas
QUEUE_KEY=message_queue
DEBOUNCE_SECONDS=5
CONTEXT_SIZE=80
LOG_LEVEL=DEBUG
```

**Comandos para subir infraestrutura local:**
```bash
# Redis (apenas isso é necessário agora)
docker run -d -p 6379:6379 --name redis redis

# Supabase é cloud - não precisa instalar localmente
```

## Cenário 2: Produção com Supabase + Evolution API

```bash
# Produção
APP_ENV=production
APP_PORT=8000

# OpenAI
OPENAI_API_KEY=sk-proj-PROD123...
OPENAI_ASSISTANT_ID=asst_PROD123...
OPENAI_MAX_OUTPUT_TOKENS=1500

# Supabase (substitui PostgreSQL local)
SUPABASE_URL=https://abc123.supabase.co
SUPABASE_KEY=eyJhbGc...

# Evolution API
EVOLUTION_BASE_URL=https://sua-evolution.com
EVOLUTION_INSTANCE_NAME=producao
EVOLUTION_INSTANCE_KEY=chave-producao

# CRM removido - sem Pipedrive

# Redis Cloud
REDIS_HOST=redis-cloud.com
REDIS_PORT=6379
REDIS_PASSWORD=senha-redis

# Notificações
PHONE_NUMBER_NOTIFICATION=5511999999999
ERROR_NOTIFICATION_ENABLED=true
ERROR_NOTIFIERS=whatsapp
LOG_LEVEL=INFO
```

## Cenário 3: Desenvolvimento com Todas as Integrações

```bash
# Completo para desenvolvimento
APP_ENV=local
APP_PORT=8000

# OpenAI
OPENAI_API_KEY=sk-proj-DEV123...
OPENAI_ASSISTANT_ID=asst_DEV123...
OPENAI_MAX_OUTPUT_TOKENS=1000
OPENAI_MAX_AUDIO_TRANSCRIBE_MB=25

# Banco Local
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=avantti_ai_dev
DB_USERNAME=postgres
DB_PASSWORD=dev123

# Z-API (desenvolvimento)
ZAPI_BASE_URL=https://api.z-api.io
ZAPI_INSTANCE_ID=dev-instance
ZAPI_INSTANCE_TOKEN=dev-token
ZAPI_CLIENT_TOKEN=dev-client-token

# Evolution API (backup)
EVOLUTION_BASE_URL=https://evolution-dev.com
EVOLUTION_INSTANCE_NAME=dev
EVOLUTION_INSTANCE_KEY=dev-key

# Pipedrive (sandbox) - REMOVIDO
# PIPE_DRIVE_BASE_URL=https://api-sandbox.pipedrive.com/v1
# PIPE_DRIVE_TOKEN=sandbox-token
# PIPE_DRIVE_OWNER_ID=999

# Redis Local
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Banco Local
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=avantti_ai_dev
DB_USERNAME=postgres
DB_PASSWORD=dev123

# Z-API (desenvolvimento)
MEETING_DURATION=30
MEETING_SCHEDULE_START_TIME=09:00
MEETING_SCHEDULE_END_TIME=18:00

# Notificações
PHONE_NUMBER_NOTIFICATION=5511999999999
ERROR_NOTIFICATION_ENABLED=true
ERROR_NOTIFIERS=whatsapp
ERROR_NOTIFICATION_PHONE_NUMBER=5511888888888

# Configurações avançadas
SELLER_MESSAGE_WAITING_TIME_IN_SECONDS=180
CONTEXT_SIZE=100
ABANDONED_CONVERSATIONS_TIME_IN_HOURS=24
DEBOUNCE_SECONDS=3
DEBOUNCE_SECONDS_TYPING=2
QUEUE_KEY=dev_message_queue
LOG_LEVEL=DEBUG
```

## 🔧 Comandos Úteis para Setup

### Docker Compose (Opção Avançada)
Crie um `docker-compose.yml`:
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: 123456
      POSTGRES_DB: avantti_ai
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

Execute: `docker-compose up -d`

### Validação por Partes
```bash
# Testar apenas OpenAI
python -c "from openai import OpenAI; print('OpenAI OK')"

# Testar apenas banco
python -c "import psycopg2; print('PostgreSQL OK')"

# Testar apenas Redis
python -c "import redis; r=redis.Redis(); r.ping(); print('Redis OK')"
```

### Logs Úteis
```bash
# Logs em tempo real
tail -f app.log

# Logs apenas de erro
grep ERROR app.log

# Logs de uma sessão específica
grep "thread_id_123" app.log
```

## 🚨 Troubleshooting Comum

### Erro: "OpenAI API key not found"
- Verifique se `OPENAI_API_KEY` está no .env
- Confirme que não há espaços extras na chave

### Erro: "Connection refused PostgreSQL"
- Verifique se PostgreSQL está rodando: `docker ps`
- Teste conexão: `psql -h localhost -U postgres`

### Erro: "Redis connection failed"
- Redis é opcional para desenvolvimento
- Configure `REDIS_HOST=localhost` se usando Docker

### WhatsApp não recebe mensagens
- Verifique se webhook está configurado corretamente
- Teste endpoint: `curl -X POST http://localhost:8000/message_receive`
- Confirme que instância WhatsApp está ativa

### Assistente não responde
- Verifique se `OPENAI_ASSISTANT_ID` existe na OpenAI
- Teste com `validate_config.py`
- Verifique logs para erros de API

## 💰 Custos Estimados (Desenvolvimento)

- **OpenAI**: ~$5-20/mês (dependendo do uso)
- **Z-API**: ~R$ 50-100/mês
- **Pipedrive**: ~R$ 30-60/mês
- **Supabase**: Gratuito até 500MB
- **Redis Cloud**: Gratuito até 30MB

**Total estimado**: R$ 100-200/mês para desenvolvimento