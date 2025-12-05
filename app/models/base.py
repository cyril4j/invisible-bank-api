"""
Base model with automatic created_at and updated_at timestamps.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import declarative_base


# Create the base class for all models
Base = declarative_base()


class BaseModel(Base):
    """
    Abstract base model with common fields for all database models.

    Provides:
    - id: Primary key (auto-increment)
    - created_at: Timestamp when record was created
    - updated_at: Timestamp when record was last updated
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
