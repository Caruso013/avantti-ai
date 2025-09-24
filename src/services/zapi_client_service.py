"""
ZAPIClient Service - Direct copy to avoid import path issues in deployment
"""
import requests
import os
import re
import time
import random
import logging

logger = logging.getLogger(__name__)

def to_json_dump(data):
    """Utility function for logging"""
    import json
    try:
        return json.dumps(data, indent=2, ensure_ascii=False)
    except:
        return str(data)


class ZAPIClientService:
    def __init__(self):
        self._base_url = os.getenv("ZAPI_BASE_URL")
        self._instance_id = os.getenv("ZAPI_INSTANCE")      # CORRIGIDO
        self._instance_token = os.getenv("ZAPI_TOKEN")      # CORRIGIDO
        self._client_token = os.getenv("ZAPI_CLIENT_TOKEN")
        self._headers = {"Content-Type": "application/json"}

    def __validate_message(self, message: str) -> bool:
        # Trata a mensagem
        message_clean = message.strip()

        # Verifica se a mensagem não está vazia
        if not message_clean:
            print("ERRO - Dados incompletos: A mensagem é obrigatória.")
            return False

        return True

    def __validate_cell_number(self, cell_number: str) -> bool:
        # Verifica se o celular não está vazio
        if not cell_number:
            logger.info(
                f"[Z-API] ERRO - Dados incompletos: O número de telefone é obrigatório. {cell_number}"
            )
            return False

        # Trata o telefone
        cell_number_clean = cell_number.strip()

        # Remove caracteres não numéricos
        cell_number_clean = re.sub(r"[^0-9]", "", cell_number_clean)

        # Verifica tamanho mínimo (11 dígitos = DDD + Celular)
        if len(cell_number_clean) < 11:
            logger.info(
                f"[Z-API] Telefone inválido. O número de celular deve conter no mínimo 11 dígitos (com DDD): {cell_number_clean}"
            )
            return False

        # Verifica tamanho máximo (13 dígitos = 11DDI + DDD + Celular)
        if len(cell_number_clean) > 13:
            print(
                f"[Z-API] Telefone inválido. O número de celular deve conter no máximo 13 dígitos (com DDI e DDD): {cell_number_clean}"
            )
            return False

        return True

    def _resolve_phone(self, phone: str) -> str:
        # Coloca o número o prefixo 9 caso o número tenha 8 dígitos
        if len(phone[4:]) == 8:
            phone = f"{phone[:4]}9{phone[4:]}"

        # Adiciona o DDI 55 caso não tenha
        if not phone.startswith("55") and len(phone) == 11:
            return f"55{phone}"

        return phone

    def __resolve_message(self, message: str) -> list[str]:
        """
        Quebra mensagens de forma inteligente:
        - Máximo 3 linhas por mensagem
        - Remove confirmações corriqueiras  
        - Separa perguntas em mensagens diferentes
        - Cria fluxo mais natural e dinâmico
        """
        
        # Remove confirmações corriqueiras e palavras desnecessárias
        message = self._clean_common_confirmations(message)
        
        if not message.strip():
            return ["Olá! Como posso ajudar você?"]
        
        # Quebra inicial por pontos e interrogações, mantendo contexto
        sentences = self._smart_sentence_split(message)
        
        # Agrupa sentenças em mensagens inteligentes
        messages = self._group_sentences_smartly(sentences)
        
        # Remove emojis de todas as mensagens
        messages = [self._remove_emojis(msg) for msg in messages]
        
        return [msg for msg in messages if msg.strip()]
    
    def _smart_sentence_split(self, message: str) -> list[str]:
        """Quebra texto de forma mais inteligente"""
        
        # Quebra por pontos finais, mas preserva contexto
        parts = re.split(r'\.(?:\s+|$)', message)
        sentences = []
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            # Se contém interrogação, quebra também por ela
            if '?' in part:
                subparts = re.split(r'\?(?:\s+|$)', part)
                for subpart in subparts:
                    subpart = subpart.strip()
                    if subpart:
                        # Adiciona ? se é pergunta
                        if self._is_question(subpart):
                            sentences.append(subpart + '?')
                        else:
                            sentences.append(subpart)
            else:
                # Adiciona ponto se necessário
                if part and not part.endswith(('.', '!', '?')):
                    part += '.'
                sentences.append(part)
        
        return [s for s in sentences if s.strip()]
    
    def _group_sentences_smartly(self, sentences: list) -> list[str]:
        """Agrupa sentenças de forma inteligente"""
        
        if not sentences:
            return []
        
        messages = []
        current_group = []
        current_length = 0
        
        for sentence in sentences:
            is_question = self._is_question(sentence)
            sentence_length = len(sentence)
            
            # Perguntas sempre ficam sozinhas ou iniciam novo grupo
            if is_question:
                # Finaliza grupo atual se existe
                if current_group:
                    messages.append(' '.join(current_group))
                    current_group = []
                    current_length = 0
                
                # Pergunta vai sozinha
                messages.append(sentence)
            else:
                # Se adicionar esta sentença vai ultrapassar ~180 chars (3 linhas), quebra
                if current_length + sentence_length > 180 and current_group:
                    messages.append(' '.join(current_group))
                    current_group = [sentence]
                    current_length = sentence_length
                else:
                    current_group.append(sentence)
                    current_length += sentence_length
        
        # Adiciona último grupo se existe
        if current_group:
            messages.append(' '.join(current_group))
        
        return messages
    
    def _clean_common_confirmations(self, message: str) -> str:
        """Remove confirmações corriqueiras e palavras desnecessárias"""
        
        # Padrões de confirmações corriqueiras para remover
        patterns_to_remove = [
            r'Perfeito!\s*',
            r'Excelente!\s*', 
            r'Ótimo!\s*',
            r'Entendi[,.]?\s*',
            r'Certo[,.]?\s*',
            r'Tudo bem[,.]?\s*',
            r'Obrigad[ao] pela informação[,.]?\s*',
            r'Vou te passar\s*',
            r'Deixe-me\s*',
            r'Vamos\s+verificar\s*',
            r'perfeitamente!\s*',
        ]
        
        cleaned = message
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Remove espaços extras e caracteres órfãos
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = re.sub(r'^[,.\s]+', '', cleaned)  # Remove pontuação no início
        
        return cleaned
    
    def _remove_emojis(self, message: str) -> str:
        """Remove todos os emojis da mensagem usando múltiplos padrões"""
        
        # Padrão 1: Remove emojis usando múltiplos padrões
        message = re.sub(r'[\U0001F600-\U0001F64F]', '', message)  # emoticons
        message = re.sub(r'[\U0001F300-\U0001F5FF]', '', message)  # symbols & pictographs
        message = re.sub(r'[\U0001F680-\U0001F6FF]', '', message)  # transport & map symbols
        message = re.sub(r'[\U0001F1E0-\U0001F1FF]', '', message)  # flags (iOS)
        message = re.sub(r'[\U00002702-\U000027B0]', '', message)
        message = re.sub(r'[\U000024C2-\U0001F251]', '', message)
        message = re.sub(r'[\U0001F900-\U0001F9FF]', '', message)  # Supplemental Symbols and Pictographs
        message = re.sub(r'[\U0001FA70-\U0001FAFF]', '', message)  # Symbols and Pictographs Extended-A
        
        # Padrão 2: Remove símbolos específicos que podem passar
        symbols_to_remove = ['😊', '😀', '😁', '😂', '🤣', '😃', '😄', '😅', '😆', '😉', '😊', 
                            '😋', '😎', '😍', '😘', '🥰', '😗', '😙', '😚', '🤪', '😜', '😝',
                            '🤑', '🤗', '🤭', '🤫', '🤔', '🤐', '🤨', '😐', '😑', '😶', '😏',
                            '😒', '🙄', '😬', '🤥', '😔', '😪', '🤤', '😴', '😷', '🤒', '🤕',
                            '🤢', '🤮', '🤧', '🥵', '🥶', '🥴', '😵', '🤯', '🤠', '🥳', '😎',
                            '🧐', '😕', '😟', '🙁', '☹️', '😮', '😯', '😲', '😳', '🥺', '😦',
                            '😧', '😨', '😰', '😥', '😢', '😭', '😱', '😖', '😣', '😞', '😓',
                            '😩', '😫', '🥱', '😤', '😡', '😠', '🤬', '😈', '👿', '💀', '☠️',
                            '💩', '🤡', '👹', '👺', '👻', '👽', '👾', '🤖', '🎃', '😺', '😸',
                            '🏢', '💰', '📍', '📞', '📌', '❌', '✅', '⚠️', '📝', '💬', '🚀',
                            '🎯', '🔥', '👨‍💻', '🏡', '💪', '🙌', '👏', '🎉', '💸', '💵', '💴',
                            '📈', '📊', '🏠', '🏗️', '🌟', '⭐', '💯', '👍', '👎', '❤️', '💙',
                            '💚', '🎁', '🎊', '🔔', '🔕', '📢', '📣', '📺', '📻', '📷', '📹',
                            '🎵', '🎶', '🟢', '🟡', '🔴', '🟠', '⚡', '💡', '🔒', '🔓', '🔑',
                            '🔐', '👥', '🔄', '▶️', '🧪', '🧹', '📱', '🤖']
        
        for symbol in symbols_to_remove:
            message = message.replace(symbol, '')
        
        # Remove espaços extras e limpa
        message = re.sub(r'\s+', ' ', message).strip()
        return message
    
    def _is_question(self, sentence: str) -> bool:
        """Identifica se uma sentença é uma pergunta"""
        
        # Se termina com ? é pergunta
        if sentence.strip().endswith('?'):
            return True
        
        # Palavras que indicam pergunta
        question_words = [
            'como', 'quando', 'onde', 'qual', 'quais', 'quanto', 'quantos', 'quantas',
            'você', 'vocês', 'gostaria', 'gostam', 'pretende', 'pretendem', 
            'tem ', 'têm', 'possui', 'possuem', 'aceita', 'aceitam',
            'quer', 'querem', 'deseja', 'desejam', 'pode', 'podem',
            'seria', 'teria', 'haveria', 'estaria', 'gostaria'
        ]
        
        sentence_lower = sentence.lower()
        
        # Se contém palavras de pergunta no início ou meio da frase
        return any(
            sentence_lower.startswith(word + ' ') or 
            ' ' + word + ' ' in sentence_lower or
            sentence_lower.startswith(word + ',') or
            ' ' + word + ',' in sentence_lower
            for word in question_words
        )

    def _resolve_url(self) -> str:
        return f"{self._base_url}/instances/{self._instance_id}/token/{self._instance_token}"

    def send_message(self, phone: str, message: str) -> bool:
        if not self.__validate_message(message) or not self.__validate_cell_number(
            phone
        ):
            logger.error(
                f"[Z-API] Dados incompletos: mensagem: {message}, telefone: {phone}"
            )
            return False

        url = self._resolve_url() + "/send-text"

        headers = {**self._headers, "Client-Token": self._client_token}

        payload = {"phone": self._resolve_phone(phone), "delayTyping": 3}

        try:
            messages = self.__resolve_message(message)

            for message in messages:
                if not message:
                    continue

                msg = message[:-1] if message.endswith(".") else message
                payload["message"] = msg
                response = requests.post(url, json=payload, headers=headers)

                logger.info(
                    f"[Z-API] Enviando mensagem para {phone}: {msg!r} payload:\n{to_json_dump(payload)} \nresponse:{to_json_dump(response.json())}"
                )

                response.raise_for_status()

                pause = random.randint(2, 3)
                time.sleep(pause)

            return True
        except Exception as e:
            logger.exception(
                f"[Z-API] ERRO - Falha ao enviar mensagem: \n{to_json_dump(e)}"
            )
            raise e