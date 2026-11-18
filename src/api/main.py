from fastapi import FastAPI

from src.api.routers.health import router as health_router

app = FastAPI(
    title="Complaints API",
)

app.include_router(health_router)