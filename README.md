# DEAP BiLSTM Authentication System

**Hardware-free EEG authentication using Bi-directional LSTM with attention mechanism**

A complete end-to-end prototype for biometric authentication using EEG signals from the DEAP dataset (subjects s01-s10). The system includes preprocessing, deep metric learning, prototype-based verification, spoof detection, score calibration, explainability, and a FastAPI backend with React frontend skeleton.

---

## 🎯 Features

- **BiLSTM Encoder** with optional temporal attention for EEG embedding extraction
- **Metric Learning** using ProxyAnchor or Triplet loss for discriminative embeddings
- **Prototype-based Authentication** with k-means clustering (k=2 prototypes per user)
- **Spoof Detection** via embedding autoencoder and reconstruction error
- **Score Calibration** using Platt scaling for probability estimates
- **Explainability** with Captum (Integrated Gradients, GradSHAP)
- **FastAPI Backend** with `/register`, `/auth/login`, `/explain` endpoints
- **React + Tailwind Frontend** skeleton components
- **Docker Deployment** ready with docker-compose
- **ONNX Export** for production deployment

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     EEG Authentication Pipeline                  │
└─────────────────────────────────────────────────────────────────┘

1. DATA PREPROCESSING
   Raw EEG (.bdf) → Bandpass (1-50Hz) → Downsample (128Hz) → 
   Z-score → Sliding Windows (2s, 1s step)

2. TRAINING PIPELINE
   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
   │   Warmup     │ →    │   Metric     │ →    │  Prototypes  │
   │ (CrossEnt)   │      │  Learning    │      │  (k-means)   │
   └──────────────┘      └──────────────┘      └──────────────┘
                                                       ↓
   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
   │ Calibration  │ ←    │    Spoof     │ ←    │  Embeddings  │
   │   (Platt)    │      │  Detector    │      │ Extraction   │
   └──────────────┘      └──────────────┘      └──────────────┘

3. INFERENCE
   Probe EEG → Preprocess → BiLSTM Encoder → Embedding
                                                  ↓
   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
   │ Similarity   │ →    │ Calibrated   │ →    │   Decision   │
   │ vs Prototype │      │ Probability  │      │ (Auth/Reject)│
   └──────────────┘      └──────────────┘      └──────────────┘
                                                  ↓
                                          ┌──────────────┐
                                          │    Spoof     │
                                          │   Detection  │
                                          └──────────────┘

4. EXPLAINABILITY
   Probe EEG → Captum Attribution → Heatmap + Top Channels/Windows
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- DEAP dataset (subjects s01-s10 in `.bdf` format)
- 8GB+ RAM recommended
- Optional: CUDA-capable GPU

### Installation

```bash
# Clone or navigate to repository
cd deap_bilstm_auth

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Data Setup

Place DEAP subject files in `data/raw/`:

```
data/raw/
├── s01.bdf
├── s02.bdf
├── ...
└── s10.bdf
```

**To obtain DEAP dataset:**
1. Visit https://www.eecs.qmul.ac.uk/mmv/datasets/deap/
2. Request access and download
3. Extract `.bdf` files to `data/raw/`

### Fast Demo (CPU-friendly)

```bash
# Run complete demo pipeline
./run_demo.sh
```

This will:
1. Preprocess 3 trials per subject (fast mode)
2. Train model with reduced epochs
3. Start FastAPI server at http://localhost:8000

---

## 📖 Detailed Usage

### 1. Preprocessing

Process all 40 trials per subject for better accuracy:

```bash
python src/preprocessing.py \
    --input_dir data/raw \
    --output_dir data/processed \
    --subjects 1 2 3 4 5 6 7 8 9 10 \
    --fs_in 512 \
    --fs_out 128 \
    --seed 42
```

**Options:**
- `--fast`: Process only 3 trials per subject (for quick testing)
- `--ica`: Enable ICA artifact removal (slow but improves quality)

**Output:** `data/processed/sXX_trialYY.npy` files

### 2. Training

Full training with all 40 trials:

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

**Training stages:**
1. **Warmup (3 epochs):** Classification with CrossEntropy
2. **Metric Learning (20 epochs):** ProxyAnchor loss for embedding space
3. **Prototype Computation:** k-means clustering (k=2) on training embeddings
4. **Spoof Detector Training:** Autoencoder on genuine embeddings
5. **Calibration:** Platt scaling on validation scores

**Outputs:**
- `models/encoder.pth` - BiLSTM encoder weights
- `models/prototypes.npz` - User prototypes
- `models/spoof_model.pth` - Spoof detector
- `models/spoof_threshold.npy` - Spoof detection threshold
- `models/calibrator.pkl` - Score calibrator
- `models/config.json` - Model configuration

### 3. Evaluation

```bash
python src/eval.py \
    --data_dir data/processed \
    --models_dir models \
    --output_dir outputs \
    --batch_size 64 \
    --device cuda
```

**Outputs:**
- `outputs/eval_results.json` - EER, FAR, FRR metrics
- `outputs/roc.png` - ROC curve
- `outputs/det.png` - DET curve
- `outputs/score_dist.png` - Score distribution

**Expected Performance (with 40 trials):**
- EER: < 5% (with proper training)
- FAR @ 1% FRR: < 2%

### 4. API Server

```bash
# Start server
cd src/api
python main.py

# Or with uvicorn directly
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Endpoints:**

- `GET /health` - Health check
- `POST /register` - Register new user with enrollment trials
- `POST /auth/login` - Authenticate user with probe trial
- `GET /explain/{id}` - Get explanation heatmap
- `GET /docs` - Interactive API documentation

**Example: Register User**

```bash
curl -X POST http://localhost:8000/register \
  -F "username=alice" \
  -F "password=secret123" \
  -F "enrollment_trials=@trial1.npy" \
  -F "enrollment_trials=@trial2.npy" \
  -F "enrollment_trials=@trial3.npy"
```

**Example: Authenticate**

```bash
curl -X POST http://localhost:8000/auth/login \
  -F "username=alice" \
  -F "password=secret123" \
  -F "probe=@probe_trial.npy"
```

**Response:**
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

### 5. Explainability

```bash
python src/captum_attrib.py
```

Or via API:
```bash
curl http://localhost:8000/explain/{explain_id} -o explanation.png
```

Generates heatmap showing important channels and time windows.

---

## 🐳 Docker Deployment

### Build and Run

```bash
cd deployments
docker-compose up --build
```

**Services:**
- Backend API: http://localhost:8000
- (Optional) Frontend: http://localhost:3000
- (Optional) PostgreSQL: localhost:5432

### Production Configuration

1. Update `docker-compose.yml` to use PostgreSQL instead of SQLite
2. Set environment variables for secrets
3. Configure nginx for frontend
4. Enable HTTPS with Let's Encrypt

---

## 🧪 ONNX Export

Export model for production deployment:

```bash
python src/inference/onnx_export.py \
    --checkpoint models/encoder.pth \
    --config models/config.json \
    --output models/encoder.onnx \
    --verify
```

Use with ONNX Runtime for faster inference:

```python
import onnxruntime as ort
session = ort.InferenceSession("models/encoder.onnx")
embedding = session.run(None, {"input": eeg_trial})[0]
```

---

## 📁 Repository Structure

```
deap_bilstm_auth/
├── data/
│   ├── raw/                    # DEAP .bdf files (s01-s10)
│   └── processed/              # Preprocessed .npy files
├── src/
│   ├── preprocessing.py        # EEG preprocessing pipeline
│   ├── augmentations.py        # Data augmentation
│   ├── dataset.py              # PyTorch Dataset & DataLoader
│   ├── attention.py            # Temporal attention module
│   ├── model.py                # BiLSTM encoder (Lightning)
│   ├── train.py                # Training pipeline
│   ├── eval.py                 # Evaluation & metrics
│   ├── prototypes.py           # Prototype computation
│   ├── calibration.py          # Score calibration
│   ├── spoof_detector.py       # Autoencoder spoof detection
│   ├── inference_utils.py      # Inference helpers
│   ├── captum_attrib.py        # Explainability
│   ├── utils/
│   │   ├── metrics.py          # FAR/FRR/EER computation
│   │   └── viz.py              # Plotting utilities
│   ├── api/
│   │   ├── main.py             # FastAPI application
│   │   └── auth_utils.py       # User database & auth
│   └── inference/
│       ├── onnx_export.py      # ONNX export
│       └── torchserve_handler.py # TorchServe handler
├── frontend/
│   ├── README.md               # Frontend setup guide
│   └── skeleton/               # React component stubs
│       ├── UploadEEG.jsx
│       ├── WaveformPlot.jsx
│       ├── HeatmapDisplay.jsx
│       └── AuthResultCard.jsx
├── deployments/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
├── models/                     # Trained models (generated)
├── outputs/                    # Evaluation outputs (generated)
├── checkpoints/                # Training checkpoints (generated)
├── requirements.txt
├── run_demo.sh                 # Quick demo script
└── README.md
```

---

## 🔬 Technical Details

### Model Architecture

**BiLSTM Encoder:**
- Input: (batch, 32 channels, 256 timesteps) @ 128 Hz
- Linear projection: 32 → 128
- Bi-LSTM: 2 layers, hidden=128
- Temporal Attention (optional): Weighted pooling over time
- FC layers: 256 → 128 → 128
- L2 normalization → 128-dim embedding

**Spoof Detector:**
- Autoencoder: 128 → 64 → 32 → 64 → 128
- Trained on genuine embeddings only
- Threshold: 99th percentile reconstruction error

### Hyperparameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `fs_out` | 128 Hz | Output sampling frequency |
| `window_size` | 2.0s (256 samples) | Sliding window size |
| `window_step` | 1.0s (128 samples) | Sliding window step |
| `batch_size` | 64 | Training batch size |
| `warmup_epochs` | 3 | Classification warmup |
| `metric_epochs` | 20 | Metric learning epochs |
| `lr` | 1e-3 | Learning rate (AdamW) |
| `k_prototypes` | 2 | Prototypes per user |
| `embedding_dim` | 128 | Embedding dimension |

### Data Splits

Per subject (40 trials total):
- **Train:** Trials 0-23 (60%)
- **Validation:** Trials 24-29 (15%)
- **Test:** Trials 30-39 (25%)

### Augmentations (Training Only)

- Channel dropout (p=0.15)
- Gaussian noise (SNR 12-28 dB)
- Time shift (±0.2s)
- Mixup (α=0.2, same user only)

---

## 📊 Expected Results

With **40 trials per subject** and full training:

| Metric | Value |
|--------|-------|
| EER | 3-8% |
| FAR @ 1% FRR | 1-3% |
| Spoof Detection Rate | >95% |
| Inference Time | <50ms (CPU) |

With **fast mode (3 trials)**:
- EER: 15-25% (demonstration only)

---

## 🛠️ Troubleshooting

### Issue: "Models not found"
**Solution:** Run training first: `python src/train.py --fast`

### Issue: Out of memory
**Solution:** 
- Reduce `batch_size` to 32 or 16
- Use `--fast` mode
- Process fewer subjects

### Issue: ICA fails during preprocessing
**Solution:** Disable ICA with `--no-ica` or use `--fast` mode (ICA disabled by default)

### Issue: Poor authentication accuracy
**Solution:**
- Train with all 40 trials (remove `--fast`)
- Increase `metric_epochs` to 50
- Use `--device cuda` for GPU acceleration
- Ensure proper data preprocessing

### Issue: API server won't start
**Solution:**
- Check models exist: `ls models/`
- Verify port 8000 is available: `lsof -i :8000`
- Check logs for errors

---

## 🔐 Security Considerations

**For Production:**
1. Use HTTPS for API endpoints
2. Implement rate limiting
3. Store passwords with bcrypt (already implemented)
4. Use PostgreSQL instead of SQLite
5. Add JWT authentication tokens
6. Encrypt EEG data at rest
7. Implement audit logging
8. Set up proper CORS policies

---

## 📚 References

- **DEAP Dataset:** Koelstra et al., "DEAP: A Database for Emotion Analysis using Physiological Signals", IEEE TAC, 2012
- **Metric Learning:** Movshovitz-Attias et al., "No Fuss Distance Metric Learning using Proxies", ICCV 2017
- **EEG Authentication:** Maiorana et al., "Eigenbrains and Eigentemplates for EEG-based Authentication", BIOSIG 2016

---

## 📝 License

This project is for research and educational purposes. DEAP dataset usage requires proper citation and adherence to their license terms.

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Multi-session enrollment
- Online learning / template update
- Cross-dataset evaluation
- Mobile/edge deployment
- Real-time streaming inference

---

## 📧 Support

For issues and questions:
1. Check troubleshooting section above
2. Review API docs at `/docs` endpoint
3. Examine logs in console output

---

**Built with:** PyTorch, PyTorch Lightning, Captum, MNE-Python, FastAPI, React, Tailwind CSS

**Last Updated:** 2025-10-05
