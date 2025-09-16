from services.message_queue_service import MessageQueueService
from interfaces.clients.database_interface import IDatabase


class ProcessIncomingMessageController:

    def __init__(self, service: MessageQueueService):
        self.service = service

    def handle(self, **kwargs) -> tuple[dict, int]:
        self.service.handle(**kwargs)

        return {"status": "success"}, 200
