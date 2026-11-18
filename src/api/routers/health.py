from fastapi import APIRouter, Depends
from sqlalchemy import text

from src.data.database_manager import DatabaseManager
from src.dependencies import get_database_manager

router = APIRouter()

@router.get("/health/live")
def live():
    return {"status":"ok"}

@router.get("/health/ready")
def ready(
    db: DatabaseManager = Depends(get_database_manager),
):
    try:
        with db.transaction() as session:
            session.execute(text("SELECT 1"))
        
        return {"status": "ready"}

    except Exception:
        return {"status": "not ready"}