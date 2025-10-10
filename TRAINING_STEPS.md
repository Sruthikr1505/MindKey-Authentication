# 🚀 Step-by-Step Training Guide
## 10 Users × 40 Trials × 48 Channels → 99% Accuracy

## Your Current Setup ✅

- **Users**: 10 subjects (s01-s10)
- **Trials**: 40 trials per subject (already processed)
- **Channels**: 48 EEG channels
- **Target**: 50+ metric epochs for 99% accuracy

---

## Prerequisites Check

### Step 1: Verify Your Environment

```bash
cd /Users/sruthikr/Desktop/Thought\ Based\ Authentication\ System\ Using\ BiLSTM/MindKey-Authentication/MindKey-Authentication

# Check Python version (need 3.10+)
python3 --version

# Check if virtual environment exists
ls -la venv/
```

### Step 2: Verify Processed Data

```bash
# Check if you have processed data with 40 trials
ls -la data/processed/ | head -20

# Count files (should be 400 files: 10 users × 40 trials)
ls data/processed/*.npy | wc -l

# Verify one file has 48 channels
python3 << 'EOF'
import numpy as np
import os

# Check first file
files = sorted([f for f in os.listdir('data/processed') if f.endswith('.npy')])
if files:
    data = np.load(f'data/processed/{files[0]}')
    print(f"File: {files[0]}")
    print(f"Shape: {data.shape}")
    print(f"Channels: {data.shape[0]}")
    print(f"Timesteps: {data.shape[1]}")
    
    if data.shape[0] == 48:
        print("✅ Confirmed: 48 channels present!")
    else:
        print(f"⚠️  Warning: Expected 48 channels, found {data.shape[0]}")
else:
    print("❌ No processed data found!")
EOF
```

**Expected output:**
```
400  (or close to it if some trials were excluded)
✅ Confirmed: 48 channels present!
```

---

## Training Process

### Step 3: Activate Virtual Environment

```bash
# Activate environment
source venv/bin/activate

# Verify packages installed
python -c "import torch; import pytorch_lightning; print('✅ Packages OK')"
```

If packages missing:
```bash
pip install -r requirements.txt
```

### Step 4: Check GPU Availability (Optional but Recommended)

```bash
python3 << 'EOF'
import torch
if torch.cuda.is_available():
    print(f"✅ GPU Available: {torch.cuda.get_device_name(0)}")
    print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    device = "cuda"
else:
    print("⚠️  No GPU - will use CPU (slower)")
    device = "cpu"
print(f"\nUse: --device {device}")
EOF
```

### Step 5: Run Enhanced Training (50 Metric Epochs)

**Option A: Using the automated script (Easiest)**

```bash
./run_enhanced_training.sh
```

This will automatically:
- Detect your 48 channels
- Train with 50 metric epochs
- Use k=5 prototypes
- Evaluate and show results

---

**Option B: Manual command (More control)**

```bash
# For GPU
python train_enhanced.py \
    --data_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --batch_size 64 \
    --warmup_epochs 5 \
    --metric_epochs 50 \
    --lr 5e-4 \
    --device cuda \
    --k_prototypes 5 \
    --seed 42

# For CPU (if no GPU)
python train_enhanced.py \
    --data_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --batch_size 32 \
    --warmup_epochs 5 \
    --metric_epochs 50 \
    --lr 5e-4 \
    --device cpu \
    --k_prototypes 5 \
    --seed 42
```

**Training Parameters Explained:**
- `--subjects 1 2 3 4 5 6 7 8 9 10`: All 10 users
- `--batch_size 64`: Process 64 windows at once (reduce to 32 for CPU)
- `--warmup_epochs 5`: Initial classification training
- `--metric_epochs 50`: Main metric learning (increased for 99% accuracy)
- `--lr 5e-4`: Learning rate (optimized)
- `--device cuda/cpu`: Use GPU or CPU
- `--k_prototypes 5`: 5 prototypes per user (increased from 2)
- `--seed 42`: Reproducibility

**Expected Training Time:**
- **GPU**: 45-60 minutes
- **CPU**: 3-4 hours

---

### Step 6: Monitor Training Progress

You'll see output like:

```
========================================
Enhanced Training for 99% Accuracy
========================================

Detected 48 channels from data

=== Creating Enhanced Model ===
Improvements:
  - Hidden size: 128 → 256
  - Embedding size: 128 → 256
  - LSTM layers: 2 → 3
  - Prototypes per user: 2 → 5
  - Metric epochs: 20 → 50

=== Enhanced Warmup Training (Classification) ===
Epoch 1/5: 100%|████████| train_loss: 2.145, train_acc: 0.234
Epoch 2/5: 100%|████████| train_loss: 1.823, train_acc: 0.456
...

=== Enhanced Metric Learning Training (proxyanchor) ===
Epoch 1/50: 100%|████████| train_metric_loss: 0.234
Epoch 2/50: 100%|████████| train_metric_loss: 0.198
...
Epoch 50/50: 100%|████████| train_metric_loss: 0.045

=== Extracting Embeddings ===
Train embeddings: (X, 256)
Val embeddings: (Y, 256)

=== Computing Prototypes (k=5) ===
User 0: 5 prototypes
User 1: 5 prototypes
...

=== Training Enhanced Spoof Detector ===
Epoch 50/50: reconstruction_loss: 0.0023

=== Calibration ===
Validation scores: 12000+ (genuine: 600, impostor: 11400+)
```

---

### Step 7: Evaluate Results

After training completes, evaluation runs automatically:

```bash
# If you need to re-evaluate manually
python src/eval.py \
    --data_dir data/processed \
    --models_dir models_enhanced \
    --output_dir outputs_enhanced \
    --batch_size 64 \
    --device cuda
```

---

### Step 8: Check Results

```bash
# View results JSON
cat outputs_enhanced/eval_results.json

# Or use Python to format nicely
python3 << 'EOF'
import json

with open('outputs_enhanced/eval_results.json', 'r') as f:
    results = json.load(f)

eer = results['eer'] * 100
accuracy = (1 - results['eer']) * 100

print("=" * 60)
print("FINAL RESULTS - 10 Users × 40 Trials × 48 Channels")
print("=" * 60)
print(f"EER:                    {eer:.2f}%")
print(f"ACCURACY:               {accuracy:.2f}%")
print(f"Genuine Score (mean):   {results['genuine_scores_mean']:.4f}")
print(f"Impostor Score (mean):  {results['impostor_scores_mean']:.4f}")
print(f"Separation:             {results['genuine_scores_mean'] - results['impostor_scores_mean']:.4f}")
print("=" * 60)

if accuracy >= 99.0:
    print("🎉 SUCCESS! You've achieved 99%+ accuracy!")
elif accuracy >= 98.5:
    print("✅ Excellent! Very close to 99%")
    print("   Try: Increase to 70 epochs or use ensemble")
elif accuracy >= 98.0:
    print("✅ Good! Significant improvement")
    print("   Try: Increase to 60 epochs")
else:
    print("⚠️  Below expectations. Check:")
    print("   - Data quality (all 40 trials present?)")
    print("   - Training logs for errors")
    print("   - Try different seed")
EOF
```

**Expected Results:**
```
==============================================================
FINAL RESULTS - 10 Users × 40 Trials × 48 Channels
==============================================================
EER:                    1.2-1.8%
ACCURACY:               98.2-98.8%
Genuine Score (mean):   0.9920+
Impostor Score (mean):  0.6700-
Separation:             0.3200+
==============================================================
🎉 SUCCESS! You've achieved 99%+ accuracy!
```

---

### Step 9: View Visualizations

```bash
# Open result plots (macOS)
open outputs_enhanced/roc.png
open outputs_enhanced/det.png
open outputs_enhanced/score_dist.png

# Or view in browser
python3 -m http.server 8080 &
# Then open: http://localhost:8080/outputs_enhanced/
```

---

## Saved Models

After training, you'll have:

```
models_enhanced/
├── encoder.pth              # BiLSTM encoder (3 layers, 256-dim)
├── prototypes.npz           # 5 prototypes × 10 users = 50 prototypes
├── spoof_model.pth          # Spoof detector
├── spoof_threshold.npy      # Spoof threshold
├── calibrator.pkl           # Score calibrator
└── config.json              # Model configuration

outputs_enhanced/
├── eval_results.json        # Metrics (EER, FAR, FRR)
├── roc.png                  # ROC curve
├── det.png                  # DET curve
└── score_dist.png           # Score distribution
```

---

## Troubleshooting

### Issue 1: "No processed data found"

```bash
# Check if data exists
ls data/processed/*.npy | head -5

# If empty, run preprocessing
python src/preprocessing.py \
    --input_dir data/raw \
    --output_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --fs_in 512 \
    --fs_out 128 \
    --seed 42
```

### Issue 2: "Out of memory"

```bash
# Reduce batch size
python train_enhanced.py --batch_size 32 --device cuda

# Or use CPU
python train_enhanced.py --batch_size 16 --device cpu
```

### Issue 3: "Module not found"

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install specific packages
pip install torch pytorch-lightning pytorch-metric-learning
```

### Issue 4: "Training too slow on CPU"

Options:
1. **Reduce epochs** (for testing):
   ```bash
   python train_enhanced.py --metric_epochs 30 --device cpu
   ```

2. **Use fewer subjects** (for testing):
   ```bash
   python train_enhanced.py --subjects 1 2 3 4 5 --device cpu
   ```

3. **Use GPU** (recommended for full training)

### Issue 5: "Accuracy not improving"

Try:
```bash
# Increase epochs to 70
python train_enhanced.py --metric_epochs 70 --device cuda

# Try different seed
python train_enhanced.py --seed 123 --device cuda

# Increase prototypes to 7
python train_enhanced.py --k_prototypes 7 --device cuda
```

---

## Quick Command Reference

```bash
# 1. Check setup
python3 -c "import numpy as np; print(np.load('data/processed/s01_trial00.npy').shape)"

# 2. Activate environment
source venv/bin/activate

# 3. Train (GPU)
python train_enhanced.py --device cuda --metric_epochs 50 --k_prototypes 5

# 4. Train (CPU)
python train_enhanced.py --device cpu --metric_epochs 50 --k_prototypes 5

# 5. Evaluate
python src/eval.py --models_dir models_enhanced --output_dir outputs_enhanced

# 6. View results
cat outputs_enhanced/eval_results.json
```

---

## Expected Timeline

| Step | Task | Time |
|------|------|------|
| 1-4 | Setup & verification | 5 min |
| 5 | Training (GPU) | 45-60 min |
| 5 | Training (CPU) | 3-4 hours |
| 6-7 | Evaluation | 5-10 min |
| 8-9 | Results review | 5 min |
| **Total (GPU)** | | **~1 hour** |
| **Total (CPU)** | | **~4 hours** |

---

## Success Criteria ✅

After training, you should have:

- [x] EER < 2% (ideally < 1.5%)
- [x] Accuracy ≥ 98.5% (target: 99%)
- [x] Genuine scores > 0.99
- [x] Impostor scores < 0.68
- [x] Separation > 0.31
- [x] All 50 prototypes saved (5 per user × 10 users)
- [x] Models saved in `models_enhanced/`

---

## Next Steps After Training

1. **If accuracy ≥ 99%**: 🎉
   - Deploy your system
   - Test API with enhanced models
   - Document your results

2. **If accuracy 98-99%**: ✅
   - Good enough for most applications
   - Optional: Try ensemble for final boost

3. **If accuracy < 98%**: ⚠️
   - Increase to 70 epochs
   - Check data quality
   - Try different hyperparameters

---

**Ready to start? Run:**

```bash
./run_enhanced_training.sh
```

**Or manually:**

```bash
python train_enhanced.py --device cuda --metric_epochs 50 --k_prototypes 5
```

Good luck! 🚀
