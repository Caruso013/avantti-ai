import json
from interfaces.repositories.abandoned_conversation_repository_interface import (
    IAbandonedConversationRepository,
)
from database.models.abandoned_conversation_model import AbandonedConversation
from interfaces.clients.database_interface import IDatabase


class AbandonedConversationRepository(IAbandonedConversationRepository):
    def __init__(self, database_client: IDatabase):
        self.db = database_client

    def find(self, phone: str) -> dict | None:
        with self.db.get_session() as session:
            conversation = (
                session.query(AbandonedConversation).filter_by(phone=phone).first()
            )
            return conversation.to_dict() if conversation else None

    def mark_as_abandoned_conversation(self, phone: str) -> bool:
        with self.db.get_session() as session:
            conversation = AbandonedConversation(phone=phone)
            session.add(conversation)
            return True

    def unmark_as_abandoned_conversation(self, phone: str) -> bool:
        with self.db.get_session() as session:
            deleted_count = (
                session.query(AbandonedConversation).filter_by(phone=phone).delete()
            )
            return deleted_count > 0

    def is_abandoned_conversation(self, phone: str) -> bool:
        with self.db.get_session() as session:

            return (
                session.query(AbandonedConversation).filter_by(phone=phone).count() > 0
            )

    def is_not_abandoned_conversation(self, phone: str) -> bool:
        with self.db.get_session() as session:
            return self.is_abandoned_conversation(phone) is False
