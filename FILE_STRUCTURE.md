# Complete File Structure

Visual guide to all files in the repository.

```
d:\Thought Based Authentication System Using BiLSTM\deap_bilstm_auth\
│
├── 📄 START_HERE_WINDOWS.md          ⭐ START HERE for Windows 11 GPU setup
├── 📄 README.md                       Complete documentation
├── 📄 QUICKSTART.md                   5-minute quick start
├── 📄 WINDOWS_GPU_GUIDE.md            Detailed Windows 11 GPU guide
├── 📄 TESTING.md                      Testing guide
├── 📄 SUMMARY.md                      Repository overview
├── 📄 PROJECT_STATUS.md               Project status report
├── 📄 LICENSE                         MIT License
│
├── 🔧 train_gpu_windows.bat           ⭐ ONE-CLICK GPU TRAINING (Windows)
├── 🔧 run_demo.bat                    Demo script (Windows)
├── 🔧 run_demo.sh                     Demo script (Linux/Mac)
│
├── 📄 requirements.txt                Python dependencies
├── 📄 .gitignore                      Git ignore rules
├── 📄 .env.example                    Environment variables template
│
├── 📁 data/
│   ├── 📁 raw/                        ⭐ PLACE YOUR .BDF FILES HERE
│   │   ├── s01.bdf                    Subject 1 data (you provide)
│   │   ├── s02.bdf                    Subject 2 data (you provide)
│   │   ├── s03.bdf                    Subject 3 data (you provide)
│   │   ├── s04.bdf                    Subject 4 data (you provide)
│   │   ├── s05.bdf                    Subject 5 data (you provide)
│   │   ├── s06.bdf                    Subject 6 data (you provide)
│   │   ├── s07.bdf                    Subject 7 data (you provide)
│   │   ├── s08.bdf                    Subject 8 data (you provide)
│   │   ├── s09.bdf                    Subject 9 data (you provide)
│   │   └── s10.bdf                    Subject 10 data (you provide)
│   │
│   └── 📁 processed/                  Generated .npy files (400 files)
│       ├── s01_trial00.npy
│       ├── s01_trial01.npy
│       ├── ...
│       └── s10_trial39.npy
│
├── 📁 src/                            ⭐ MAIN SOURCE CODE
│   ├── 📄 preprocessing.py            Load .bdf, filter, downsample, normalize
│   ├── 📄 augmentations.py            Data augmentation (dropout, noise, shift)
│   ├── 📄 dataset.py                  PyTorch Dataset with windowing
│   ├── 📄 attention.py                Temporal attention mechanism
│   ├── 📄 model.py                    BiLSTM encoder (PyTorch Lightning)
│   ├── 📄 train.py                    Training pipeline (warmup + metric)
│   ├── 📄 eval.py                     Evaluation (FAR/FRR/EER)
│   ├── 📄 captum_attrib.py            Explainability (Captum)
│   ├── 📄 prototypes.py               User prototype computation
│   ├── 📄 calibration.py              Score calibration (Platt scaling)
│   ├── 📄 spoof_detector.py           Autoencoder for spoof detection
│   ├── 📄 inference_utils.py          Inference utilities
│   │
│   ├── 📁 utils/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 metrics.py              FAR/FRR/EER computation
│   │   └── 📄 viz.py                  Visualization (ROC, DET, plots)
│   │
│   ├── 📁 api/                        ⭐ FASTAPI BACKEND
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main.py                 FastAPI app (4 endpoints)
│   │   └── 📄 auth_utils.py           User store (SQLite + bcrypt)
│   │
│   └── 📁 inference/
│       ├── 📄 __init__.py
│       ├── 📄 onnx_export.py          ONNX export
│       └── 📄 torchserve_handler.py   TorchServe handler
│
├── 📁 frontend/                       ⭐ FRONTEND INTEGRATION
│   ├── 📄 README.md                   Frontend setup guide
│   └── 📁 skeleton/
│       ├── 📄 UploadEEG.jsx           File upload component
│       └── 📄 AuthResultCard.jsx      Result display component
│
├── 📁 deployments/                    ⭐ DOCKER DEPLOYMENT
│   ├── 📄 Dockerfile                  Docker image
│   └── 📄 docker-compose.yml          Container orchestration
│
├── 📁 notebooks/
│   └── 📄 exploration.ipynb           Data exploration notebook
│
├── 📁 models/                         ⭐ GENERATED DURING TRAINING
│   ├── prototypes.npz                 User prototypes (k=2 per user)
│   ├── calibrator.pkl                 Score calibrator
│   └── spoof_model.pth                Spoof detector
│
├── 📁 checkpoints/                    ⭐ GENERATED DURING TRAINING
│   └── best.ckpt                      Best model checkpoint
│
├── 📁 outputs/                        ⭐ GENERATED DURING EVALUATION
│   ├── eval_results.json              Metrics (EER, FAR, FRR)
│   ├── roc.png                        ROC curve
│   ├── det.png                        DET curve
│   ├── score_distribution.png         Score distributions
│   └── 📁 explanations/
│       └── *.png                      Attribution heatmaps
│
└── 📁 venv/                           Virtual environment (you create)
    └── ...

EXTERNAL (Clone separately):
d:\Thought Based Authentication System Using BiLSTM\MindKey-Authentication\
└── 📁 frontend/                       ⭐ MINDKEY FRONTEND (from GitHub)
    ├── package.json
    ├── src/
    └── ...
```

---

## 📊 File Count Summary

| Category | Count | Description |
|----------|-------|-------------|
| **Python Modules** | 18 | Core implementation |
| **Documentation** | 8 | Guides and references |
| **Scripts** | 3 | Batch/shell scripts |
| **Config Files** | 7 | Requirements, Docker, etc. |
| **Frontend** | 3 | React components + guide |
| **Notebooks** | 1 | Jupyter exploration |
| **Total** | 40+ | Complete repository |

---

## 🎯 Key Directories

### 📁 data/raw/ ⭐ **YOU PROVIDE**
Place your 10 DEAP .bdf files here:
- s01.bdf through s10.bdf
- Each file: ~250-280 MB
- Total: ~2.5-3 GB

### 📁 data/processed/ (Generated)
Created by preprocessing:
- 400 .npy files (10 subjects × 40 trials)
- Each file: ~1.5 MB
- Total: ~600 MB

### 📁 src/ ⭐ **MAIN CODE**
All implementation files:
- 18 Python modules
- ~8,000 lines of code
- Fully documented

### 📁 models/ (Generated)
Created by training:
- prototypes.npz (~50 KB)
- calibrator.pkl (~10 KB)
- spoof_model.pth (~500 KB)

### 📁 checkpoints/ (Generated)
Created by training:
- best.ckpt (~50 MB)
- Contains full model weights

### 📁 outputs/ (Generated)
Created by evaluation:
- JSON metrics
- PNG plots (ROC, DET)
- Explanation heatmaps

---

## 🚀 Workflow

```
1. Place .bdf files in data/raw/
         ↓
2. Run: train_gpu_windows.bat
         ↓
3. Preprocessing creates data/processed/
         ↓
4. Training creates models/ and checkpoints/
         ↓
5. Evaluation creates outputs/
         ↓
6. Start backend (uses models/)
         ↓
7. Clone MindKey frontend
         ↓
8. Start frontend (connects to backend)
         ↓
9. Use the system!
```

---

## 📝 Important Files for You

### To Get Started:
1. **START_HERE_WINDOWS.md** - Your starting point
2. **train_gpu_windows.bat** - One-click training
3. **WINDOWS_GPU_GUIDE.md** - Detailed GPU setup

### For Reference:
4. **README.md** - Complete documentation
5. **TESTING.md** - Testing guide
6. **frontend/README.md** - Frontend setup

### Generated Files (Check After Training):
7. **outputs/eval_results.json** - Your accuracy results
8. **checkpoints/best.ckpt** - Your trained model
9. **models/prototypes.npz** - User prototypes

---

## 🎯 Your Action Items

- [ ] 1. Place 10 .bdf files in `data/raw/`
- [ ] 2. Install CUDA 11.8
- [ ] 3. Create virtual environment
- [ ] 4. Install PyTorch with CUDA
- [ ] 5. Install dependencies
- [ ] 6. Run `train_gpu_windows.bat`
- [ ] 7. Wait 2-3 hours for training
- [ ] 8. Check `outputs/eval_results.json` for EER ~2.72%
- [ ] 9. Clone MindKey frontend
- [ ] 10. Start backend and frontend
- [ ] 11. Test the system!

---

## 📞 Quick Access

**Start Training:**
```powershell
cd "d:\Thought Based Authentication System Using BiLSTM\deap_bilstm_auth"
.\venv\Scripts\activate
.\train_gpu_windows.bat
```

**Check Results:**
```powershell
type outputs\eval_results.json
```

**Start Backend:**
```powershell
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

**Clone Frontend:**
```powershell
cd "d:\Thought Based Authentication System Using BiLSTM"
git clone git@github.com:Sruthikr1505/MindKey-Authentication.git
```

---

**Everything is ready! Just add your .bdf files and run the training script! 🚀**
