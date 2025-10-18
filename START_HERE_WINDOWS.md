# 🚀 START HERE - Windows 11 GPU Setup

**Quick start guide for training on Windows 11 with GPU acceleration**

---

## ✅ Prerequisites Checklist

- [x] Windows 11
- [x] NVIDIA GPU (CUDA-capable)
- [x] Python 3.10 or 3.11 installed
- [x] 10 DEAP .bdf files (s01.bdf - s10.bdf) downloaded
- [x] Git installed (for cloning MindKey frontend)

---

## 🎯 Your Configuration

Based on your requirements:

| Parameter | Value |
|-----------|-------|
| **Subjects** | 10 (s01-s10) |
| **Channels** | 48 |
| **Trials per subject** | 40 |
| **Total trials** | 400 |
| **Epochs** | 30 |
| **Target Accuracy** | 97.28% |
| **Device** | CUDA (GPU) |
| **Frontend** | MindKey (from GitHub) |

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install CUDA (One-time setup)

1. **Download CUDA 11.8**:
   - Go to: https://developer.nvidia.com/cuda-11-8-0-download-archive
   - Select: Windows → x86_64 → 11 → exe (local)
   - Install with default settings

2. **Verify installation**:
```powershell
nvcc --version
nvidia-smi
```

### Step 2: Setup Python Environment

```powershell
# Navigate to project
cd "d:\Thought Based Authentication System Using BiLSTM\deap_bilstm_auth"

# Create virtual environment
python -m venv venv

# Activate
.\venv\Scripts\activate

# Install PyTorch with CUDA
pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cu118

# Install other dependencies
pip install -r requirements.txt

# Verify GPU
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}')"
```

### Step 3: Place Your Data Files

Copy your 10 DEAP .bdf files to:
```
d:\Thought Based Authentication System Using BiLSTM\deap_bilstm_auth\data\raw\
```

**Required files:**
- s01.bdf
- s02.bdf
- s03.bdf
- s04.bdf
- s05.bdf
- s06.bdf
- s07.bdf
- s08.bdf
- s09.bdf
- s10.bdf

**Verify:**
```powershell
dir data\raw\*.bdf
```

---

## 🎯 ONE-CLICK TRAINING (Recommended)

Simply run this batch file:

```powershell
.\train_gpu_windows.bat
```

This will:
1. ✅ Preprocess all 400 trials (48 channels)
2. ✅ Train for 30 epochs on GPU
3. ✅ Evaluate and generate metrics
4. ✅ Save all models and results

**Expected time:** 2-3 hours on RTX 3060/3070

---

## 📊 What Happens During Training

### Phase 1: Preprocessing (~15-20 min)
- Loads 10 .bdf files
- Processes 40 trials per subject
- Applies bandpass filter (1-50 Hz)
- Downsamples to 128 Hz
- Normalizes data
- Saves 400 .npy files

### Phase 2: Training (~2-3 hours on GPU)
- **Warmup (3 epochs)**: Classification training
- **Metric Learning (30 epochs)**: ProxyAnchor loss
- Computes user prototypes (k=2 per user)
- Trains spoof detector
- Calibrates scores

### Phase 3: Evaluation (~2-3 min)
- Computes FAR, FRR, EER
- Generates ROC curve
- Generates DET curve
- Saves results to `outputs/`

---

## 📈 Expected Results

After training completes, check `outputs\eval_results.json`:

```json
{
  "eer": 0.0272,           // Target: ~2.72% (97.28% accuracy)
  "eer_threshold": 0.8234,
  "genuine_scores": {
    "mean": 0.8523,
    "std": 0.0456
  },
  "impostor_scores": {
    "mean": 0.3421,
    "std": 0.1234
  }
}
```

**Target Performance:**
- ✅ EER: ~2.72%
- ✅ Accuracy: ~97.28%
- ✅ FAR @ FRR=1%: <5%

---

## 🎨 Setup Frontend (MindKey)

### Step 1: Clone MindKey Repository

```powershell
# Navigate to parent directory
cd "d:\Thought Based Authentication System Using BiLSTM"

# Clone MindKey
git clone git@github.com:Sruthikr1505/MindKey-Authentication.git

# Navigate to frontend
cd MindKey-Authentication\frontend
```

### Step 2: Install Dependencies

```powershell
npm install
```

### Step 3: Configure API Endpoint

Create `.env` file in `MindKey-Authentication\frontend\`:

```
REACT_APP_API_URL=http://localhost:8000
```

### Step 4: Start Backend

```powershell
# In deap_bilstm_auth directory
cd "d:\Thought Based Authentication System Using BiLSTM\deap_bilstm_auth"
.\venv\Scripts\activate
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### Step 5: Start Frontend

```powershell
# In MindKey-Authentication\frontend directory
cd "d:\Thought Based Authentication System Using BiLSTM\MindKey-Authentication\frontend"
npm start
```

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🔍 Monitor Training Progress

### GPU Monitoring

```powershell
# In another PowerShell window
nvidia-smi -l 1
```

Watch for:
- GPU Utilization: Should be 80-95%
- Memory Usage: ~4-6 GB
- Temperature: Should stay below 80°C

### Training Logs

The training script will show:
- Epoch progress
- Loss values
- Validation metrics
- ETA for completion

---

## 📁 Output Files

After training, you'll have:

```
checkpoints/
└── best.ckpt                    # Trained model

models/
├── prototypes.npz               # User prototypes (k=2 per user)
├── calibrator.pkl               # Score calibrator
└── spoof_model.pth              # Spoof detector

outputs/
├── eval_results.json            # Metrics (EER, FAR, FRR)
├── roc.png                      # ROC curve
├── det.png                      # DET curve
└── score_distribution.png       # Score distributions

data/processed/
└── *.npy                        # 400 preprocessed trials
```

---

## 🐛 Troubleshooting

### GPU Not Detected

```powershell
# Reinstall PyTorch with CUDA
pip uninstall torch torchvision
pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cu118
```

### Out of Memory

```powershell
# Reduce batch size in train_gpu_windows.bat
# Change --batch_size 64 to --batch_size 32
```

### Missing .bdf Files

Ensure all 10 files are in `data\raw\`:
```powershell
dir data\raw\*.bdf
```

Should show 10 files.

### Frontend Can't Connect

1. Check backend is running: http://localhost:8000/health
2. Verify `.env` file in frontend has correct URL
3. Check Windows Firewall isn't blocking port 8000

---

## 📞 Quick Reference Commands

```powershell
# Activate environment
.\venv\Scripts\activate

# Check GPU
python -c "import torch; print(torch.cuda.is_available())"

# Full training (one command)
.\train_gpu_windows.bat

# Start backend
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Monitor GPU
nvidia-smi -l 1

# Check results
type outputs\eval_results.json
```

---

## ✅ Success Checklist

- [ ] CUDA installed and working
- [ ] Virtual environment created
- [ ] PyTorch with CUDA installed
- [ ] GPU detected by PyTorch
- [ ] All 10 .bdf files in `data\raw\`
- [ ] Dependencies installed
- [ ] Training completed (30 epochs)
- [ ] EER ~2.72% achieved
- [ ] Backend running on port 8000
- [ ] MindKey frontend cloned
- [ ] Frontend running on port 3000
- [ ] Can register and authenticate users

---

## 🎉 You're Ready!

**To start training right now:**

```powershell
cd "d:\Thought Based Authentication System Using BiLSTM\deap_bilstm_auth"
.\venv\Scripts\activate
.\train_gpu_windows.bat
```

**Expected total time:** 2-3 hours  
**Expected accuracy:** 97.28%

---

## 📚 Additional Resources

- **Full Documentation**: `README.md`
- **Windows GPU Guide**: `WINDOWS_GPU_GUIDE.md`
- **Testing Guide**: `TESTING.md`
- **API Documentation**: http://localhost:8000/docs (after starting backend)

---

**Questions?** Check `WINDOWS_GPU_GUIDE.md` for detailed troubleshooting.

**Good luck with your training! 🚀**
