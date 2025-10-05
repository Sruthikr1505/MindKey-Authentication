#!/bin/bash
# Demo script for EEG Authentication System
# Runs preprocessing, training, and starts the API server

set -e  # Exit on error

echo "======================================"
echo "EEG Authentication System - Demo"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check if data exists
if [ ! -d "data/raw" ] || [ -z "$(ls -A data/raw/*.bdf 2>/dev/null)" ]; then
    echo -e "${YELLOW}Warning: No .bdf files found in data/raw/${NC}"
    echo "Please place DEAP subject files (s01.bdf - s10.bdf) in data/raw/"
    echo ""
    echo "To download DEAP dataset:"
    echo "1. Visit: https://www.eecs.qmul.ac.uk/mmv/datasets/deap/"
    echo "2. Request access and download the dataset"
    echo "3. Extract subject files to data/raw/"
    echo ""
    echo "Alternatively, for Kaggle (if available):"
    echo "  kaggle datasets download -d username/deap-dataset"
    echo "  (Requires ~/.kaggle/kaggle.json with API credentials)"
    echo ""
    read -p "Press Enter to continue with existing data or Ctrl+C to exit..."
fi

# Step 1: Preprocessing
echo ""
echo -e "${BLUE}Step 1: Preprocessing EEG data (fast mode)${NC}"
echo "Processing subjects 1-10 with first 3 trials each..."

python src/preprocessing.py \
    --input_dir data/raw \
    --output_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --fast \
    --fs_in 512 \
    --fs_out 128 \
    --seed 42

echo -e "${GREEN}✓ Preprocessing complete${NC}"

# Step 2: Training
echo ""
echo -e "${BLUE}Step 2: Training BiLSTM model (fast mode)${NC}"
echo "Running quick training with reduced epochs..."

python src/train.py \
    --data_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --batch_size 32 \
    --warmup_epochs 1 \
    --metric_epochs 2 \
    --lr 0.001 \
    --metric_loss proxyanchor \
    --use_attention \
    --fast \
    --device cpu \
    --seed 42

echo -e "${GREEN}✓ Training complete${NC}"

# Step 3: Evaluation (optional)
echo ""
read -p "Run evaluation? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Step 3: Evaluating model${NC}"
    
    python src/eval.py \
        --data_dir data/processed \
        --models_dir models \
        --output_dir outputs \
        --batch_size 32 \
        --device cpu \
        --seed 42
    
    echo -e "${GREEN}✓ Evaluation complete${NC}"
    echo "Results saved to outputs/"
fi

# Step 4: Start API server
echo ""
echo -e "${BLUE}Step 4: Starting FastAPI server${NC}"
echo "Server will be available at http://localhost:8000"
echo "API docs at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd src/api
python main.py

# Note: The script will stay running until Ctrl+C
