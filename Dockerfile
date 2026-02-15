# Use official lightweight Python image
FROM python:3.11-slim

# Prevent Python from writing pyc files
# ENV PYTHONDONTWRITEBYTECODE=1

# Prevent Python from buffering stdout/stderr
# ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

COPY requirements.txt .
#
# # Install system dependencies (if needed later)
# RUN apt-get update && apt-get install -y build-essential \
#     && rm -rf /var/lib/apt/lists/*
#
# # Copy requirements first (better caching)
# COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirments.txt

COPY . .
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8080"]
#
# # Copy project
# COPY ./app ./app
#
# # Expose port
# EXP