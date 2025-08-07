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

# Install PyTorch CPU only first
RUN pip install --no-cache-dir torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu

# Install other requirements
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

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    PYTHONFAULTHANDLER=1

# Clean up Python cache
RUN find /usr/local -type d -name "__pycache__" -exec rm -r {} + \
    && find /usr/local -name "*.pyc" -delete \
    && find /root/.local -type d -name "__pycache__" -exec rm -r {} + \
    && find /root/.local -name "*.pyc" -delete

# Expose the port the app runs on
EXPOSE $PORT

# Command to run the application with optimized Gunicorn settings
CMD ["gunicorn", "main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:$PORT", "--timeout", "120"]
