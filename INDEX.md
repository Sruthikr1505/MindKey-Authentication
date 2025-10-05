# Repository Index - DEAP BiLSTM Authentication System

## 📚 Documentation Files (Read These First)

| File | Purpose | Read Time |
|------|---------|-----------|
| **README.md** | Main documentation - comprehensive guide | 15 min |
| **QUICKSTART.md** | Fast 5-minute setup guide | 5 min |
| **PROJECT_SUMMARY.md** | Complete project overview | 10 min |
| **COMMANDS_SUMMARY.md** | All commands reference | 5 min |
| **ARCHITECTURE.md** | System architecture details | 20 min |

## 🚀 Quick Start

```bash
# 1. Verify setup
./verify_setup.py

# 2. Run fast demo
./run_demo.sh

# 3. Test API
./test_api.sh
```

## 📁 File Organization

### Core Python Modules (src/)

#### Data Processing
- `src/preprocessing.py` - Load and preprocess EEG data
- `src/augmentations.py` - Data augmentation techniques
- `src/dataset.py` - PyTorch Dataset and DataLoader

#### Model Components
- `src/model.py` - BiLSTM encoder (main model)
- `src/attention.py` - Temporal attention mechanism

#### Training & Evaluation
- `src/train.py` - Complete training pipeline
- `src/eval.py` - Evaluation with metrics

#### Authentication Components
- `src/prototypes.py` - User prototype computation
- `src/calibration.py` - Score calibration
- `src/spoof_detector.py` - Spoof detection
- `src/inference_utils.py` - Inference helpers

#### Utilities
- `src/utils/metrics.py` - FAR/FRR/EER computation
- `src/utils/viz.py` - Plotting functions
- `src/captum_attrib.py` - Explainability

#### API Backend
- `src/api/main.py` - FastAPI application
- `src/api/auth_utils.py` - User database

#### Deployment
- `src/inference/onnx_export.py` - ONNX export
- `src/inference/torchserve_handler.py` - TorchServe handler

### Frontend (frontend/)
- `frontend/README.md` - Setup guide
- `frontend/skeleton/UploadEEG.jsx` - File upload
- `frontend/skeleton/WaveformPlot.jsx` - Waveform display
- `frontend/skeleton/HeatmapDisplay.jsx` - Heatmap display
- `frontend/skeleton/AuthResultCard.jsx` - Result card

### Deployment (deployments/)
- `deployments/Dockerfile` - Backend container
- `deployments/docker-compose.yml` - Multi-container setup
- `deployments/nginx.conf` - Nginx config

### Configuration
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables
- `.gitignore` - Git ignore rules

### Scripts
- `run_demo.sh` - Fast demo script
- `test_api.sh` - API testing
- `verify_setup.py` - Setup verification

## 🎯 Common Tasks

### First Time Setup
1. Read `QUICKSTART.md`
2. Run `./verify_setup.py`
3. Place DEAP data in `data/raw/`
4. Run `./run_demo.sh`

### Development Workflow
1. Modify code in `src/`
2. Test with `python src/module.py`
3. Train with `python src/train.py --fast`
4. Evaluate with `python src/eval.py`

### API Development
1. Start server: `cd src/api && python main.py`
2. View docs: http://localhost:8000/docs
3. Test endpoints: `./test_api.sh`

### Frontend Development
1. Read `frontend/README.md`
2. Setup React app
3. Copy components from `frontend/skeleton/`
4. Connect to API

### Deployment
1. Build: `cd deployments && docker-compose build`
2. Run: `docker-compose up`
3. Access: http://localhost:8000

## 📊 Generated Files (After Running)

### After Preprocessing
- `data/processed/s01_trial00.npy` through `s10_trial39.npy`

### After Training
- `models/encoder.pth` - Model weights
- `models/prototypes.npz` - User prototypes
- `models/spoof_model.pth` - Spoof detector
- `models/spoof_threshold.npy` - Threshold
- `models/calibrator.pkl` - Calibrator
- `models/config.json` - Model config
- `checkpoints/*.ckpt` - Training checkpoints

### After Evaluation
- `outputs/eval_results.json` - Metrics
- `outputs/roc.png` - ROC curve
- `outputs/det.png` - DET curve
- `outputs/score_dist.png` - Score distribution

### After API Usage
- `data/users.db` - User database
- `data/user_prototypes/*.npy` - User enrollments
- `outputs/explanations/*.png` - Explanation heatmaps

## 🔍 Finding Information

### "How do I...?"

| Task | File to Check |
|------|---------------|
| Install dependencies | `QUICKSTART.md`, `requirements.txt` |
| Run fast demo | `QUICKSTART.md`, `run_demo.sh` |
| Preprocess data | `src/preprocessing.py`, `COMMANDS_SUMMARY.md` |
| Train model | `src/train.py`, `COMMANDS_SUMMARY.md` |
| Evaluate model | `src/eval.py`, `COMMANDS_SUMMARY.md` |
| Use API | `src/api/main.py`, `test_api.sh` |
| Deploy with Docker | `deployments/docker-compose.yml` |
| Export to ONNX | `src/inference/onnx_export.py` |
| Build frontend | `frontend/README.md` |
| Understand architecture | `ARCHITECTURE.md` |
| See all commands | `COMMANDS_SUMMARY.md` |
| Troubleshoot | `README.md` (Troubleshooting section) |

### "What does this file do?"

| File Pattern | Purpose |
|--------------|---------|
| `src/*.py` | Core Python modules |
| `src/api/*.py` | API backend |
| `src/utils/*.py` | Utility functions |
| `src/inference/*.py` | Model export/serving |
| `frontend/skeleton/*.jsx` | React components |
| `deployments/*` | Docker configuration |
| `*.md` | Documentation |
| `*.sh` | Shell scripts |

## 📖 Reading Order (Recommended)

### For Quick Start (30 minutes)
1. `QUICKSTART.md` (5 min)
2. Run `./verify_setup.py` (1 min)
3. Run `./run_demo.sh` (10 min)
4. Read `PROJECT_SUMMARY.md` (10 min)
5. Explore API docs at http://localhost:8000/docs (5 min)

### For Full Understanding (2 hours)
1. `README.md` (20 min)
2. `ARCHITECTURE.md` (20 min)
3. `src/model.py` - read code (15 min)
4. `src/train.py` - read code (15 min)
5. `src/api/main.py` - read code (15 min)
6. `COMMANDS_SUMMARY.md` (10 min)
7. Run full training (30 min)

### For Development (Ongoing)
1. Start with `QUICKSTART.md`
2. Reference `COMMANDS_SUMMARY.md` for commands
3. Read relevant `src/*.py` files
4. Check `ARCHITECTURE.md` for design decisions
5. Use `README.md` for troubleshooting

## 🎓 Learning Path

### Beginner
1. ✅ Run fast demo
2. ✅ Understand data flow (read `ARCHITECTURE.md`)
3. ✅ Test API endpoints
4. ✅ View evaluation results

### Intermediate
1. ✅ Run full training (40 trials)
2. ✅ Modify hyperparameters
3. ✅ Implement custom augmentations
4. ✅ Build frontend UI

### Advanced
1. ✅ Add new metric learning losses
2. ✅ Implement cross-dataset evaluation
3. ✅ Deploy to production
4. ✅ Optimize for mobile/edge

## 🔗 External Resources

- **DEAP Dataset**: https://www.eecs.qmul.ac.uk/mmv/datasets/deap/
- **PyTorch Docs**: https://pytorch.org/docs/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **MNE-Python**: https://mne.tools/
- **Captum**: https://captum.ai/

## ✅ Checklist

### Before Starting
- [ ] Python 3.10+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] DEAP data files in `data/raw/`
- [ ] Ran `./verify_setup.py` successfully

### After Demo
- [ ] Preprocessing completed
- [ ] Model trained
- [ ] API server running
- [ ] Successfully registered a user
- [ ] Successfully authenticated

### For Production
- [ ] Full training (40 trials) completed
- [ ] Evaluation metrics acceptable (EER < 5%)
- [ ] Docker deployment tested
- [ ] Frontend built and connected
- [ ] Security review completed
- [ ] Documentation updated

## 📞 Getting Help

1. **Check documentation**: Start with `README.md` and `QUICKSTART.md`
2. **Run verification**: `./verify_setup.py`
3. **Check logs**: Look at console output for errors
4. **API docs**: Visit http://localhost:8000/docs
5. **Troubleshooting**: See `README.md` Troubleshooting section

## 🎯 Key Files Summary

| Category | Must-Read Files |
|----------|----------------|
| **Getting Started** | `QUICKSTART.md`, `verify_setup.py`, `run_demo.sh` |
| **Documentation** | `README.md`, `PROJECT_SUMMARY.md`, `ARCHITECTURE.md` |
| **Core Code** | `src/model.py`, `src/train.py`, `src/eval.py` |
| **API** | `src/api/main.py`, `test_api.sh` |
| **Deployment** | `deployments/docker-compose.yml`, `Dockerfile` |
| **Reference** | `COMMANDS_SUMMARY.md`, `INDEX.md` (this file) |

---

**Total Files**: 50+ files
**Lines of Code**: ~5,000+ lines
**Documentation**: ~3,000+ lines

**Status**: ✅ Complete and ready to use

**Last Updated**: 2025-10-05
