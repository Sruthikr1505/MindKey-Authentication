#!/bin/bash
# Fast Training (30 epochs)
# Use this when you need results quickly
# Expected: 98-98.5% accuracy
# Time: 2-3 hours on MPS

set -e

echo "=========================================="
echo "FAST TRAINING (30 EPOCHS)"
echo "Target: 98-98.5% accuracy"
echo "Time: 2-3 hours"
echo "=========================================="
echo ""

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "❌ Virtual environment not found!"
    exit 1
fi

echo ""
echo "Configuration:"
echo "  - Users: 10 (s01-s10)"
echo "  - Batch size: 64"
echo "  - Warmup epochs: 5"
echo "  - Metric epochs: 30 (FAST)"
echo "  - Prototypes: 5 per user"
echo "  - Device: Auto-detect (MPS/CUDA/CPU)"
echo ""

read -p "Start fast training? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Training cancelled."
    exit 0
fi

echo ""
echo "=========================================="
echo "Training Started: $(date)"
echo "Expected completion: ~2-3 hours"
echo "=========================================="
echo ""

# Run training
python train_enhanced.py \
    --data_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --batch_size 64 \
    --warmup_epochs 5 \
    --metric_epochs 30 \
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
    
    print(f"EER:                    {eer:.2f}%")
    print(f"ACCURACY:               {accuracy:.2f}%")
    print(f"Genuine Score:          {results['genuine_scores_mean']:.4f}")
    print(f"Impostor Score:         {results['impostor_scores_mean']:.4f}")
    print("=" * 50)
    
    if accuracy >= 98.5:
        print("🎉 Excellent! 98.5%+ accuracy!")
    elif accuracy >= 98.0:
        print("✅ Great! 98%+ accuracy!")
    else:
        print(f"✓ Accuracy: {accuracy:.2f}%")
        
except FileNotFoundError:
    print("❌ Results file not found")
EOF

echo ""
echo "Models saved to: models_enhanced/"
echo "Results saved to: outputs_enhanced/"
echo ""
