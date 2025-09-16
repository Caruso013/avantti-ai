from controllers.process_incoming_message_controller import (
    ProcessIncomingMessageController,
)
from container.services import ServiceContainer


class ControllerContainer:

    def __init__(self, services: ServiceContainer):
        self._services = services

    @property
    def process_incoming_message_controller(self) -> ProcessIncomingMessageController:
        return ProcessIncomingMessageController(
            service=self._services.message_queue_service,
        )
