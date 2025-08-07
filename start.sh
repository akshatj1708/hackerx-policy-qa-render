#!/bin/bash

# Exit on error
set -e

# Install Python dependencies
pip install -r requirements.txt

# Run the FastAPI application
uvicorn main:app \
    --host 0.0.0.0 \
    --port ${PORT:-10000} \
    --workers ${WORKERS:-4} \
    --log-level info
