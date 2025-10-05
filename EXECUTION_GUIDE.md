# Execution Guide - Step-by-Step Instructions

## 🎯 Complete Workflow for Better Accuracy (Using All 40 Trials)

This guide provides exact commands to run the system with all 40 trials per subject for production-quality results.

---

## Prerequisites Checklist

- [x] Python 3.10+ installed
- [x] DEAP dataset files (s01.bdf - s10.bdf) in `data/raw/` directory
- [x] 8GB+ RAM available
- [x] ~2GB free disk space
- [x] Terminal/command line access

---

## Step 1: Environment Setup (5 minutes)

### Navigate to Project Directory

```bash
cd "/Users/sruthikr/Desktop/Thought Based Authentiction System Using BiLSTM/deap_bilstm_auth"
```

### Create Virtual Environment

```bash
python3 -m venv venv
```

### Activate Virtual Environment

```bash
source venv/bin/activate
```

**Note**: You'll see `(venv)` prefix in your terminal prompt.

### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected time**: 3-5 minutes

### Verify Installation

```bash
./verify_setup.py
```

**Expected output**: All checks should pass with ✓ marks.

---

## Step 2: Data Preprocessing (15-20 minutes)

### Preprocess All 40 Trials Per Subject

```bash
python src/preprocessing.py \
    --input_dir data/raw \
    --output_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --fs_in 512 \
    --fs_out 128 \
    --seed 42
```

**What this does**:
- Loads each subject's .bdf file
- Applies bandpass filter (1-50 Hz)
- Downsamples from 512 Hz to 128 Hz
- Normalizes each channel (z-score)
- Saves 40 trials per subject as .npy files

**Expected output**:
- 400 files in `data/processed/` (10 subjects × 40 trials)
- Files named: `s01_trial00.npy` through `s10_trial39.npy`

**Progress**: You'll see a progress bar for each subject.

**Verification**:
```bash
ls data/processed/ | wc -l
# Should output: 400
```

---

## Step 3: Model Training (30-60 minutes on CPU)

### Full Training with All Trials

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

**If you have a GPU** (much faster - 10-15 minutes):
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
    --device cuda \
    --seed 42
```

**What this does**:
1. **Warmup Phase (3 epochs)**: Trains classification head
2. **Metric Learning (20 epochs)**: Learns discriminative embeddings
3. **Prototype Computation**: Creates 2 prototypes per user
4. **Spoof Detector Training**: Trains autoencoder
5. **Calibration**: Fits Platt scaling

**Expected output**:
```
models/
├── encoder.pth              # BiLSTM model weights
├── prototypes.npz           # User prototypes (k=2)
├── spoof_model.pth          # Spoof detector
├── spoof_threshold.npy      # Spoof threshold
├── calibrator.pkl           # Score calibrator
└── config.json              # Model configuration
```

**Progress indicators**:
- Epoch progress bars
- Loss values decreasing
- Validation metrics

**Verification**:
```bash
ls -lh models/
# Should see 6 files
```

---

## Step 4: Model Evaluation (3-5 minutes)

### Run Evaluation on Test Set

```bash
python src/eval.py \
    --data_dir data/processed \
    --models_dir models \
    --output_dir outputs \
    --batch_size 64 \
    --device cpu \
    --seed 42
```

**What this does**:
- Extracts embeddings from test set
- Computes similarity scores
- Calculates FAR, FRR, EER
- Generates ROC and DET curves

**Expected output**:
```
outputs/
├── eval_results.json        # Metrics (EER, FAR, FRR)
├── roc.png                  # ROC curve
├── det.png                  # DET curve
└── score_dist.png           # Score distribution
```

### View Results

```bash
# View metrics
cat outputs/eval_results.json | python -m json.tool

# Open plots (macOS)
open outputs/roc.png
open outputs/det.png
open outputs/score_dist.png
```

**Expected metrics** (with 40 trials):
- **EER**: 3-8%
- **FAR @ 1% FRR**: 1-3%

---

## Step 5: Start API Server

### Launch FastAPI Backend

```bash
cd src/api
python main.py
```

**Expected output**:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Server is now running at**: http://localhost:8000

**API Documentation**: http://localhost:8000/docs

**Keep this terminal open** - the server will continue running.

---

## Step 6: Test Authentication (In New Terminal)

### Open New Terminal and Activate Environment

```bash
cd "/Users/sruthikr/Desktop/Thought Based Authentiction System Using BiLSTM/deap_bilstm_auth"
source venv/bin/activate
```

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

**Expected response**:
```json
{
  "status": "healthy",
  "models_loaded": true,
  "database_connected": true
}
```

### Test 2: Register User

```bash
curl -X POST http://localhost:8000/register \
  -F "username=alice" \
  -F "password=secret123" \
  -F "enrollment_trials=@data/processed/s01_trial00.npy" \
  -F "enrollment_trials=@data/processed/s01_trial01.npy" \
  -F "enrollment_trials=@data/processed/s01_trial02.npy"
```

**Expected response**:
```json
{
  "success": true,
  "message": "User 'alice' registered successfully with 3 enrollment trials",
  "username": "alice"
}
```

### Test 3: Authenticate (Genuine User)

```bash
curl -X POST http://localhost:8000/auth/login \
  -F "username=alice" \
  -F "password=secret123" \
  -F "probe=@data/processed/s01_trial03.npy"
```

**Expected response**:
```json
{
  "authenticated": true,
  "score": 0.87,
  "probability": 0.92,
  "is_spoof": false,
  "spoof_error": 0.0023,
  "explain_id": "uuid-here",
  "message": "Authentication successful"
}
```

### Test 4: Authenticate (Impostor)

```bash
curl -X POST http://localhost:8000/auth/login \
  -F "username=alice" \
  -F "password=secret123" \
  -F "probe=@data/processed/s02_trial00.npy"
```

**Expected response**:
```json
{
  "authenticated": false,
  "score": 0.35,
  "probability": 0.28,
  "is_spoof": false,
  "spoof_error": 0.0019,
  "explain_id": "uuid-here",
  "message": "Authentication failed: similarity too low"
}
```

### Test 5: Get Explanation

```bash
# Use explain_id from previous response
curl http://localhost:8000/explain/{explain_id} -o explanation.png
open explanation.png
```

---

## Step 7: Interactive API Testing

### Open API Documentation

Visit in your browser: **http://localhost:8000/docs**

This provides an interactive interface to:
- Test all endpoints
- See request/response schemas
- Try different parameters

---

## Expected Timeline

| Step | Task | Time (CPU) | Time (GPU) |
|------|------|-----------|-----------|
| 1 | Setup | 5 min | 5 min |
| 2 | Preprocessing | 15-20 min | 15-20 min |
| 3 | Training | 30-60 min | 10-15 min |
| 4 | Evaluation | 3-5 min | 1-2 min |
| 5 | Start API | 1 min | 1 min |
| 6 | Test API | 2 min | 2 min |
| **Total** | **~60-90 min** | **~35-45 min** |

---

## Troubleshooting

### Issue: "No module named 'src'"

**Solution**:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### Issue: "CUDA out of memory"

**Solution**: Use CPU or reduce batch size:
```bash
python src/train.py --device cpu --batch_size 32
```

### Issue: "Port 8000 already in use"

**Solution**:
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
```

### Issue: "Models not found" when starting API

**Solution**: Train the model first (Step 3)

### Issue: Poor authentication accuracy

**Possible causes**:
- Not enough training epochs
- Using fast mode (only 3 trials)
- Data preprocessing issues

**Solution**: Run full training with all 40 trials as shown above.

---

## Verification Checklist

After completing all steps, verify:

- [ ] 400 files in `data/processed/`
- [ ] 6 files in `models/` directory
- [ ] 4 files in `outputs/` directory
- [ ] API server running at http://localhost:8000
- [ ] Health check returns "healthy"
- [ ] User registration successful
- [ ] Genuine authentication returns `authenticated: true`
- [ ] Impostor authentication returns `authenticated: false`
- [ ] EER < 10% in evaluation results

---

## Next Steps

### 1. Export Model to ONNX

```bash
python src/inference/onnx_export.py \
    --checkpoint models/encoder.pth \
    --config models/config.json \
    --output models/encoder.onnx \
    --verify
```

### 2. Deploy with Docker

```bash
cd deployments
docker-compose up --build
```

### 3. Build Frontend

See `frontend/README.md` for React app setup.

### 4. Experiment with Hyperparameters

Try different configurations:
- More epochs: `--metric_epochs 50`
- Different loss: `--metric_loss triplet`
- Larger batch: `--batch_size 128` (requires more RAM)

---

## Summary of Commands (Copy-Paste Ready)

```bash
# 1. Setup
cd "/Users/sruthikr/Desktop/Thought Based Authentiction System Using BiLSTM/deap_bilstm_auth"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Preprocess (all 40 trials)
python src/preprocessing.py \
    --input_dir data/raw \
    --output_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --fs_out 128 \
    --seed 42

# 3. Train (full training)
python src/train.py \
    --data_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --batch_size 64 \
    --warmup_epochs 3 \
    --metric_epochs 20 \
    --use_attention \
    --device cpu \
    --seed 42

# 4. Evaluate
python src/eval.py \
    --data_dir data/processed \
    --models_dir models \
    --output_dir outputs

# 5. Start API
cd src/api && python main.py
```

---

**Status**: ✅ Ready to execute
**Last Updated**: 2025-10-05
