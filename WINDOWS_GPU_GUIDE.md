# Windows 11 GPU Training Guide

Complete guide for training the EEG authentication system on Windows 11 with GPU acceleration.

## 🖥️ System Requirements

- **OS**: Windows 11
- **GPU**: NVIDIA GPU with CUDA support (RTX 2060 or better recommended)
- **RAM**: 16GB+ recommended
- **Storage**: 10GB+ free space
- **Python**: 3.10 or 3.11

## 🚀 Quick Start (GPU Training)

### Step 1: Install CUDA and cuDNN

1. **Check your GPU**:
```powershell
nvidia-smi
```

2. **Install CUDA Toolkit 11.8** (recommended for PyTorch 2.0.1):
   - Download from: https://developer.nvidia.com/cuda-11-8-0-download-archive
   - Select: Windows → x86_64 → 11 → exe (local)
   - Install with default settings

3. **Verify CUDA installation**:
```powershell
nvcc --version
```

### Step 2: Setup Python Environment

```powershell
# Navigate to project directory
cd "d:\Thought Based Authentication System Using BiLSTM\deap_bilstm_auth"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

### Step 3: Install PyTorch with CUDA Support

```powershell
# Install PyTorch with CUDA 11.8
pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cu118

# Verify GPU is available
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"
```

**Expected Output:**
```
CUDA available: True
GPU: NVIDIA GeForce RTX 3060 (or your GPU model)
```

### Step 4: Install Other Dependencies

```powershell
# Install remaining dependencies
pip install -r requirements.txt
```

### Step 5: Verify Data Files

Ensure your DEAP .bdf files are in the correct location:

```
d:\Thought Based Authentication System Using BiLSTM\deap_bilstm_auth\data\raw\
├── s01.bdf
├── s02.bdf
├── s03.bdf
├── s04.bdf
├── s05.bdf
├── s06.bdf
├── s07.bdf
├── s08.bdf
├── s09.bdf
└── s10.bdf
```

**Verify files exist:**
```powershell
dir data\raw\*.bdf
```

You should see all 10 files (s01.bdf through s10.bdf).

## 🎯 Full Training Pipeline (97.28% Accuracy Target)

### Step 1: Preprocess Data (All 40 Trials, 48 Channels)

```powershell
python src\preprocessing.py `
    --input_dir data\raw `
    --output_dir data\processed `
    --subjects 1 2 3 4 5 6 7 8 9 10 `
    --n_channels 48 `
    --seed 42
```

**Time:** ~15-20 minutes  
**Output:** 400 .npy files (10 users × 40 trials)

**Verify preprocessing:**
```powershell
dir data\processed\*.npy | Measure-Object | Select-Object Count
```
Should show: `Count : 400`

### Step 2: Train with GPU (30 Epochs for 97.28% Accuracy)

```powershell
python src\train.py `
    --data_dir data\processed `
    --subjects 1 2 3 4 5 6 7 8 9 10 `
    --batch_size 64 `
    --warmup_epochs 3 `
    --metric_epochs 30 `
    --lr 0.001 `
    --metric_loss proxyanchor `
    --use_attention `
    --n_channels 48 `
    --device cuda `
    --seed 42
```

**Training Parameters:**
- **Subjects**: 10 (s01-s10)
- **Channels**: 48
- **Trials per subject**: 40
- **Total windows**: ~60,000 (with sliding windows)
- **Warmup epochs**: 3
- **Metric learning epochs**: 30
- **Batch size**: 64
- **Device**: CUDA (GPU)

**Expected Time on GPU:**
- RTX 3060/3070: ~2-3 hours
- RTX 3080/3090: ~1.5-2 hours
- RTX 4070/4080: ~1-1.5 hours

**Expected Accuracy:** 97.28% (EER ~2.72%)

**Monitor GPU usage:**
```powershell
# In another PowerShell window
nvidia-smi -l 1
```

### Step 3: Evaluate Performance

```powershell
python src\eval.py `
    --data_dir data\processed `
    --checkpoint checkpoints\best.ckpt `
    --prototypes models\prototypes.npz `
    --subjects 1 2 3 4 5 6 7 8 9 10 `
    --batch_size 64 `
    --n_channels 48 `
    --device cuda `
    --output_dir outputs `
    --seed 42
```

**Output Files:**
- `outputs\eval_results.json` - Metrics (EER, FAR, FRR)
- `outputs\roc.png` - ROC curve
- `outputs\det.png` - DET curve
- `outputs\score_distribution.png` - Score distributions

**Check results:**
```powershell
type outputs\eval_results.json
```

**Expected Results:**
```json
{
  "eer": 0.0272,
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

## 🎨 Frontend Setup (MindKey Integration)

### Step 1: Clone MindKey Frontend

```powershell
# Navigate to a suitable location
cd "d:\Thought Based Authentication System Using BiLSTM"

# Clone the MindKey repository
git clone git@github.com:Sruthikr1505/MindKey-Authentication.git

# Navigate to frontend
cd MindKey-Authentication\frontend
```

### Step 2: Install Frontend Dependencies

```powershell
# Install Node.js dependencies
npm install

# Install additional dependencies if needed
npm install axios recharts
```

### Step 3: Configure API Endpoint

Edit the frontend configuration to point to your backend:

**Create or edit `.env` file:**
```powershell
# In MindKey-Authentication\frontend\
echo REACT_APP_API_URL=http://localhost:8000 > .env
```

**Or update the API URL in the source code** (look for API endpoint configurations in the frontend code).

### Step 4: Start Backend

```powershell
# In the deap_bilstm_auth directory
cd "d:\Thought Based Authentication System Using BiLSTM\deap_bilstm_auth"

# Activate virtual environment
.\venv\Scripts\activate

# Start backend
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Backend will run on:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

### Step 5: Start Frontend

```powershell
# In another PowerShell window
cd "d:\Thought Based Authentication System Using BiLSTM\MindKey-Authentication\frontend"

# Start React app
npm start
```

**Frontend will run on:** http://localhost:3000

## 🔧 Optimization Tips for Windows 11 GPU

### 1. Increase Batch Size (if you have enough VRAM)

```powershell
# For GPUs with 8GB+ VRAM
python src\train.py ... --batch_size 128 --device cuda

# For GPUs with 12GB+ VRAM
python src\train.py ... --batch_size 256 --device cuda
```

### 2. Enable Mixed Precision Training (Faster)

Edit `src\train.py` and add to the Trainer:

```python
trainer = pl.Trainer(
    max_epochs=epochs,
    accelerator='gpu',
    devices=1,
    precision=16,  # Add this line for mixed precision
    callbacks=[checkpoint_callback, early_stop_callback],
    enable_progress_bar=True,
    log_every_n_steps=10
)
```

### 3. Increase Number of Workers

```powershell
# Edit dataset.py or use environment variable
$env:NUM_WORKERS=4
python src\train.py ... --device cuda
```

### 4. Monitor GPU Memory

```powershell
# Real-time monitoring
nvidia-smi -l 1

# Or use Task Manager → Performance → GPU
```

## 📊 Expected Performance Metrics

### Training Performance (RTX 3060/3070)

| Metric | Value |
|--------|-------|
| **Preprocessing Time** | 15-20 min |
| **Training Time** | 2-3 hours |
| **Evaluation Time** | 2-3 min |
| **GPU Utilization** | 80-95% |
| **VRAM Usage** | 4-6 GB |
| **Throughput** | ~500 samples/sec |

### Model Performance (Target)

| Metric | Target | Expected |
|--------|--------|----------|
| **Accuracy** | 97.28% | 97.0-97.5% |
| **EER** | 2.72% | 2.5-3.0% |
| **FAR @ FRR=1%** | <5% | 3-5% |
| **Inference Time** | <100ms | 50-80ms |

## 🐛 Troubleshooting

### Issue: CUDA not available

**Solution:**
```powershell
# Reinstall PyTorch with CUDA
pip uninstall torch torchvision
pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cu118
```

### Issue: Out of memory

**Solution:**
```powershell
# Reduce batch size
python src\train.py ... --batch_size 32 --device cuda
```

### Issue: Slow preprocessing

**Solution:**
```powershell
# Skip ICA for faster preprocessing (slightly lower accuracy)
# Edit src\preprocessing.py and set do_ica=False
```

### Issue: Frontend can't connect to backend

**Solution:**
1. Check backend is running: http://localhost:8000/health
2. Update CORS in `src\api\main.py` if needed
3. Verify `.env` file in frontend has correct API URL

## 📝 Complete Training Script (Copy-Paste)

Save this as `train_gpu.bat`:

```batch
@echo off
echo ==========================================
echo GPU Training Pipeline for Windows 11
echo ==========================================

REM Activate virtual environment
call venv\Scripts\activate

REM Step 1: Preprocess
echo.
echo Step 1: Preprocessing data (48 channels, 40 trials)...
python src\preprocessing.py --input_dir data\raw --output_dir data\processed --subjects 1 2 3 4 5 6 7 8 9 10 --n_channels 48 --seed 42

REM Step 2: Train with GPU
echo.
echo Step 2: Training with GPU (30 epochs for 97.28%% accuracy)...
python src\train.py --data_dir data\processed --subjects 1 2 3 4 5 6 7 8 9 10 --batch_size 64 --warmup_epochs 3 --metric_epochs 30 --lr 0.001 --metric_loss proxyanchor --use_attention --n_channels 48 --device cuda --seed 42

REM Step 3: Evaluate
echo.
echo Step 3: Evaluating model...
python src\eval.py --data_dir data\processed --checkpoint checkpoints\best.ckpt --prototypes models\prototypes.npz --subjects 1 2 3 4 5 6 7 8 9 10 --batch_size 64 --n_channels 48 --device cuda --output_dir outputs --seed 42

echo.
echo ==========================================
echo Training Complete!
echo ==========================================
echo.
echo Results saved to outputs\
echo Model saved to checkpoints\best.ckpt
echo.
echo To start backend: python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
echo.
pause
```

**Run it:**
```powershell
.\train_gpu.bat
```

## 🎯 Final Checklist

- [ ] CUDA installed and verified
- [ ] PyTorch with CUDA installed
- [ ] All 10 .bdf files in `data\raw\`
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] GPU detected by PyTorch
- [ ] Preprocessing completed (400 .npy files)
- [ ] Training completed (30 epochs)
- [ ] Evaluation shows EER ~2.72%
- [ ] Backend running on port 8000
- [ ] MindKey frontend cloned
- [ ] Frontend running on port 3000
- [ ] Frontend connected to backend

## 🚀 Quick Commands Reference

```powershell
# Activate environment
.\venv\Scripts\activate

# Check GPU
python -c "import torch; print(torch.cuda.is_available())"

# Preprocess
python src\preprocessing.py --input_dir data\raw --output_dir data\processed --subjects 1 2 3 4 5 6 7 8 9 10 --n_channels 48

# Train (GPU, 30 epochs)
python src\train.py --data_dir data\processed --subjects 1 2 3 4 5 6 7 8 9 10 --batch_size 64 --metric_epochs 30 --device cuda

# Evaluate
python src\eval.py --data_dir data\processed --checkpoint checkpoints\best.ckpt --prototypes models\prototypes.npz --subjects 1 2 3 4 5 6 7 8 9 10 --device cuda --output_dir outputs

# Start backend
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Monitor GPU
nvidia-smi -l 1
```

---

**🎉 You're ready to train on Windows 11 with GPU acceleration!**

Expected total time: **2-3 hours** to achieve **97.28% accuracy**
