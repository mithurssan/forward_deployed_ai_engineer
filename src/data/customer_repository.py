from app.database.database_manager import DatabaseManager
from app.models.customer import Customer

class CustomerRepository:
    def get_by_id(self, customer_id: int):
        with DatabaseManager() as db:
            cursor = db.execute(
                """
                SELECT customer_id, first_name, last_name, email
                FROM customer
                WHERE customer_id = ?
                """,
                (customer_id)
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return Customer(
                customer_id=row["customer_id"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                email=row["email"]
            )