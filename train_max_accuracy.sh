#!/bin/bash
# Maximum Accuracy Training (50+ epochs)
# Use this for final production model when you have time
# Expected: 98.5-99% accuracy
# Time: 4-5 hours on MPS

set -e

echo "=========================================="
echo "MAXIMUM ACCURACY TRAINING"
echo "Target: 98.5-99% accuracy"
echo "Time: 4-5 hours"
echo "=========================================="
echo ""

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "❌ Virtual environment not found!"
    echo "Run: python3 -m venv venv"
    exit 1
fi

# Check if data exists
if [ ! -d "data/processed" ] || [ -z "$(ls -A data/processed)" ]; then
    echo "❌ No processed data found!"
    echo "Run preprocessing first"
    exit 1
fi

echo ""
echo "Configuration:"
echo "  - Users: 10 (s01-s10)"
echo "  - Batch size: 64"
echo "  - Warmup epochs: 5"
echo "  - Metric epochs: 50 (MAXIMUM)"
echo "  - Prototypes: 5 per user"
echo "  - Device: Auto-detect (MPS/CUDA/CPU)"
echo ""

read -p "Start maximum accuracy training? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Training cancelled."
    exit 0
fi

echo ""
echo "=========================================="
echo "Training Started: $(date)"
echo "=========================================="
echo ""

# Run training with maximum settings
python train_enhanced.py \
    --data_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --batch_size 64 \
    --warmup_epochs 5 \
    --metric_epochs 50 \
    --lr 5e-4 \
    --k_prototypes 5 \
    --seed 42

echo ""
echo "=========================================="
echo "Training Completed: $(date)"
echo "=========================================="
echo ""

# Auto-evaluate
echo "Running evaluation..."
python src/eval.py \
    --data_dir data/processed \
    --models_dir models_enhanced \
    --output_dir outputs_enhanced \
    --batch_size 64 \
    --device mps

echo ""
echo "=========================================="
echo "RESULTS"
echo "=========================================="

# Display results
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
        print("🎉 EXCELLENT! Achieved 99%+ accuracy!")
    elif accuracy >= 98.5:
        print("✅ Great! 98.5%+ accuracy achieved!")
    elif accuracy >= 98.0:
        print("✅ Good! 98%+ accuracy achieved!")
    else:
        print(f"✓ Accuracy: {accuracy:.2f}%")
        
except FileNotFoundError:
    print("❌ Results file not found")
    print("Check for errors in training logs above")
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
