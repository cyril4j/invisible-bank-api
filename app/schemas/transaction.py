"""
Transaction schemas.
"""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Literal, Optional


class DepositRequest(BaseModel):
    """Deposit request."""
    account_id: int
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)


class WithdrawalRequest(BaseModel):
    """Withdrawal request."""
    account_id: int
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)


class TransferRequest(BaseModel):
    """Transfer request."""
    from_account_id: int
    to_routing_number: str = Field(..., min_length=9, max_length=9)
    to_account_number: str = Field(..., min_length=1, max_length=20)
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=500)


class TransactionResponse(BaseModel):
    """Transaction response."""
    id: int
    transaction_id: str
    account_id: int
    transaction_type: str
    amount: Decimal
    peer_routing_number: Optional[str]
    peer_account_number: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
