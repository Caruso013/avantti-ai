import os
import requests
import logging

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        self.headers = {
            'apikey': self.key,
            'Authorization': f"Bearer {self.key}",
            'Content-Type': 'application/json'
        }
    
    def buscar_contexto_conversa(self, phone):
        """Busca histórico no Supabase"""
        try:
            url = f"{self.url}/rest/v1/conversations"
            params = {
                'phone': f'eq.{phone}',
                'order': 'created_at.desc',
                'limit': '10'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                mensagens = response.json()
                contexto = []
                for msg in reversed(mensagens):  # Ordem cronológica
                    if msg.get('text'):
                        # Formato compatível com OpenAIService
                        contexto.append({
                            "sender": msg.get('role', 'user'),  # 'user' ou 'assistant'
                            "message": msg.get('text'),          # Conteúdo da mensagem
                            "timestamp": msg.get('created_at')   # Para debug
                        })
                logger.info(f"✅ Contexto carregado: {len(contexto)} mensagens para {phone}")
                
                # Log do contexto para debug
                for i, ctx in enumerate(contexto):
                    logger.debug(f"Contexto[{i}]: {ctx['sender']} - {ctx['message'][:30]}...")
                
                return contexto
            else:
                logger.warning(f"Erro ao buscar contexto: {response.status_code}")
                return []
            return []
        except Exception as e:
            logger.error(f"Erro ao buscar contexto: {e}")
            return []

    def salvar_mensagem(self, phone, message, role):
        """Salva mensagem no Supabase"""
        try:
            url = f"{self.url}/rest/v1/conversations"
            data = {
                'phone': phone,
                'role': role,  # 'user' ou 'assistant'
                'text': message
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code == 201:
                logger.info(f"Mensagem salva: {role} - {phone}")
                return True
            logger.error(f"Erro Supabase: {response.status_code}")
            return False
        except Exception as e:
            logger.error(f"Erro ao salvar mensagem: {e}")
            return False
    
    def verificar_ultima_apresentacao(self, phone):
        """Verifica quando foi a última apresentação da IA para este telefone"""
        try:
            from datetime import datetime, timedelta, timezone
            
            # Busca a última mensagem da IA que contém apresentação
            url = f"{self.url}/rest/v1/conversations"
            params = {
                'phone': f'eq.{phone}',
                'role': 'eq.assistant',
                'text': 'ilike.%Eliane, da Evex Imóveis%',
                'order': 'created_at.desc',
                'limit': '1'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    ultima_apresentacao = data[0]
                    timestamp_str = ultima_apresentacao.get('created_at')
                    
                    if timestamp_str:
                        # Parse timestamp (ISO format com timezone)
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        agora = datetime.now(timezone.utc)
                        
                        diferenca = agora - timestamp
                        horas_desde_apresentacao = diferenca.total_seconds() / 3600
                        
                        logger.info(f"⏰ Última apresentação foi há {horas_desde_apresentacao:.1f} horas para {phone}")
                        
                        return {
                            'teve_apresentacao': True,
                            'timestamp': timestamp,
                            'horas_desde': horas_desde_apresentacao,
                            'precisa_reapresentar': horas_desde_apresentacao > 12
                        }
                
                logger.info(f"✨ Primeira apresentação para {phone}")
                return {
                    'teve_apresentacao': False,
                    'precisa_reapresentar': True
                }
            else:
                logger.error(f"Erro ao verificar última apresentação: {response.text}")
                return {'teve_apresentacao': False, 'precisa_reapresentar': True}
                
        except Exception as e:
            logger.error(f"Erro ao verificar última apresentação: {e}")
            return {'teve_apresentacao': False, 'precisa_reapresentar': True}