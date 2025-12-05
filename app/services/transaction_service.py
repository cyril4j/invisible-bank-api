"""
Transaction service for deposits, withdrawals, and transfers.
"""
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.transaction import Transaction
from app.models.account import Account
from app.schemas.transaction import DepositRequest, WithdrawalRequest, TransferRequest
from app.core.exceptions import InsufficientFundsError, AccountNotFoundError, UnauthorizedError
from app.config import settings
from app.core.logging_config import logger


class TransactionService:
    """Transaction processing service."""

    @staticmethod
    def create_deposit(db: Session, user_id: int, request: DepositRequest) -> Transaction:
        """
        Create a deposit transaction.

        Args:
            db: Database session
            user_id: Account holder ID
            request: Deposit request

        Returns:
            Transaction: Created transaction

        Raises:
            AccountNotFoundError: If account doesn't exist
            UnauthorizedError: If user doesn't own the account
        """
        # Verify account ownership
        account = db.query(Account).filter(Account.id == request.account_id).first()
        if not account:
            raise AccountNotFoundError()
        if account.account_holder_id != user_id:
            raise UnauthorizedError("Access denied to this account")

        # Create transaction
        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            account_id=request.account_id,
            transaction_type="deposit",
            amount=request.amount,
            description=request.description
        )

        # Update account balance
        account.balance += request.amount

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        logger.info(f"Deposit: ${request.amount} to account {account.account_number}")
        return transaction

    @staticmethod
    def create_withdrawal(db: Session, user_id: int, request: WithdrawalRequest) -> Transaction:
        """
        Create a withdrawal transaction.

        Args:
            db: Database session
            user_id: Account holder ID
            request: Withdrawal request

        Returns:
            Transaction: Created transaction

        Raises:
            AccountNotFoundError: If account doesn't exist
            UnauthorizedError: If user doesn't own the account
            InsufficientFundsError: If insufficient balance
        """
        # Verify account ownership
        account = db.query(Account).filter(Account.id == request.account_id).first()
        if not account:
            raise AccountNotFoundError()
        if account.account_holder_id != user_id:
            raise UnauthorizedError("Access denied to this account")

        # Check sufficient funds
        if account.balance < request.amount:
            raise InsufficientFundsError(
                f"Insufficient funds. Balance: ${account.balance}, Requested: ${request.amount}"
            )

        # Create transaction
        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            account_id=request.account_id,
            transaction_type="withdrawal",
            amount=request.amount,
            description=request.description
        )

        # Update account balance
        account.balance -= request.amount

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        logger.info(f"Withdrawal: ${request.amount} from account {account.account_number}")
        return transaction

    @staticmethod
    def create_transfer(db: Session, user_id: int, request: TransferRequest) -> Transaction:
        """
        Create a transfer transaction.

        Args:
            db: Database session
            user_id: Account holder ID
            request: Transfer request

        Returns:
            Transaction: Created transaction
        """
        # Get source account
        from_account = db.query(Account).filter(Account.id == request.from_account_id).first()
        if not from_account:
            raise AccountNotFoundError("Source account not found")
        if from_account.account_holder_id != user_id:
            raise UnauthorizedError("Access denied to source account")

        # Check sufficient funds
        if from_account.balance < request.amount:
            raise InsufficientFundsError()

        # Create outgoing transaction
        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            account_id=request.from_account_id,
            transaction_type="transfer",
            amount=request.amount,
            peer_routing_number=request.to_routing_number,
            peer_account_number=request.to_account_number,
            description=request.description
        )

        # Deduct from source
        from_account.balance -= request.amount

        # If internal transfer (same routing number), credit destination
        if request.to_routing_number == settings.routing_number:
            to_account = db.query(Account).filter(
                Account.account_number == request.to_account_number
            ).first()

            if to_account:
                # Create incoming transaction
                incoming_transaction = Transaction(
                    transaction_id=str(uuid.uuid4()),
                    account_id=to_account.id,
                    transaction_type="transfer",
                    amount=request.amount,
                    peer_routing_number=settings.routing_number,
                    peer_account_number=from_account.account_number,
                    description=f"Transfer from {from_account.account_number}"
                )
                to_account.balance += request.amount
                db.add(incoming_transaction)

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        logger.info(f"Transfer: ${request.amount} from {from_account.account_number} to {request.to_account_number}")
        return transaction

    @staticmethod
    def get_transactions(db: Session, user_id: int, account_id: Optional[int] = None) -> List[Transaction]:
        """
        Get transactions for user (optionally filtered by account).

        Args:
            db: Database session
            user_id: Account holder ID
            account_id: Optional account ID filter

        Returns:
            List[Transaction]: Transactions
        """
        # Get user's account IDs
        account_ids = [acc.id for acc in db.query(Account).filter(
            Account.account_holder_id == user_id
        ).all()]

        query = db.query(Transaction).filter(Transaction.account_id.in_(account_ids))

        if account_id:
            # Verify ownership
            if account_id not in account_ids:
                raise UnauthorizedError("Access denied to this account")
            query = query.filter(Transaction.account_id == account_id)

        return query.order_by(Transaction.created_at.desc()).all()
