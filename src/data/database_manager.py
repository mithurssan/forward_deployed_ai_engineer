import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DatabaseManager:
    def __init__(self):
        database_url = os.getenv(
            "DATABASE_URL",
            "sqlite:///complaints.db"
        )

        self.engine = create_engine(database_url)

        self.SessionLocal = sessionmaker(
            bind=self.engine
        )

    @contextmanager
    def transaction(self):
        with self.SessionLocal() as session:
            with session.begin():
                yield session
