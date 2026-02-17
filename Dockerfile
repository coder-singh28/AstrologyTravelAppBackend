FROM python:3.11-slim

WORKDIR /app

# Install unzip
RUN apt-get update && apt-get install -y unzip && rm -rf /var/lib/apt/lists/*

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY static.zip .

# Unzip
RUN unzip static.zip && rm static.zip

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
