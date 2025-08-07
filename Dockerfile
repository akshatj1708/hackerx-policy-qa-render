# Stage 1: Build stage with minimal Debian
FROM python:3.10-slim as builder

WORKDIR /app

# Install minimal build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and use virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install only necessary build dependencies first
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install PyTorch CPU only first with specific index
RUN pip install --no-cache-dir torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu

# Install core dependencies first
RUN pip install --no-cache-dir \
    numpy==1.26.4 \
    safetensors==0.4.2 \
    huggingface-hub==0.21.4 \
    filelock==3.13.1

# Install remaining requirements
COPY requirements-optimized.txt .
RUN pip install --no-cache-dir -r requirements-optimized.txt

# Stage 2: Final stage - ultra-slim
FROM python:3.10-slim

WORKDIR /app

# Install only absolutely necessary runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only necessary application files
COPY main.py .
COPY .env.sample .

# Set environment variables with default values
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    PYTHONFAULTHANDLER=1

# Clean up Python cache
RUN find /usr/local -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true \
    && find /usr/local -name "*.pyc" -delete 2>/dev/null || true

# Create a start script to handle the PORT variable
RUN echo '#!/bin/sh\n\
set -e\n\n# Use the PORT environment variable if set, otherwise default to 8000\nPORT=${PORT:-8000}\n\n# Start Gunicorn with the specified port\nexec gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT' > /app/start.sh \
    && chmod +x /app/start.sh

# Expose the port the app runs on
EXPOSE $PORT

# Run the application using the start script
CMD ["/app/start.sh"]
