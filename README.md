# 🤖 Avantti AI - Assistente Inteligente para WhatsApp

Sistema de atendimento automatizado usando OpenAI Assistant API, integrado com WhatsApp via Z-API ou Evolution API.

## 🚀 Configuração Rápida

### 1. Clonar e Instalar Dependências
```bash
git clone <repository-url>
cd Avantti-Ai
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente
```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar com suas configurações
nano .env  # ou use seu editor favorito
```

**Configurações mínimas obrigatórias:**
- `OPENAI_API_KEY`: Sua chave da API OpenAI
- `OPENAI_ASSISTANT_ID`: ID do seu assistente OpenAI
- `SUPABASE_URL`: URL do seu projeto Supabase
- `SUPABASE_KEY`: Chave do Supabase
- API do WhatsApp (Z-API ou Evolution)

📖 **Guia completo**: [CONFIGURACAO_VARIAVEIS.md](CONFIGURACAO_VARIAVEIS.md)

### 3. Validar Configurações
```bash
python validate_config.py
```

### 4. Executar Aplicação
```bash
python start_server.py
```

## 🏗️ Arquitetura

### Principais Componentes
- **Controllers**: Processamento de mensagens recebidas
- **Services**: Lógica de negócio (transcrição, geração de resposta, orquestração)
- **Clients**: Integrações externas (OpenAI, WhatsApp APIs, Pipedrive, Supabase)
- **Tools**: Ferramentas para o assistente (CRM, agendamento)
- **Workers**: Processamento assíncrono de filas

### Fluxo de Mensagens
1. **Recebimento**: Webhook `/message_receive` recebe mensagens
2. **Fila**: Mensagens são enfileiradas para processamento
3. **Processamento**: Worker processa com debounce para evitar spam
4. **IA**: Assistente OpenAI gera resposta contextual
5. **Resposta**: Mensagem é enviada via WhatsApp API

## 🔧 APIs Suportadas

### WhatsApp
- **Z-API**: Serviço brasileiro de WhatsApp Business API
- **Evolution API**: API open-source para WhatsApp

### CRM
- **Dados salvos diretamente no Supabase** (Pipedrive removido)
- Gestão de leads simplificada

### Banco de Dados
- **Supabase**: Banco principal (PostgreSQL gerenciado)
- **Redis**: Cache e filas (opcional)

## 📱 Funcionalidades

### Assistente IA
- Respostas contextuais baseadas no histórico
- Transcrição automática de áudios
- Integração com ferramentas externas

### Gestão de Leads
- Criação automática de leads no CRM
- Agendamento de reuniões
- Transferência para atendimento humano

### Monitoramento
- Logs detalhados de todas as operações
- Notificações de erro via WhatsApp
- Métricas de performance

## 🛠️ Desenvolvimento

### Estrutura do Projeto
```
├── app.py                 # Aplicação Flask principal
├── start_server.py        # Script de inicialização
├── validate_config.py     # Validador de configurações
├── controllers/           # Controladores REST
├── services/             # Lógica de negócio
├── clients/              # Integrações externas
├── tools/                # Ferramentas do assistente
├── workers/              # Processamento assíncrono
├── database/             # Modelos e configuração DB
└── utils/                # Utilitários diversos
```

### Executar Testes
```bash
pytest
```

### Logs e Debug
Configure `LOG_LEVEL=DEBUG` no .env para logs detalhados.

## 🔒 Segurança

- Nunca commite o arquivo `.env`
- Use chaves API diferentes para cada ambiente
- Configure notificações de erro apenas em produção
- Monitore uso das APIs para controlar custos

## 📞 Suporte

1. **Configuração**: Consulte [CONFIGURACAO_VARIAVEIS.md](CONFIGURACAO_VARIAVEIS.md)
2. **Validação**: Execute `python validate_config.py`
3. **Logs**: Verifique os logs da aplicação
4. **Issues**: Abra uma issue no repositório

## 🎯 Próximos Passos

Após a configuração:
1. **Configure seu projeto Supabase**: Siga [SUPABASE_SCHEMA.md](SUPABASE_SCHEMA.md) para criar as tabelas
2. Crie um assistente na plataforma OpenAI
3. Configure webhook do WhatsApp para `http://seu-servidor:8000/message_receive`
4. Teste enviando uma mensagem para o número configurado
5. ~~Configure Pipedrive para gestão de leads~~ (Removido - leads salvos no Supabase)
6. Ajuste prompts e ferramentas conforme necessário
