FROM python:3.11

WORKDIR /app

# Install required system dependencies + unzip
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    build-essential \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    proj-data \
    proj-bin \
    unzip \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Unzip safely (won't fail if not present)
RUN unzip -o static.zip || true

# Railway dynamic port support
#CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
ENV APP_ENV=prod
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

