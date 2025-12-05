"""
Statement schemas.
"""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from typing import List, Optional


class StatementTransaction(BaseModel):
    """Transaction in statement."""
    transaction_id: str
    transaction_type: str
    amount: Decimal
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AccountStatement(BaseModel):
    """Statement for a single account."""
    account_id: int
    account_number: str
    account_type: str
    balance: Decimal
    transactions: List[StatementTransaction]


class Statement(BaseModel):
    """Complete statement for user."""
    period_start: datetime
    period_end: datetime
    accounts: List[AccountStatement]
    total_transactions: int
