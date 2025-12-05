"""
AccountHolder model - serves as users table with authentication and customer data.
"""
from sqlalchemy import Column, String, Date, LargeBinary, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class AccountHolder(BaseModel):
    """
    Account holder model (combines user authentication + customer information).

    This table serves dual purpose:
    - User authentication (email, password_hash)
    - Customer personal information (name, SSN, DOB, address)
    """
    __tablename__ = "account_holders"

    # Personal Information
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Encrypted sensitive data (stored as binary)
    ssn_encrypted = Column(LargeBinary, nullable=False)

    # Additional personal data
    date_of_birth = Column(Date, nullable=False)
    mailing_address = Column(String(500), nullable=False)

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    accounts = relationship("Account", back_populates="account_holder", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<AccountHolder(id={self.id}, email='{self.email}', name='{self.name}')>"
