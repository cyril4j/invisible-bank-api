"""
Transaction endpoints.
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.account_holder import AccountHolder
from app.schemas.transaction import (
    DepositRequest, WithdrawalRequest, TransferRequest, TransactionResponse
)
from app.services.transaction_service import TransactionService


router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/deposit", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_deposit(
    request: DepositRequest,
    current_user: AccountHolder = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a deposit transaction."""
    return TransactionService.create_deposit(db, current_user.id, request)


@router.post("/withdraw", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_withdrawal(
    request: WithdrawalRequest,
    current_user: AccountHolder = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a withdrawal transaction."""
    return TransactionService.create_withdrawal(db, current_user.id, request)


@router.post("/transfer", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transfer(
    request: TransferRequest,
    current_user: AccountHolder = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a transfer transaction."""
    return TransactionService.create_transfer(db, current_user.id, request)


@router.get("", response_model=List[TransactionResponse])
async def list_transactions(
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    current_user: AccountHolder = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's transactions."""
    return TransactionService.get_transactions(db, current_user.id, account_id)
