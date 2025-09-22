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
AVANTTI_VERSION = "3.0.0"
AVANTTI_CODENAME = "Contact2Sale Distribution"

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

print("=== AVANTTI AI - ELIANE V3 MODULAR ===")

# Sistema de filas melhorado
message_queues = {}
processing_lock = threading.Lock()
active_processors = set()

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
    """Processa fila de mensagens usando o novo handler"""
    queue = get_queue_for_phone(phone)
    
    logger.info(f"Iniciando processamento para {phone} - {queue.qsize()} mensagens")
    
    while not queue.empty():
        try:
            message_data = queue.get(timeout=5)
            message_text = message_data.get('message', '')
            message_type = message_data.get('type', 'text')
            
            logger.info(f"Processando {message_type}: '{message_text[:50]}...' de {phone}")
            
            if message_text:
                metrics['messages_processed'] += 1
                
                # Cria dados para o handler
                if message_type == 'audio':
                    metrics['audio_transcriptions'] += 1
                    # Para áudio, usa handler específico
                    handler_data = {
                        'phone': phone,
                        'message': {'audioUrl': message_text}  # URL do áudio
                    }
                    message_handler.processar_mensagem_audio(handler_data)
                else:
                    # Para texto, imagem, vídeo
                    handler_data = {
                        'phone': phone,
                        'message': {'text': message_text}
                    }
                    message_handler.processar_mensagem_texto(handler_data)
            
            queue.task_done()
            time.sleep(1)  # Evita spam
            
        except Exception as e:
            logger.error(f"Erro no processamento: {e}")
            metrics['errors'] += 1
            try:
                queue.task_done()
            except:
                pass
    
    logger.info(f"Processamento concluído para {phone}")

def start_queue_processor(phone):
    """Inicia processador da fila com melhor controle"""
    global active_processors
    
    with processing_lock:
        if phone in active_processors:
            logger.info(f"Processador já ativo para {phone}")
            return
        
        active_processors.add(phone)
        logger.info(f"Iniciando processador para {phone}")
    
    def worker():
        try:
            process_message_queue(phone)
        except Exception as e:
            logger.error(f"Erro no worker: {e}")
        finally:
            with processing_lock:
                active_processors.discard(phone)
                logger.info(f"Processador finalizado para {phone}")
    
    thread = threading.Thread(target=worker, name=f"queue-{phone}")
    thread.daemon = True
    thread.start()

def extract_message_content(payload):
    """Extrai conteúdo da mensagem dependendo do tipo"""
    try:
        if not isinstance(payload, dict):
            return None, 'invalid'
        
        # Mensagem de texto
        if payload.get('text'):
            text_obj = payload.get('text', {})
            if isinstance(text_obj, dict):
                message = text_obj.get('message', '').strip()
                if len(message) > 4000:
                    message = message[:4000] + "... [truncado]"
                return message, 'text'
            return str(text_obj)[:4000], 'text'
        
        # Mensagem de áudio
        elif payload.get('audio'):
            audio_obj = payload.get('audio', {})
            if isinstance(audio_obj, dict):
                audio_url = audio_obj.get('audioUrl') or audio_obj.get('url')
                if audio_url and audio_url.startswith(('http://', 'https://')):
                    # Retorna URL para ser processada pelo handler
                    return audio_url, 'audio'
                else:
                    return "URL de áudio inválida", 'audio_error'
        
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
    return jsonify({"status": "healthy", "service": "avantti-ai-eliane-v3"}), 200

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
    ║                🤖 AVANTTI AI v{AVANTTI_VERSION}                      ║
    ║              {AVANTTI_CODENAME:<25}               ║
    ║                    Sistema Evex Imóveis                      ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  ✅ NOVIDADES DESTA VERSÃO:                                  ║
    ║  🔄 Distribuição automática entre 11 equipes                ║
    ║  📱 Mensagens quebradas em WhatsApp                         ║
    ║  🎯 Integração Contact2Sale completa                        ║
    ║  📊 Sistema de estatísticas de leads                        ║
    ║  🚫 Remoção de agendamento de visitas                       ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  📋 CONFIGURAÇÕES ATIVAS:                                   ║"""
    
    # Verifica configurações
    config_lines = []
    
    # Contact2Sale
    c2s_enabled = bool(os.getenv("C2S_JWT_TOKEN"))
    distribution_enabled = os.getenv("C2S_USE_TEAM_DISTRIBUTION", "false").lower() == "true"
    distribution_method = os.getenv("C2S_DISTRIBUTION_METHOD", "round_robin")
    
    if c2s_enabled:
        config_lines.append("    ║  🟢 Contact2Sale: ATIVO                                     ║")
        if distribution_enabled:
            config_lines.append(f"    ║  🔄 Distribuição: {distribution_method.upper():<15}                   ║")
            
            # Conta equipes ativas
            try:
                from services.lead_distributor_service import LeadDistributor
                distributor = LeadDistributor()
                active_teams = len(distributor.get_active_teams())
                config_lines.append(f"    ║  👥 Equipes ativas: {active_teams:<2}                                   ║")
            except:
                config_lines.append("    ║  👥 Equipes ativas: 11                                      ║")
        else:
            config_lines.append("    ║  🔄 Distribuição: DESABILITADA                             ║")
    else:
        config_lines.append("    ║  🔴 Contact2Sale: DESABILITADO                             ║")
    
    # WhatsApp API
    whatsapp_api = os.getenv("WHATSAPP_API", "evolution").upper()
    config_lines.append(f"    ║  📱 WhatsApp API: {whatsapp_api:<15}                        ║")
    
    # Outros serviços
    redis_enabled = bool(os.getenv("REDIS_URL"))
    supabase_enabled = bool(os.getenv("SUPABASE_URL"))
    openai_enabled = bool(os.getenv("OPENAI_API_KEY"))
    
    config_lines.append(f"    ║  🔴 Redis: {'ATIVO' if redis_enabled else 'INATIVO':<15}                        ║")
    config_lines.append(f"    ║  🟢 Supabase: {'ATIVO' if supabase_enabled else 'INATIVO':<15}                     ║")
    config_lines.append(f"    ║  🟢 OpenAI: {'ATIVO' if openai_enabled else 'INATIVO':<15}                       ║")
    
    config_lines.append("    ╠══════════════════════════════════════════════════════════════╣")
    config_lines.append(f"    ║  🚀 Servidor na porta: {os.getenv('PORT', 5000):<5}                              ║")
    config_lines.append(f"    ║  📅 Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S'):<15}                ║")
    config_lines.append("    ╚══════════════════════════════════════════════════════════════╝")
    
    full_banner = banner + "\n" + "\n".join(config_lines)
    
    print(full_banner)
    logger.info(f"🚀 Avantti AI v{AVANTTI_VERSION} ({AVANTTI_CODENAME}) iniciado com sucesso!")
    
    if c2s_enabled and distribution_enabled:
        logger.info("✅ Sistema de distribuição de leads Contact2Sale ATIVO")
        logger.info(f"📊 Método de distribuição: {distribution_method}")
    elif c2s_enabled:
        logger.info("✅ Contact2Sale ativo (distribuição desabilitada)")
    else:
        logger.warning("⚠️ Contact2Sale DESABILITADO")
    
    # Log adicional para EasyPanel
    logger.info("=" * 60)
    logger.info(f"🌟 NOVA VERSÃO ATIVA: v{AVANTTI_VERSION}")
    logger.info("🏢 Cliente: Evex Imóveis")
    logger.info("🔄 Distribuição automática de leads implementada")
    logger.info("📱 Mensagens otimizadas para WhatsApp")
    logger.info("=" * 60)
    
    return full_banner


if __name__ == "__main__":
    # Exibe banner de inicialização
    print_startup_banner()
    
    # Inicia servidor
    app.run(host="0.0.0.0", port=int(os.getenv('PORT', 5000)), debug=False)
