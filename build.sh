#!/bin/bash

# Install Git LFS
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt-get install -y git-lfs
git lfs install
git lfs pull

# Install Python dependencies
pip install -r requirements.txt

# Build frontend
cd frontend/eeg-auth-app
npm install
npm run build
cd ../..
