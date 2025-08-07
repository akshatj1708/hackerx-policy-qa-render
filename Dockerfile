# Stage 1: Build stage with Debian slim
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    g++ \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with optimized flags
COPY requirements-optimized.txt .
RUN pip install --no-cache-dir --user -r requirements-optimized.txt

# Stage 2: Final stage
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy only the necessary files from the builder stage
COPY --from=builder /root/.local /root/.local
COPY . .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=0

# Clean up Python cache
RUN find /usr/local -type d -name "__pycache__" -exec rm -r {} + \
    && find /usr/local -name "*.pyc" -delete \
    && find /root/.local -type d -name "__pycache__" -exec rm -r {} + \
    && find /root/.local -name "*.pyc" -delete

# Expose the port the app runs on
EXPOSE $PORT

# Command to run the application with optimized Gunicorn settings
CMD ["gunicorn", "main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:$PORT", "--timeout", "120"]
