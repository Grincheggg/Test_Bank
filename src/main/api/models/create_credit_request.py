from typing import Annotated

from pydantic import Field

from src.main.api.generators.creation_rule import CreationRule
from src.main.api.models.base_model import BaseModel


class CreateCreditRequest(BaseModel):
    account_id: int = Field(..., alias="accountId")
    amount: Annotated[float, CreationRule(regex=r'^([5-9]\d{3}|1[0-4]\d{3}|15000)$')]
    term_months: Annotated[int, CreationRule(regex=r'^([1-9]|[1-5]\d|60)$')] = Field(..., alias="termMonths")
