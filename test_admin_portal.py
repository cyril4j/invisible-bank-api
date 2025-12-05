"""
Test script for admin portal.
"""
import asyncio
import sys
from httpx import AsyncClient
from app.main import app
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.services.auth_service import AuthService
from app.schemas.auth import SignupRequest
from app.schemas.account import AccountCreate
from app.schemas.transaction import DepositRequest
from app.services.account_service import AccountService
from app.services.transaction_service import TransactionService
from datetime import date


async def test_admin_portal():
    """Test admin portal with sample data."""

    # 1. Initialize database
    print("Initializing database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # 2. Create test data
    print("Creating test data...")
    db = SessionLocal()

    try:
        # Create 3 users with accounts
        for i in range(1, 4):
            signup = SignupRequest(
                name=f"Test User {i}",
                email=f"user{i}@test.com",
                password="password123",
                ssn=f"123-45-678{i}",
                date_of_birth=date(1990, 1, i),
                mailing_address=f"{i} Test Street, Test City, TS 12345"
            )
            token_response = AuthService.signup(db, signup)
            print(f"  Created user: {signup.email}")

            # Decode token to get user_id
            from app.core.security import decode_token
            payload = decode_token(token_response.access_token)
            user_id = payload["user_id"]

            # Create checking account
            checking = AccountCreate(account_type="checking")
            account = AccountService.create_account(db, user_id, checking)
            print(f"    Created checking account: {account.account_number}")

            # Create some deposits
            for j in range(1, 4):
                deposit = DepositRequest(
                    account_id=account.id,
                    amount=100.00 * j,
                    description=f"Test deposit {j}"
                )
                TransactionService.create_deposit(db, user_id, deposit)
            print(f"    Created 3 deposits")

    finally:
        db.close()

    # 3. Test admin endpoint
    print("\nTesting admin portal endpoint...")

    async with AsyncClient(app=app, base_url="https://test", verify=False) as client:
        # Test without authentication (should fail)
        print("  Testing without auth...")
        response = await client.get("/admin")
        print(f"    Status: {response.status_code} (expected 401)")

        # Test with wrong credentials
        print("  Testing with wrong credentials...")
        response = await client.get("/admin", auth=("wrong", "wrong"))
        print(f"    Status: {response.status_code} (expected 401)")

        # Test with correct credentials
        print("  Testing with correct credentials...")
        response = await client.get("/admin", auth=("admin", "admin"))
        print(f"    Status: {response.status_code} (expected 200)")

        if response.status_code == 200:
            print(f"    Response length: {len(response.text)} bytes")
            print(f"    Content type: {response.headers.get('content-type')}")

            # Check if HTML contains expected content
            html = response.text
            if "Admin Dashboard" in html:
                print("    ✓ Contains 'Admin Dashboard'")
            if "Total Users" in html:
                print("    ✓ Contains 'Total Users'")
            if "Recent Accounts" in html:
                print("    ✓ Contains 'Recent Accounts'")
            if "Recent Transactions" in html:
                print("    ✓ Contains 'Recent Transactions'")

            print("\n✅ Admin portal test PASSED!")
            return True
        else:
            print(f"\n❌ Admin portal test FAILED! Expected 200, got {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False


if __name__ == "__main__":
    result = asyncio.run(test_admin_portal())
    sys.exit(0 if result else 1)
