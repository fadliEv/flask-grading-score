from dataclasses import dataclass

@dataclass
class CustomerResponse:
    id: int
    name: str
    email: str
