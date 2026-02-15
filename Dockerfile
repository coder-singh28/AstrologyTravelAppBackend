FROM python:3.11-slim

WORKDIR /app

# Install system deps (needed for psycopg2, cryptography etc.)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port (Railway will inject PORT)
EXPOSE 8080

# Use Railway dynamic PORT
CMD ["sh", "-c", "uvicorn app.application:app --host 0.0.0.0 --port $PORT"]
