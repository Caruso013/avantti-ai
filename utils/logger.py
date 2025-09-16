import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys
import json

# Cria a pasta 'logs' se não existir
if not os.path.exists("logs"):
    os.makedirs("logs")

# Define o logger principal
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logger = logging.getLogger("application")
logger.setLevel(LOG_LEVEL)

# Formato dos logs
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# === Console Handler (terminal) ===
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# === File Handler para logs gerais (app.log) ===
file_handler = TimedRotatingFileHandler(
    filename="logs/app.log",
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8",
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# === File Handler para logs de erros (error.log) ===
error_file_handler = TimedRotatingFileHandler(
    filename="logs/error.log",
    when="midnight",
    interval=1,
    backupCount=30,
    encoding="utf-8",
)
error_file_handler.setFormatter(formatter)
error_file_handler.setLevel(logging.ERROR)
logger.addHandler(error_file_handler)

# Função para capturar exceções não tratadas


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Deixa Ctrl+C passar normal
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


# Registra o handler de exceções globais
sys.excepthook = handle_exception


def to_json_dump(obj):
    return json.dumps(obj, default=str, indent=4, ensure_ascii=False)
