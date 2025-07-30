FROM python:3.12-slim

# Add this line before running the app
COPY .env .env

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python packages (this includes nltk)
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK stopwords after nltk is installed
RUN python -m nltk.downloader stopwords

# Copy the rest of the app
COPY . .

# Start the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
