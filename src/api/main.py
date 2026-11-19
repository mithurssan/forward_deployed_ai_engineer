from fastapi import FastAPI

from src.api.routers.health import router as health_router
from src.api.routers.customers import router as customers_router
from src.api.routers.complaints import router as complaints_router

from src.api.error_handlers import (
    domain_error_handler,
    unexpected_error_handler,
)
from src.api.middleware import request_middleware

from src.domain.errors import (
    CustomerNotFound,
    ComplaintNotFound,
    InvalidTransition,
    ApprovalRequired,
    ValidationError,
    ForbiddenRole,
    DependencyUnavailable,
)

from src.data.database_manager import DatabaseManager
from src.app.models.base import Base
import logging

logging.basicConfig(level=logging.INFO)

db = DatabaseManager()

Base.metadata.create_all(bind=db.engine)


app = FastAPI(
    title="Complaints API",
)


app.middleware("http")(request_middleware)


for error_type in (
    CustomerNotFound,
    ComplaintNotFound,
    InvalidTransition,
    ApprovalRequired,
    ValidationError,
    ForbiddenRole,
    DependencyUnavailable,
):
    app.add_exception_handler(
        error_type,
        domain_error_handler,
    )


app.add_exception_handler(
    Exception,
    unexpected_error_handler,
)


app.include_router(health_router)
app.include_router(customers_router)
app.include_router(complaints_router)