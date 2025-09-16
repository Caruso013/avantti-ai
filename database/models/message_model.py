import json
from database.config import Base
from sqlalchemy import Column, Integer, Text, String
from sqlalchemy import DateTime, func
from sqlalchemy.orm import relationship
from database.mixins.serializable_mixin import SerializableMixin


class Message(Base, SerializableMixin):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "phone": self.phone,
            "role": self.role,
            "created_at": self.created_at,
        }

        try:
            data["content"] = json.loads(self.content)
        except (json.JSONDecodeError, TypeError):
            data["content"] = str(self.content)

        return data
