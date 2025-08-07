#!/bin/bash

# Exit on error
set -e

# Set Python memory management variables
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Install Python dependencies with no-cache to save space
pip install --no-cache-dir -r requirements.txt

# Calculate workers based on available CPU (but limit to 1 for free tier)
CPU_COUNT=$(nproc)
WORKER_COUNT=1  # Force single worker for Render free tier

# Set PyTorch memory management
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128

# Run the FastAPI application with optimized settings
echo "Starting server with $WORKER_COUNT worker(s) on port ${PORT:-10000}"
uvicorn main:app \
    --host 0.0.0.0 \
    --port ${PORT:-10000} \
    --workers $WORKER_COUNT \
    --limit-max-requests 1000 \
    --timeout-keep-alive 30 \
    --log-level info
