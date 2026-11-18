from src.data.database_manager import DatabaseManager
from src.services.complaint_service import ComplaintService

db = DatabaseManager()

def get_database_manager():
    return db

def get_complaint_service():
    return ComplaintService(db)