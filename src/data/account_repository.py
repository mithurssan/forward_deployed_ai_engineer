from app.database.database_manager import DatabaseManager
from app.models.account import Account

class AccountRepository:
    def get_for_customer(self, customer_id):
        with DatabaseManager() as db:
            cursor = db.execute(
                """
                SELECT account_id, customer_id, account_type
                FROM account
                WHERE customer_id = ?
                """,
                (customer_id,)
            )

            row = cursor.fetchall()

            return [
                Account(
                    account_id=row["account_id"]
                    customer_id=row["customer_id"]
                    account_type=row["account_type"]
                )
                for row in rows
            ]