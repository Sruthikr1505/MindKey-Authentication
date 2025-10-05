#!/bin/bash
set -e  # Exit on error

# Set Python version
export PYTHON_VERSION=3.9.16

# Create necessary directories
mkdir -p static
mkdir -p models
mkdir -p data/processed

# Set up Python environment
python -m pip install --upgrade pip
pip install -r requirements.txt

# Install production dependencies
pip install gunicorn uvicorn[standard] python-multipart python-jose[cryptography] passlib[bcrypt] pydantic[email] sqlalchemy alembic

# Build frontend
echo "Building frontend..."
cd frontend/eeg-auth-app
npm install --legacy-peer-deps
npm run build
cd ../..

# Move frontend build to static directory
cp -r frontend/eeg-auth-app/dist/* static/

# Set permissions
chmod -R 755 static
chmod -R 755 models

# Create a minimal essential model if it doesn't exist
if [ ! -f "models/essential_model.pt" ]; then
    echo "No essential model found. Creating a minimal one..."
    python -c "import torch; torch.save({'dummy': True}, 'models/essential_model.pt')
fi

echo "Build completed successfully!"
