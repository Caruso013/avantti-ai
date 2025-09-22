"""
Interfaces para clientes externos
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class LeadInfo:
    """Informações do lead extraídas da conversa"""
    name: Optional[str] = None
    phone: str = ""
    email: Optional[str] = None
    interest: Optional[str] = None
    budget: Optional[str] = None
    location: Optional[str] = None
    message: str = ""
    source: str = "WhatsApp IA"


class CRMClientInterface(ABC):
    """Interface base para clientes CRM"""
    
    @abstractmethod
    def create_lead(self, lead_info: LeadInfo) -> Dict[str, Any]:
        """Cria um novo lead no CRM"""
        pass
    
    @abstractmethod
    def update_lead(self, lead_id: str, update_data: Dict) -> Dict[str, Any]:
        """Atualiza dados de um lead"""
        pass
    
    @abstractmethod
    def search_lead_by_phone(self, phone: str) -> Optional[Dict]:
        """Busca lead pelo telefone"""
        pass
    
    @abstractmethod
    def add_interaction(self, lead_id: str, message: str) -> Dict[str, Any]:
        """Adiciona interação/mensagem ao lead"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Testa conexão com o CRM"""
        pass