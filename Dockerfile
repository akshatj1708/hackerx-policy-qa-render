# Stage 1: Build stage with minimal Alpine base
FROM python:3.10-alpine as builder

WORKDIR /app

# Install build dependencies and upgrade pip
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    py3-pip && \
    pip install --upgrade pip

# Install Python dependencies with optimized flags
COPY requirements-optimized.txt .
RUN pip install --no-cache-dir --user -r requirements-optimized.txt

# Clean up build dependencies
RUN apk del .build-deps

# Stage 2: Final stage
FROM python:3.10-alpine

WORKDIR /app

# Install runtime dependencies
RUN apk add --no-cache libstdc++

# Copy only the necessary files from the builder stage
COPY --from=builder /root/.local /root/.local
COPY . .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=0 \
    PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128 \
    PYTORCH_NO_CUDA_MEMORY_CACHING=1

# Clean up Python cache
RUN find /usr/local -type d -name "__pycache__" -exec rm -r {} + \
    && find /usr/local -name "*.pyc" -delete \
    && find /root/.local -type d -name "__pycache__" -exec rm -r {} + \
    && find /root/.local -name "*.pyc" -delete

# Expose the port the app runs on
EXPOSE $PORT

# Command to run the application with optimized Gunicorn settings
CMD ["gunicorn", "main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:$PORT", "--timeout", "120"]
