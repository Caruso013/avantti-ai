# 🚀 DEPLOY GUIDE - AVANTTI AI v3.0.0
## Contact2Sale Distribution System

### 📋 RESUMO DA VERSÃO
- **Versão**: 3.0.0
- **Codinome**: Contact2Sale Distribution  
- **Cliente**: Evex Imóveis
- **Data**: 22/09/2025

### ✨ PRINCIPAIS FUNCIONALIDADES
✅ **Sistema de distribuição automática** entre 11 equipes Evex Imóveis  
✅ **Integração completa Contact2Sale** com criação/busca de leads  
✅ **Quebra automática de mensagens** WhatsApp por ponto/interrogação  
✅ **Remoção de agendamento de visitas** do prompt  
✅ **Banner de inicialização** com status das configurações  
✅ **Endpoint /version** para monitoramento  
✅ **Sistema de estatísticas** de distribuição de leads  

### 🔧 VARIÁVEIS DE AMBIENTE OBRIGATÓRIAS

Adicione estas variáveis no EasyPanel:

```bash
# Contact2Sale - OBRIGATÓRIAS
C2S_JWT_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczpcL1wvY29udGFjdDJzYWxlLmNvbS5iclwvYXBpXC9hdXRoXC9sb2dpbiIsImlhdCI6MTcyNjk2OTc3MCwiZXhwIjoxNzI3MDU2MTcwLCJuYmYiOjE3MjY5Njk3NzAsImp0aSI6IkJ5dWJacUpOUG15RjZObWoiLCJzdWIiOjQ3OTIwLCJwcnYiOiIyM2JkNWM4OTQ5ZjYwMGFkYjM5ZTcwMWM0MDA4NzJkYjdhNTk3NmY3In0.dA3lGYuiTk_T5KMFGhYVyB2fQ7GudLAOpnHgSgHsNX8
C2S_COMPANY_ID=c9433557c1656dea3004165b6bcb7e2a

# Distribuição de Leads - OBRIGATÓRIAS
C2S_USE_TEAM_DISTRIBUTION=true
C2S_DISTRIBUTION_METHOD=round_robin

# Outras variáveis existentes (manter as atuais)
OPENAI_API_KEY=...
ZAPI_TOKEN=...
# etc...
```

### 🏢 EQUIPES CONFIGURADAS (11 EQUIPES)

| ID | Nome | Seller ID | Prioridade | Estado |
|----|------|-----------|------------|--------|
| 1 | Equipe São Paulo | 35962 | 1 | SP |
| 2 | Equipe Rio de Janeiro | 36028 | 1 | RJ |
| 3 | Equipe Minas Gerais | 35963 | 2 | MG |
| 4 | Equipe Sul (RS/SC/PR) | 35964 | 2 | Sul |
| 5 | Equipe Nordeste | 35965 | 3 | NE |
| 6 | Equipe Brasília | 35966 | 2 | DF |
| 7 | Equipe Goiás | 35967 | 3 | GO |
| 8 | Equipe Espírito Santo | 35968 | 3 | ES |
| 9 | Equipe Mato Grosso | 35969 | 4 | MT |
| 10 | Equipe Centro-Oeste | 35970 | 4 | Centro-Oeste |
| 11 | Equipe Nacional | 35971 | 5 | Nacional |

### 📊 MONITORAMENTO

#### 1. Banner de Inicialização
Verifique nos logs do EasyPanel se aparece:
```
🚀 ================================
🏢 AVANTTI AI v3.0.0 INICIADO!
🚀 ================================
✅ Sistema de distribuição: ATIVO
✅ Contact2Sale: INTEGRADO  
✅ Equipes configuradas: 11
✅ Método: round_robin
🎯 Cliente: Evex Imóveis
📅 22/09/2025 18:30:49
🚀 ================================
```

#### 2. Endpoint de Versão
Teste: `curl https://seu-dominio.com/version`

Resposta esperada:
```json
{
  "version": "3.0.0",
  "name": "Contact2Sale Distribution",
  "client": "Evex Imóveis",
  "uptime": "5 minutes",
  "distribution_stats": {...}
}
```

#### 3. Estatísticas de Distribuição  
Teste: `curl https://seu-dominio.com/version`
```json
{
  "distribution_stats": {
    "total_leads": 0,
    "teams": {
      "1": {"name": "Equipe São Paulo", "count": 0},
      "2": {"name": "Equipe Rio de Janeiro", "count": 0}
    },
    "last_reset": "2025-09-22T18:30:49"
  }
}
```

### 🧪 TESTES DISPONÍVEIS

Scripts criados para validação:
- `test_contact2sale_integration.py` - Testa integração completa
- `test_lead_distribution.py` - Testa distribuição entre equipes  
- `test_company_id.py` - Valida Company ID
- `test_message_split.py` - Testa quebra de mensagens
- `test_startup_banner.py` - Testa banner de inicialização

### 📝 COMO FUNCIONA

1. **Lead chega** via WhatsApp
2. **AI processa** sem mencionar visitas 
3. **Mensagem é quebrada** em frases separadas
4. **Lead é distribuído** para próxima equipe (round-robin)
5. **Contact2Sale recebe** lead com seller_id da equipe
6. **Estatísticas são atualizadas**

### 🔄 DEPLOY NO EASYPANEL

1. **Faça o push** do código:
   ```bash
   git push origin main
   ```

2. **Configure as variáveis** de ambiente no EasyPanel

3. **Deploy** e verifique os logs

4. **Teste o endpoint** `/version`

5. **Monitore** a distribuição de leads

### 🆘 TROUBLESHOOTING

#### Se não aparecer o banner:
- Verifique se as variáveis estão configuradas
- Reinicie o container no EasyPanel

#### Se distribuição não funcionar:
- Verifique `C2S_USE_TEAM_DISTRIBUTION=true`
- Teste o endpoint `/version` para ver as estatísticas

#### Se Contact2Sale falhar:
- Verifique o JWT token (pode expirar)
- Verifique o Company ID
- Teste com `test_contact2sale_integration.py`

### 📞 SUPORTE

Em caso de problemas:
1. Verifique os logs do EasyPanel
2. Teste o endpoint `/version`
3. Execute os scripts de teste
4. Verifique as variáveis de ambiente

---
**🎯 Tudo pronto para produção! O sistema está 100% funcional e testado.**