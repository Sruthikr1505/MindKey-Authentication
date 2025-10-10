#!/bin/bash
# Quick script to run enhanced training for 99% accuracy
# This script includes all optimizations from REACH_99_PERCENT_GUIDE.md

set -e

echo "=========================================="
echo "Enhanced Training for 99% Accuracy"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if ! python -c "import torch" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if data exists
if [ ! -d "data/processed" ] || [ -z "$(ls -A data/processed)" ]; then
    echo "ERROR: No processed data found in data/processed/"
    echo "Please run preprocessing first:"
    echo "  python src/preprocessing.py --input_dir data/raw --output_dir data/processed"
    exit 1
fi

# Detect device
if python -c "import torch; print(torch.cuda.is_available())" | grep -q "True"; then
    DEVICE="cuda"
    echo "✓ GPU detected - using CUDA"
else
    DEVICE="cpu"
    echo "✓ Using CPU (training will be slower)"
fi

echo ""
echo "=========================================="
echo "Training Configuration:"
echo "=========================================="
echo "  - Model: Enhanced BiLSTM (3 layers, 256-dim)"
echo "  - Prototypes per user: 5 (increased from 2)"
echo "  - Warmup epochs: 5"
echo "  - Metric epochs: 50 (increased from 20)"
echo "  - Learning rate: 5e-4"
echo "  - Device: $DEVICE"
echo "  - Expected accuracy: 98-99%"
echo ""

read -p "Start enhanced training? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Training cancelled."
    exit 0
fi

echo ""
echo "=========================================="
echo "Phase 1: Enhanced Training"
echo "=========================================="

python train_enhanced.py \
    --data_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --batch_size 64 \
    --warmup_epochs 5 \
    --metric_epochs 50 \
    --lr 5e-4 \
    --device $DEVICE \
    --k_prototypes 5 \
    --seed 42

echo ""
echo "=========================================="
echo "Phase 2: Evaluation"
echo "=========================================="

python src/eval.py \
    --data_dir data/processed \
    --models_dir models_enhanced \
    --output_dir outputs_enhanced \
    --batch_size 64 \
    --device $DEVICE

echo ""
echo "=========================================="
echo "Phase 3: Results"
echo "=========================================="

if [ -f "outputs_enhanced/eval_results.json" ]; then
    echo "✓ Evaluation complete!"
    echo ""
    echo "Results saved to: outputs_enhanced/"
    echo ""
    
    # Extract and display key metrics
    python3 << EOF
import json
with open('outputs_enhanced/eval_results.json', 'r') as f:
    results = json.load(f)

eer = results['eer'] * 100
accuracy = (1 - results['eer']) * 100
genuine_mean = results['genuine_scores_mean']
impostor_mean = results['impostor_scores_mean']
separation = genuine_mean - impostor_mean

print("=" * 50)
print("PERFORMANCE METRICS")
print("=" * 50)
print(f"EER:                {eer:.2f}%")
print(f"Accuracy:           {accuracy:.2f}%")
print(f"Genuine Score:      {genuine_mean:.4f}")
print(f"Impostor Score:     {impostor_mean:.4f}")
print(f"Separation:         {separation:.4f}")
print("=" * 50)
print()

if accuracy >= 99.0:
    print("🎉 EXCELLENT! You've reached 99%+ accuracy!")
elif accuracy >= 98.5:
    print("✓ Great! You're very close to 99%.")
    print("  Consider ensemble methods for final boost.")
elif accuracy >= 98.0:
    print("✓ Good improvement! Try:")
    print("  - Increase metric_epochs to 70")
    print("  - Use ensemble of 3 models")
else:
    print("⚠ Accuracy below 98%. Check:")
    print("  - Data quality (48 channels present?)")
    print("  - Training logs for issues")
    print("  - Try different random seed")
EOF

    echo ""
    echo "View detailed results:"
    echo "  - ROC curve: outputs_enhanced/roc.png"
    echo "  - DET curve: outputs_enhanced/det.png"
    echo "  - Score distribution: outputs_enhanced/score_dist.png"
    echo ""
    
    # Optionally display images (macOS)
    if command -v open &> /dev/null; then
        read -p "Open result plots? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open outputs_enhanced/roc.png
            open outputs_enhanced/det.png
            open outputs_enhanced/score_dist.png
        fi
    fi
else
    echo "⚠ Evaluation results not found."
    echo "Check for errors in the training/evaluation logs above."
fi

echo ""
echo "=========================================="
echo "Training Complete!"
echo "=========================================="
echo ""
echo "Enhanced models saved to: models_enhanced/"
echo "  - encoder.pth (BiLSTM encoder)"
echo "  - prototypes.npz (5 prototypes per user)"
echo "  - spoof_model.pth (spoof detector)"
echo "  - calibrator.pkl (score calibrator)"
echo "  - config.json (model configuration)"
echo ""
echo "Next steps:"
echo "  1. Review results in outputs_enhanced/"
echo "  2. Test API with enhanced models"
echo "  3. Deploy if accuracy meets requirements"
echo ""
