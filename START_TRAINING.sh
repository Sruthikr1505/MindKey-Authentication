#!/bin/bash
# Simple script to start training with your setup:
# 10 users × 40 trials × 48 channels → 50 metric epochs

set -e

echo "=========================================="
echo "Training: 10 Users × 40 Trials × 48 Ch"
echo "Target: 99% Accuracy with 50 Epochs"
echo "=========================================="
echo ""

# Step 1: Check data
echo "Step 1: Verifying data..."
FILE_COUNT=$(ls data/processed/*.npy 2>/dev/null | wc -l | tr -d ' ')
echo "✓ Found $FILE_COUNT processed files"

if [ "$FILE_COUNT" -ne 400 ]; then
    echo "⚠️  Warning: Expected 400 files (10 users × 40 trials), found $FILE_COUNT"
fi

# Step 2: Activate environment
echo ""
echo "Step 2: Setting up environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "✓ Virtual environment activated"

# Step 3: Install dependencies if needed
echo ""
echo "Step 3: Checking dependencies..."
if ! python -c "import torch" 2>/dev/null; then
    echo "Installing dependencies (this may take a few minutes)..."
    pip install -q -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

# Step 4: Check GPU
echo ""
echo "Step 4: Checking compute device..."
DEVICE=$(python3 << 'EOF'
import torch
if torch.cuda.is_available():
    print("cuda")
else:
    print("cpu")
EOF
)

if [ "$DEVICE" = "cuda" ]; then
    echo "✓ GPU available - training will be fast (~45-60 min)"
    BATCH_SIZE=64
else
    echo "✓ Using CPU - training will be slower (~3-4 hours)"
    BATCH_SIZE=32
fi

# Step 5: Verify channels
echo ""
echo "Step 5: Verifying channel count..."
python3 << 'EOF'
import numpy as np
data = np.load('data/processed/s01_trial00.npy')
n_channels = data.shape[0]
print(f"✓ Detected {n_channels} channels")
if n_channels != 48:
    print(f"⚠️  Warning: Expected 48 channels, found {n_channels}")
    print(f"   Training will use {n_channels} channels")
EOF

# Step 6: Start training
echo ""
echo "=========================================="
echo "Starting Enhanced Training"
echo "=========================================="
echo "Configuration:"
echo "  - Users: 10 (s01-s10)"
echo "  - Trials: 40 per user"
echo "  - Channels: 48"
echo "  - Warmup epochs: 5"
echo "  - Metric epochs: 50"
echo "  - Prototypes per user: 5"
echo "  - Device: $DEVICE"
echo "  - Batch size: $BATCH_SIZE"
echo ""

read -p "Press Enter to start training (or Ctrl+C to cancel)..."

echo ""
echo "Training started at $(date)"
echo ""

python train_enhanced.py \
    --data_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --batch_size $BATCH_SIZE \
    --warmup_epochs 5 \
    --metric_epochs 50 \
    --lr 5e-4 \
    --device $DEVICE \
    --k_prototypes 5 \
    --seed 42

echo ""
echo "Training completed at $(date)"
echo ""

# Step 7: Evaluate
echo "=========================================="
echo "Evaluating Model"
echo "=========================================="

python src/eval.py \
    --data_dir data/processed \
    --models_dir models_enhanced \
    --output_dir outputs_enhanced \
    --batch_size $BATCH_SIZE \
    --device $DEVICE

# Step 8: Display results
echo ""
echo "=========================================="
echo "FINAL RESULTS"
echo "=========================================="

python3 << 'EOF'
import json

try:
    with open('outputs_enhanced/eval_results.json', 'r') as f:
        results = json.load(f)
    
    eer = results['eer'] * 100
    accuracy = (1 - results['eer']) * 100
    genuine = results['genuine_scores_mean']
    impostor = results['impostor_scores_mean']
    separation = genuine - impostor
    
    print(f"EER:                    {eer:.2f}%")
    print(f"ACCURACY:               {accuracy:.2f}%")
    print(f"Genuine Score (mean):   {genuine:.4f}")
    print(f"Impostor Score (mean):  {impostor:.4f}")
    print(f"Separation:             {separation:.4f}")
    print("=" * 50)
    
    if accuracy >= 99.0:
        print("🎉 SUCCESS! Achieved 99%+ accuracy!")
    elif accuracy >= 98.5:
        print("✅ Excellent! Very close to 99%")
    elif accuracy >= 98.0:
        print("✅ Good improvement from baseline")
    else:
        print("⚠️  Below target. Consider:")
        print("   - Increase to 70 epochs")
        print("   - Try ensemble methods")
    
except FileNotFoundError:
    print("❌ Results file not found")
    print("Check for errors in training/evaluation logs above")
EOF

echo ""
echo "Models saved to: models_enhanced/"
echo "Results saved to: outputs_enhanced/"
echo ""
echo "View plots:"
echo "  open outputs_enhanced/roc.png"
echo "  open outputs_enhanced/det.png"
echo "  open outputs_enhanced/score_dist.png"
echo ""
