import os

class Settings:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///complaints.db",
    )

settings = Settings()

