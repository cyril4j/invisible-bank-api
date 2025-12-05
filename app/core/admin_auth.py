"""
Basic HTTP authentication for admin portal.
"""
import secrets
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

# Hardcoded credentials (for demo purposes)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"


def verify_admin_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Verify admin credentials using HTTP Basic Authentication.

    Args:
        credentials: HTTP Basic credentials from request

    Returns:
        Username if valid

    Raises:
        HTTPException: If credentials are invalid
    """
    # Use secrets.compare_digest to prevent timing attacks
    is_username_correct = secrets.compare_digest(
        credentials.username.encode("utf8"), ADMIN_USERNAME.encode("utf8")
    )
    is_password_correct = secrets.compare_digest(
        credentials.password.encode("utf8"), ADMIN_PASSWORD.encode("utf8")
    )

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
