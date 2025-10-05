# Dockerfile for EEG Authentication Backend
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for MNE
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libhdf5-dev \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY models/ ./models/
COPY data/ ./data/

# Create necessary directories
RUN mkdir -p outputs/explanations data/user_prototypes checkpoints

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run FastAPI with uvicorn
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
