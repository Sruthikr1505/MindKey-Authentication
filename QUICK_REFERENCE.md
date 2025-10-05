# Quick Reference Card

## 🚀 Getting Started (First Time)

```bash
# 1. Copy your downloaded .bdf files
cp ~/Downloads/s*.bdf data/raw/

# 2. Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Verify setup
./verify_setup.py
```

---

## 📊 Full Training Pipeline (All 40 Trials)

```bash
# Step 1: Preprocess (15-20 min)
python src/preprocessing.py \
    --input_dir data/raw \
    --output_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10

# Step 2: Train (30-60 min CPU, 10-15 min GPU)
python src/train.py \
    --data_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --warmup_epochs 3 \
    --metric_epochs 20 \
    --use_attention \
    --device cpu

# Step 3: Evaluate (3-5 min)
python src/eval.py

# Step 4: Start API (Terminal 1)
cd src/api && python main.py

# Step 5: Start Frontend (Terminal 2)
cd frontend/eeg-auth-app && npm run dev
```

---

## 🔗 URLs

| Service | URL |
|---------|-----|
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **Frontend** | http://localhost:5173 |

---

## 🧪 API Testing

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/register \
  -F "username=alice" \
  -F "password=secret123" \
  -F "enrollment_trials=@data/processed/s01_trial00.npy" \
  -F "enrollment_trials=@data/processed/s01_trial01.npy"

# Authenticate (genuine)
curl -X POST http://localhost:8000/auth/login \
  -F "username=alice" \
  -F "password=secret123" \
  -F "probe=@data/processed/s01_trial03.npy"

# Authenticate (impostor)
curl -X POST http://localhost:8000/auth/login \
  -F "username=alice" \
  -F "password=secret123" \
  -F "probe=@data/processed/s02_trial00.npy"
```

---

## 📁 File Locations

```
data/raw/               ← Your .bdf files (s01-s10)
data/processed/         ← 400 .npy files (generated)
models/                 ← Trained models (generated)
outputs/                ← Evaluation results (generated)
src/                    ← Python source code
frontend/eeg-auth-app/  ← React frontend
```

---

## 📊 Expected Results (40 Trials)

| Metric | Value |
|--------|-------|
| **EER** | 3-8% |
| **FAR @ 1% FRR** | 1-3% |
| **Genuine Score** | 0.75-0.95 |
| **Impostor Score** | 0.15-0.45 |

---

## 🔧 Common Commands

```bash
# Activate environment
source venv/bin/activate

# Check processed files
ls data/processed/ | wc -l  # Should be 400

# Check models
ls -lh models/  # Should have 6 files

# View results
cat outputs/eval_results.json | python -m json.tool

# Kill server on port 8000
lsof -ti:8000 | xargs kill -9
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **START_HERE.md** | Entry point |
| **COMPLETE_SETUP_GUIDE.md** | Full step-by-step guide |
| **QUICKSTART.md** | 5-minute setup |
| **README.md** | Complete documentation |
| **COMMANDS_SUMMARY.md** | All commands |

---

## ✅ Checklist

- [ ] .bdf files in `data/raw/` (10 files)
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] 400 files in `data/processed/`
- [ ] 6 files in `models/`
- [ ] EER < 10%
- [ ] Backend running on :8000
- [ ] Frontend running on :5173
- [ ] Successful authentication test

---

**Need detailed help?** → See `COMPLETE_SETUP_GUIDE.md`
