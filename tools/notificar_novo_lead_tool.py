"""
Ferramenta para notificar e registrar novos leads com integração Contact2Sale
"""

import os
import re
import logging
from interfaces.tools.tool_interface import ITool
from interfaces.clients.ai_interface import IAI
from interfaces.clients.chat_interface import IChat
from services.contact2sale_service import Contact2SaleService
from interfaces.clients import LeadInfo
from utils.logger import logger, to_json_dump

class NotificarNovoLeadTool(ITool):
    name = "notificar_novo_lead"
    model = "gpt-4o-mini"
    
    def __init__(
        self,
        ai_client: IAI,
        chat_client: IChat,
    ):
        self.ai = ai_client
        self.chat = chat_client
        
        # Inicializa Contact2Sale se configurado
        self.c2s_enabled = bool(os.getenv("C2S_JWT_TOKEN"))
        if self.c2s_enabled:
            try:
                self.c2s_service = Contact2SaleService()
                logger.info("✅ Contact2Sale integração ativada")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar Contact2Sale: {e}")
                self.c2s_enabled = False
        else:
            logger.info("ℹ️ Contact2Sale não configurado - integração desabilitada")
    
    def _clean_phone(self, phone: str) -> str:
        """Limpa formatação do telefone"""
        return re.sub(r'[^\d]', '', phone)
    
    def _extract_name_from_phone(self, phone: str) -> str:
        """Extrai nome do contato se possível"""
        # Por enquanto retorna formato padrão
        # Pode ser melhorado para buscar nome real do contato
        clean_phone = self._clean_phone(phone)
        return f"Cliente {clean_phone[-4:]}"
    
    def _create_lead_info(self, arguments: dict) -> LeadInfo:
        """Converte argumentos da ferramenta para LeadInfo"""
        phone = self._clean_phone(arguments.get("telefone", ""))
        
        # Extrai informações dos argumentos
        nome = arguments.get("nome", "").strip()
        if not nome:
            nome = self._extract_name_from_phone(phone)
        
        projeto = arguments.get("projeto", "").strip()
        preco_medio = arguments.get("preco_medio", 0)
        
        # Monta mensagem de interesse
        interesse_parts = []
        if projeto:
            interesse_parts.append(f"Projeto: {projeto}")
        if preco_medio:
            interesse_parts.append(f"Orçamento: R$ {preco_medio:,.2f}")
        
        interesse = " | ".join(interesse_parts) if interesse_parts else "Interesse demonstrado via WhatsApp"
        
        return LeadInfo(
            name=nome,
            phone=phone,
            email=None,  # Não temos email no WhatsApp inicialmente
            message=f"Lead interessado em {projeto}" if projeto else "Novo contato via WhatsApp",
            source="WhatsApp IA - Avantti",
            interest=interesse,
            budget=f"R$ {preco_medio:,.2f}" if preco_medio else None,
            location=None  # Pode ser implementado depois
        )
    
    def _send_to_contact2sale(self, lead_info: LeadInfo) -> dict:
        """Envia lead para Contact2Sale"""
        if not self.c2s_enabled:
            return {
                "success": False,
                "message": "Contact2Sale não configurado",
                "service": "disabled"
            }
        
        try:
            # Testa conexão primeiro
            if not self.c2s_service.test_connection():
                return {
                    "success": False,
                    "message": "Falha na conexão com Contact2Sale",
                    "service": "connection_error"
                }
            
            # Cria ou atualiza lead
            result = self.c2s_service.get_or_create_lead(lead_info)
            
            return {
                "success": result.get("success", False),
                "message": result.get("message", ""),
                "lead_id": result.get("lead_id"),
                "action": result.get("action", "unknown"),
                "service": "contact2sale"
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na integração Contact2Sale: {str(e)}")
            return {
                "success": False,
                "message": f"Erro interno: {str(e)}",
                "service": "contact2sale_error"
            }
    
    def _send_notification_to_team(self, lead_info: LeadInfo, c2s_result: dict):
        """Envia notificação para equipe"""
        notification_phone = os.getenv("NOTIFICATION_WHATSAPP_NUMBER")
        if not notification_phone:
            logger.info("📱 Número de notificação não configurado")
            return
        
        try:
            # Monta mensagem de notificação
            status_emoji = "✅" if c2s_result.get("success") else "⚠️"
            action_text = {
                "created": "🆕 NOVO LEAD",
                "updated": "🔄 LEAD ATUALIZADO", 
                "unknown": "📋 LEAD PROCESSADO"
            }.get(c2s_result.get("action", "unknown"), "📋 LEAD PROCESSADO")
            
            message_parts = [
                f"{status_emoji} {action_text}",
                "",
                f"👤 Nome: {lead_info.name}",
                f"📱 Telefone: {lead_info.phone}",
            ]
            
            if lead_info.interest:
                message_parts.append(f"🎯 Interesse: {lead_info.interest}")
            
            if lead_info.budget:
                message_parts.append(f"💰 Orçamento: {lead_info.budget}")
            
            if lead_info.message:
                message_parts.append(f"💬 Mensagem: {lead_info.message}")
            
            # Status da integração
            message_parts.extend([
                "",
                f"🔗 Contact2Sale: {c2s_result.get('message', 'N/A')}"
            ])
            
            if c2s_result.get("lead_id"):
                message_parts.append(f"🆔 ID Lead: {c2s_result['lead_id']}")
            
            notification_message = "\n".join(message_parts)
            
            # Envia notificação
            self.chat.send_message(
                phone=notification_phone,
                message=notification_message
            )
            
            logger.info(f"📨 Notificação enviada para {notification_phone}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar notificação: {str(e)}")
    
    def _function_call_output(
        self,
        function_call_id: str,
        call_id: str,
        call_name: str,
        output: str,
        arguments: dict,
    ) -> tuple[list, str, str]:
        """Processa saída da function call"""
        fc_input, response = self.ai.function_call_output(
            function_call_id=function_call_id,
            call_id=call_id,
            call_name=call_name,
            output=output,
            arguments=arguments,
            model=self.model,
        )

        all_output = [
            content.get("text")
            for message in response.get("output", [])
            if message.get("status", "") == "completed"
            for content in message.get("content", [])
            if content.get("type") == "output_text"
        ]

        fc_msg_id = response["output"][0]["id"]
        all_output_in_text = ". ".join(all_output) or ""

        return (fc_input, fc_msg_id, all_output_in_text)
    
    async def execute(
        self,
        function_call_id: str,
        call_id: str,
        call_name: str,
        arguments: dict,
    ) -> list[dict]:
        """Executa a notificação de novo lead"""
        
        logger.info(
            f"[NOTIFICAR LEAD] Executando ferramenta: {self.name} | "
            f"function_call_id: {function_call_id} | arguments: {to_json_dump(arguments)}"
        )
        
        try:
            # Extrai dados do lead
            lead_info = self._create_lead_info(arguments)
            
            logger.info(f"[NOTIFICAR LEAD] Lead info criado: {to_json_dump(lead_info.__dict__)}")
            
            # Envia para Contact2Sale
            c2s_result = self._send_to_contact2sale(lead_info)
            
            logger.info(f"[NOTIFICAR LEAD] Resultado C2S: {to_json_dump(c2s_result)}")
            
            # Envia notificação para equipe
            self._send_notification_to_team(lead_info, c2s_result)
            
            # Monta resposta para o usuário
            if c2s_result.get("success"):
                success_msg = f"✅ Lead registrado com sucesso! "
                if c2s_result.get("action") == "created":
                    success_msg += "Novo lead criado no CRM."
                elif c2s_result.get("action") == "updated":
                    success_msg += "Lead existente atualizado."
                else:
                    success_msg += "Lead processado no CRM."
                
                function_output = success_msg
            else:
                function_output = (
                    "✅ Sua solicitação foi registrada! Nossa equipe entrará em contato em breve. "
                    f"(Nota técnica: {c2s_result.get('message', 'Sistema em manutenção')})"
                )
            
            # Processa function call output
            fc_input, fc_msg_id, final_output = self._function_call_output(
                function_call_id=function_call_id,
                call_id=call_id,
                call_name=call_name,
                output=function_output,
                arguments=arguments,
            )
            
            logger.info(
                f"[NOTIFICAR LEAD] Resposta final: {final_output}"
            )
            
            return [
                *fc_input,
                {
                    "id": fc_msg_id,
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": final_output,
                        }
                    ],
                },
            ]
            
        except Exception as e:
            logger.error(f"❌ [NOTIFICAR LEAD] Erro na execução: {str(e)}")
            
            # Retorna resposta de fallback
            error_output = (
                "✅ Sua solicitação foi registrada! Nossa equipe entrará em contato em breve."
            )
            
            fc_input, fc_msg_id, final_output = self._function_call_output(
                function_call_id=function_call_id,
                call_id=call_id,
                call_name=call_name,
                output=error_output,
                arguments=arguments,
            )
            
            return [
                *fc_input,
                {
                    "id": fc_msg_id,
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": final_output,
                        }
                    ],
                },
            ]