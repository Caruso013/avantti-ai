# 📋 Guia de Configuração - Variáveis de Ambiente

Este documento explica como configurar corretamente todas as variáveis de ambiente do sistema Avantti AI.

## 🔴 CONFIGURAÇÕES OBRIGATÓRIAS

### 1. OpenAI (Obrigatório)
```bash
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_ASSISTANT_ID=asst_your-assistant-id
```
- **Como obter**: Acesse https://platform.openai.com/
- **OPENAI_API_KEY**: Sua chave da API OpenAI
- **OPENAI_ASSISTANT_ID**: ID do assistente que você criou na plataforma OpenAI

### 2. Supabase (Banco de Dados - Obrigatório)
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```
- **Como obter**: Acesse https://supabase.com/
- **SUPABASE_URL**: URL do seu projeto Supabase
- **SUPABASE_KEY**: Chave pública (anon key) do projeto

### 3. WhatsApp API (Obrigatório - escolha uma opção)

#### Opção A: Z-API
```bash
ZAPI_BASE_URL=https://api.z-api.io
ZAPI_INSTANCE_ID=your-instance-id
ZAPI_INSTANCE_TOKEN=your-instance-token
ZAPI_CLIENT_TOKEN=your-client-token
```

#### Opção B: Evolution API
```bash
EVOLUTION_BASE_URL=https://your-evolution-api.com
EVOLUTION_INSTANCE_NAME=your-instance-name
EVOLUTION_INSTANCE_KEY=your-instance-key
```

### 4. CRM - REMOVIDO
O sistema não usa mais integração com CRM externo (Pipedrive removido).

## 🟡 CONFIGURAÇÕES IMPORTANTES

### 1. CRM - REMOVIDO
O sistema não utiliza mais integração com CRM externo (Pipedrive foi removido).

### 2. Redis (Cache)
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
```
- **Instalação local**: `redis-server`
- **Docker**: `docker run -d -p 6379:6379 redis`

### 3. Notificações
```bash
PHONE_NUMBER_NOTIFICATION=5511999999999
```
- **Formato**: Código do país + DDD + número (sem símbolos)
- **Exemplo**: 5511999999999 (Brasil, SP, 99999-9999)

## 🟢 CONFIGURAÇÕES OPCIONAIS (já têm valores padrão)

### 1. Configurações da Aplicação
```bash
APP_ENV=local                      # local, stage, production
APP_PORT=8000                      # Porta do servidor
DEBOUNCE_SECONDS=5                 # Tempo de debounce para mensagens
DEBOUNCE_SECONDS_TYPING=3          # Tempo de debounce para "digitando"
QUEUE_KEY=message_queue            # Nome da fila de mensagens
```

### 2. Configurações OpenAI
```bash
OPENAI_BASE_URL=https://api.openai.com/v1  # URL base (padrão OpenAI)
OPENAI_MAX_OUTPUT_TOKENS=1000              # Máximo de tokens na resposta
OPENAI_MAX_AUDIO_TRANSCRIBE_MB=25          # Tamanho máximo do áudio (MB)
```

### 3. Configurações de Reuniões
```bash
MEETING_DURATION=30                # Duração em minutos
MEETING_SCHEDULE_START_TIME=09:00  # Horário de início
MEETING_SCHEDULE_END_TIME=18:00    # Horário de fim
```

### 4. Configurações Avançadas
```bash
SELLER_MESSAGE_WAITING_TIME_IN_SECONDS=180  # Tempo de espera vendedor (3 min)
CONTEXT_SIZE=80                              # Número de mensagens no contexto
ABANDONED_CONVERSATIONS_TIME_IN_HOURS=24    # Tempo para conversa abandonada
LOG_LEVEL=INFO                               # Nível de log (DEBUG, INFO, WARNING, ERROR)
```

### 5. Tratamento de Erros
```bash
ERROR_NOTIFICATION_ENABLED=false    # Habilitar notificações de erro
ERROR_NOTIFIERS=whatsapp            # Tipos de notificadores
ERROR_NOTIFICATION_PHONE_NUMBER=    # Número para erros
ERROR_NOTIFICATION_INSTANCE=        # Instância para erros
ERROR_NOTIFICATION_INSTANCE_KEY=    # Chave da instância
```

## 🚀 PRIMEIROS PASSOS

### 1. Configuração Mínima para Desenvolvimento
```bash
# .env mínimo para rodar local
APP_ENV=local
APP_PORT=8000

# OpenAI (OBRIGATÓRIO)
OPENAI_API_KEY=sk-your-key-here
OPENAI_ASSISTANT_ID=asst-your-id-here

# Supabase (OBRIGATÓRIO)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# WhatsApp (escolha Z-API OU Evolution)
ZAPI_BASE_URL=https://api.z-api.io
ZAPI_INSTANCE_ID=your-instance
ZAPI_INSTANCE_TOKEN=your-token
ZAPI_CLIENT_TOKEN=your-client-token
```

### 2. Instalação das Dependências
```bash
# Redis (para cache)
docker run -d -p 6379:6379 redis

# Não é mais necessário PostgreSQL local - usando Supabase
```

### 3. Validação
Execute o servidor para verificar se tudo está configurado:
```bash
python start_server.py
```

## ⚠️ DICAS IMPORTANTES

1. **Nunca commite o arquivo .env** - ele já está no .gitignore
2. **Use .env.example** como referência para novos desenvolvedores
3. **Teste uma configuração por vez** para identificar problemas
4. **Configure logs em DEBUG** durante desenvolvimento (`LOG_LEVEL=DEBUG`)
5. **Use Redis para melhor performance** mesmo em desenvolvimento

## 🔒 SEGURANÇA

- Mantenha suas chaves API seguras
- Use variáveis diferentes para cada ambiente (dev, stage, prod)
- Monitore o uso das APIs para evitar custos excessivos
- Configure notificações de erro apenas em produção

## 📞 SUPORTE

Se encontrar problemas:
1. Verifique os logs da aplicação
2. Confirme se todas as variáveis obrigatórias estão configuradas
3. Teste as conexões individualmente (banco, Redis, APIs)
4. Consulte a documentação específica de cada serviço