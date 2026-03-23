# 1. Use a stable Python base image
FROM python:3.10-slim

# 2. Install system dependencies for Scipy, Postgres, and C-extensions
# Required for your data science and DB libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    gfortran \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Set the working directory
WORKDIR /app

# 4. Copy requirements first for better caching
COPY requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy all files (including your 'app' folder)
COPY . .

# 7. Start the app
# IMPORTANT: This assumes your FastAPI variable in main.py is named 'app'
# If it is named 'main', change the end to 'app.main:main'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
