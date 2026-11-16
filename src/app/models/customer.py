from dataclasses import dataclass

@dataclass
class Customer:
    customer_id: int
    first_name: str
    last_name: str
    email: str