import json
from time import perf_counter
from uuid import uuid4

from fastapi import Request

from src.logging_config import configure_logging

logger = configure_logging()

async def request_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID")

    if not correlation_id:
        correlation_id = str(uuid4())

    request.state.correlation_id = correlation_id

    start = perf_counter()

    try:
        response = await call_next(request)

        outcome = (
            "success"
            if response.status_code < 400
            else "failure"
        )

        return response

    except Exception:
        outcome = "failure"
        raise

    finally:
        duration_ms = (perf_counter() - start) * 1000

        logger.info(
            json.dumps({
                "operation": f"{request.method} {request.url.path}",
                "outcome": outcome,
                "duration_ms": round(duration_ms, 2),
                "correlation_id": correlation_id,
            })
        )