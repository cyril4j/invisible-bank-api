"""
Account holder schemas.
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class AccountHolderResponse(BaseModel):
    """Account holder response (no sensitive data)."""
    id: int
    name: str
    email: EmailStr
    date_of_birth: date
    mailing_address: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountHolderUpdate(BaseModel):
    """Account holder update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    mailing_address: Optional[str] = Field(None, min_length=1, max_length=500)
