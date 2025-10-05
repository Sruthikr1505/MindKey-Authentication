# Quick Start Guide

## 🚀 Fast Demo on CPU (5 minutes)

### Step 1: Setup

```bash
# Navigate to project
cd deap_bilstm_auth

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Prepare Data

Place DEAP `.bdf` files in `data/raw/`:
- `s01.bdf` through `s10.bdf`

### Step 3: Run Demo

```bash
./run_demo.sh
```

This automatically:
1. Preprocesses 3 trials per subject (fast mode)
2. Trains model with 1 warmup + 2 metric epochs
3. Computes prototypes and calibrator
4. Trains spoof detector
5. Starts API server

### Step 4: Test API

Open another terminal:

```bash
# Activate environment
source venv/bin/activate

# Test health endpoint
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs  # macOS
# or visit http://localhost:8000/docs in browser
```

---

## 📊 Full Training (Better Accuracy)

For production-quality results, train with all 40 trials:

### Step 1: Preprocess All Trials

```bash
python src/preprocessing.py \
    --input_dir data/raw \
    --output_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --fs_out 128 \
    --seed 42
```

**Time:** ~10-20 minutes (without ICA)

### Step 2: Full Training

```bash
python src/train.py \
    --data_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --batch_size 64 \
    --warmup_epochs 3 \
    --metric_epochs 20 \
    --use_attention \
    --device cpu \
    --seed 42
```

**Time:** ~30-60 minutes on CPU, ~10-15 minutes on GPU

### Step 3: Evaluate

```bash
python src/eval.py \
    --data_dir data/processed \
    --models_dir models \
    --output_dir outputs \
    --device cpu
```

**Outputs:**
- `outputs/eval_results.json` - Metrics (EER, FAR, FRR)
- `outputs/roc.png` - ROC curve
- `outputs/det.png` - DET curve

### Step 4: Start API

```bash
cd src/api
python main.py
```

---

## 🔧 Common Commands

### Preprocessing

```bash
# Fast mode (3 trials)
python src/preprocessing.py --fast --subjects 1 2 3

# Full mode (40 trials)
python src/preprocessing.py --subjects 1 2 3 4 5 6 7 8 9 10

# With ICA artifact removal (slow)
python src/preprocessing.py --ica --subjects 1 2
```

### Training

```bash
# Fast demo
python src/train.py --fast --device cpu

# Full training on GPU
python src/train.py --device cuda --metric_epochs 50

# With triplet loss instead of ProxyAnchor
python src/train.py --metric_loss triplet
```

### Evaluation

```bash
# Basic evaluation
python src/eval.py

# On GPU
python src/eval.py --device cuda
```

### API Server

```bash
# Development mode (auto-reload)
cd src/api
python main.py

# Production mode with uvicorn
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### ONNX Export

```bash
python src/inference/onnx_export.py --verify
```

---

## 🐳 Docker Quick Start

```bash
cd deployments
docker-compose up --build
```

Access API at http://localhost:8000

---

## 📝 API Usage Examples

### Register User

```bash
curl -X POST http://localhost:8000/register \
  -F "username=alice" \
  -F "password=secret123" \
  -F "enrollment_trials=@data/processed/s01_trial00.npy" \
  -F "enrollment_trials=@data/processed/s01_trial01.npy" \
  -F "enrollment_trials=@data/processed/s01_trial02.npy"
```

### Authenticate

```bash
curl -X POST http://localhost:8000/auth/login \
  -F "username=alice" \
  -F "password=secret123" \
  -F "probe=@data/processed/s01_trial03.npy"
```

### Get Explanation

```bash
# Use explain_id from authentication response
curl http://localhost:8000/explain/{explain_id} -o explanation.png
```

---

## 🎯 Expected Timeline

| Task | Fast Mode | Full Mode |
|------|-----------|-----------|
| Preprocessing | 2-3 min | 10-20 min |
| Training | 5-10 min | 30-60 min (CPU) |
| Evaluation | 1-2 min | 3-5 min |
| **Total** | **~10 min** | **~45-90 min** |

*Times are approximate for CPU. GPU training is 3-5x faster.*

---

## ❓ Troubleshooting

**Q: "No module named 'src'"**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

**Q: "Models not found"**
```bash
# Train the model first
python src/train.py --fast
```

**Q: "Out of memory"**
```bash
# Reduce batch size
python src/train.py --batch_size 16 --fast
```

**Q: "Port 8000 already in use"**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
```

---

## 📚 Next Steps

1. ✅ Run fast demo
2. ✅ Test API endpoints
3. ✅ Train with full data
4. ✅ Evaluate performance
5. 📱 Build frontend (see `frontend/README.md`)
6. 🚀 Deploy with Docker
7. 🔬 Experiment with hyperparameters

---

**Need help?** Check the main [README.md](README.md) for detailed documentation.
