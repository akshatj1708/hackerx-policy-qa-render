#!/bin/bash

# Exit on error
set -e

# Set Python memory management variables
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Optimize Python memory management
export PYTHONHASHSEED=0  # Reproducible hashing
export PYTHONFAULTHANDLER=1  # Better error messages on crash

# Set PyTorch memory management
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:64
export TORCH_CUDA_ALLOC_CONF=max_split_size_mb:64

# Disable Numba JIT to save memory
export NUMBA_DISABLE_JIT=1

# Install Python dependencies with no-cache to save space
pip install --no-cache-dir -r requirements.txt

# Force single worker for Render free tier (memory optimization)
WORKER_COUNT=1

# Calculate available memory (in MB)
if [ -f /proc/meminfo ]; then
    TOTAL_MEM_MB=$(awk '/MemTotal/ {printf "%.0f", $2/1024}' /proc/meminfo)
    # Reserve some memory for the system
    WORKER_MEM_MB=$((TOTAL_MEM_MB - 200))
    # Ensure we have at least 100MB per worker
    if [ $WORKER_MEM_MB -lt 300 ]; then
        WORKER_MEM_MB=300
    fi
else
    # Default to 300MB if we can't detect memory
    WORKER_MEM_MB=300
fi

# Set memory limits for Python
export PYTHONMALLOC=malloc  # Use system malloc instead of pymalloc
export PYTHONMALLOCSTATS=1  # Enable memory allocation statistics

# Run the FastAPI application with optimized settings
echo "Starting server with $WORKER_COUNT worker(s) on port ${PORT:-10000} with ${WORKER_MEM_MB}MB memory per worker"

# Use gunicorn with uvicorn workers for better memory management
gunicorn main:app \
    --bind 0.0.0.0:${PORT:-10000} \
    --workers $WORKER_COUNT \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --keep-alive 30 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --worker-tmp-dir /dev/shm \
    --log-level info \
    --worker-connections 10 \
    --threads 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --preload  # Load application code before forking workers
