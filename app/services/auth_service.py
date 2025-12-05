"""
Authentication service for signup and login.
"""
from sqlalchemy.orm import Session
from app.models.account_holder import AccountHolder
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.utils.encryption import encryption_service
from app.core.exceptions import AuthenticationError, ValidationError
from app.core.logging_config import logger


class AuthService:
    """Authentication service."""

    @staticmethod
    def signup(db: Session, request: SignupRequest) -> TokenResponse:
        """
        Register a new user.

        Args:
            db: Database session
            request: Signup request data

        Returns:
            TokenResponse: Access and refresh tokens

        Raises:
            ValidationError: If email already exists
        """
        # Check if email already exists
        existing_user = db.query(AccountHolder).filter(
            AccountHolder.email == request.email
        ).first()

        if existing_user:
            raise ValidationError("Email already registered")

        # Hash password and encrypt SSN
        password_hash = hash_password(request.password)
        ssn_encrypted = encryption_service.encrypt(request.ssn)

        # Create new account holder
        account_holder = AccountHolder(
            name=request.name,
            email=request.email,
            password_hash=password_hash,
            ssn_encrypted=ssn_encrypted,
            date_of_birth=request.date_of_birth,
            mailing_address=request.mailing_address,
            is_active=True
        )

        db.add(account_holder)
        db.commit()
        db.refresh(account_holder)

        logger.info(f"New user registered: {account_holder.email}")

        # Create tokens
        token_data = {"user_id": account_holder.id, "email": account_holder.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    @staticmethod
    def login(db: Session, request: LoginRequest) -> TokenResponse:
        """
        Authenticate user and return tokens.

        Args:
            db: Database session
            request: Login request data

        Returns:
            TokenResponse: Access and refresh tokens

        Raises:
            AuthenticationError: If credentials are invalid
        """
        # Find user by email
        user = db.query(AccountHolder).filter(
            AccountHolder.email == request.email
        ).first()

        if not user or not user.is_active:
            raise AuthenticationError("Invalid email or password")

        # Verify password
        if not verify_password(request.password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        logger.info(f"User logged in: {user.email}")

        # Create tokens
        token_data = {"user_id": user.id, "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
