"""
Application configuration management using Pydantic Settings.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application Settings
    app_name: str = "Invisible Bank API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8443
    reload: bool = True

    # Security Keys
    secret_key: str
    encryption_key: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Database Configuration
    database_url: str

    # TLS/SSL Certificates
    ssl_cert_path: str = "./runtime/certs/cert.pem"
    ssl_key_path: str = "./runtime/certs/key.pem"

    # CORS Settings
    cors_origins: str = "http://localhost:3000,http://localhost:8080"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "./runtime/log/bank-api.log"

    # Bank Institution Details
    routing_number: str = "123456789"


# Global settings instance
settings = Settings()
