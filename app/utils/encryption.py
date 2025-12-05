"""
Encryption utilities for sensitive data (SSN, card numbers).
Uses Fernet (AES-128 CBC) for symmetric encryption.
"""
from cryptography.fernet import Fernet
from app.config import settings


class EncryptionService:
    """Service for encrypting and decrypting sensitive data."""

    def __init__(self):
        """Initialize encryption cipher with key from settings."""
        self.cipher_suite = Fernet(settings.encryption_key.encode())

    def encrypt(self, plaintext: str) -> bytes:
        """
        Encrypt plaintext string to bytes.

        Args:
            plaintext: String to encrypt

        Returns:
            bytes: Encrypted data

        Example:
            >>> service = EncryptionService()
            >>> encrypted = service.encrypt("123-45-6789")
            >>> type(encrypted)
            <class 'bytes'>
        """
        return self.cipher_suite.encrypt(plaintext.encode())

    def decrypt(self, encrypted: bytes) -> str:
        """
        Decrypt bytes to plaintext string.

        Args:
            encrypted: Encrypted bytes

        Returns:
            str: Decrypted plaintext

        Raises:
            InvalidToken: If decryption fails (corrupted data or wrong key)

        Example:
            >>> service = EncryptionService()
            >>> encrypted = service.encrypt("123-45-6789")
            >>> service.decrypt(encrypted)
            '123-45-6789'
        """
        return self.cipher_suite.decrypt(encrypted).decode()


# Global encryption service instance
encryption_service = EncryptionService()
