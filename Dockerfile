# 1. Use a stable Python base image
FROM python:3.10-slim

# 2. Install system dependencies for Scipy, Postgres, and C-extensions
# These are required to build scipy and psycopg2 from source on Render
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    gfortran \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy requirements first (helps with faster builds/caching)
COPY requirements.txt .

# 5. Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy everything from your repo into the container
COPY . .

# 7. Start the FastAPI app 
# This points to the folder 'app' and the file 'main.py'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
