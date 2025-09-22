"""
Configurações para integração Contact2Sale
"""

import os
from typing import Optional, Dict, Any

class Contact2SaleConfig:
    """Configurações centralizadas para Contact2Sale"""
    
    # Credenciais
    JWT_TOKEN: Optional[str] = os.getenv("C2S_JWT_TOKEN")
    COMPANY_ID: Optional[str] = os.getenv("C2S_COMPANY_ID") 
    SELLER_ID: Optional[str] = os.getenv("C2S_SELLER_ID")
    
    # Configurações padrão
    DEFAULT_SOURCE: str = os.getenv("C2S_DEFAULT_SOURCE", "WhatsApp IA - Avantti")
    
    # Configurações de integração
    ENABLED: bool = bool(JWT_TOKEN)
    AUTO_CREATE_LEADS: bool = os.getenv("C2S_AUTO_CREATE_LEADS", "true").lower() == "true"
    AUTO_UPDATE_LEADS: bool = os.getenv("C2S_AUTO_UPDATE_LEADS", "true").lower() == "true"
    SEND_NOTIFICATIONS: bool = os.getenv("C2S_SEND_NOTIFICATIONS", "true").lower() == "true"
    
    # Mapeamento de campos
    FIELD_MAPPING: Dict[str, str] = {
        "name": "name",
        "phone": "phone", 
        "email": "email",
        "message": "body",
        "source": "source",
        "interest": "description",
        "budget": "custom_budget",
        "location": "city"
    }
    
    # Configurações de retry
    MAX_RETRIES: int = int(os.getenv("C2S_MAX_RETRIES", "3"))
    RETRY_DELAY: int = int(os.getenv("C2S_RETRY_DELAY", "5"))  # segundos
    
    # Tags automáticas
    AUTO_TAGS: list = [
        "WhatsApp",
        "IA Automatizada", 
        "Lead Quente"
    ]
    
    @classmethod
    def is_configured(cls) -> bool:
        """Verifica se Contact2Sale está configurado"""
        return bool(cls.JWT_TOKEN)
    
    @classmethod
    def get_validation_errors(cls) -> list[str]:
        """Retorna lista de erros de configuração"""
        errors = []
        
        if not cls.JWT_TOKEN:
            errors.append("C2S_JWT_TOKEN não configurado")
            
        # Aviso para configurações opcionais
        if not cls.COMPANY_ID:
            errors.append("C2S_COMPANY_ID não definido (será obtido via API)")
            
        if not cls.SELLER_ID:
            errors.append("C2S_SELLER_ID não definido (leads não terão vendedor específico)")
            
        return errors
    
    @classmethod
    def get_summary(cls) -> Dict[str, Any]:
        """Retorna resumo da configuração"""
        return {
            "enabled": cls.ENABLED,
            "configured": cls.is_configured(),
            "jwt_token_present": bool(cls.JWT_TOKEN),
            "company_id": cls.COMPANY_ID or "auto-detect",
            "seller_id": cls.SELLER_ID or "none",
            "default_source": cls.DEFAULT_SOURCE,
            "auto_create_leads": cls.AUTO_CREATE_LEADS,
            "auto_update_leads": cls.AUTO_UPDATE_LEADS,
            "send_notifications": cls.SEND_NOTIFICATIONS,
            "max_retries": cls.MAX_RETRIES,
            "validation_errors": cls.get_validation_errors()
        }

# Configurações específicas para diferentes tipos de lead
LEAD_TYPE_CONFIGS = {
    "real_estate": {
        "source": "WhatsApp IA - Imóveis",
        "tags": ["Imóveis", "WhatsApp", "IA"],
        "priority": "high"
    },
    "general": {
        "source": "WhatsApp IA - Geral", 
        "tags": ["WhatsApp", "IA"],
        "priority": "medium"
    },
    "support": {
        "source": "WhatsApp IA - Suporte",
        "tags": ["Suporte", "WhatsApp"],
        "priority": "low"
    }
}

# Mapeamento de status C2S
C2S_STATUS_MAPPING = {
    "new": "Novo Lead - Qualificado por IA",
    "qualified": "Lead Qualificado",
    "contacted": "Contato Realizado", 
    "no_response": "Não Responde",
    "not_interested": "Não Interessado",
    "converted": "Convertido"
}