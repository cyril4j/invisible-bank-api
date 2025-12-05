"""
Admin service for dashboard data.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.account_holder import AccountHolder
from datetime import datetime


class AdminService:
    """Admin dashboard service."""

    @staticmethod
    def get_recent_accounts(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most recently created accounts.

        Args:
            db: Database session
            limit: Number of accounts to retrieve

        Returns:
            List of account dictionaries with holder information
        """
        accounts = (
            db.query(Account)
            .join(AccountHolder)
            .order_by(Account.created_at.desc())
            .limit(limit)
            .all()
        )

        result = []
        for account in accounts:
            result.append({
                "id": account.id,
                "account_number": account.account_number,
                "account_type": account.account_type,
                "balance": float(account.balance),
                "holder_name": account.account_holder.name,
                "holder_email": account.account_holder.email,
                "created_at": account.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "is_active": account.is_active
            })

        return result

    @staticmethod
    def get_recent_transactions(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most recent transactions in the system.

        Args:
            db: Database session
            limit: Number of transactions to retrieve

        Returns:
            List of transaction dictionaries with account information
        """
        transactions = (
            db.query(Transaction)
            .join(Account)
            .join(AccountHolder)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
            .all()
        )

        result = []
        for txn in transactions:
            result.append({
                "id": txn.id,
                "transaction_id": txn.transaction_id,
                "transaction_type": txn.transaction_type,
                "amount": float(txn.amount),
                "account_number": txn.account.account_number,
                "holder_name": txn.account.account_holder.name,
                "description": txn.description or "",
                "peer_account": txn.peer_account_number or "",
                "peer_routing": txn.peer_routing_number or "",
                "created_at": txn.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })

        return result

    @staticmethod
    def get_dashboard_stats(db: Session) -> Dict[str, Any]:
        """
        Get dashboard statistics.

        Args:
            db: Database session

        Returns:
            Dictionary with system statistics
        """
        total_accounts = db.query(Account).count()
        total_transactions = db.query(Transaction).count()
        total_users = db.query(AccountHolder).count()

        # Calculate total system balance
        total_balance = db.query(func.sum(Account.balance)).scalar() or 0

        return {
            "total_accounts": total_accounts,
            "total_transactions": total_transactions,
            "total_users": total_users,
            "total_balance": float(total_balance)
        }
