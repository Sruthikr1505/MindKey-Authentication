# Quick Start Guide

Get the EEG authentication system running in 5 minutes!

## Prerequisites

✅ Python 3.10+  
✅ DEAP dataset files (s01.bdf - s10.bdf) in `data/raw/`  
✅ 8GB+ RAM  

## Fast Demo (CPU, 10 minutes)

### Windows

```bash
# Run the demo script
run_demo.bat
```

### Linux/Mac

```bash
# Make executable
chmod +x run_demo.sh

# Run demo
./run_demo.sh
```

## Manual Steps

### 1. Install Dependencies (2 minutes)

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Preprocess Data (3 minutes - fast mode)

```bash
python src/preprocessing.py \
    --input_dir data/raw \
    --output_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --fast \
    --n_channels 48
```

**Output**: Processed .npy files in `data/processed/`

### 3. Train Model (5 minutes - demo mode)

```bash
python src/train.py \
    --data_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --fast \
    --device cpu
```

**Output**: 
- `checkpoints/best.ckpt` - Trained model
- `models/prototypes.npz` - User prototypes
- `models/calibrator.pkl` - Score calibrator
- `models/spoof_model.pth` - Spoof detector

### 4. Start Backend (instant)

```bash
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

**Access**: http://localhost:8000/docs

### 5. Test API

```bash
# Health check
curl http://localhost:8000/health

# Register user (prepare 2+ enrollment trials)
curl -X POST http://localhost:8000/register \
  -F 'username=alice' \
  -F 'password=secure123' \
  -F 'enrollment_trials=@data/processed/s01_trial00.npy' \
  -F 'enrollment_trials=@data/processed/s01_trial01.npy'

# Authenticate
curl -X POST http://localhost:8000/auth/login \
  -F 'username=alice' \
  -F 'password=secure123' \
  -F 'probe_trial=@data/processed/s01_trial02.npy'
```

## Full Training (for 97%+ accuracy)

**Time**: 2-3 hours on GPU, 8-10 hours on CPU

```bash
# Preprocess all trials (40 per subject)
python src/preprocessing.py \
    --input_dir data/raw \
    --output_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --n_channels 48

# Train with full epochs
python src/train.py \
    --data_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --batch_size 64 \
    --warmup_epochs 3 \
    --metric_epochs 30 \
    --device cuda  # or cpu
```

## Evaluate Performance

```bash
python src/eval.py \
    --data_dir data/processed \
    --checkpoint checkpoints/best.ckpt \
    --prototypes models/prototypes.npz \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --output_dir outputs
```

**Output**:
- `outputs/eval_results.json` - Metrics (EER, FAR, FRR)
- `outputs/roc.png` - ROC curve
- `outputs/det.png` - DET curve

## Frontend Setup

```bash
# Clone MindKey frontend
git clone git@github.com:Sruthikr1505/MindKey-Authentication.git
cd MindKey-Authentication/frontend

# Install and run
npm install
npm start
```

Update API endpoint to `http://localhost:8000` in frontend config.

## Docker Deployment

```bash
cd deployments
docker-compose up --build
```

Access at http://localhost:8000

## Troubleshooting

**Issue**: Out of memory  
**Fix**: Reduce batch size `--batch_size 32` or use fewer subjects

**Issue**: Slow on CPU  
**Fix**: Use `--fast` flag or enable GPU `--device cuda`

**Issue**: Can't find .bdf files  
**Fix**: Ensure files are in `data/raw/` as `s01.bdf`, `s02.bdf`, etc.

**Issue**: Import errors  
**Fix**: Ensure you're in the virtual environment and installed all dependencies

## Next Steps

- 📊 Explore data: `jupyter notebook notebooks/exploration.ipynb`
- 📖 Read full docs: `README.md`
- 🔧 Customize hyperparameters in `src/train.py`
- 🚀 Deploy to production with Docker

## Support

For issues, check `README.md` troubleshooting section or open a GitHub issue.
