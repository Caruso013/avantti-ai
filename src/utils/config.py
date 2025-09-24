import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """Gerenciador de configurações e variáveis de ambiente"""
    
    def __init__(self):
        self.required_vars = [
            'OPENAI_API_KEY',
            'ZAPI_INSTANCE', 
            'ZAPI_TOKEN',
            'SUPABASE_URL',
            'SUPABASE_KEY'
        ]
    
    def validate_config(self) -> bool:
        """Valida se todas as variáveis obrigatórias estão definidas"""
        missing_vars = []
        
        for var in self.required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Variáveis de ambiente faltando: {', '.join(missing_vars)}")
            return False
        
        logger.info("Todas as variáveis de ambiente estão configuradas")
        return True
    
    def get_config(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Obtém configuração com valor padrão"""
        return os.getenv(key, default)
    
    def get_int_config(self, key: str, default: int = 0) -> int:
        """Obtém configuração como inteiro"""
        try:
            return int(os.getenv(key, default))
        except (ValueError, TypeError):
            return default
    
    def get_bool_config(self, key: str, default: bool = False) -> bool:
        """Obtém configuração como boolean"""
        value = os.getenv(key, '').lower()
        return value in ('true', '1', 'yes', 'on')
    
    def log_config_status(self):
        """Log do status das configurações (sem revelar valores sensíveis)"""
        logger.info("=== STATUS DAS CONFIGURACOES ===")
        
        for var in self.required_vars:
            status = "OK" if os.getenv(var) else "FALTANDO"
            logger.info(f"{var}: {status}")
        
        # Configurações opcionais
        optional_configs = {
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
            'DELAY_RESPOSTA': os.getenv('DELAY_RESPOSTA', '10'),
            'DELAY_ENTRE_MENSAGENS': os.getenv('DELAY_ENTRE_MENSAGENS', '3')
        }
        
        logger.info("=== CONFIGURACOES OPCIONAIS ===")
        for key, value in optional_configs.items():
            logger.info(f"{key}: {value}")

# Instância global
config_manager = ConfigManager()