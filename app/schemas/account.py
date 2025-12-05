"""
Account schemas.
"""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Literal, Optional


class AccountCreate(BaseModel):
    """Create account request."""
    account_type: Literal["checking", "savings"]


class AccountResponse(BaseModel):
    """Account response."""
    id: int
    account_holder_id: int
    account_number: str
    routing_number: str
    account_type: str
    balance: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountUpdate(BaseModel):
    """Update account request."""
    account_type: Optional[Literal["checking", "savings"]] = None
