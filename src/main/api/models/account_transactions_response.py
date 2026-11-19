from src.main.api.models.base_model import BaseModel


class AccountTransactionResponse(BaseModel):
    id: int
    number: str
    balance: float
