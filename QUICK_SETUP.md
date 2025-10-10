# ⚡ Quick Setup & Training

## Current Status
✅ Virtual environment created  
⏳ Installing dependencies (in progress)...

## After Installation Completes

### Step 1: Activate Environment
```bash
source venv/bin/activate
```

### Step 2: Verify Installation
```bash
python -c "import torch; import pytorch_lightning; print('✅ Ready to train!')"
```

### Step 3: Start Training (Choose One)

**Option A: Automated Script (Easiest)**
```bash
./START_TRAINING.sh
```

**Option B: Direct Command**
```bash
# For GPU
python train_enhanced.py --device cuda --metric_epochs 50 --k_prototypes 5

# For CPU
python train_enhanced.py --device cpu --metric_epochs 50 --k_prototypes 5
```

## Your Configuration
- **Users**: 10 (s01-s10)
- **Trials**: 40 per user (400 files total)
- **Channels**: 48
- **Metric Epochs**: 50
- **Prototypes**: 5 per user
- **Target**: 99% accuracy

## Expected Time
- **GPU**: 45-60 minutes
- **CPU**: 3-4 hours

## What Gets Trained
1. **Warmup**: 5 epochs (classification)
2. **Metric Learning**: 50 epochs (embedding space)
3. **Prototypes**: 5 per user (50 total)
4. **Spoof Detector**: 50 epochs
5. **Calibration**: Platt scaling

## Output
Models saved to: `models_enhanced/`
Results saved to: `outputs_enhanced/`

## View Results
```bash
cat outputs_enhanced/eval_results.json
```

## Troubleshooting

### If installation fails:
```bash
# Try installing core packages first
./venv/bin/pip install torch pytorch-lightning numpy scipy scikit-learn
./venv/bin/pip install -r requirements.txt
```

### If "command not found":
```bash
# Make scripts executable
chmod +x START_TRAINING.sh run_enhanced_training.sh
```

### If out of memory:
```bash
# Reduce batch size
python train_enhanced.py --batch_size 32 --device cuda
```

## Next Steps After Training
1. Check accuracy in `outputs_enhanced/eval_results.json`
2. View plots: `open outputs_enhanced/*.png`
3. If accuracy ≥ 99%: Success! 🎉
4. If accuracy < 99%: Increase to 70 epochs

---

**Ready?** Wait for installation to complete, then run:
```bash
source venv/bin/activate
./START_TRAINING.sh
```
