import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import settings

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)

        self.SessionLocal = sessionmaker(
            bind=self.engine
        )

    @contextmanager
    def transaction(self):
        with self.SessionLocal() as session:
            with session.begin():
                yield session
