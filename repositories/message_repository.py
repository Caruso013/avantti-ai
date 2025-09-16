import json
from interfaces.repositories.message_repository_interface import IMessageRepository
from database.models.message_model import Message
from interfaces.clients.database_interface import IDatabase
from datetime import datetime, timedelta
from sqlalchemy import func, and_, not_, select, exists


class MessageRepository(IMessageRepository):
    def __init__(self, database_client: IDatabase):
        self.db = database_client

    def all(self) -> list:
        with self.db.get_session() as session:
            messages = session.query(Message).all()
            return [message for message in messages] or []

    def get_latest_customer_messages(
        self, phone: int | None = None, limit: int = 20
    ) -> list:
        with self.db.get_session() as session:
            query = (
                session.query(Message)
                .filter_by(phone=phone)
                .order_by(Message.id.desc())
            )

            if limit:
                query = query.limit(limit)

            messages = query.all()

            return [message.to_dict() for message in messages] or []

    def get_abandoned_conversation_numbers(self, until_time: datetime) -> list:
        max_time = until_time - timedelta(hours=1)

        with self.db.get_session() as session:
            # Subquery: última mensagem assistant por número
            last_assistant = (
                session.query(
                    Message.phone,
                    func.max(Message.created_at).label("last_assistant_time"),
                )
                .filter(Message.role == "assistant")
                .group_by(Message.phone)
                .subquery()
            )

            # Subquery: números que possuem mensagens com "function_call"
            has_function_call = (
                session.query(Message.phone)
                .filter(Message.content.ilike("%function_call%"))
                .distinct()
                .subquery()
            )

            # Query final: seleciona números com última mensagem de assistente entre 5h e 6h atrás e sem function_call
            query = session.query(last_assistant.c.phone).filter(
                last_assistant.c.last_assistant_time <= until_time,
                last_assistant.c.last_assistant_time >= max_time,
                ~last_assistant.c.phone.in_(select(has_function_call.c.phone)),
            )

            messages = session.execute(query).scalars().all()
            return messages or []

    def create(self, phone: str, role: str, content: str | list) -> dict:
        with self.db.get_session() as session:
            message = Message(
                phone=phone,
                role=role,
                content=content if isinstance(content, str) else json.dumps(content),
            )
            session.add(message)
            return message.to_dict()
