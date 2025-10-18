#!/bin/bash

# Demo script for EEG Authentication System
# This script demonstrates the complete pipeline on CPU with fast mode

set -e  # Exit on error

echo "=========================================="
echo "EEG Authentication System - Demo Script"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Setup virtual environment
echo -e "\n${BLUE}Step 1: Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "Virtual environment created"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "Virtual environment activated"

# Step 2: Install dependencies
echo -e "\n${BLUE}Step 2: Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}Dependencies installed${NC}"

# Step 3: Data preparation (instructions only - user should have data)
echo -e "\n${BLUE}Step 3: Data preparation${NC}"
echo "Expected data structure:"
echo "  data/raw/s01.bdf"
echo "  data/raw/s02.bdf"
echo "  ..."
echo "  data/raw/s10.bdf"
echo ""
echo "If you don't have the data, download from DEAP dataset:"
echo "  https://www.eecs.qmul.ac.uk/mmv/datasets/deap/"
echo ""
read -p "Press Enter to continue (assuming data is present)..."

# Step 4: Preprocessing (fast mode - only 3 trials per subject)
echo -e "\n${BLUE}Step 4: Preprocessing EEG data (fast mode)...${NC}"
python src/preprocessing.py \
    --input_dir data/raw \
    --output_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --fast \
    --n_channels 48 \
    --seed 42

echo -e "${GREEN}Preprocessing complete${NC}"

# Step 5: Training (demo mode - minimal epochs)
echo -e "\n${BLUE}Step 5: Training model (demo mode - reduced epochs)...${NC}"
python src/train.py \
    --data_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --batch_size 32 \
    --warmup_epochs 1 \
    --metric_epochs 2 \
    --lr 0.001 \
    --metric_loss proxyanchor \
    --use_attention \
    --n_channels 48 \
    --device cpu \
    --fast \
    --seed 42

echo -e "${GREEN}Training complete${NC}"

# Step 6: Evaluation
echo -e "\n${BLUE}Step 6: Evaluating model...${NC}"
python src/eval.py \
    --data_dir data/processed \
    --checkpoint checkpoints/best.ckpt \
    --prototypes models/prototypes.npz \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --batch_size 32 \
    --n_channels 48 \
    --device cpu \
    --output_dir outputs \
    --seed 42

echo -e "${GREEN}Evaluation complete. Results saved to outputs/${NC}"

# Step 7: Start backend server
echo -e "\n${BLUE}Step 7: Starting FastAPI backend...${NC}"
echo "Backend will run on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""
echo "API Endpoints:"
echo "  - POST /register - Register new user"
echo "  - POST /auth/login - Authenticate user"
echo "  - GET /explain/{id} - Get explanation"
echo "  - GET /health - Health check"
echo ""

# Run in background for demo
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Backend started with PID: $BACKEND_PID"
sleep 5  # Wait for server to start

# Step 8: Test authentication endpoint
echo -e "\n${BLUE}Step 8: Testing authentication endpoint...${NC}"

# Find a processed trial file for testing
TRIAL_FILE=$(find data/processed -name "s01_trial00.npy" | head -1)

if [ -f "$TRIAL_FILE" ]; then
    echo "Using trial file: $TRIAL_FILE"
    
    # Test health endpoint
    echo -e "\n${YELLOW}Testing health endpoint...${NC}"
    curl -X GET http://localhost:8000/health
    
    echo -e "\n\n${YELLOW}To test authentication, use:${NC}"
    echo "curl -X POST http://localhost:8000/auth/login \\"
    echo "  -F 'username=testuser' \\"
    echo "  -F 'password=testpass' \\"
    echo "  -F 'probe_trial=@$TRIAL_FILE'"
    echo ""
    echo "Note: You need to register a user first using /register endpoint"
else
    echo "No trial file found for testing"
fi

echo -e "\n${GREEN}=========================================="
echo "Demo setup complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Backend is running at http://localhost:8000"
echo "2. View API docs at http://localhost:8000/docs"
echo "3. Check evaluation results in outputs/"
echo "4. To stop backend: kill $BACKEND_PID"
echo ""
echo "For full training (30 epochs), run without --fast flag:"
echo "  python src/train.py --data_dir data/processed --subjects 1 2 3 4 5 6 7 8 9 10 --metric_epochs 30"
echo ""

# Keep script running
wait $BACKEND_PID
