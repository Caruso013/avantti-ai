#!/usr/bin/env python3
"""
Script para verificar leads no Contact2Sale
Testa conexão e lista leads recentes
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

try:
    from services.contact2sale_service import Contact2SaleService
    from clients.contact2sale_client import Contact2SaleClient
except ImportError as e:
    print(f"❌ Erro ao importar: {e}")
    print("⚠️ Execute este script na raiz do projeto")
    sys.exit(1)

def testar_conexao_c2s():
    """Testa conexão com Contact2Sale"""
    
    print("🔗 TESTANDO CONEXÃO COM CONTACT2SALE")
    print("=" * 50)
    
    # Verificar variáveis de ambiente
    jwt_token = os.getenv("C2S_JWT_TOKEN")
    company_id = os.getenv("C2S_COMPANY_ID_EVEX")
    
    if not jwt_token:
        print("❌ C2S_JWT_TOKEN não configurado")
        return None
        
    if not company_id:
        print("⚠️ C2S_COMPANY_ID_EVEX não configurado")
    
    try:
        # Criar cliente
        client = Contact2SaleClient(jwt_token=jwt_token, company_id=company_id)
        
        # Testar conexão
        if client.test_connection():
            print("✅ Conexão com Contact2Sale OK")
            return client
        else:
            print("❌ Falha na conexão com Contact2Sale")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def buscar_leads_recentes(client, dias=7):
    """Busca leads dos últimos dias"""
    
    print(f"\n📋 BUSCANDO LEADS DOS ÚLTIMOS {dias} DIAS")
    print("=" * 50)
    
    try:
        # Buscar todos os leads
        response = client.get_leads()
        
        if not response.success:
            print(f"❌ Erro ao buscar leads: {response.error}")
            return []
        
        leads = response.data.get("data", []) if response.data else []
        
        if not leads:
            print("ℹ️ Nenhum lead encontrado")
            return []
        
        # Filtrar leads recentes
        data_limite = datetime.now() - timedelta(days=dias)
        leads_recentes = []
        
        for lead in leads:
            try:
                # Tentar diferentes formatos de data
                created_at = lead.get("attributes", {}).get("created_at", "")
                if created_at:
                    # Assumir formato ISO
                    data_lead = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if data_lead.replace(tzinfo=None) >= data_limite:
                        leads_recentes.append(lead)
            except:
                # Se não conseguir parsear a data, incluir mesmo assim
                leads_recentes.append(lead)
        
        print(f"📊 {len(leads_recentes)} leads encontrados")
        return leads_recentes
        
    except Exception as e:
        print(f"❌ Erro ao buscar leads: {e}")
        return []

def exibir_detalhes_leads(leads):
    """Exibe detalhes dos leads"""
    
    if not leads:
        return
    
    print(f"\n📋 DETALHES DOS LEADS")
    print("=" * 50)
    
    for i, lead in enumerate(leads, 1):
        attrs = lead.get("attributes", {})
        
        print(f"\n🔹 LEAD #{i}")
        print(f"   ID: {lead.get('id', 'N/A')}")
        print(f"   Nome: {attrs.get('name', 'N/A')}")
        print(f"   Telefone: {attrs.get('phone', 'N/A')}")
        print(f"   Email: {attrs.get('email', 'N/A')}")
        print(f"   Fonte: {attrs.get('source', 'N/A')}")
        print(f"   Projeto: {attrs.get('brand', 'N/A')} - {attrs.get('model', 'N/A')}")
        print(f"   Criado em: {attrs.get('created_at', 'N/A')}")
        print(f"   Status: {attrs.get('status', 'N/A')}")
        
        if attrs.get('body'):
            print(f"   Mensagem: {attrs.get('body')[:100]}...")

def buscar_por_telefone(client, telefone):
    """Busca lead específico por telefone"""
    
    print(f"\n🔍 BUSCANDO LEAD POR TELEFONE: {telefone}")
    print("=" * 50)
    
    try:
        response = client.search_leads_by_phone(telefone)
        
        if not response.success:
            print(f"❌ Erro na busca: {response.error}")
            return None
        
        leads = response.data.get("data", []) if response.data else []
        
        if leads:
            lead = leads[0]
            print("✅ Lead encontrado!")
            print(f"   ID: {lead.get('id')}")
            print(f"   Nome: {lead.get('attributes', {}).get('name')}")
            print(f"   Status: {lead.get('attributes', {}).get('status')}")
            return lead
        else:
            print("ℹ️ Nenhum lead encontrado com este telefone")
            return None
            
    except Exception as e:
        print(f"❌ Erro na busca: {e}")
        return None

def verificar_leads_whatsapp_ia(leads):
    """Verifica leads criados pela IA do WhatsApp"""
    
    leads_ia = []
    
    for lead in leads:
        attrs = lead.get("attributes", {})
        fonte = attrs.get("source", "").lower()
        
        if "whatsapp" in fonte and "ia" in fonte:
            leads_ia.append(lead)
    
    if leads_ia:
        print(f"\n🤖 LEADS CRIADOS PELA IA DO WHATSAPP: {len(leads_ia)}")
        print("=" * 50)
        
        for lead in leads_ia:
            attrs = lead.get("attributes", {})
            print(f"✅ {attrs.get('name')} - {attrs.get('phone')} - {attrs.get('created_at')}")
    else:
        print(f"\n🤖 NENHUM LEAD CRIADO PELA IA ENCONTRADO")
        print("   Possíveis motivos:")
        print("   - Sistema ainda não foi testado com leads reais")
        print("   - Leads foram criados com fonte diferente")
        print("   - Erro na configuração")

def main():
    """Função principal"""
    
    print("🔍 VERIFICADOR DE LEADS NO CONTACT2SALE")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # 1. Testar conexão
    client = testar_conexao_c2s()
    if not client:
        print("\n❌ Não foi possível conectar ao Contact2Sale")
        return
    
    # 2. Buscar leads recentes
    leads = buscar_leads_recentes(client, dias=7)
    
    # 3. Exibir detalhes
    exibir_detalhes_leads(leads[:5])  # Mostrar apenas os 5 primeiros
    
    # 4. Verificar leads da IA
    verificar_leads_whatsapp_ia(leads)
    
    # 5. Opção de buscar por telefone específico
    print(f"\n" + "=" * 60)
    print("💡 DICAS PARA VERIFICAR REGISTROS:")
    print("   1. Execute este script após criar um lead teste")
    print("   2. Verifique os logs do sistema em app.log")
    print("   3. Acesse o painel do Contact2Sale diretamente")
    print("   4. Monitore notificações no WhatsApp da equipe")

if __name__ == "__main__":
    main()