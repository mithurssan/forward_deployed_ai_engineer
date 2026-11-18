from fastapi import APIRouter, Depends

from src.dependencies import get_complaint_service
from src.services.complaint_service import ComplaintService

router = APIRouter()

@router.get("/complaints/{complaint_id}")
def get_complaint(
    complaint_id: str,
    service: ComplaintService = Depends(get_complaint_service),
):
    return service.get_complaint(complaint_id)

