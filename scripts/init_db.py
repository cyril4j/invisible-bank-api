#!/usr/bin/env python
"""
Initialize the database by creating all tables from SQLAlchemy models.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.session import engine
from app.db.base import Base
from app.core.logging_config import logger


def init_db():
    """
    Create all database tables based on SQLAlchemy models.
    """
    logger.info("Initializing database...")

    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # List created tables
        tables = Base.metadata.tables.keys()
        logger.info(f"Created tables: {', '.join(tables)}")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    init_db()
