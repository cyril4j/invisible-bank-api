"""
Generators for account numbers, card numbers, etc.
"""
import random
from sqlalchemy.orm import Session
from app.models.account import Account


def generate_account_number(db: Session) -> str:
    """
    Generate a unique 10-digit account number.

    Args:
        db: Database session for checking uniqueness

    Returns:
        str: Unique 10-digit account number
    """
    while True:
        number = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        # Check if number already exists
        existing = db.query(Account).filter(Account.account_number == number).first()
        if not existing:
            return number


def generate_card_number() -> str:
    """
    Generate a 16-digit card number compliant with Luhn algorithm.

    Returns:
        str: 16-digit card number
    """
    # Generate first 15 digits randomly
    digits = [random.randint(0, 9) for _ in range(15)]

    # Calculate Luhn checksum for the 16th digit
    checksum = 0
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 0:  # Every second digit from the right
            doubled = digit * 2
            checksum += doubled if doubled < 10 else doubled - 9
        else:
            checksum += digit

    check_digit = (10 - (checksum % 10)) % 10
    digits.append(check_digit)

    return ''.join(map(str, digits))
