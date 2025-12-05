"""
Statement service for generating account statements.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.account import Account
from app.models.transaction import Transaction
from app.schemas.statement import Statement, AccountStatement, StatementTransaction


class StatementService:
    """Statement generation service."""

    @staticmethod
    def get_user_statement(db: Session, user_id: int, days: int = 30) -> Statement:
        """
        Generate statement for all user accounts.

        Args:
            db: Database session
            user_id: Account holder ID
            days: Number of days to include (default: 30)

        Returns:
            Statement: Complete statement
        """
        # Get all accounts for user
        accounts = db.query(Account).filter(
            Account.account_holder_id == user_id
        ).all()

        period_start = datetime.utcnow() - timedelta(days=days)
        period_end = datetime.utcnow()

        account_statements = []
        total_transactions = 0

        for account in accounts:
            # Get transactions for this account in the period
            transactions = db.query(Transaction).filter(
                Transaction.account_id == account.id,
                Transaction.created_at >= period_start
            ).order_by(Transaction.created_at.desc()).all()

            # Convert to statement transactions
            statement_transactions = [
                StatementTransaction(
                    transaction_id=t.transaction_id,
                    transaction_type=t.transaction_type,
                    amount=t.amount,
                    description=t.description,
                    created_at=t.created_at
                )
                for t in transactions
            ]

            account_statements.append(AccountStatement(
                account_id=account.id,
                account_number=account.account_number,
                account_type=account.account_type,
                balance=account.balance,
                transactions=statement_transactions
            ))

            total_transactions += len(transactions)

        return Statement(
            period_start=period_start,
            period_end=period_end,
            accounts=account_statements,
            total_transactions=total_transactions
        )
