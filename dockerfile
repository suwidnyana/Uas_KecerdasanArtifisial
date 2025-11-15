# Gunakan base image Python slim
FROM python:3.11-slim

# Install dependencies yang dibutuhkan SciPy + scikit-fuzzy
RUN apt-get update && apt-get install -y \
    gfortran \
    build-essential \
    libatlas-base-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements terlebih dahulu (agar layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy seluruh source code
COPY . .

# Expose port untuk Railway
EXPOSE 5000

# Jalankan Flask
CMD ["python", "app.py"]
