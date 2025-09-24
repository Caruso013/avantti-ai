#!/usr/bin/env python3
"""
Script para validar as configurações do ambiente Avantti AI
Execute: python validate_config.py
"""

import os
import sys
from dotenv import load_dotenv
import redis
import requests
from openai import OpenAI

# Carrega as variáveis de ambiente
load_dotenv()

class ConfigValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success = []
        
    def log_error(self, message):
        self.errors.append(f"❌ ERRO: {message}")
        
    def log_warning(self, message):
        self.warnings.append(f"⚠️  AVISO: {message}")
        
    def log_success(self, message):
        self.success.append(f"✅ OK: {message}")
        
    def check_required_env_vars(self):
        """Verifica variáveis obrigatórias"""
        print("\n🔍 Verificando variáveis obrigatórias...")
        
        required_vars = [
            'OPENAI_API_KEY',
            'OPENAI_ASSISTANT_ID',
            'SUPABASE_URL',
            'SUPABASE_KEY'
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                self.log_error(f"Variável {var} não configurada")
            else:
                self.log_success(f"Variável {var} configurada")
    
    def check_whatsapp_api(self):
        """Verifica se pelo menos uma API do WhatsApp está configurada"""
        print("\n📱 Verificando APIs do WhatsApp...")
        
        zapi_configured = all([
            os.getenv('ZAPI_BASE_URL'),
            os.getenv('ZAPI_INSTANCE'),
            os.getenv('ZAPI_TOKEN'),
            os.getenv('ZAPI_CLIENT_TOKEN')
        ])
        
        evolution_configured = all([
            os.getenv('EVOLUTION_BASE_URL'),
            os.getenv('EVOLUTION_INSTANCE_NAME'),
            os.getenv('EVOLUTION_INSTANCE_KEY')
        ])
        
        if zapi_configured:
            self.log_success("Z-API configurada")
        elif evolution_configured:
            self.log_success("Evolution API configurada")
        else:
            self.log_error("Nenhuma API do WhatsApp configurada (Z-API ou Evolution)")
    
    def test_database_connection(self):
        """Testa conexão com Supabase"""
        print("\n🗄️  Testando conexão com Supabase...")
        
        try:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')
            
            if not url or not key:
                self.log_error("Configurações do Supabase incompletas")
                return
            
            # Teste básico de conectividade
            response = requests.get(f"{url}/rest/v1/", headers={
                'apikey': key,
                'Authorization': f'Bearer {key}'
            }, timeout=10)
            
            if response.status_code == 200:
                self.log_success("Conexão com Supabase OK")
            else:
                self.log_error(f"Erro Supabase: Status {response.status_code}")
                
        except Exception as e:
            self.log_error(f"Erro ao conectar no Supabase: {str(e)}")
    
    def test_redis_connection(self):
        """Testa conexão com Redis"""
        print("\n🔄 Testando conexão com Redis...")
        
        try:
            host = os.getenv('REDIS_HOST', 'localhost')
            port = int(os.getenv('REDIS_PORT', 6379))
            password = os.getenv('REDIS_PASSWORD', None)
            
            r = redis.Redis(host=host, port=port, password=password, decode_responses=True)
            r.ping()
            self.log_success("Conexão com Redis OK")
            
        except Exception as e:
            self.log_warning(f"Redis não acessível: {str(e)} (opcional para desenvolvimento)")
    
    def test_openai_connection(self):
        """Testa conexão com OpenAI"""
        print("\n🤖 Testando conexão com OpenAI...")
        
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
            
            if not api_key:
                self.log_error("OPENAI_API_KEY não configurada")
                return
                
            if not assistant_id:
                self.log_error("OPENAI_ASSISTANT_ID não configurada")
                return
            
            client = OpenAI(api_key=api_key)
            
            # Testa listagem de modelos (operação simples)
            models = client.models.list()
            self.log_success("Conexão com OpenAI OK")
            
            # Testa se o assistente existe
            try:
                assistant = client.beta.assistants.retrieve(assistant_id)
                self.log_success(f"Assistente '{assistant.name}' encontrado")
            except Exception as e:
                self.log_error(f"Assistente não encontrado: {str(e)}")
                
        except Exception as e:
            self.log_error(f"Erro ao conectar com OpenAI: {str(e)}")
    
    def test_supabase_connection(self):
        """Testa conexão avançada com Supabase (opcional)"""
        print("\n🗃️  Testando funcionalidades avançadas do Supabase...")
        
        try:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')
            
            if not url or not key:
                self.log_warning("Supabase não configurado")
                return
            
            # Teste de listagem de tabelas (se tiver permissão)
            response = requests.get(f"{url}/rest/v1/", headers={
                'apikey': key,
                'Authorization': f'Bearer {key}',
                'Accept': 'application/json'
            }, timeout=5)
            
            if response.status_code == 200:
                self.log_success("Funcionalidades avançadas do Supabase OK")
            else:
                self.log_warning(f"Supabase básico OK, mas funcionalidades avançadas limitadas")
                
        except Exception as e:
            self.log_warning(f"Erro ao testar funcionalidades avançadas: {str(e)}")
    
    def check_optional_configs(self):
        """Verifica configurações opcionais importantes"""
        print("\n⚙️  Verificando configurações opcionais...")
        
        # CRM removido - Pipedrive não é mais usado
        self.log_success("CRM: Usando Supabase diretamente (Pipedrive removido)")
        
        # Notificações
        if os.getenv('PHONE_NUMBER_NOTIFICATION'):
            self.log_success("Número para notificações configurado")
        else:
            self.log_warning("Número para notificações não configurado")
        
        # Log level
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_success(f"Nível de log: {log_level}")
    
    def print_results(self):
        """Imprime os resultados da validação"""
        print("\n" + "="*60)
        print("📊 RESUMO DA VALIDAÇÃO")
        print("="*60)
        
        if self.success:
            print("\n✅ SUCESSOS:")
            for msg in self.success:
                print(f"  {msg}")
        
        if self.warnings:
            print("\n⚠️  AVISOS:")
            for msg in self.warnings:
                print(f"  {msg}")
        
        if self.errors:
            print("\n❌ ERROS:")
            for msg in self.errors:
                print(f"  {msg}")
            print("\n🔧 AÇÃO NECESSÁRIA:")
            print("  - Configure as variáveis em erro no arquivo .env")
            print("  - Consulte CONFIGURACAO_VARIAVEIS.md para detalhes")
        else:
            print("\n🎉 CONFIGURAÇÃO VÁLIDA!")
            print("  Todas as configurações obrigatórias estão OK")
        
        print(f"\n📈 ESTATÍSTICAS:")
        print(f"  Sucessos: {len(self.success)}")
        print(f"  Avisos: {len(self.warnings)}")
        print(f"  Erros: {len(self.errors)}")
        
        return len(self.errors) == 0

def main():
    print("🚀 VALIDADOR DE CONFIGURAÇÃO - AVANTTI AI")
    print("="*60)
    
    # Verifica se o arquivo .env existe
    if not os.path.exists('.env'):
        print("❌ Arquivo .env não encontrado!")
        print("💡 Copie o arquivo .env.example para .env e configure as variáveis")
        sys.exit(1)
    
    validator = ConfigValidator()
    
    # Executa todas as validações
    validator.check_required_env_vars()
    validator.check_whatsapp_api()
    validator.test_database_connection()
    validator.test_redis_connection()
    validator.test_openai_connection()
    validator.test_supabase_connection()
    validator.check_optional_configs()
    
    # Mostra resultados
    success = validator.print_results()
    
    if success:
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("  1. Execute: python start_server.py")
        print("  2. Teste o endpoint: POST http://localhost:8000/message_receive")
        sys.exit(0)
    else:
        print("\n🔧 ANTES DE CONTINUAR:")
        print("  1. Corrija os erros listados acima")
        print("  2. Execute novamente: python validate_config.py")
        sys.exit(1)

if __name__ == "__main__":
    main()