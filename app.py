from flask import Flask, request, jsonify
import os
import sys
import threading
import time
from queue import Queue
from datetime import datetime
from dotenv import load_dotenv
import logging

# Versão da aplicação
AVANTTI_VERSION = "FINAL"
AVANTTI_CODENAME = "AVANTTI AI - ELIANE VERSÃO FINAL!"

# Adiciona o diretório atual ao PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Imports dos novos módulos
from src.handlers.message_handler import MessageHandler
from src.utils.config import ConfigManager

# Configuração de logging melhorado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()
app = Flask(__name__)

# Validação de configurações
config_manager = ConfigManager()
if not config_manager.validate_config():
    logger.error("Configuracoes invalidas. Verifique as variaveis de ambiente.")
    exit(1)

print("============================================================")
print("🚀 AVANTTI AI - ELIANE VERSÃO FINAL! 🚀")
print("============================================================")
print("🤖 Sistema de buffer ativo - Debounce: 5 segundos")
print("⏰ Timer contínuo: ✅ Ativo (cancelável)")
print("📦 Consolidação de mensagens: ✅ Ativo")
print("📞 Function calling: ✅ Ativo")
print("🎯 Registro automático de leads: ✅ Ativo")
print("============================================================")
print("🤖 Sistema de buffer ativo - Debounce: 5 segundos")
print("📞 Function calling: ✅ Ativo")  
print("🎯 Registro automático de leads: ✅ Ativo")
print("============================================================")

# Sistema de filas melhorado com debounce contínuo
message_queues = {}
processing_lock = threading.Lock()
active_processors = set()
debounce_timers = {}  # Timers para debounce por telefone

# Handler principal
message_handler = MessageHandler()

# Métricas simples
metrics = {
    'messages_processed': 0,
    'audio_transcriptions': 0,
    'errors': 0,
    'uptime_start': datetime.now()
}

def get_queue_for_phone(phone):
    """Obtém fila do telefone"""
    if phone not in message_queues:
        message_queues[phone] = Queue()
    return message_queues[phone]

def process_message_queue(phone):
    """Processa fila de mensagens consolidadas (já após debounce)"""
    queue = get_queue_for_phone(phone)
    
    logger.info(f"🔄 Processando fila para {phone} - {queue.qsize()} mensagens acumuladas")
    
    # Coleta todas as mensagens da fila (sem esperar - já foi feito o debounce)
    messages_to_process = []
    while not queue.empty():
        try:
            message_data = queue.get(timeout=0.1)
            messages_to_process.append(message_data)
            queue.task_done()
        except:
            break
    
    if not messages_to_process:
        logger.info(f"❌ Nenhuma mensagem para processar para {phone}")
        return
    
    # 🔍 VERIFICA SE HÁ MENSAGENS DE ÁUDIO
    audio_messages = [msg for msg in messages_to_process if msg.get('type') == 'audio']
    
    if audio_messages:
        # 🎵 PRIORIZA ÁUDIO - processa apenas a primeira mensagem de áudio
        logger.info(f"🎵 Detectado {len(audio_messages)} mensagem(ns) de áudio - processando áudio")
        audio_data = audio_messages[0]  # Processa apenas a primeira
        
        try:
            metrics['audio_transcriptions'] += 1
            
            # Cria dados para o handler de áudio
            handler_data = {
                'phone': phone,
                'message': {
                    'audioUrl': audio_data.get('message', '')
                }
            }
            message_handler.processar_mensagem_audio(handler_data)
            
            logger.info(f"✅ Áudio processado com sucesso para {phone}")
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento de áudio: {e}")
            metrics['errors'] += 1
        
        logger.info(f"🏁 Processamento de áudio concluído para {phone}")
        return
    
    # 🎯 CONSOLIDA MENSAGENS DE TEXTO/IMAGEM/VIDEO
    logger.info(f"📝 Consolidando {len(messages_to_process)} mensagens em uma resposta única")
    
    # Extrai texto de todas as mensagens
    consolidated_messages = []
    for i, msg in enumerate(messages_to_process):
        text = msg.get('message', '')
        if text and text.strip():
            consolidated_messages.append(text.strip())
            logger.debug(f"  Msg [{i+1}]: '{text[:50]}...'")
    
    # Junta todas as mensagens com separador
    consolidated_text = " | ".join(consolidated_messages)
    
    logger.info(f"🎯 Mensagem consolidada: '{consolidated_text[:100]}...'")
    logger.info(f"📦 Total de {len(consolidated_messages)} mensagens consolidadas")
    
    try:
        # Usa a mensagem consolidada
        message_text = consolidated_text
        message_type = 'text'  # Sempre texto consolidado
        
        logger.info(f"🔥 Processando mensagem consolidada: '{message_text[:50]}...' de {phone}")
        
        if message_text:
            metrics['messages_processed'] += 1
            
            # Cria dados para o handler
            handler_data = {
                'phone': phone,
                'message': {'text': message_text}
            }
            message_handler.processar_mensagem_texto(handler_data)
        
        logger.info(f"✅ Mensagem consolidada processada com sucesso para {phone}")
        
    except Exception as e:
        logger.error(f"❌ Erro no processamento da mensagem consolidada: {e}")
        metrics['errors'] += 1
    
    logger.info(f"🏁 Processamento concluído para {phone}")

def start_queue_processor(phone):
    """Inicia processador da fila com debounce contínuo"""
    global active_processors, debounce_timers
    
    with processing_lock:
        # Se já existe um timer, cancela o anterior
        if phone in debounce_timers:
            debounce_timers[phone].cancel()
            logger.info(f"🔄 Timer anterior cancelado para {phone} - nova mensagem recebida")
        
        # Se já tem processador ativo, apenas redefine o timer
        if phone in active_processors:
            logger.info(f"⏱️ Processador ativo para {phone} - redefinindo timer de 5s")
        else:
            logger.info(f"🚀 Iniciando novo processador para {phone}")
            active_processors.add(phone)
        
        # Cria novo timer de 5 segundos
        timer = threading.Timer(5.0, lambda: _execute_processor(phone))
        debounce_timers[phone] = timer
        timer.start()
        
        logger.info(f"⏰ Timer de 5s iniciado para {phone}")

def _execute_processor(phone):
    """Executa o processamento após o debounce"""
    try:
        logger.info(f"🎯 Executando processamento para {phone} após debounce")
        process_message_queue(phone)
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
    finally:
        with processing_lock:
            active_processors.discard(phone)
            debounce_timers.pop(phone, None)
            logger.info(f"🏁 Processador finalizado para {phone}")

def extract_message_content(payload):
    """Extrai conteúdo da mensagem dependendo do tipo"""
    try:
        if not isinstance(payload, dict):
            return None, 'invalid'
        
        # Verifica se é mensagem de áudio (múltiplas possibilidades)
        if payload.get('audio') or payload.get('message', {}).get('audio'):
            audio_obj = payload.get('audio') or payload.get('message', {}).get('audio', {})
            if isinstance(audio_obj, dict):
                audio_url = audio_obj.get('audioUrl') or audio_obj.get('url')
                if audio_url and audio_url.startswith(('http://', 'https://')):
                    logger.info(f"🎵 Áudio detectado: {audio_url[:50]}...")
                    return audio_url, 'audio'
        
        # Verifica se a mensagem contém uma URL que parece ser de áudio
        message_obj = payload.get('message', {})
        if isinstance(message_obj, dict):
            conversation = message_obj.get('conversation', '').strip()
            if conversation and conversation.startswith(('http://', 'https://')) and ('audio' in conversation.lower() or 'temp-file' in conversation.lower()):
                logger.info(f"🎵 Áudio detectado via URL na conversa: {conversation[:50]}...")
                return conversation, 'audio'
        
        # Mensagem de texto
        if payload.get('text') or payload.get('message', {}).get('conversation'):
            text_obj = payload.get('text') or payload.get('message', {}).get('conversation', '')
            if isinstance(text_obj, dict):
                message = text_obj.get('message', '').strip()
                if len(message) > 4000:
                    message = message[:4000] + "... [truncado]"
                return message, 'text'
            elif isinstance(text_obj, str):
                message = text_obj.strip()
                if len(message) > 4000:
                    message = message[:4000] + "... [truncado]"
                return message, 'text'
        
        # Mensagem de imagem com caption
        elif payload.get('image'):
            image_obj = payload.get('image', {})
            if isinstance(image_obj, dict):
                caption = image_obj.get('caption', '').strip()[:1000]
                if caption:
                    return f"[Imagem] {caption}", 'image'
                else:
                    return "[Imagem recebida] Como posso ajudar?", 'image'
        
        # Mensagem de vídeo com caption  
        elif payload.get('video'):
            video_obj = payload.get('video', {})
            if isinstance(video_obj, dict):
                caption = video_obj.get('caption', '').strip()[:1000]
                if caption:
                    return f"[Vídeo] {caption}", 'video'
                else:
                    return "[Vídeo recebido] Como posso ajudar?", 'video'
        
        return None, 'unknown'
        
    except Exception as e:
        logger.error(f"Erro na extração de conteúdo: {e}")
        return None, 'error'

@app.route("/", methods=["GET"])
def health_check():
    active_count = len(active_processors)
    queue_count = sum(q.qsize() for q in message_queues.values())
    uptime = datetime.now() - metrics['uptime_start']
    
    return jsonify({
        "status": "ok", 
        "message": "Avantti AI - Eliane V2 funcionando!",
        "active_processors": active_count,
        "queued_messages": queue_count,
        "total_phones": len(message_queues),
        "metrics": {
            "messages_processed": metrics['messages_processed'],
            "audio_transcriptions": metrics['audio_transcriptions'],
            "errors": metrics['errors'],
            "uptime_seconds": int(uptime.total_seconds())
        },
        "version": "2.0",
        "features": ["audio_transcription", "queue_system", "context_memory"]
    }), 200

@app.route("/metrics", methods=["GET"])
def metrics_endpoint():
    """Endpoint dedicado para métricas detalhadas"""
    uptime = datetime.now() - metrics['uptime_start']
    
    return jsonify({
        "uptime_seconds": int(uptime.total_seconds()),
        "messages_processed": metrics['messages_processed'],
        "audio_transcriptions": metrics['audio_transcriptions'],
        "errors": metrics['errors'],
        "active_processors": len(active_processors),
        "total_queues": len(message_queues),
        "queued_messages": sum(q.qsize() for q in message_queues.values()),
        "queue_details": {
            phone: queue.qsize() 
            for phone, queue in message_queues.items()
        }
    }), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "avantti-ai-eliane-v4"}), 200

@app.route("/version", methods=["GET"])
def version():
    """Endpoint para verificar versão e configurações da aplicação"""
    c2s_enabled = bool(os.getenv("C2S_JWT_TOKEN"))
    distribution_enabled = os.getenv("C2S_USE_TEAM_DISTRIBUTION", "false").lower() == "true"
    
    version_info = {
        "version": AVANTTI_VERSION,
        "codename": AVANTTI_CODENAME,
        "service": "avantti-ai-evex",
        "client": "Evex Imóveis",
        "uptime": str(datetime.now() - metrics['uptime_start']),
        "features": {
            "contact2sale": c2s_enabled,
            "lead_distribution": distribution_enabled,
            "message_splitting": True,
            "whatsapp_api": os.getenv("WHATSAPP_API", "evolution"),
            "distribution_method": os.getenv("C2S_DISTRIBUTION_METHOD", "round_robin") if distribution_enabled else None
        },
        "stats": {
            "messages_processed": metrics['messages_processed'],
            "errors": metrics['errors'],
            "active_teams": 11 if distribution_enabled else 1
        },
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify(version_info), 200

@app.route("/update-prompt", methods=["POST"])
def update_prompt():
    """Endpoint para atualizar o prompt da IA"""
    try:
        data = request.get_json()
        new_prompt = data.get('prompt', '').strip()
        
        if not new_prompt:
            return jsonify({"status": "error", "message": "Prompt não pode estar vazio"}), 400
        
        if len(new_prompt) > 10000:  # Limite de tamanho
            return jsonify({"status": "error", "message": "Prompt muito longo (máx 10.000 chars)"}), 400
        
        # Atualiza via handler
        success = message_handler.atualizar_prompt(new_prompt)
        
        if success:
            logger.info("Prompt atualizado com sucesso")
            return jsonify({
                "status": "success", 
                "message": "Prompt atualizado com sucesso",
                "prompt_length": len(new_prompt)
            }), 200
        else:
            return jsonify({"status": "error", "message": "Falha ao atualizar prompt"}), 500
            
    except Exception as e:
        logger.error(f"Erro ao atualizar prompt: {e}")
        return jsonify({"status": "error", "message": "Erro interno"}), 500

@app.route("/set-lead-data", methods=["POST"])
def set_lead_data():
    """Endpoint para configurar dados de um lead"""
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()
        lead_info = data.get('lead_data', {})
        
        if not phone:
            return jsonify({"status": "error", "message": "Telefone obrigatório"}), 400
        
        # Valida campos permitidos
        allowed_fields = ['nome', 'email', 'empreendimento', 'faixa_valor', 'id_anuncio']
        filtered_data = {k: v for k, v in lead_info.items() if k in allowed_fields}
        
        if not filtered_data:
            return jsonify({"status": "error", "message": "Nenhum dado válido fornecido"}), 400
        
        # Atualiza dados via handler
        message_handler.lead_data_service.atualizar_dados_lead(phone, filtered_data)
        
        logger.info(f"Dados do lead {phone} configurados: {list(filtered_data.keys())}")
        return jsonify({
            "status": "success",
            "message": f"Dados do lead {phone} atualizados",
            "updated_fields": list(filtered_data.keys())
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao configurar dados do lead: {e}")
        return jsonify({"status": "error", "message": "Erro interno"}), 500

@app.route("/get-lead-data/<phone>", methods=["GET"])
def get_lead_data(phone):
    """Endpoint para consultar dados de um lead"""
    try:
        if not phone:
            return jsonify({"status": "error", "message": "Telefone obrigatório"}), 400
        
        lead_data = message_handler.lead_data_service.get_lead_data_for_prompt(phone)
        
        return jsonify({
            "status": "success",
            "phone": phone,
            "lead_data": lead_data
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao buscar dados do lead: {e}")
        return jsonify({"status": "error", "message": "Erro interno"}), 500

@app.route("/message_receive", methods=["POST"])
def message_receive():
    """Endpoint principal com suporte a áudio"""
    try:
        payload = request.get_json(silent=True) or {}
        
        # Validação de IP (opcional - descomente se necessário)
        # client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        # if not validate_client_ip(client_ip):
        #     return jsonify({"status": "forbidden"}), 403
        
        phone = payload.get('phone', '').strip()
        
        # Validação do telefone
        if not phone or len(phone) < 10 or not phone.replace('+', '').isdigit():
            return jsonify({"status": "ignored", "reason": "invalid_phone"}), 200
        
        if payload.get('fromMe', False):
            return jsonify({"status": "ignored", "reason": "from_bot"}), 200
        
        # Rate limiting simples por telefone
        current_time = time.time()
        if phone in message_queues:
            queue = message_queues[phone]
            if queue.qsize() > 10:  # Máximo 10 mensagens na fila
                logger.warning(f"Rate limit atingido para {phone}")
                return jsonify({"status": "rate_limited"}), 429
        
        # Extrai conteúdo baseado no tipo
        message_text, message_type = extract_message_content(payload)
        
        if not message_text or len(message_text.strip()) == 0:
            return jsonify({"status": "ignored", "reason": "no_content"}), 200
        
        logger.info(f"Webhook recebido: {message_type} de {phone}")
        
        # Adiciona à fila
        queue = get_queue_for_phone(phone)
        queue.put({
            'message': message_text,
            'type': message_type,
            'timestamp': datetime.now().isoformat(),
            'phone': phone,
            'ip': request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        })
        
        # Inicia processador
        start_queue_processor(phone)
        
        return jsonify({
            "status": "queued", 
            "message": "Processando...",
            "type": message_type
        }), 200
        
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        metrics['errors'] += 1
        return jsonify({"status": "error", "message": "Internal server error"}), 500

def print_startup_banner():
    """Exibe banner de inicialização com informações da versão"""
    banner = f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                AVANTTI AI v{AVANTTI_VERSION}                         ║
    ║              {AVANTTI_CODENAME:<25}               ║
    ║                    Sistema Evex Imóveis                      ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  NOVIDADES DESTA VERSÃO:                                     ║
    ║  - Distribuição automática entre 11 equipes                 ║
    ║  - Mensagens quebradas em WhatsApp                          ║
    ║  - Integração Contact2Sale completa                         ║
    ║  - Sistema de estatísticas de leads                         ║
    ║  - Remoção de agendamento de visitas                        ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  CONFIGURAÇÕES ATIVAS:                                      ║"""
    
    # Verifica configurações
    config_lines = []
    
    # Contact2Sale
    c2s_enabled = bool(os.getenv("C2S_JWT_TOKEN"))
    distribution_enabled = os.getenv("C2S_USE_TEAM_DISTRIBUTION", "false").lower() == "true"
    distribution_method = os.getenv("C2S_DISTRIBUTION_METHOD", "round_robin")
    
    if c2s_enabled:
        config_lines.append("    ║  Contact2Sale: ATIVO                                        ║")
        if distribution_enabled:
            config_lines.append(f"    ║  Distribuição: {distribution_method.upper():<15}                      ║")
            
            # Conta equipes ativas
            try:
                from services.lead_distributor_service import LeadDistributor
                distributor = LeadDistributor()
                active_teams = len(distributor.get_active_teams())
                config_lines.append(f"    ║  Equipes ativas: {active_teams:<2}                                      ║")
            except:
                config_lines.append("    ║  Equipes ativas: 11                                         ║")
        else:
            config_lines.append("    ║  Distribuição: DESABILITADA                                ║")
    else:
        config_lines.append("    ║  Contact2Sale: DESABILITADO                                ║")
    
    # WhatsApp API
    whatsapp_api = os.getenv("WHATSAPP_API", "evolution").upper()
    config_lines.append(f"    ║  WhatsApp API: {whatsapp_api:<15}                           ║")
    
    # Outros serviços
    redis_enabled = bool(os.getenv("REDIS_URL"))
    supabase_enabled = bool(os.getenv("SUPABASE_URL"))
    openai_enabled = bool(os.getenv("OPENAI_API_KEY"))
    
    config_lines.append(f"    ║  Redis: {'ATIVO' if redis_enabled else 'INATIVO':<15}                           ║")
    config_lines.append(f"    ║  Supabase: {'ATIVO' if supabase_enabled else 'INATIVO':<15}                       ║")
    config_lines.append(f"    ║  OpenAI: {'ATIVO' if openai_enabled else 'INATIVO':<15}                         ║")
    
    config_lines.append("    ╠══════════════════════════════════════════════════════════════╣")
    config_lines.append(f"    ║  Servidor na porta: {os.getenv('PORT', 5000):<5}                                ║")
    config_lines.append(f"    ║  Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S'):<15}                  ║")
    config_lines.append("    ╚══════════════════════════════════════════════════════════════╝")
    
    full_banner = banner + "\n" + "\n".join(config_lines)
    
    print(full_banner)
    logger.info(f"Avantti AI v{AVANTTI_VERSION} ({AVANTTI_CODENAME}) iniciado com sucesso!")
    
    if c2s_enabled and distribution_enabled:
        logger.info("Sistema de distribuição de leads Contact2Sale ATIVO")
        logger.info(f"Método de distribuição: {distribution_method}")
    elif c2s_enabled:
        logger.info("Contact2Sale ativo (distribuição desabilitada)")
    else:
        logger.warning("Contact2Sale DESABILITADO")
    
    # Log adicional para EasyPanel
    logger.info("=" * 60)
    logger.info(f"NOVA VERSÃO ATIVA: v{AVANTTI_VERSION}")
    logger.info("Cliente: Evex Imóveis")
    logger.info("Distribuição automática de leads implementada")
    logger.info("Mensagens otimizadas para WhatsApp")
    logger.info("=" * 60)
    
    return full_banner


if __name__ == "__main__":
    # Exibe banner de inicialização
    print_startup_banner()
    
    # Inicia servidor
    app.run(host="0.0.0.0", port=int(os.getenv('PORT', 5000)), debug=False)
