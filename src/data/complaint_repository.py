from app.database.database_manager import DatabaseManager
from app.models.complaint import Complaint

class ComplaintRepository:
    def get_by_id(self, complaint_id: int):

        with DatabaseManager() as db:
            cursor = db.execute(
                """
                SELECT complaint_id,
                customer_id,
                account_id,
                category,
                status,
                date_opened,
                date_closed,
                channel
                priority,
                complaint_text
                FROM complaint
                WHERE complaint_id = ?
                """,
                (complaint_id)
            )

            row = cursor.fetchone()

            if row is None:
                return None
            
            return Complaint(
                complaint_id=row["complaint_id"],
                customer_id=row["customer_id"],
                account_id=row["account_id"],
                category=row["category"],
                status=row["status"],
                date_opened=row["date_opened"],
                date_closed=row["dat_closed"],
                channel=row["channel"]
                priority=row["priority"],
                complaint_text=row["complaint_text"]
            )

    def get_for_customer(self, customer_id):
        with DatabaseManager() as db:
            cursor = db.execute(
                """
                SELECT complaint_id,
                customer_id,
                account_id,
                category,
                status,
                date_opened,
                date_closed,
                channel
                priority,
                complaint_text
                FROM complaint
                WHERE customer_id = ?
                """,
                (customer_id,)
            )

            rows = cursor.fetchall()

            return [
                Complaint(
                complaint_id=row["complaint_id"],
                customer_id=row["customer_id"],
                account_id=row["account_id"],
                category=row["category"],
                status=row["status"],
                date_opened=row["date_opened"],
                date_closed=row["dat_closed"],
                channel=row["channel"]
                priority=row["priority"],
                complaint_text=row["complaint_text"]
                )
                for row in rows
            ]
    
    def create(
        self,
        customer_id: int,
        account_id: int,
        category: str,
        status: str,
        date_opened: str,
        channel: str,
        priority: str,
        complaint_text: str
    ):
        with DatabaseManager() as db:
            cursor = db.execute(
                """
                INSERT INTO complaint (
                    customer_id,
                    account_id,
                    category,
                    status,
                    date_opened,
                    date_closed,
                    channel,
                    priority,
                    complaint_text
                )
                VALUES (?,?,?,?,?,?,?,?,?)
                """,
                (
                    customer_id,
                    account_id,
                    category,
                    status,
                    date_opened,
                    None,
                    channel,
                    priority,
                    comaplint_text
                )
            )

            complaint_id = cursor.lastrowid

            return Complaint(
                complaint_id=complaint_id,
                customer_id=customer_id,
                account_id=account_id,
                category=category,
                status=status,
                date_opened=date_opened,
                date_closed=None,
                channel=channel,
                priority=priority,
                complaitn_text=complaint_text
            )