import os

from dotenv import load_dotenv

load_dotenv()

def get_embedding_config():
    endpoint = os.getenv("AI_API_BASE_URL")
    api_key = os.getenv("AI_API_KEY")
    model = os.getenv("AI_EMBEDDING_MODEL")

    missing = []

    if not endpoint:
        missing.append("AI_API_BASE_URL")

    if not api_key:
        missing.append("AI_API_KEY")
    
    if not model:
        missing.append("AI_EMBEDDING_MODEL")

    if missing:
        raise ValueError(
            "Missing environment variables: "
            + ", ".join(missing)
        )

    return {
        "endpoint": endpoint,
        "api_key": api_key,
        "model": model,
        "dimensions": None,
        "batch_size": 32,
        "normalise": True,
    }
