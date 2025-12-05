"""
Custom exceptions for the banking API.
"""


class BankAPIException(Exception):
    """Base exception for all API errors."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(BankAPIException):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class UnauthorizedError(BankAPIException):
    """User not authorized for this action."""

    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message, status_code=403)


class NotFoundError(BankAPIException):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(BankAPIException):
    """Validation error."""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=422)


class InsufficientFundsError(BankAPIException):
    """Insufficient funds for transaction."""

    def __init__(self, message: str = "Insufficient funds"):
        super().__init__(message, status_code=400)


class AccountNotFoundError(NotFoundError):
    """Account not found."""

    def __init__(self, message: str = "Account not found"):
        super().__init__(message)


class TransactionError(BankAPIException):
    """Transaction processing error."""

    def __init__(self, message: str = "Transaction failed"):
        super().__init__(message, status_code=400)
