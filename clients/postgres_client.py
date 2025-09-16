from typing import Generator, ContextManager
from contextlib import contextmanager
from database.config import SessionLocal
from sqlalchemy.orm import Session
from interfaces.clients.database_interface import IDatabase


class PostgresClient(IDatabase):
    def __init__(self):
        self._SessionLocal = SessionLocal

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        session = self._SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close(self) -> None:
        self._SessionLocal().close()
