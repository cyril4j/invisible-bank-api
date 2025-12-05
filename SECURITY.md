# Security Considerations

## Overview

This document outlines the security measures implemented in the Invisible Bank API and provides guidelines for maintaining a secure production deployment.

## Current Security Implementations

### 1. Authentication & Authorization

#### JWT Token-Based Authentication
- **Access Tokens**: 15-minute expiration (configurable)
- **Refresh Tokens**: 7-day expiration (configurable)
- **Algorithm**: HMAC-SHA256 (HS256)
- **Token Storage**: Client-side only (never stored server-side in current implementation)

**Security Considerations:**
- ✅ Short-lived access tokens minimize exposure window
- ✅ Refresh tokens allow session extension without re-authentication
- ⚠️ **Production Requirement**: Implement token blacklisting for logout
- ⚠️ **Production Requirement**: Consider using asymmetric keys (RS256) for microservices

#### Password Security
- **Algorithm**: Argon2id (via passlib)
- **Characteristics**:
  - Memory-hard algorithm resistant to GPU attacks
  - Automatic salt generation
  - Cost parameters automatically managed
  - Industry-standard recommended by OWASP

**Configuration:**
```python
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
```

**Security Measures:**
- ✅ Passwords never stored in plaintext
- ✅ Passwords never logged or transmitted except during initial authentication
- ✅ Minimum password length: 8 characters
- ⚠️ **Recommendation**: Implement password complexity requirements

### 2. Data Encryption

#### Encryption at Rest

**SSN (Social Security Numbers):**
- **Algorithm**: Fernet (AES-128 in CBC mode)
- **Storage**: Binary blob in database
- **Key Management**: Environment variable (development)

**Card Numbers:**
- **Algorithm**: Fernet (AES-128 in CBC mode)
- **Storage**: Binary blob in database
- **Display**: Only last 4 digits exposed in API responses
- **Key Management**: Environment variable (development)

**Implementation:**
```python
class EncryptionService:
    def __init__(self):
        self.cipher_suite = Fernet(settings.encryption_key.encode())

    def encrypt(self, plaintext: str) -> bytes:
        return self.cipher_suite.encrypt(plaintext.encode())

    def decrypt(self, encrypted: bytes) -> str:
        return self.cipher_suite.decrypt(encrypted).decode()
```

**Security Considerations:**
- ✅ Sensitive data encrypted before storage
- ✅ Encryption keys separated from application code
- ⚠️ **Critical for Production**: Implement proper key rotation strategy
- ⚠️ **Critical for Production**: Use AWS KMS, Azure Key Vault, or HashiCorp Vault

#### Encryption in Transit

**TLS/HTTPS:**
- **Protocol**: TLS 1.2+ (enforced via Uvicorn)
- **Certificates**: Self-signed (development), CA-signed required (production)
- **Port**: 8443 (HTTPS)
- **Headers**: HSTS enabled with 1-year max-age

**Configuration:**
```python
response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
```

**Security Measures:**
- ✅ All endpoints served over HTTPS
- ✅ HTTP connections not supported
- ✅ HSTS prevents protocol downgrade attacks
- ⚠️ **Production Requirement**: Obtain proper CA-signed certificates (Let's Encrypt recommended)

### 3. OWASP Top 10 Protection

#### A01:2021 – Broken Access Control
**Protections Implemented:**
- ✅ JWT-based authentication required for sensitive endpoints
- ✅ Ownership validation on all resource access (accounts, transactions, cards)
- ✅ User can only access their own data
- ✅ Foreign key constraints enforce data relationships

**Example:**
```python
def get_account(db: Session, account_id: int, user_id: int):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise NotFoundError("Account not found")
    if account.account_holder_id != user_id:
        raise UnauthorizedError("Access denied")
    return account
```

#### A02:2021 – Cryptographic Failures
**Protections Implemented:**
- ✅ Argon2 for password hashing (not MD5/SHA1)
- ✅ Fernet (AES) for sensitive data encryption
- ✅ TLS for data in transit
- ✅ Secure random number generation for tokens
- ⚠️ **Production Gap**: Key rotation not implemented
- ⚠️ **Production Gap**: Hardware Security Module (HSM) not used

#### A03:2021 – Injection
**Protections Implemented:**
- ✅ SQLAlchemy ORM with parameterized queries
- ✅ No raw SQL queries in codebase
- ✅ Pydantic validation on all inputs
- ✅ Type checking and validation

**Example:**
```python
# Safe - parameterized query via ORM
user = db.query(AccountHolder).filter(
    AccountHolder.email == request.email
).first()

# NEVER do this (vulnerable to SQL injection):
# db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

#### A04:2021 – Insecure Design
**Protections Implemented:**
- ✅ Principle of least privilege (users only access own resources)
- ✅ Separation of concerns (models, services, controllers)
- ✅ Input validation at API boundary
- ✅ Business logic validation in service layer
- ✅ Rate limiting to prevent abuse

#### A05:2021 – Security Misconfiguration
**Protections Implemented:**
- ✅ Security headers (HSTS, X-Frame-Options, X-Content-Type-Options)
- ✅ Debug mode disabled in production (via environment variable)
- ✅ API documentation disabled in production
- ✅ Detailed error messages only in development
- ✅ Environment-based configuration

**Security Headers:**
```python
response.headers["X-Content-Type-Options"] = "nosniff"
response.headers["X-Frame-Options"] = "DENY"
response.headers["X-XSS-Protection"] = "1; mode=block"
response.headers["Strict-Transport-Security"] = "max-age=31536000"
```

#### A06:2021 – Vulnerable and Outdated Components
**Protections Implemented:**
- ✅ Modern framework versions (FastAPI, Pydantic, SQLAlchemy)
- ✅ Security-focused libraries (passlib, cryptography, python-jose)
- ✅ Requirements pinned to specific versions
- ⚠️ **Recommendation**: Regular dependency updates and vulnerability scanning

**Dependency Management:**
```bash
# Check for vulnerabilities
pip install safety
safety check -r requirements.txt

# Update dependencies
pip-review --auto
```

#### A07:2021 – Identification and Authentication Failures
**Protections Implemented:**
- ✅ Strong password hashing (Argon2)
- ✅ Token-based authentication with expiration
- ✅ No session fixation vulnerabilities (stateless JWT)
- ⚠️ **Missing**: Multi-factor authentication (MFA)
- ⚠️ **Missing**: Account lockout after failed attempts
- ⚠️ **Missing**: Password reset functionality

#### A08:2021 – Software and Data Integrity Failures
**Protections Implemented:**
- ✅ Signed JWT tokens prevent tampering
- ✅ Database constraints ensure data integrity
- ✅ Transaction atomicity (database transactions)
- ⚠️ **Missing**: Code signing
- ⚠️ **Missing**: Dependency verification (checksums)

#### A09:2021 – Security Logging and Monitoring Failures
**Protections Implemented:**
- ✅ Structured JSON logging with trace IDs
- ✅ All authentication attempts logged
- ✅ All transactions logged with context
- ✅ Error conditions logged with stack traces
- ✅ Request/response logging with duration
- ⚠️ **Missing**: Real-time alerting
- ⚠️ **Missing**: Security event correlation
- ⚠️ **Missing**: Log aggregation and analysis

**Logging Example:**
```python
logger.info(
    "User logged in",
    extra={
        "trace_id": get_request_id(),
        "user_id": user.id,
        "email": user.email,
        "ip_address": request.client.host
    }
)
```

#### A10:2021 – Server-Side Request Forgery (SSRF)
**Protections Implemented:**
- ✅ No external URL fetching based on user input
- ✅ Internal transfers validated against own routing number
- ⚠️ **If implementing**: Whitelist allowed external services

### 4. Additional Security Measures

#### Rate Limiting
**Implementation:** SlowAPI
**Limits:**
- Default: 60 requests per minute per IP
- Configurable via environment variable
- Applied globally to all endpoints

**Configuration:**
```python
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@limiter.limit("5/minute")
@app.post("/auth/login")
async def login(request: Request, ...):
    ...
```

**Recommendations:**
- ✅ Prevents brute force attacks
- ✅ Mitigates DoS attacks
- ⚠️ **Production**: Implement Redis-based rate limiting for distributed systems
- ⚠️ **Production**: Different limits for authenticated vs. unauthenticated users

#### CORS (Cross-Origin Resource Sharing)
**Configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Configured via .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Security Considerations:**
- ✅ Origins whitelist configured via environment
- ⚠️ **Production**: Restrict to specific origins (not wildcard)
- ⚠️ **Production**: Limit allowed methods to required ones only

#### Request Validation
**Pydantic Schemas:**
- All request bodies validated
- Type checking enforced
- Custom validators for business rules
- Automatic error responses for invalid data

**Example:**
```python
class SignupRequest(BaseModel):
    email: EmailStr  # Validates email format
    ssn: str = Field(..., description="Format: XXX-XX-XXXX")

    @validator('ssn')
    def validate_ssn_format(cls, v):
        if not validate_ssn(v):
            raise ValueError('SSN must be in format XXX-XX-XXXX')
        return v
```

## Known Security Gaps (For Production)

### Critical (Must Fix Before Production)

1. **Key Management**
   - **Current**: Encryption keys in .env file
   - **Required**: AWS KMS, Azure Key Vault, or HashiCorp Vault
   - **Impact**: High - key compromise exposes all encrypted data

2. **Database**
   - **Current**: SQLite (file-based)
   - **Required**: PostgreSQL with proper access controls
   - **Impact**: High - SQLite not designed for production

3. **Token Blacklisting**
   - **Current**: No logout mechanism
   - **Required**: Redis-based token blacklist
   - **Impact**: Medium - compromised tokens valid until expiration

4. **TLS Certificates**
   - **Current**: Self-signed certificates
   - **Required**: CA-signed certificates (Let's Encrypt)
   - **Impact**: High - prevents MITM attacks

### High Priority (Should Implement)

5. **Multi-Factor Authentication (MFA)**
   - **Impact**: High - additional authentication layer
   - **Recommendation**: TOTP (Google Authenticator, Authy)

6. **Account Lockout**
   - **Impact**: Medium - prevents brute force attacks
   - **Recommendation**: Lock after 5 failed attempts, 15-minute cooldown

7. **Password Reset**
   - **Impact**: Medium - account recovery mechanism
   - **Recommendation**: Time-limited tokens sent via email

8. **Audit Logging**
   - **Impact**: High - compliance and forensics
   - **Recommendation**: Immutable audit trail for all sensitive operations

9. **API Rate Limiting (Enhanced)**
   - **Impact**: Medium - better DoS protection
   - **Recommendation**: Redis-based, per-endpoint limits

10. **Input Sanitization**
    - **Impact**: Medium - XSS prevention
    - **Recommendation**: HTML/script tag stripping

### Medium Priority (Nice to Have)

11. **Web Application Firewall (WAF)**
    - **Recommendation**: AWS WAF, Cloudflare
    - **Benefit**: Additional layer against common attacks

12. **DDoS Protection**
    - **Recommendation**: Cloudflare, AWS Shield
    - **Benefit**: Service availability

13. **Security Scanning**
    - **Recommendation**: OWASP ZAP, Burp Suite, Snyk
    - **Benefit**: Automated vulnerability detection

14. **Penetration Testing**
    - **Recommendation**: Annual third-party pentests
    - **Benefit**: Real-world attack simulation

## Security Best Practices for Deployment

### Environment Variables
```bash
# NEVER commit these to version control
SECRET_KEY=<generated-secret>
ENCRYPTION_KEY=<generated-key>

# Use different keys for each environment
# Development, Staging, Production should have unique keys
```

### Key Generation
```bash
# JWT Secret Key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Encryption Key (Fernet)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Database Security
```sql
-- Use dedicated database user with minimal privileges
CREATE USER bank_api WITH PASSWORD 'secure_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO bank_api;
-- NO DROP, CREATE, ALTER privileges
```

### Network Security
```bash
# Firewall rules (example for AWS Security Groups)
# HTTPS only, specific IP ranges
Inbound:
  - Port 8443 (HTTPS): 0.0.0.0/0 (or specific IPs)
  - Port 22 (SSH): <admin-ip>/32

Outbound:
  - All traffic (or specific as needed)
```

### Monitoring & Alerting
```python
# Critical events to monitor:
- Failed login attempts (> 5 in 5 minutes)
- Unusual transaction patterns
- High error rates
- Slow response times
- Certificate expiration (< 30 days)
- Disk space (> 80% full)
```

## Incident Response Plan

### Security Breach Response

1. **Immediate Actions**
   - Isolate affected systems
   - Revoke all active tokens (if token blacklist implemented)
   - Change all secrets and encryption keys
   - Review logs for extent of breach

2. **Investigation**
   - Identify attack vector
   - Determine data accessed/exfiltrated
   - Timeline reconstruction using logs
   - Preserve evidence for forensics

3. **Remediation**
   - Patch vulnerabilities
   - Force password resets for affected users
   - Re-encrypt sensitive data with new keys
   - Deploy fixes

4. **Communication**
   - Notify affected users (if PII compromised)
   - Comply with data breach notification laws
   - Update security documentation

5. **Post-Mortem**
   - Document lessons learned
   - Implement preventive measures
   - Update incident response procedures

## Compliance Considerations

### PCI DSS (Payment Card Industry Data Security Standard)
**Relevant Requirements:**
- ✅ Requirement 3: Protect stored cardholder data (encryption implemented)
- ✅ Requirement 4: Encrypt transmission of cardholder data (TLS)
- ✅ Requirement 6: Develop secure systems (OWASP compliance)
- ✅ Requirement 8: Identify and authenticate access (JWT)
- ⚠️ Requirement 10: Track and monitor access (partial - needs enhancement)

### GDPR (General Data Protection Regulation)
**Considerations:**
- ✅ Data encryption (at rest and in transit)
- ✅ Access controls (authorization)
- ⚠️ Right to erasure (account deletion implemented, but need data purging)
- ⚠️ Data breach notification (need process)
- ⚠️ Privacy by design (good foundation, needs enhancement)

### SOC 2 (Service Organization Control 2)
**Trust Service Criteria:**
- ✅ Security (encryption, access controls)
- ✅ Availability (logging, monitoring foundation)
- ⚠️ Processing Integrity (needs validation)
- ⚠️ Confidentiality (good, needs enhancement)
- ⚠️ Privacy (needs data handling policies)

## Security Testing

### Automated Testing
```bash
# Dependency vulnerability scanning
pip install safety
safety check -r requirements.txt

# Static analysis
pip install bandit
bandit -r app/

# Secret scanning
pip install detect-secrets
detect-secrets scan
```

### Manual Testing Checklist
- [ ] SQL injection attempts
- [ ] XSS payload injection
- [ ] JWT token tampering
- [ ] CSRF token bypass
- [ ] Unauthorized access attempts
- [ ] Rate limiting effectiveness
- [ ] Password strength enforcement
- [ ] Session timeout verification

## Security Contacts

For security issues or vulnerabilities:
1. **DO NOT** create public GitHub issues
2. Email security concerns to: security@invisiblebank.com (configure)
3. Include: Description, steps to reproduce, impact assessment

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-05 | Initial security documentation |

## References

- [OWASP Top 10 2021](https://owasp.org/www-project-top-ten/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [PCI DSS Requirements](https://www.pcisecuritystandards.org/)
- [GDPR Compliance](https://gdpr.eu/)
