from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


class Database:
    def __init__(self, database_url: str) -> None:
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        self.engine = create_engine(database_url, future=True, connect_args=connect_args)
        self.session_factory = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False, future=True)

    def init_schema(self) -> None:
        from src.storage import schema  # noqa: F401

        Base.metadata.create_all(self.engine)

