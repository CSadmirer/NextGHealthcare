# 1. Use a stable Python base image
FROM python:3.10-slim

# 2. Install system dependencies for Scipy, Postgres, and C-extensions
# These are required to build your heavy math/DB libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    gfortran \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Set the working directory
# We set this to / so that 'import app.core' works correctly
WORKDIR /

# 4. Copy requirements first for better caching
COPY requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy all files into the container
COPY . .

# 7. Start the app
# We use 'app.main:app' because your FastAPI instance is 'app' 
# inside the file 'app/main.py'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
