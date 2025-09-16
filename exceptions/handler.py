import traceback
import os
from datetime import datetime
from functools import wraps
from utils.logger import logger
from typing import Dict, Any, List, Callable
from .notifier_factory import NotifierFactory
from .notifications import NotifierInterface


class ErrorHandler:
    """Handler principal para tratamento de erros"""

    def __init__(self, container):
        self.logger = logger
        self.container = container
        self.notifiers: List[NotifierInterface] = NotifierFactory.create_notifiers(
            self.container
        )

    def handle_error(
        self,
        error: Exception,
        service: str,
        func_name: str,
        file_path: str,
        line_number: int,
    ):
        """
        Processar erro: fazer log e enviar notificações

        Args:
            error: Exceção capturada
            service: Nome do serviço/cliente
            func_name: Nome da função onde ocorreu o erro
            file_path: Caminho do arquivo
            line_number: Número da linha
        """

        error_data = self._build_error_data(
            error, service, func_name, file_path, line_number
        )

        self._log_error(error_data)

        self._send_notifications(error_data)

    def _build_error_data(
        self,
        error: Exception,
        service: str,
        func_name: str,
        file_path: str,
        line_number: int,
    ) -> Dict[str, Any]:
        """Montar dicionário com dados do erro"""
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "service": service,
            "function": func_name,
            "file": os.path.basename(file_path),
            "line": line_number,
            "error_type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(),
        }

    def _log_error(self, error_data: Dict[str, Any]):
        """Fazer log do erro"""
        log_message = (
            f"[{error_data['service']}] {error_data['error_type']}: {error_data['message']} "
            f"({error_data['file']}:{error_data['line']} in {error_data['function']})"
        )
        self.logger.error(log_message)

    def _send_notifications(self, error_data: Dict[str, Any]):
        """Enviar notificações para todos os notificadores ativos"""
        for notifier in self.notifiers:
            try:
                notifier.send_notification(error_data)
            except Exception as e:
                self.logger.error(
                    f"Falha ao enviar notificação via {type(notifier).__name__}: {e}"
                )


# Instância global
def setup_error_handler(container):
    global _error_handler
    _error_handler = ErrorHandler(container)


def handle_errors(service: str):
    """
    Decorator para tratamento automático de erros

    Args:
        service: Nome do serviço/cliente para identificação

    Usage:
        @handle_errors("PIPEDRIVE")
        def create_deal(self, data):
            # Sua lógica aqui
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                # Obter informações do frame atual
                frame = traceback.extract_tb(error.__traceback__)[-1]

                _error_handler.handle_error(
                    error=error,
                    service=service,
                    func_name=func.__name__,
                    file_path=frame.filename,
                    line_number=frame.lineno,
                )

                # Re-raise o erro para manter o comportamento original
                raise

        return wrapper

    return decorator
