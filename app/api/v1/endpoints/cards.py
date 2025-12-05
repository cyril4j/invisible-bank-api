"""
Card endpoints.
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.account_holder import AccountHolder
from app.schemas.card import CardCreate, CardResponse
from app.services.card_service import CardService


router = APIRouter(prefix="/cards", tags=["Cards"])


@router.post("", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
async def create_card(
    request: CardCreate,
    current_user: AccountHolder = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new card."""
    card = CardService.create_card(db, current_user.id, request)
    return CardService.get_card_response(card)


@router.get("", response_model=List[CardResponse])
async def list_cards(
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    current_user: AccountHolder = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's cards."""
    cards = CardService.get_user_cards(db, current_user.id, account_id)
    return [CardService.get_card_response(card) for card in cards]
