"""
Statement endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.account_holder import AccountHolder
from app.schemas.statement import Statement
from app.services.statement_service import StatementService


router = APIRouter(prefix="/statements", tags=["Statements"])


@router.get("", response_model=Statement)
async def get_statement(
    current_user: AccountHolder = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get 30-day statement for all accounts."""
    return StatementService.get_user_statement(db, current_user.id, days=30)
