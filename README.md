# Invisible Bank API

A production-grade REST API for banking operations built with FastAPI, SQLAlchemy, and SQLite.

## Features

- **User Authentication**: JWT-based authentication with access and refresh tokens
- **Account Management**: Create and manage checking and savings accounts
- **Transactions**: Deposits, withdrawals, and transfers (internal and external)
- **Card Management**: Issue debit and credit cards
- **Statements**: Generate 30-day transaction statements
- **Security**:
  - Argon2 password hashing
  - AES-256 encryption for SSN and card numbers
  - TLS/HTTPS encryption
  - OWASP protection (SQL injection, XSS, CSRF, rate limiting)
  - Security headers (HSTS, X-Frame-Options, etc.)
- **Logging**: Structured JSON logging with daily rotation and trace IDs
- **Testing**: Comprehensive unit and integration tests
- **Docker**: Containerized deployment

## Technology Stack

- **Python 3.9+**
- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM
- **SQLite** - Database (development)
- **Pydantic 2.0** - Data validation
- **Passlib + Argon2** - Password hashing
- **Python-JOSE** - JWT tokens
- **Cryptography (Fernet)** - Data encryption
- **Pytest** - Testing framework
- **Docker** - Containerization

## Quick Start

### 1. Local Development

```bash
# Clone repository
git clone git@github.com:cyril4j/invisible-bank-api.git
cd invisible-bank-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Initialize database
python scripts/init_db.py

# Generate TLS certificates
bash scripts/generate_certs.sh

# Start server
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8443 \
    --reload \
    --ssl-keyfile ./runtime/certs/key.pem \
    --ssl-certfile ./runtime/certs/cert.pem
```

Access the API at: `https://localhost:8443`

### 2. Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `https://localhost:8443/docs`
- ReDoc: `https://localhost:8443/redoc`

## API Endpoints

### Authentication (Public)
- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens

### Accounts (Authenticated)
- `POST /api/v1/accounts` - Create account
- `GET /api/v1/accounts` - List user's accounts
- `GET /api/v1/accounts/{id}` - Get specific account

### Transactions (Authenticated)
- `POST /api/v1/transactions/deposit` - Deposit funds
- `POST /api/v1/transactions/withdraw` - Withdraw funds
- `POST /api/v1/transactions/transfer` - Transfer funds
- `GET /api/v1/transactions` - List transactions

### Cards (Authenticated)
- `POST /api/v1/cards` - Create card
- `GET /api/v1/cards` - List cards

### Statements (Authenticated)
- `GET /api/v1/statements` - Get 30-day statement

## Example Usage

### 1. Sign Up

```bash
curl -k -X POST https://localhost:8443/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "ssn": "123-45-6789",
    "date_of_birth": "1990-01-01",
    "mailing_address": "123 Main St, City, State 12345"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### 2. Create Account

```bash
curl -k -X POST https://localhost:8443/api/v1/accounts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "account_type": "checking"
  }'
```

### 3. Deposit Funds

```bash
curl -k -X POST https://localhost:8443/api/v1/transactions/deposit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "account_id": 1,
    "amount": 1000.00,
    "description": "Initial deposit"
  }'
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/integration/test_auth_endpoints.py

# View coverage report
open htmlcov/index.html
```

## Configuration

Environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret key | (required) |
| `ENCRYPTION_KEY` | Fernet encryption key | (required) |
| `DATABASE_URL` | Database connection string | `sqlite:///./runtime/bank.db` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ROUTING_NUMBER` | Bank routing number | `123456789` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiration | `15` |

## Security Features

### Data Encryption
- **SSN**: Encrypted at rest using Fernet (AES-128 CBC)
- **Card Numbers**: Encrypted at rest using Fernet
- **Passwords**: Hashed using Argon2 (never stored in plaintext)

### OWASP Protection
- ✅ SQL Injection: SQLAlchemy ORM with parameterized queries
- ✅ XSS: Proper content-type headers and JSON serialization
- ✅ CSRF: Double-submit cookie pattern
- ✅ Authentication: JWT tokens with expiration
- ✅ Rate Limiting: IP-based and user-based limits
- ✅ Security Headers: HSTS, X-Frame-Options, X-Content-Type-Options

### TLS/HTTPS
- All endpoints served over HTTPS
- Self-signed certificates for development (included)
- Production requires proper CA-signed certificates

## Database Schema

### Tables
- **account_holders**: User authentication and personal information
- **accounts**: Bank accounts (checking/savings)
- **transactions**: Deposits, withdrawals, transfers
- **cards**: Debit/credit cards

All tables include:
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

## Logging

Structured JSON logs with daily rotation:
- **Location**: `runtime/log/bank-api.log`
- **Format**: JSON with trace IDs for request correlation
- **Rotation**: Daily, keeps 30 days of logs
- **Content**: Request/response details, errors, transaction events

## Project Structure

```
invisible-bank-api/
├── app/
│   ├── api/v1/endpoints/    # API route handlers
│   ├── core/                # Security, logging, exceptions
│   ├── db/                  # Database session and models
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── services/            # Business logic
│   ├── utils/               # Utilities (encryption, validators, etc.)
│   ├── config.py            # Configuration management
│   ├── dependencies.py      # FastAPI dependencies
│   └── main.py              # FastAPI application
├── tests/
│   ├── integration/         # API integration tests
│   └── unit/                # Unit tests
├── scripts/
│   ├── generate_certs.sh    # Generate TLS certificates
│   └── init_db.py           # Initialize database
├── runtime/
│   ├── log/                 # Application logs
│   └── certs/               # TLS certificates
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

## Development

### Generate New Keys

```bash
# Secret key for JWT
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Encryption key for Fernet
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Reset Database

```bash
rm runtime/bank.db
python scripts/init_db.py
```

## Production Considerations

⚠️ **This implementation is for development/educational purposes. For production:**

1. **Database**: Migrate to PostgreSQL or MySQL
2. **TLS Certificates**: Use proper CA-signed certificates (Let's Encrypt)
3. **Key Management**: Use AWS KMS, HashiCorp Vault, or similar
4. **Environment Variables**: Never commit `.env` to version control
5. **Rate Limiting**: Implement Redis-based rate limiting
6. **Monitoring**: Add Prometheus metrics, Grafana dashboards
7. **Backup**: Implement automated database backups
8. **Load Balancing**: Use nginx or cloud load balancers
9. **API Gateway**: Consider AWS API Gateway or Kong

## License

This project is for educational purposes.

## Author

Built with FastAPI, SQLAlchemy, and production-grade security practices.
