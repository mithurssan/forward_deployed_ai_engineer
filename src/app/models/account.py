from dataclasses import dataclass

@dataclass
class Account:
    account_id: int
    customer_id: int
    account_type: str