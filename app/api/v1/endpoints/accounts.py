"""
Account endpoints.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.account_holder import AccountHolder
from app.schemas.account import AccountCreate, AccountResponse
from app.services.account_service import AccountService


router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    request: AccountCreate,
    current_user: AccountHolder = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new account."""
    account = AccountService.create_account(db, current_user.id, request)
    return account


@router.get("", response_model=List[AccountResponse])
async def list_accounts(
    current_user: AccountHolder = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all user's accounts."""
    return AccountService.get_user_accounts(db, current_user.id)


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    current_user: AccountHolder = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific account."""
    return AccountService.get_account(db, account_id, current_user.id)
