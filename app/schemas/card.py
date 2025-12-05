"""
Card schemas.
"""
from datetime import datetime
from pydantic import BaseModel
from typing import Literal


class CardCreate(BaseModel):
    """Create card request."""
    account_id: int
    card_type: Literal["credit", "debit"]


class CardResponse(BaseModel):
    """Card response (card number masked)."""
    id: int
    account_id: int
    card_number_last4: str  # Only last 4 digits
    card_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
