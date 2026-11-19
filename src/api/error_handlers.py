from fastapi import Request
from fastapi.responses import JSONResponse

async def domain_error_handler(
    request: Request,
    exc: Exception,
):
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "code": exc.code,
            "message": str(exc),
            "correlation_id": request.state.correlation_id,
        },
    )

async def unexpected_error_handler(
    request: Request,
    exc: Exception,
):
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_ERROR",
            "message": (
                "Unexpected error. Quote the correlation ID "
                "when reporting it."
            ),
            "correlation_id": request.state.correlation_id,
        },
    )