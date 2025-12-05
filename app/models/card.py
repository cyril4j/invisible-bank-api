"""
Card model for debit and credit cards.
"""
from sqlalchemy import Column, LargeBinary, String, Integer, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Card(BaseModel):
    """
    Card model for debit or credit cards.
    """
    __tablename__ = "cards"

    # Associated account
    account_id = Column(
        Integer,
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Card number (encrypted 16-digit number stored as binary)
    card_number_encrypted = Column(LargeBinary, nullable=False)

    # Card type
    card_type = Column(String(10), nullable=False)  # 'credit' or 'debit'

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint("card_type IN ('credit', 'debit')", name="check_card_type"),
    )

    # Relationships
    account = relationship("Account", back_populates="cards")

    def __repr__(self) -> str:
        return f"<Card(id={self.id}, type='{self.card_type}', account_id={self.account_id})>"
