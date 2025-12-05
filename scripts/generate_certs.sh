#!/bin/bash
# Generate self-signed TLS certificates for local development

set -e

CERT_DIR="./runtime/certs"
CERT_FILE="${CERT_DIR}/cert.pem"
KEY_FILE="${CERT_DIR}/key.pem"

echo "Generating self-signed TLS certificates for local development..."

# Create certs directory if it doesn't exist
mkdir -p "${CERT_DIR}"

# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes \
    -out "${CERT_FILE}" \
    -keyout "${KEY_FILE}" \
    -days 365 \
    -subj "/C=US/ST=State/L=City/O=Invisible Bank/CN=localhost"

echo "✓ Certificates generated successfully:"
echo "  - Certificate: ${CERT_FILE}"
echo "  - Private Key: ${KEY_FILE}"
echo ""
echo "Note: These are self-signed certificates for development only."
echo "Browsers will show security warnings. For production, use proper CA-signed certificates."
