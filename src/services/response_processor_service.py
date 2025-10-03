#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Response Processor Service
=========================

Serviço dedicado para processar e limpar respostas da IA
garantindo 100% de assertividade antes do envio para Z-API.

Funcionalidades:
- Detecção automática de JSON
- Múltiplas camadas de extração
- Validação de conteúdo
- Fallbacks robustos
- Logging detalhado
"""

import re
import json
import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

class ResponseProcessorService:
    """
    Serviço para processar respostas da IA e garantir que apenas
    texto limpo seja enviado para o cliente via Z-API.
    """
    
    def __init__(self):
        self.stats = {
            "total_processed": 0,
            "json_detected": 0,
            "json_extracted": 0,
            "fallback_used": 0,
            "clean_responses": 0,
            "failed_extractions": 0
        }
    
    def processar_resposta(self, resposta_bruta: str, contexto: Dict[str, Any] = None) -> List[str]:
        """
        Processa uma resposta bruta da IA e retorna lista de mensagens limpas.
        
        Args:
            resposta_bruta: Resposta direta da OpenAI
            contexto: Contexto adicional para logging/debug
            
        Returns:
            Lista de mensagens limpas prontas para envio
        """
        try:
            self.stats["total_processed"] += 1
            
            if not resposta_bruta or not resposta_bruta.strip():
                logger.warning("Resposta vazia recebida")
                return self._get_resposta_padrao()
            
            resposta_bruta = resposta_bruta.strip()
            
            # ETAPA 1: Detecção de JSON
            if self._detectar_json(resposta_bruta):
                self.stats["json_detected"] += 1
                logger.info("JSON detectado na resposta - iniciando extração...")
                
                # ETAPA 2: Extração primária
                conteudo_extraido = self._extrair_reply_json(resposta_bruta)
                
                if conteudo_extraido:
                    self.stats["json_extracted"] += 1
                    logger.info(f"✅ JSON extraído com sucesso: {conteudo_extraido[:50]}...")
                    return self._quebrar_em_mensagens(conteudo_extraido)
                
                # ETAPA 3: Fallbacks progressivos
                logger.warning("Extração primária falhou - tentando fallbacks...")
                conteudo_fallback = self._tentar_fallbacks(resposta_bruta)
                
                if conteudo_fallback:
                    self.stats["fallback_used"] += 1
                    logger.info(f"✅ Fallback bem-sucedido: {conteudo_fallback[:50]}...")
                    return self._quebrar_em_mensagens(conteudo_fallback)
                
                # ETAPA 4: Última tentativa - limpeza agressiva
                logger.error("Todos os fallbacks falharam - tentando limpeza agressiva...")
                conteudo_limpo = self._limpeza_agressiva(resposta_bruta)
                
                if conteudo_limpo:
                    logger.info(f"✅ Limpeza agressiva funcionou: {conteudo_limpo[:50]}...")
                    return self._quebrar_em_mensagens(conteudo_limpo)
                
                # ETAPA 5: Falha total - resposta de emergência
                self.stats["failed_extractions"] += 1
                logger.error("❌ FALHA TOTAL na extração - usando resposta de emergência")
                return self._get_resposta_emergencia(contexto)
            
            else:
                # Resposta já está limpa
                self.stats["clean_responses"] += 1
                logger.info("Resposta já está limpa (sem JSON)")
                return self._quebrar_em_mensagens(resposta_bruta)
                
        except Exception as e:
            logger.error(f"Erro crítico no processamento: {e}")
            return self._get_resposta_emergencia(contexto)
    
    def _detectar_json(self, texto: str) -> bool:
        """Detecta se o texto contém estruturas JSON"""
        indicadores_json = [
            '{ "reply"',
            '{"reply"',
            '"reply":',
            '"c2s":',
            '"schedule":',
            '}",'
        ]
        
        texto_lower = texto.lower()
        return any(indicador.lower() in texto_lower for indicador in indicadores_json)
    
    def _extrair_reply_json(self, texto: str) -> Optional[str]:
        """Extração primária de reply do JSON"""
        try:
            # Limpa texto
            texto_limpo = re.sub(r'\s+', ' ', texto.strip())
            
            # Procura início do JSON
            start_patterns = ['{ "reply"', '{"reply"']
            start_pos = -1
            
            for pattern in start_patterns:
                pos = texto_limpo.find(pattern)
                if pos != -1:
                    start_pos = pos
                    break
            
            if start_pos == -1:
                return None
            
            # Encontra fim do JSON balanceando chaves
            bracket_count = 0
            end_pos = start_pos
            
            for i, char in enumerate(texto_limpo[start_pos:], start_pos):
                if char == '{':
                    bracket_count += 1
                elif char == '}':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_pos = i + 1
                        break
            
            # Extrai e parseia JSON
            json_text = texto_limpo[start_pos:end_pos]
            json_obj = json.loads(json_text)
            
            reply = json_obj.get('reply', '').strip()
            return reply if reply else None
            
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Falha na extração primária: {e}")
            return None
    
    def _tentar_fallbacks(self, texto: str) -> Optional[str]:
        """Múltiplos métodos de fallback para extração"""
        
        # Fallback 1: Regex simples
        patterns = [
            r'"reply":\s*"([^"]+)"',
            r'"reply"\s*:\s*"([^"]+)"', 
            r'reply":\s*"([^"]+)"',
            r'"reply":\s*\'([^\']+)\'',
            r'"reply":\s*"([^"]*)"'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, texto, re.IGNORECASE | re.DOTALL)
            if match:
                reply = match.group(1).strip()
                if reply and len(reply) > 3:
                    logger.info(f"Fallback regex funcionou: {pattern}")
                    return reply
        
        # Fallback 2: Extração antes de "c2s"
        if '"c2s"' in texto:
            antes_c2s = texto.split('"c2s"')[0]
            match = re.search(r'"([^"]{10,})"', antes_c2s)
            if match:
                possivel_reply = match.group(1).strip()
                if not possivel_reply.startswith('{') and len(possivel_reply) > 5:
                    logger.info("Fallback 'antes de c2s' funcionou")
                    return possivel_reply
        
        # Fallback 3: Primeira linha significativa
        linhas = texto.split('\n')
        for linha in linhas:
            linha = linha.strip().strip('"').strip("'")
            if (len(linha) > 10 and 
                not linha.startswith('{') and 
                not linha.startswith('[') and
                'reply' not in linha.lower() and
                'json' not in linha.lower()):
                logger.info("Fallback 'primeira linha' funcionou")
                return linha
        
        return None
    
    def _limpeza_agressiva(self, texto: str) -> Optional[str]:
        """Última tentativa - limpeza agressiva do texto"""
        try:
            # Remove caracteres JSON óbvios
            texto_limpo = texto
            
            # Remove estruturas JSON completas
            texto_limpo = re.sub(r'\{[^}]*"reply"[^}]*\}', '', texto_limpo, flags=re.DOTALL)
            texto_limpo = re.sub(r'\{[^}]*"c2s"[^}]*\}', '', texto_limpo, flags=re.DOTALL)
            
            # Remove marcadores JSON
            for marcador in ['"reply":', '"c2s":', '"schedule":', '{', '}', '[', ']']:
                texto_limpo = texto_limpo.replace(marcador, '')
            
            # Limpa espaços e quebras
            texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()
            
            # Remove aspas excessivas
            texto_limpo = texto_limpo.strip('"').strip("'")
            
            if len(texto_limpo) > 10 and self._validar_conteudo(texto_limpo):
                logger.info("Limpeza agressiva bem-sucedida")
                return texto_limpo
            
            return None
            
        except Exception as e:
            logger.error(f"Erro na limpeza agressiva: {e}")
            return None
    
    def _validar_conteudo(self, texto: str) -> bool:
        """Valida se o conteúdo extraído é adequado para envio"""
        if not texto or len(texto) < 3:
            return False
        
        # Verifica se não é apenas código/JSON
        indicadores_ruins = ['null', 'undefined', '{}', '[]', 'NaN']
        if any(ind in texto for ind in indicadores_ruins):
            return False
        
        # Verifica se tem pelo menos algumas letras
        letras = sum(1 for c in texto if c.isalpha())
        return letras >= 5
    
    def _quebrar_em_mensagens(self, texto: str) -> List[str]:
        """Quebra texto em mensagens naturais"""
        # Remove espaços extras
        texto = re.sub(r'\s+', ' ', texto.strip())
        
        # Quebra por pontos finais e perguntas
        sentences = re.split(r'([.!?]+\s+)', texto)
        
        mensagens = []
        mensagem_atual = ""
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i] if i < len(sentences) else ""
            punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
            
            frase_completa = sentence + punctuation
            
            if len(mensagem_atual + frase_completa) > 200 and mensagem_atual:
                mensagens.append(mensagem_atual.strip())
                mensagem_atual = frase_completa
            else:
                mensagem_atual += frase_completa
        
        if mensagem_atual.strip():
            mensagens.append(mensagem_atual.strip())
        
        return mensagens if mensagens else [texto]
    
    def _get_resposta_padrao(self) -> List[str]:
        """Resposta padrão para casos de resposta vazia"""
        return ["Olá! Obrigada pela mensagem. Nossa equipe retornará em breve."]
    
    def _get_resposta_emergencia(self, contexto: Dict[str, Any] = None) -> List[str]:
        """Resposta de emergência quando tudo falha"""
        if contexto and contexto.get('is_primeira_mensagem'):
            return ["Olá! Sou a Eliane da Evex Imóveis. Como posso ajudar você hoje?"]
        else:
            return ["Desculpe, ocorreu um erro técnico. Nossa equipe retornará em breve."]
    
    def get_stats(self) -> Dict[str, int]:
        """Retorna estatísticas do processamento"""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reseta estatísticas"""
        self.stats = {key: 0 for key in self.stats}
        logger.info("Estatísticas resetadas")

# Instância global para uso no sistema
response_processor = ResponseProcessorService()