"""
DIAGNÓSTICO COMPLETO DO SISTEMA
Identifica qual código está realmente rodando e onde estão os problemas
"""

import os
import sys
from pathlib import Path

def check_directory_structure():
    """Verifica a estrutura de diretórios do projeto"""
    print("\n" + "="*80)
    print("📁 ESTRUTURA DE DIRETÓRIOS")
    print("="*80)
    
    root = Path(__file__).parent
    
    # Verificar pastas principais
    folders_to_check = [
        "app/bot",
        "app/services", 
        "src/handlers",
        "src/services",
        "clients",
        "services",
        "controllers"
    ]
    
    for folder in folders_to_check:
        path = root / folder
        exists = path.exists()
        symbol = "✅" if exists else "❌"
        print(f"{symbol} {folder:30} {'EXISTE' if exists else 'NÃO EXISTE'}")
        
        if exists and path.is_dir():
            files = list(path.glob("*.py"))
            for file in files[:5]:  # Mostrar apenas 5 primeiros
                print(f"   └─ {file.name}")

def check_main_files():
    """Verifica arquivos principais de entrada"""
    print("\n" + "="*80)
    print("🚀 ARQUIVOS DE ENTRADA")
    print("="*80)
    
    root = Path(__file__).parent
    
    entry_files = [
        "app.py",
        "main.py", 
        "start_server.py",
        "server_simple.py"
    ]
    
    for file in entry_files:
        path = root / file
        exists = path.exists()
        symbol = "✅" if exists else "❌"
        
        if exists:
            size = path.stat().st_size
            print(f"{symbol} {file:30} {size:>10} bytes")
        else:
            print(f"{symbol} {file:30} NÃO EXISTE")

def check_imports_in_app():
    """Analisa imports em app.py para descobrir qual arquitetura está ativa"""
    print("\n" + "="*80)
    print("🔍 ANÁLISE DE IMPORTS EM app.py")
    print("="*80)
    
    root = Path(__file__).parent
    app_file = root / "app.py"
    
    if not app_file.exists():
        print("❌ app.py não encontrado!")
        return
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Procurar imports
    import_patterns = [
        "from app.bot",
        "from src.handlers",
        "from src.services",
        "from clients",
        "from services",
        "from controllers",
        "MessageHandler",
        "OpenAIService",
        "SupabaseService"
    ]
    
    for pattern in import_patterns:
        found = pattern in content
        symbol = "✅" if found else "❌"
        print(f"{symbol} {pattern}")

def check_message_handler_location():
    """Encontra onde está o MessageHandler real"""
    print("\n" + "="*80)
    print("🎯 LOCALIZANDO MessageHandler")
    print("="*80)
    
    root = Path(__file__).parent
    
    possible_locations = [
        "src/handlers/message_handler.py",
        "app/bot/logic.py",
        "services/message_handler.py",
        "handlers/message_handler.py"
    ]
    
    for location in possible_locations:
        path = root / location
        if path.exists():
            print(f"✅ ENCONTRADO: {location}")
            
            # Verificar se tem classe MessageHandler
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "class MessageHandler" in content:
                    print(f"   └─ Contém classe MessageHandler")
                if "def processar_mensagem" in content:
                    print(f"   └─ Contém método processar_mensagem")
                if "def get_ai_response" in content:
                    print(f"   └─ Contém função get_ai_response")
        else:
            print(f"❌ NÃO EXISTE: {location}")

def check_openai_service_location():
    """Encontra onde está o OpenAIService real"""
    print("\n" + "="*80)
    print("🤖 LOCALIZANDO OpenAIService")
    print("="*80)
    
    root = Path(__file__).parent
    
    possible_locations = [
        "src/services/openai_service.py",
        "app/services/openai_service.py",
        "services/openai_service.py",
        "clients/openai_client.py"
    ]
    
    for location in possible_locations:
        path = root / location
        if path.exists():
            print(f"✅ ENCONTRADO: {location}")
            
            # Verificar métodos importantes
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "gerar_resposta" in content:
                    print(f"   └─ Contém método gerar_resposta")
                if "Response Processor" in content or "response_processor" in content:
                    print(f"   └─ Usa Response Processor")
                if "consolidat" in content.lower():
                    print(f"   └─ Tem lógica de consolidação")
        else:
            print(f"❌ NÃO EXISTE: {location}")

def check_queue_system():
    """Verifica se sistema de fila está implementado"""
    print("\n" + "="*80)
    print("📋 SISTEMA DE FILAS/DEBOUNCE")
    print("="*80)
    
    root = Path(__file__).parent
    app_file = root / "app.py"
    
    if not app_file.exists():
        print("❌ app.py não encontrado!")
        return
    
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    queue_indicators = {
        "import queue": "Import do módulo queue",
        "import threading": "Import do módulo threading",
        "Queue()": "Criação de Queue",
        "Thread(": "Criação de Thread",
        "message_queues": "Dicionário de filas",
        "debounce": "Sistema de debounce",
        "consolidat": "Consolidação de mensagens",
        "process_message_queue": "Função de processamento de fila"
    }
    
    for indicator, description in queue_indicators.items():
        found = indicator in content
        symbol = "✅" if found else "❌"
        print(f"{symbol} {description:40} {'SIM' if found else 'NÃO'}")

def generate_summary():
    """Gera resumo do diagnóstico"""
    print("\n" + "="*80)
    print("📊 RESUMO DO DIAGNÓSTICO")
    print("="*80)
    
    root = Path(__file__).parent
    
    # Determinar arquitetura ativa
    has_src = (root / "src/handlers").exists()
    has_app_bot = (root / "app/bot").exists()
    
    print("\n🏗️ ARQUITETURA DETECTADA:")
    if has_src and has_app_bot:
        print("⚠️  CONFLITO: Ambas as arquiteturas existem!")
        print("   - src/ (nova arquitetura)")
        print("   - app/bot/ (arquitetura antiga)")
        print("\n🔴 PROBLEMA: Código confuso com múltiplas implementações")
    elif has_src:
        print("✅ Arquitetura: src/ (modular)")
    elif has_app_bot:
        print("✅ Arquitetura: app/bot/ (com Celery)")
    else:
        print("❌ Nenhuma arquitetura clara identificada!")
    
    # Verificar sistema de fila
    print("\n📋 SISTEMA DE PROCESSAMENTO:")
    app_file = root / "app.py"
    if app_file.exists():
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "Queue()" in content and "Thread(" in content:
            print("✅ Sistema de fila com threading IMPLEMENTADO")
        else:
            print("❌ Sistema de fila NÃO implementado ou incompleto")
        
        if "consolidat" in content.lower():
            print("✅ Lógica de consolidação PRESENTE")
        else:
            print("❌ Lógica de consolidação AUSENTE")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔬 DIAGNÓSTICO COMPLETO DO SISTEMA AVANTTI AI")
    print("="*80)
    
    check_directory_structure()
    check_main_files()
    check_imports_in_app()
    check_message_handler_location()
    check_openai_service_location()
    check_queue_system()
    generate_summary()
    
    print("\n" + "="*80)
    print("✅ DIAGNÓSTICO CONCLUÍDO")
    print("="*80)
    print("\n📝 Próximos passos:")
    print("1. Analise o resumo acima")
    print("2. Identifique qual arquitetura está realmente rodando")
    print("3. Compartilhe este relatório para análise detalhada")
    print("\n")
