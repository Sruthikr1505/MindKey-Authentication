#!/bin/bash

# Set Python version
export PYTHON_VERSION=3.9.16

# Update pip and install Python dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn uvicorn[standard]

# Build frontend
cd frontend/eeg-auth-app
npm install
npm run build
cd ../..

# Create necessary directories
mkdir -p static
mkdir -p models

# Set permissions
chmod +x /opt/render/project/src/.venv/bin/*
