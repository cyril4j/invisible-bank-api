"""
Card service for managing debit/credit cards.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.card import Card
from app.models.account import Account
from app.schemas.card import CardCreate, CardResponse
from app.utils.generators import generate_card_number
from app.utils.encryption import encryption_service
from app.core.exceptions import AccountNotFoundError, UnauthorizedError
from app.core.logging_config import logger


class CardService:
    """Card management service."""

    @staticmethod
    def create_card(db: Session, user_id: int, request: CardCreate) -> Card:
        """
        Create a new card for an account.

        Args:
            db: Database session
            user_id: Account holder ID
            request: Card creation request

        Returns:
            Card: Created card
        """
        # Verify account ownership
        account = db.query(Account).filter(Account.id == request.account_id).first()
        if not account:
            raise AccountNotFoundError()
        if account.account_holder_id != user_id:
            raise UnauthorizedError("Access denied to this account")

        # Generate and encrypt card number
        card_number = generate_card_number()
        card_number_encrypted = encryption_service.encrypt(card_number)

        card = Card(
            account_id=request.account_id,
            card_number_encrypted=card_number_encrypted,
            card_type=request.card_type,
            is_active=True
        )

        db.add(card)
        db.commit()
        db.refresh(card)

        logger.info(f"Card created: {request.card_type} card for account {account.account_number}")
        return card

    @staticmethod
    def get_user_cards(db: Session, user_id: int, account_id: Optional[int] = None) -> List[Card]:
        """
        Get all cards for user (optionally filtered by account).

        Args:
            db: Database session
            user_id: Account holder ID
            account_id: Optional account ID filter

        Returns:
            List[Card]: User's cards
        """
        # Get user's account IDs
        account_ids = [acc.id for acc in db.query(Account).filter(
            Account.account_holder_id == user_id
        ).all()]

        query = db.query(Card).filter(Card.account_id.in_(account_ids))

        if account_id:
            if account_id not in account_ids:
                raise UnauthorizedError("Access denied to this account")
            query = query.filter(Card.account_id == account_id)

        return query.all()

    @staticmethod
    def get_card_response(card: Card) -> CardResponse:
        """
        Convert Card model to CardResponse with masked card number.

        Args:
            card: Card model instance

        Returns:
            CardResponse: Response with last 4 digits only
        """
        # Decrypt card number and get last 4 digits
        card_number = encryption_service.decrypt(card.card_number_encrypted)
        last4 = card_number[-4:]

        return CardResponse(
            id=card.id,
            account_id=card.account_id,
            card_number_last4=last4,
            card_type=card.card_type,
            is_active=card.is_active,
            created_at=card.created_at,
            updated_at=card.updated_at
        )
