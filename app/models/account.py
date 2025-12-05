"""
Account model for bank accounts (checking/savings).
"""
from decimal import Decimal
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, CheckConstraint, Numeric
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Account(BaseModel):
    """
    Bank account model (checking or savings).
    """
    __tablename__ = "accounts"

    # Owner
    account_holder_id = Column(
        Integer,
        ForeignKey("account_holders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Account identifiers
    account_number = Column(String(20), unique=True, nullable=False, index=True)
    routing_number = Column(String(9), nullable=False, default="123456789")

    # Account type
    account_type = Column(String(10), nullable=False)  # 'checking' or 'savings'

    # Balance
    balance = Column(Numeric(15, 2), nullable=False, default=Decimal("0.00"))

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint("account_type IN ('checking', 'savings')", name="check_account_type"),
        CheckConstraint("balance >= 0", name="check_positive_balance"),
    )

    # Relationships
    account_holder = relationship("AccountHolder", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
    cards = relationship("Card", back_populates="account", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Account(id={self.id}, account_number='{self.account_number}', type='{self.account_type}', balance={self.balance})>"
