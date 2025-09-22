"""
Contact2Sale Service
Serviço para integração com CRM Contact2Sale com distribuição de leads
"""

import os
import logging
from typing import Dict, Optional, Any, List
from clients.contact2sale_client import Contact2SaleClient, LeadData, C2SResponse
from interfaces.clients import CRMClientInterface, LeadInfo
from services.lead_distributor_service import LeadDistributor

logger = logging.getLogger(__name__)


class Contact2SaleService(CRMClientInterface):
    """Serviço para integração com Contact2Sale CRM"""
    
    def __init__(self):
        # Carrega configurações do .env
        self.jwt_token = os.getenv("C2S_JWT_TOKEN")
        self.company_id = os.getenv("C2S_COMPANY_ID")
        self.seller_id = os.getenv("C2S_SELLER_ID")
        self.default_source = os.getenv("C2S_DEFAULT_SOURCE", "WhatsApp IA")
        self.use_distribution = os.getenv("C2S_USE_TEAM_DISTRIBUTION", "true").lower() == "true"
        
        if not self.jwt_token:
            raise ValueError("C2S_JWT_TOKEN não configurado no .env")
        
        # Inicializa distribuidor de leads
        if self.use_distribution:
            self.distributor = LeadDistributor()
            logger.info("Distribuição de leads entre equipes ATIVADA")
        else:
            self.distributor = None
            logger.info("Distribuição de leads DESATIVADA - usando company_id fixo")
        
        # Inicializa cliente (será atualizado dinamicamente se usar distribuição)
        self.client = Contact2SaleClient(
            jwt_token=self.jwt_token,
            company_id=self.company_id,
            seller_id=self.seller_id
        )
        
        # Cache para informações da empresa
        self._company_info = None
        self._seller_info = None
        
        logger.info("Contact2Sale service initialized")
    
    def _get_target_company_id(self, lead_info: LeadInfo) -> tuple[str, str]:
        """Determina qual company_id usar para o lead"""
        if self.use_distribution and self.distributor:
            # Converte LeadInfo para dict para o distribuidor
            lead_dict = {
                "name": lead_info.name,
                "phone": lead_info.phone,
                "email": lead_info.email,
                "message": lead_info.message,
                "source": lead_info.source,
                "interest": lead_info.interest,
                "budget": lead_info.budget,
                "location": lead_info.location
            }
            
            # Obtém próxima equipe
            team = self.distributor.get_next_team(lead_dict)
            return team.company_id, team.name
        else:
            # Usa company_id fixo configurado
            return self.company_id, "Evex Imóveis"
    
    def _create_client_for_team(self, company_id: str) -> Contact2SaleClient:
        """Cria cliente específico para uma equipe"""
        return Contact2SaleClient(
            jwt_token=self.jwt_token,
            company_id=company_id,
            seller_id=self.seller_id
        )
        """Garante que temos as informações da empresa"""
        if self._company_info is None:
            response = self.client.get_user_info()
            if response.success and response.data:
                self._company_info = response.data.get("data", {})
                
                # Atualiza company_id se não estava configurado
                if not self.company_id and "company_id" in self._company_info:
                    self.company_id = self._company_info["company_id"]
                    self.client.company_id = self.company_id
                    logger.info(f"Company ID obtido automaticamente: {self.company_id}")
    
    def _extract_lead_data(self, lead_info: LeadInfo) -> LeadData:
        """Converte LeadInfo para LeadData do C2S"""
        # Monta mensagem completa
        body_parts = []
        if lead_info.message:
            body_parts.append(lead_info.message)
        
        if lead_info.interest:
            body_parts.append(f"Interesse: {lead_info.interest}")
        
        if lead_info.budget:
            body_parts.append(f"Orçamento: {lead_info.budget}")
        
        if lead_info.location:
            body_parts.append(f"Localização: {lead_info.location}")
        
        body = "\n".join(body_parts) if body_parts else "Conversa iniciada via WhatsApp"
        
        return LeadData(
            name=lead_info.name or "Cliente WhatsApp",
            phone=lead_info.phone,
            email=lead_info.email,
            body=body,
            source=lead_info.source or self.default_source,
            description=f"Lead gerado automaticamente via {lead_info.source or self.default_source}",
            city=lead_info.location
        )
    
    def create_lead(self, lead_info: LeadInfo) -> Dict[str, Any]:
        """Cria um novo lead no Contact2Sale com distribuição automática"""
        try:
            # Determina equipe de destino
            target_company_id, team_name = self._get_target_company_id(lead_info)
            
            # Cria cliente específico para a equipe
            team_client = self._create_client_for_team(target_company_id)
            
            # Converte dados do lead
            lead_data = self._extract_lead_data(lead_info)
            
            # Cria lead no C2S
            response = team_client.create_lead(lead_data)
            
            if response.success:
                lead_id = None
                if response.data and "data" in response.data:
                    lead_id = response.data["data"].get("id")
                
                logger.info(f"✅ Lead criado no C2S para {team_name}: {lead_id} - {lead_info.name} ({lead_info.phone})")
                
                return {
                    "success": True,
                    "lead_id": lead_id,
                    "team_name": team_name,
                    "company_id": target_company_id,
                    "message": f"Lead criado com sucesso na equipe {team_name}",
                    "data": response.data
                }
            else:
                logger.error(f"❌ Erro ao criar lead no C2S: {response.error}")
                return {
                    "success": False,
                    "error": response.error,
                    "team_name": team_name,
                    "message": f"Falha ao criar lead na equipe {team_name}"
                }
                
        except Exception as e:
            logger.error(f"❌ Exceção ao criar lead: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erro interno ao criar lead"
            }
    
    def update_lead(self, lead_id: str, update_data: Dict) -> Dict[str, Any]:
        """Atualiza dados de um lead"""
        try:
            response = self.client.update_lead(lead_id, update_data)
            
            if response.success:
                logger.info(f"✅ Lead atualizado no C2S: {lead_id}")
                return {
                    "success": True,
                    "message": "Lead atualizado com sucesso",
                    "data": response.data
                }
            else:
                logger.error(f"❌ Erro ao atualizar lead no C2S: {response.error}")
                return {
                    "success": False,
                    "error": response.error,
                    "message": "Falha ao atualizar lead"
                }
                
        except Exception as e:
            logger.error(f"❌ Exceção ao atualizar lead: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erro interno ao atualizar lead"
            }
    
    def search_lead_by_phone(self, phone: str) -> Optional[Dict]:
        """Busca lead pelo telefone"""
        try:
            response = self.client.search_leads_by_phone(phone)
            
            if response.success and response.data:
                leads = response.data.get("data", [])
                if leads:
                    lead = leads[0]  # Retorna o primeiro lead encontrado
                    logger.info(f"✅ Lead encontrado no C2S: {lead.get('id')} - {phone}")
                    return lead
                else:
                    logger.info(f"ℹ️ Nenhum lead encontrado no C2S para: {phone}")
                    return None
            else:
                logger.warning(f"⚠️ Erro na busca por lead: {response.error}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Exceção ao buscar lead: {str(e)}")
            return None
    
    def add_interaction(self, lead_id: str, message: str) -> Dict[str, Any]:
        """Adiciona interação/mensagem ao lead"""
        try:
            response = self.client.add_message_to_lead(lead_id, message)
            
            if response.success:
                logger.info(f"✅ Mensagem adicionada ao lead {lead_id}")
                return {
                    "success": True,
                    "message": "Interação adicionada com sucesso",
                    "data": response.data
                }
            else:
                logger.error(f"❌ Erro ao adicionar mensagem: {response.error}")
                return {
                    "success": False,
                    "error": response.error,
                    "message": "Falha ao adicionar interação"
                }
                
        except Exception as e:
            logger.error(f"❌ Exceção ao adicionar interação: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erro interno ao adicionar interação"
            }
    
    def mark_lead_as_interacted(self, lead_id: str) -> Dict[str, Any]:
        """Marca lead como interagido"""
        try:
            response = self.client.mark_lead_as_interacted(lead_id)
            
            if response.success:
                logger.info(f"✅ Lead marcado como interagido: {lead_id}")
                return {
                    "success": True,
                    "message": "Lead marcado como interagido",
                    "data": response.data
                }
            else:
                logger.error(f"❌ Erro ao marcar lead como interagido: {response.error}")
                return {
                    "success": False,
                    "error": response.error,
                    "message": "Falha ao marcar lead como interagido"
                }
                
        except Exception as e:
            logger.error(f"❌ Exceção ao marcar lead: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erro interno"
            }
    
    def get_or_create_lead(self, lead_info: LeadInfo) -> Dict[str, Any]:
        """Busca lead existente ou cria um novo"""
        try:
            # Primeiro tenta encontrar lead existente
            existing_lead = self.search_lead_by_phone(lead_info.phone)
            
            if existing_lead:
                lead_id = existing_lead.get("id")
                logger.info(f"📋 Lead existente encontrado: {lead_id}")
                
                # Adiciona nova mensagem ao lead existente
                if lead_info.message:
                    self.add_interaction(lead_id, lead_info.message)
                
                # Marca como interagido
                self.mark_lead_as_interacted(lead_id)
                
                return {
                    "success": True,
                    "lead_id": lead_id,
                    "action": "updated",
                    "message": "Lead existente atualizado",
                    "data": existing_lead
                }
            else:
                # Cria novo lead
                result = self.create_lead(lead_info)
                if result["success"]:
                    result["action"] = "created"
                return result
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter/criar lead: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao processar lead"
            }
    
    def test_connection(self) -> bool:
        """Testa conexão com Contact2Sale"""
        try:
            response = self.client.test_connection()
            if response:
                self._ensure_company_info()
                logger.info("✅ Conexão com Contact2Sale validada")
                return True
            else:
                logger.error("❌ Falha na conexão com Contact2Sale")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao testar conexão: {str(e)}")
            return False
    
    def get_company_info(self) -> Optional[Dict]:
        """Retorna informações da empresa"""
        self._ensure_company_info()
        return self._company_info
    
    def get_sellers(self) -> Optional[List[Dict]]:
        """Lista vendedores da empresa"""
        try:
            response = self.client.get_sellers()
            if response.success and response.data:
                return response.data.get("data", [])
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao listar vendedores: {str(e)}")
            return None
    
    def get_distribution_stats(self, days: int = 7) -> Dict:
        """Retorna estatísticas de distribuição de leads"""
        if self.distributor:
            return self.distributor.get_distribution_stats(days)
        return {}
    
    def set_team_active(self, company_id: str, active: bool) -> bool:
        """Ativa/desativa uma equipe na distribuição"""
        if self.distributor:
            self.distributor.set_team_active(company_id, active)
            return True
        return False
    
    def get_teams(self) -> List[Dict]:
        """Lista todas as equipes disponíveis"""
        if self.distributor:
            return [
                {
                    "company_id": team.company_id,
                    "name": team.name,
                    "active": team.active,
                    "priority": team.priority
                }
                for team in self.distributor.teams
            ]
        return []
    
    def get_distribution_method(self) -> str:
        """Retorna método de distribuição atual"""
        if self.distributor:
            return self.distributor.distribution_method
        return "disabled"