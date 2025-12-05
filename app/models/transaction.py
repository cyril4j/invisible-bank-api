"""
Transaction model for financial transactions.
"""
from decimal import Decimal
from sqlalchemy import Column, String, Integer, ForeignKey, CheckConstraint, Numeric
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Transaction(BaseModel):
    """
    Transaction model for deposits, withdrawals, and transfers.
    """
    __tablename__ = "transactions"

    # Unique transaction identifier (UUID)
    transaction_id = Column(String(36), unique=True, nullable=False, index=True)

    # Associated account
    account_id = Column(
        Integer,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Transaction details
    transaction_type = Column(String(20), nullable=False)  # 'deposit', 'withdrawal', 'transfer'
    amount = Column(Numeric(15, 2), nullable=False)

    # Peer account information (for transfers)
    peer_routing_number = Column(String(9), nullable=True)
    peer_account_number = Column(String(20), nullable=True)

    # Description
    description = Column(String(500), nullable=True)

    # Constraints
    __table_args__ = (
        CheckConstraint("transaction_type IN ('deposit', 'withdrawal', 'transfer')", name="check_transaction_type"),
        CheckConstraint("amount > 0", name="check_positive_amount"),
    )

    # Relationships
    account = relationship("Account", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, transaction_id='{self.transaction_id}', type='{self.transaction_type}', amount={self.amount})>"
