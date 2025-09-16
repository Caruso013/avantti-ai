# 🗄️ ESTRUTURA DO BANCO DE DADOS - SUPABASE

Este documento descreve a estrutura das tabelas necessárias no Supabase para o funcionamento do sistema Avantti AI.

## 📊 Tabelas Principais

### 1. customers (Clientes)
```sql
CREATE TABLE customers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    phone VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    auto_response BOOLEAN DEFAULT true,
    status VARCHAR(50) DEFAULT 'active'
);

-- Índices
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_customers_status ON customers(status);
```

### 2. threads (Conversas/Threads)
```sql
CREATE TABLE threads (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    openai_thread_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'active'
);

-- Índices
CREATE INDEX idx_threads_customer_id ON threads(customer_id);
CREATE INDEX idx_threads_openai_thread_id ON threads(openai_thread_id);
```

### 3. messages (Mensagens)
```sql
CREATE TABLE messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    thread_id UUID REFERENCES threads(id) ON DELETE CASCADE,
    phone VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text', -- text, audio, image, etc.
    direction VARCHAR(10) NOT NULL, -- inbound, outbound
    openai_message_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'
);

-- Índices
CREATE INDEX idx_messages_thread_id ON messages(thread_id);
CREATE INDEX idx_messages_phone ON messages(phone);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_direction ON messages(direction);
```

### 4. leads (Leads/Prospects) - NOVA TABELA
```sql
CREATE TABLE leads (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_name VARCHAR(255),
    lead_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    motivation TEXT,
    status VARCHAR(50) DEFAULT 'new_lead',
    source VARCHAR(100) DEFAULT 'whatsapp_ai',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    contacted_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'
);

-- Índices
CREATE INDEX idx_leads_phone ON leads(phone);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_created_at ON leads(created_at);
CREATE INDEX idx_leads_source ON leads(source);
```

### 5. abandoned_conversations (Conversas Abandonadas)
```sql
CREATE TABLE abandoned_conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    phone VARCHAR(20) NOT NULL,
    last_message_at TIMESTAMP WITH TIME ZONE NOT NULL,
    abandoned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notified BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}'
);

-- Índices
CREATE INDEX idx_abandoned_conversations_phone ON abandoned_conversations(phone);
CREATE INDEX idx_abandoned_conversations_last_message_at ON abandoned_conversations(last_message_at);
CREATE INDEX idx_abandoned_conversations_notified ON abandoned_conversations(notified);
```

## 🔧 Comandos para Criação

### Via Supabase Dashboard (SQL Editor)
1. Acesse seu projeto no Supabase Dashboard
2. Vá em "SQL Editor"
3. Execute os comandos SQL acima na ordem apresentada

### Via CLI do Supabase (se estiver usando localmente)
```bash
# Instalar CLI
npm install -g supabase

# Login
supabase login

# Inicializar projeto
supabase init

# Criar migration
supabase migration new create_initial_tables

# Editar o arquivo de migration gerado e adicionar o SQL acima
# Executar migration
supabase db push
```

## 📝 Políticas de Segurança (RLS)

### Habilitar RLS em todas as tabelas
```sql
-- Habilitar Row Level Security
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE abandoned_conversations ENABLE ROW LEVEL SECURITY;

-- Política para permitir todas as operações via service key
-- (para uso pelo backend da aplicação)
CREATE POLICY "Allow service key access" ON customers
    FOR ALL USING (true);

CREATE POLICY "Allow service key access" ON threads
    FOR ALL USING (true);

CREATE POLICY "Allow service key access" ON messages
    FOR ALL USING (true);

CREATE POLICY "Allow service key access" ON leads
    FOR ALL USING (true);

CREATE POLICY "Allow service key access" ON abandoned_conversations
    FOR ALL USING (true);
```

## 🔄 Triggers e Funções

### Atualização automática de timestamps
```sql
-- Função para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers
CREATE TRIGGER update_customers_updated_at 
    BEFORE UPDATE ON customers 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_threads_updated_at 
    BEFORE UPDATE ON threads 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leads_updated_at 
    BEFORE UPDATE ON leads 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## 📊 Views Úteis

### View de leads com informações completas
```sql
CREATE VIEW leads_summary AS
SELECT 
    l.id,
    l.company_name,
    l.lead_name,
    l.phone,
    l.motivation,
    l.status,
    l.source,
    l.created_at,
    l.updated_at,
    c.name as customer_name,
    COUNT(m.id) as total_messages
FROM leads l
LEFT JOIN customers c ON c.phone = l.phone
LEFT JOIN threads t ON t.customer_id = c.id
LEFT JOIN messages m ON m.thread_id = t.id
GROUP BY l.id, c.name;
```

### View de atividade recente
```sql
CREATE VIEW recent_activity AS
SELECT 
    'message' as activity_type,
    m.phone,
    m.content as description,
    m.created_at
FROM messages m
WHERE m.created_at > NOW() - INTERVAL '24 hours'

UNION ALL

SELECT 
    'lead' as activity_type,
    l.phone,
    CONCAT('Novo lead: ', l.lead_name, ' - ', l.company_name) as description,
    l.created_at
FROM leads l
WHERE l.created_at > NOW() - INTERVAL '24 hours'

ORDER BY created_at DESC;
```

## 🚀 Dados de Teste

### Inserir dados de exemplo
```sql
-- Cliente de teste
INSERT INTO customers (phone, name) VALUES 
('5511999999999', 'Cliente Teste');

-- Lead de teste
INSERT INTO leads (company_name, lead_name, phone, motivation) VALUES
('Empresa Teste', 'João Silva', '5511999999999', 'Implementar IA para atendimento');
```

## 🔍 Consultas Úteis

### Verificar estrutura criada
```sql
-- Listar todas as tabelas
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Verificar colunas de uma tabela
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'leads';
```

### Estatísticas básicas
```sql
-- Contagem de registros
SELECT 
    (SELECT COUNT(*) FROM customers) as customers,
    (SELECT COUNT(*) FROM leads) as leads,
    (SELECT COUNT(*) FROM messages) as messages,
    (SELECT COUNT(*) FROM threads) as threads;
```

## ⚠️ Notas Importantes

1. **Backup**: Configure backups automáticos no Supabase
2. **Monitoramento**: Configure alertas para uso de recursos
3. **Indexes**: Monitore performance e adicione índices conforme necessário
4. **RLS**: As políticas RLS são básicas - ajuste conforme sua necessidade de segurança
5. **Migrations**: Use o sistema de migrations para mudanças futuras

## 🔗 Próximos Passos

1. Execute os SQLs de criação no seu projeto Supabase
2. Verifique se todas as tabelas foram criadas corretamente
3. Configure as variáveis `SUPABASE_URL` e `SUPABASE_KEY` no .env
4. Execute `python validate_config.py` para testar a conexão
5. Faça um teste enviando uma mensagem para o sistema