FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY .env .env

# Create runtime directories
RUN mkdir -p runtime/log runtime/certs

# Generate self-signed certificates for development
RUN openssl req -x509 -newkey rsa:4096 -nodes \
    -out runtime/certs/cert.pem \
    -keyout runtime/certs/key.pem \
    -days 365 \
    -subj "/C=US/ST=State/L=City/O=Invisible Bank/CN=localhost"

# Initialize database
RUN python scripts/init_db.py

# Expose HTTPS port
EXPOSE 8443

# Start server
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8443", \
     "--ssl-keyfile", "./runtime/certs/key.pem", \
     "--ssl-certfile", "./runtime/certs/cert.pem"]
