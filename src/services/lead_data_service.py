import logging
import json
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class LeadDataService:
    """Serviço para gerenciar dados de leads e variáveis dinâmicas"""
    
    def __init__(self):
        # Cache temporário de dados de leads (em produção, usar Redis/BD)
        self.leads_cache = {}
    
    def extrair_dados_lead_do_telefone(self, phone: str) -> Dict:
        """
        Extrai/busca dados do lead baseado no telefone
        Em produção, isso consultaria o banco de dados ou CRM
        """
        try:
            # Por enquanto, retorna dados padrão
            # No futuro, isso consultará Supabase/CRM para buscar:
            # - Nome do lead
            # - Email
            # - Empreendimento de interesse
            # - Faixa de valor
            # - ID do anúncio original
            
            if phone in self.leads_cache:
                return self.leads_cache[phone]
            
            # Dados padrão quando não há informações
            default_data = {
                'nome': '',  # Vazio para usar saudação neutra
                'telefone': phone,
                'email': '',
                'empreendimento': 'nosso empreendimento',
                'faixa_valor': 'sua faixa de interesse',
                'id_anuncio': '',
                'timestamp': datetime.now().isoformat()
            }
            
            return default_data
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados do lead {phone}: {e}")
            return self._get_default_lead_data(phone)
    
    def _get_default_lead_data(self, phone: str) -> Dict:
        """Dados padrão quando há erro"""
        return {
            'nome': '',
            'telefone': phone,
            'email': '',
            'empreendimento': 'nosso empreendimento',
            'faixa_valor': 'sua faixa de interesse', 
            'id_anuncio': '',
            'timestamp': datetime.now().isoformat()
        }
    
    def atualizar_dados_lead(self, phone: str, dados: Dict):
        """Atualiza dados do lead (ex: quando ele fala o nome)"""
        try:
            if phone not in self.leads_cache:
                self.leads_cache[phone] = self._get_default_lead_data(phone)
            
            # Atualiza campos específicos
            self.leads_cache[phone].update(dados)
            logger.info(f"Dados do lead {phone} atualizados: {list(dados.keys())}")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar dados do lead {phone}: {e}")
    
    def detectar_nome_na_mensagem(self, message: str, phone: str):
        """
        Detecta se o lead mencionou seu nome na mensagem
        Implementação básica - pode ser melhorada com NLP
        """
        try:
            message_lower = message.lower().strip()
            
            # Padrões comuns de apresentação
            patterns = [
                r'meu nome é ([\w\s]+)',
                r'me chamo ([\w\s]+)',
                r'sou (?:o|a) ([\w\s]+)',
                r'^([\w\s]+) aqui',
                r'aqui é (?:o|a) ([\w\s]+)'
            ]
            
            import re
            for pattern in patterns:
                match = re.search(pattern, message_lower)
                if match:
                    nome = match.group(1).strip().title()
                    # Filtra nomes muito curtos ou comuns
                    if len(nome) > 2 and nome not in ['Oi', 'Olá', 'Sim', 'Não']:
                        self.atualizar_dados_lead(phone, {'nome': nome})
                        logger.info(f"Nome detectado na conversa: {nome}")
                        return nome
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao detectar nome: {e}")
            return None
    
    def salvar_dados_lead_permanente(self, phone: str):
        """
        Salva dados do lead permanentemente (Supabase/BD)
        Para implementar no futuro
        """
        try:
            if phone in self.leads_cache:
                lead_data = self.leads_cache[phone]
                # TODO: Implementar salvamento no Supabase
                logger.info(f"Lead {phone} salvo: {lead_data}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erro ao salvar lead {phone}: {e}")
            return False
    
    def get_lead_data_for_prompt(self, phone: str) -> Dict:
        """Obtém dados formatados para uso no prompt"""
        try:
            lead_data = self.extrair_dados_lead_do_telefone(phone)
            
            # Formata dados para o prompt
            formatted_data = {
                'nome': lead_data.get('nome', ''),
                'telefone': lead_data.get('telefone', phone),
                'email': lead_data.get('email', ''),
                'empreendimento': lead_data.get('empreendimento', 'nosso empreendimento'),
                'faixa_valor': lead_data.get('faixa_valor', 'sua faixa de interesse'),
                'id_anuncio': lead_data.get('id_anuncio', ''),
                'timestamp': lead_data.get('timestamp', datetime.now().isoformat())
            }
            
            return formatted_data
            
        except Exception as e:
            logger.error(f"Erro ao obter dados para prompt: {e}")
            return self._get_default_lead_data(phone)