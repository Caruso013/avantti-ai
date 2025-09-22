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
                for msg in reversed(mensagens):
                    if msg.get('text'):
                        contexto.append({
                            "role": msg.get('role', 'user'),
                            "content": msg.get('text')
                        })
                logger.info(f"Contexto carregado: {len(contexto)} mensagens para {phone}")
                return contexto
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