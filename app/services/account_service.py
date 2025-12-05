"""
Account service for managing bank accounts.
"""
from sqlalchemy.orm import Session
from typing import List
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountResponse
from app.utils.generators import generate_account_number
from app.config import settings
from app.core.exceptions import NotFoundError, UnauthorizedError
from app.core.logging_config import logger


class AccountService:
    """Account management service."""

    @staticmethod
    def create_account(db: Session, user_id: int, request: AccountCreate) -> Account:
        """
        Create a new account for user.

        Args:
            db: Database session
            user_id: Account holder ID
            request: Account creation request

        Returns:
            Account: Created account
        """
        account_number = generate_account_number(db)

        account = Account(
            account_holder_id=user_id,
            account_number=account_number,
            routing_number=settings.routing_number,
            account_type=request.account_type,
            balance=0.00,
            is_active=True
        )

        db.add(account)
        db.commit()
        db.refresh(account)

        logger.info(f"Account created: {account.account_number} for user {user_id}")
        return account

    @staticmethod
    def get_user_accounts(db: Session, user_id: int) -> List[Account]:
        """
        Get all accounts for a user.

        Args:
            db: Database session
            user_id: Account holder ID

        Returns:
            List[Account]: User's accounts
        """
        return db.query(Account).filter(
            Account.account_holder_id == user_id
        ).all()

    @staticmethod
    def get_account(db: Session, account_id: int, user_id: int) -> Account:
        """
        Get specific account with ownership check.

        Args:
            db: Database session
            account_id: Account ID
            user_id: Account holder ID

        Returns:
            Account: The account

        Raises:
            NotFoundError: If account doesn't exist
            UnauthorizedError: If user doesn't own the account
        """
        account = db.query(Account).filter(Account.id == account_id).first()

        if not account:
            raise NotFoundError("Account not found")

        if account.account_holder_id != user_id:
            raise UnauthorizedError("Access denied to this account")

        return account
