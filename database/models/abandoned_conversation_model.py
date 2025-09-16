import json
from database.config import Base
from sqlalchemy import Column, Integer, Text, String
from sqlalchemy import DateTime, func
from sqlalchemy.orm import relationship
from database.mixins.serializable_mixin import SerializableMixin


class AbandonedConversation(Base, SerializableMixin):
    __tablename__ = "abandoned_conversations"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "phone": self.phone,
            "created_at": self.created_at,
        }

        return data
