from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.routers.health import router as health_router
from src.api.routers.customers import router as customers_router
from src.api.routers.complaints import router as complaints_router
from src.domain.errors import (
    CustomerNotFound,
    ComplaintNotFound,
)
from src.data.database_manager import DatabaseManager
from src.app.models.base import Base

db = DatabaseManager()

Base.metadata.create_all(bind=db.engine)

app = FastAPI(
    title="Complaints API",
)

app.include_router(health_router)
app.include_router(customers_router)
app.include_router(complaints_router)

@app.exception_handler(CustomerNotFound)
@app.exception_handler(ComplaintNotFound)
async def not_found_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "code": exc.code,
            "message": str(exc),
        },
    )

