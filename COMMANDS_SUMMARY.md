# Command Reference - Complete EEG Authentication System

## 🎯 Fast Demo on CPU (Exact Commands)

### Setup (One-time)

```bash
cd /Users/sruthikr/Desktop/Thought\ Based\ Authentiction\ System\ Using\ BiLSTM/deap_bilstm_auth

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run Complete Demo

```bash
# Single command to run everything
./run_demo.sh
```

**OR** run steps manually:

### Step 1: Preprocessing (Fast Mode - 3 trials per subject)

```bash
python src/preprocessing.py \
    --input_dir data/raw \
    --output_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --fast \
    --fs_in 512 \
    --fs_out 128 \
    --seed 42
```

**Expected output**: `data/processed/s01_trial00.npy` through `s10_trial02.npy` (30 files total)

### Step 2: Training (Fast Mode - 1 warmup + 2 metric epochs)

```bash
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
```

**Expected output**: 
- `models/encoder.pth`
- `models/prototypes.npz`
- `models/spoof_model.pth`
- `models/spoof_threshold.npy`
- `models/calibrator.pkl`
- `models/config.json`

### Step 3: Start API Server

```bash
cd src/api
python main.py
```

**Server will run at**: http://localhost:8000

**API docs at**: http://localhost:8000/docs

### Step 4: Test Authentication (In another terminal)

```bash
# Activate environment
source venv/bin/activate

# Health check
curl http://localhost:8000/health

# Register a user (using processed trials as enrollment)
curl -X POST http://localhost:8000/register \
  -F "username=testuser" \
  -F "password=test123" \
  -F "enrollment_trials=@data/processed/s01_trial00.npy" \
  -F "enrollment_trials=@data/processed/s01_trial01.npy"

# Authenticate
curl -X POST http://localhost:8000/auth/login \
  -F "username=testuser" \
  -F "password=test123" \
  -F "probe=@data/processed/s01_trial02.npy"
```

---

## 📊 Full Training (All 40 Trials - Better Accuracy)

### Step 1: Preprocess All Trials

```bash
python src/preprocessing.py \
    --input_dir data/raw \
    --output_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --fs_in 512 \
    --fs_out 128 \
    --seed 42
```

**Time**: ~10-20 minutes
**Output**: 400 files (10 subjects × 40 trials)

### Step 2: Full Training

```bash
python src/train.py \
    --data_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --batch_size 64 \
    --warmup_epochs 3 \
    --metric_epochs 20 \
    --lr 0.001 \
    --metric_loss proxyanchor \
    --use_attention \
    --device cpu \
    --seed 42
```

**Time**: ~30-60 minutes on CPU, ~10-15 minutes on GPU
**For GPU**: Change `--device cpu` to `--device cuda`

### Step 3: Evaluation

```bash
python src/eval.py \
    --data_dir data/processed \
    --models_dir models \
    --output_dir outputs \
    --batch_size 64 \
    --device cpu \
    --seed 42
```

**Output**:
- `outputs/eval_results.json` - Contains EER, FAR, FRR
- `outputs/roc.png` - ROC curve
- `outputs/det.png` - DET curve
- `outputs/score_dist.png` - Score distribution

### Step 4: View Results

```bash
# View metrics
cat outputs/eval_results.json | python -m json.tool

# Open plots (macOS)
open outputs/roc.png
open outputs/det.png
```

---

## 🔧 Advanced Commands

### Preprocessing with ICA (Artifact Removal)

```bash
python src/preprocessing.py \
    --input_dir data/raw \
    --output_dir data/processed \
    --subjects 1 2 3 \
    --ica \
    --fs_out 128 \
    --seed 42
```

**Note**: ICA is slow (~2-3 min per subject)

### Training with Triplet Loss

```bash
python src/train.py \
    --data_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --metric_loss triplet \
    --metric_epochs 30 \
    --device cuda
```

### Training without Attention

```bash
python src/train.py \
    --data_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --device cpu
```

(Note: `--use_attention` is a flag, omit it to disable)

### Export to ONNX

```bash
python src/inference/onnx_export.py \
    --checkpoint models/encoder.pth \
    --config models/config.json \
    --output models/encoder.onnx \
    --verify
```

**Output**: `models/encoder.onnx`

---

## 🐳 Docker Commands

### Build and Run

```bash
cd deployments
docker-compose up --build
```

**Access**:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Run in Background

```bash
docker-compose up -d
```

### View Logs

```bash
docker-compose logs -f backend
```

### Stop

```bash
docker-compose down
```

### Rebuild

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

---

## 📝 API Testing Commands

### Health Check

```bash
curl http://localhost:8000/health
```

### Register User

```bash
curl -X POST http://localhost:8000/register \
  -F "username=alice" \
  -F "password=secret123" \
  -F "enrollment_trials=@data/processed/s01_trial00.npy" \
  -F "enrollment_trials=@data/processed/s01_trial01.npy" \
  -F "enrollment_trials=@data/processed/s01_trial02.npy"
```

### Authenticate (Genuine)

```bash
curl -X POST http://localhost:8000/auth/login \
  -F "username=alice" \
  -F "password=secret123" \
  -F "probe=@data/processed/s01_trial03.npy"
```

### Authenticate (Impostor)

```bash
curl -X POST http://localhost:8000/auth/login \
  -F "username=alice" \
  -F "password=secret123" \
  -F "probe=@data/processed/s02_trial00.npy"
```

### Get Explanation

```bash
# Replace {explain_id} with ID from auth response
curl http://localhost:8000/explain/{explain_id} -o explanation.png
```

### View API Documentation

```bash
# macOS
open http://localhost:8000/docs

# Linux
xdg-open http://localhost:8000/docs

# Or just visit in browser
```

---

## 🧪 Testing Individual Modules

### Test Preprocessing

```bash
python src/preprocessing.py --help
```

### Test Dataset

```bash
python src/dataset.py
```

### Test Model

```bash
python src/model.py
```

### Test Attention

```bash
python src/attention.py
```

### Test Augmentations

```bash
python src/augmentations.py
```

### Test Prototypes

```bash
python src/prototypes.py
```

### Test Calibration

```bash
python src/calibration.py
```

### Test Spoof Detector

```bash
python src/spoof_detector.py
```

### Test Metrics

```bash
python src/utils/metrics.py
```

### Test Visualization

```bash
python src/utils/viz.py
```

---

## 🔍 Debugging Commands

### Check Python Path

```bash
echo $PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Check Installed Packages

```bash
pip list | grep torch
pip list | grep mne
pip list | grep fastapi
```

### Check GPU Availability

```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### Check Data Files

```bash
ls -lh data/raw/
ls -lh data/processed/ | wc -l
```

### Check Model Files

```bash
ls -lh models/
```

### Check Disk Space

```bash
df -h .
```

### Monitor Training (in another terminal)

```bash
watch -n 1 'ls -lh checkpoints/'
```

---

## 📊 Performance Profiling

### Time Preprocessing

```bash
time python src/preprocessing.py --fast --subjects 1
```

### Time Training

```bash
time python src/train.py --fast --device cpu
```

### Time Evaluation

```bash
time python src/eval.py --device cpu
```

### Profile with cProfile

```bash
python -m cProfile -o profile.stats src/train.py --fast
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(20)"
```

---

## 🧹 Cleanup Commands

### Remove Processed Data

```bash
rm -rf data/processed/*
```

### Remove Models

```bash
rm -rf models/*
rm -rf checkpoints/*
```

### Remove Outputs

```bash
rm -rf outputs/*
```

### Remove Database

```bash
rm -f data/users.db
```

### Clean Python Cache

```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Complete Reset

```bash
rm -rf data/processed/* models/* checkpoints/* outputs/* data/users.db
find . -type d -name "__pycache__" -exec rm -rf {} +
```

---

## 📦 Package Management

### Update Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Freeze Current Environment

```bash
pip freeze > requirements_frozen.txt
```

### Install in Editable Mode

```bash
pip install -e .
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| **Fast demo** | `./run_demo.sh` |
| **Preprocess (fast)** | `python src/preprocessing.py --fast` |
| **Train (fast)** | `python src/train.py --fast` |
| **Evaluate** | `python src/eval.py` |
| **Start API** | `cd src/api && python main.py` |
| **Test API** | `./test_api.sh` |
| **Docker up** | `cd deployments && docker-compose up` |
| **Export ONNX** | `python src/inference/onnx_export.py --verify` |

---

**Tip**: All Python scripts have `--help` option for detailed usage:
```bash
python src/train.py --help
```
