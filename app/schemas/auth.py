"""
Authentication schemas for request/response validation.
"""
from datetime import date
from pydantic import BaseModel, EmailStr, Field, validator
from app.utils.validators import validate_ssn, validate_age


class SignupRequest(BaseModel):
    """User signup request."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8)
    ssn: str = Field(..., description="Format: XXX-XX-XXXX")
    date_of_birth: date
    mailing_address: str = Field(..., min_length=1, max_length=500)

    @validator('ssn')
    def validate_ssn_format(cls, v):
        if not validate_ssn(v):
            raise ValueError('SSN must be in format XXX-XX-XXXX')
        return v

    @validator('date_of_birth')
    def validate_age_requirement(cls, v):
        if not validate_age(v, minimum_age=18):
            raise ValueError('Must be at least 18 years old')
        return v


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str
