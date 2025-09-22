"""
Contact2Sale API Client
Cliente HTTP para integração com a API da Contact2Sale
"""

import requests
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class LeadData:
    """Estrutura de dados para criação de lead no C2S"""
    name: str
    phone: str
    email: Optional[str] = None
    body: str = ""
    source: str = "WhatsApp IA"
    description: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    price: Optional[str] = None
    city: Optional[str] = None
    neighbourhood: Optional[str] = None
    url: Optional[str] = None


@dataclass
class C2SResponse:
    """Resposta padronizada da API C2S"""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    status_code: Optional[int] = None


class Contact2SaleClient:
    """Cliente para integração com API Contact2Sale"""
    
    def __init__(self, jwt_token: str, company_id: Optional[str] = None, seller_id: Optional[str] = None):
        self.jwt_token = jwt_token
        self.company_id = company_id
        self.seller_id = seller_id
        self.base_url = "https://api.contact2sale.com/integration"
        
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        logger.info("Contact2Sale client initialized")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> C2SResponse:
        """Faz requisição HTTP para API C2S"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            logger.info(f"Making {method} request to: {url}")
            
            if method.upper() == "GET":
                response = self.session.get(url, params=data)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code >= 200 and response.status_code < 300:
                try:
                    response_data = response.json()
                    return C2SResponse(success=True, data=response_data, status_code=response.status_code)
                except ValueError:
                    return C2SResponse(success=True, data={"message": "Success"}, status_code=response.status_code)
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", error_msg)
                except ValueError:
                    error_msg = response.text or error_msg
                
                logger.error(f"API Error: {error_msg}")
                return C2SResponse(success=False, error=error_msg, status_code=response.status_code)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return C2SResponse(success=False, error=f"Request failed: {str(e)}")
    
    def get_user_info(self) -> C2SResponse:
        """Obtém informações do usuário e empresa"""
        return self._make_request("GET", "/me")
    
    def get_companies(self) -> C2SResponse:
        """Lista empresas do usuário"""
        return self._make_request("GET", "/me")
    
    def get_sellers(self) -> C2SResponse:
        """Lista vendedores da empresa"""
        return self._make_request("GET", "/sellers")
    
    def create_lead(self, lead_data: LeadData) -> C2SResponse:
        """Cria um novo lead no C2S"""
        payload = {
            "data": {
                "type": "lead",
                "attributes": {
                    "source": lead_data.source,
                    "name": lead_data.name,
                    "phone": lead_data.phone,
                    "body": lead_data.body
                }
            }
        }
        
        # Adiciona campos opcionais se fornecidos
        attributes = payload["data"]["attributes"]
        
        if lead_data.email:
            attributes["email"] = lead_data.email
        if lead_data.description:
            attributes["description"] = lead_data.description
        if lead_data.brand:
            attributes["brand"] = lead_data.brand
        if lead_data.model:
            attributes["model"] = lead_data.model
        if lead_data.price:
            attributes["price"] = lead_data.price
        if lead_data.city:
            attributes["city"] = lead_data.city
        if lead_data.neighbourhood:
            attributes["neighbourhood"] = lead_data.neighbourhood
        if lead_data.url:
            attributes["url"] = lead_data.url
        
        logger.info(f"Creating lead for: {lead_data.name} ({lead_data.phone})")
        return self._make_request("POST", "/leads", payload)
    
    def get_lead(self, lead_id: str) -> C2SResponse:
        """Obtém detalhes de um lead específico"""
        return self._make_request("GET", f"/leads/{lead_id}")
    
    def get_leads(self, filters: Optional[Dict] = None) -> C2SResponse:
        """Lista leads com filtros opcionais"""
        params = filters or {}
        return self._make_request("GET", "/leads", params)
    
    def update_lead(self, lead_id: str, update_data: Dict) -> C2SResponse:
        """Atualiza dados de um lead"""
        return self._make_request("PATCH", f"/leads/{lead_id}", update_data)
    
    def add_message_to_lead(self, lead_id: str, message: str) -> C2SResponse:
        """Adiciona mensagem a um lead"""
        payload = {"body": message}
        return self._make_request("POST", f"/leads/{lead_id}/create_message", payload)
    
    def mark_lead_as_interacted(self, lead_id: str) -> C2SResponse:
        """Marca lead como interagido"""
        return self._make_request("POST", f"/leads/{lead_id}/mark_as_interacted")
    
    def get_tags(self) -> C2SResponse:
        """Lista tags da empresa"""
        return self._make_request("GET", "/tags")
    
    def create_tag(self, tag_name: str, autofill: bool = False, instructions: str = "") -> C2SResponse:
        """Cria uma nova tag"""
        payload = {
            "tag": {
                "name": tag_name,
                "autofill": autofill,
                "instructions": instructions
            }
        }
        return self._make_request("POST", "/tags", payload)
    
    def add_tag_to_lead(self, lead_id: str, tag_id: str) -> C2SResponse:
        """Associa tag a um lead"""
        payload = {"tag_id": tag_id}
        return self._make_request("POST", f"/leads/{lead_id}/create_tag", payload)
    
    def search_leads_by_phone(self, phone: str) -> C2SResponse:
        """Busca leads pelo número de telefone"""
        # Remove formatação do telefone para busca
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        filters = {"phone": clean_phone}
        return self.get_leads(filters)
    
    def search_leads_by_email(self, email: str) -> C2SResponse:
        """Busca leads pelo email"""
        filters = {"email": email}
        return self.get_leads(filters)
    
    def test_connection(self) -> bool:
        """Testa conexão com API C2S"""
        response = self.get_user_info()
        if response.success:
            logger.info("✅ Conexão com Contact2Sale OK")
            return True
        else:
            logger.error(f"❌ Falha na conexão com Contact2Sale: {response.error}")
            return False