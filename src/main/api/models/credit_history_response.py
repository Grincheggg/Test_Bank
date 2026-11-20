from typing import List

from pydantic import Field

from src.main.api.models.base_model import BaseModel


class CreditItem(BaseModel):
    credit_id: int = Field(..., alias="creditId")
    account_id: int = Field(..., alias="accountId")
    amount: int
    term_months: int = Field(..., alias="termMonths")
    balance: float


class CreditHistoryResponse(BaseModel):
    user_id: int = Field(..., alias="userId")
    credits: List[CreditItem]
