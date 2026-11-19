from src.data.database_manager import DatabaseManager
from src.app.models.customer import Customer
from src.app.models.account import Account


db = DatabaseManager()

with db.transaction() as session:

    customer = Customer(
        customer_id=1,
        first_name="John",
        last_name="Smith",
        email="john@example.com",
    )

    account = Account(
        account_id="AC00001",
        customer_id=1,
        account_type="Current",
    )

    session.add(customer)
    session.add(account)

print("Test customer and account created.")