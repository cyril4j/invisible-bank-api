"""
Database base - imports all models for Alembic migrations.
"""
# Import Base from models
from app.models.base import Base  # noqa

# Import all models to register them with SQLAlchemy
from app.models.account_holder import AccountHolder  # noqa
from app.models.account import Account  # noqa
from app.models.transaction import Transaction  # noqa
from app.models.card import Card  # noqa

# This ensures all models are registered with Base.metadata
# which is needed for Alembic auto-generation of migrations
