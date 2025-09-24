import requests
import os
import re
import time
import random
from utils.logger import logger, to_json_dump
from interfaces.clients.chat_interface import IChat


class ZAPIClient(IChat):
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
        """Remove todos os emojis da mensagem"""
        
        # Padrão para detectar e remover emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "😊🏢💰📍📞📌❌✅🤖⚠️📝💬🚀🎯🔥👨‍💻🏡💪🙌👏🎉💸💵💴📈📊🏠🏗️🌟⭐💯👍👎❤️💙💚🎁🎊🔔🔕📢📣📺📻📷📹🎵🎶🟢🟡🔴🟠⚡💡🔒🔓🔑🔐👥🔄"
            "]+", flags=re.UNICODE)
        
        # Remove emojis e limpa espaços extras
        cleaned = emoji_pattern.sub('', message)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
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
    
    def _finalize_message(self, sentences: list) -> str:
        """Finaliza uma mensagem juntando as sentenças"""
        
        if not sentences:
            return ""
            
        # Junta sentenças
        message = ' '.join(sentences)
        
        # Adiciona pontuação final se necessário
        if not re.search(r'[.!?]$', message.strip()):
            if self._is_question(message):
                message += '?'
            else:
                message += '.'
        
        return message.strip()

    def set_instance(self, instance: str, instance_key: str) -> None:
        self._instance_id = instance
        self._instance_token = instance_key

    def is_valid_message(self, **kwargs) -> bool:
        phone = self.get_phone(**kwargs)

        if not phone:
            return False

        return not kwargs["isGroup"] and kwargs["status"] == "RECEIVED"

    def is_image(self, **kwargs) -> bool:
        return "image" in kwargs and kwargs["image"].get("imageUrl") is not None

    def is_audio_message(self, **kwargs) -> bool:
        return "audio" in kwargs

    def is_file(self, **kwargs) -> bool:
        return (
            "document" in kwargs and kwargs["document"].get("documentUrl") is not None
        )

    def get_message(self, **kwargs) -> str:
        if "text" in kwargs:
            return str(kwargs["text"]["message"])

        return "Olá, Tenho interesse e queria mais informações, por favor."

    def get_phone(self, **kwargs) -> str:
        return self._resolve_phone(kwargs.get("phone", "")) or ""

    def _get_audio_url(self, **kwargs) -> str:
        try:
            url: str = kwargs["audio"]["audioUrl"]

            if not url:
                raise KeyError(
                    f"[Z-API] Erro ao recuperar url do audio: \n{to_json_dump(kwargs)}"
                )

            return kwargs["audio"]["audioUrl"]
        except KeyError as e:
            logger.error(e)
            raise e

    def get_audio_bytes(self, **kwargs) -> str:
        url = self._get_audio_url(**kwargs)
        return requests.get(url, timeout=15).content

    def get_image_url(self, **kwargs) -> str:
        return kwargs.get("image", {}).get("imageUrl", "")

    def get_image_caption(self, **kwargs) -> str:
        return kwargs.get("image", {}).get(
            "caption", "Responda o usuário conforme o contexto e a imagem enviada"
        )

    def get_file_url(self, **kwargs) -> str:
        return kwargs.get("document", {}).get("documentUrl", "")

    def get_file_caption(self, **kwargs) -> str:
        return kwargs.get("document", {}).get(
            "caption",
            "interprete o arquivo e responda o usuário conforme o contexto e o arquivo enviado",
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

    def send_button_list(self, phone: str, message: str, buttons: list) -> dict:
        url = self._resolve_url() + "/send-button-list"

        headers = {**self._headers, "Client-Token": self._client_token}

        # Remove emojis da mensagem dos botões
        clean_message = self._remove_emojis(message)

        payload = {
            "phone": self._resolve_phone(phone),
            "message": clean_message,
            "buttonList": {
                "buttons": buttons,
            },
            "delayTyping": 3,
        }

        try:
            if not buttons:
                logger.error(f"[Z-API] Lista de botões vazia: {phone}")
                return

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            logger.info(
                f"[Z-API] Lista de botões enviada para {phone}: \n{to_json_dump(response.json())}"
            )

        except Exception as e:
            logger.exception(
                f"[Z-API] ERRO - Falha ao enviar lista de botões: \n{to_json_dump(e)}"
            )
            raise e
