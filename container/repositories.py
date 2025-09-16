from container.clients import ClientContainer
from repositories.message_repository import MessageRepository
from repositories.abandoned_conversation_repository import (
    AbandonedConversationRepository,
)


class RepositoryContainer:

    def __init__(self, clients: ClientContainer):
        self._clients = clients

    @property
    def message(self):
        return MessageRepository(database_client=self._clients.database)

    @property
    def abandoned_conversation(self):
        return AbandonedConversationRepository(database_client=self._clients.database)
