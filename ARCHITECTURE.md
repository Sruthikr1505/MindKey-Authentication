# System Architecture

## Overview

The DEAP BiLSTM Authentication System is a complete end-to-end biometric authentication pipeline using EEG signals. The architecture follows a modular design with clear separation between data processing, model training, inference, and deployment.

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                   │
├─────────────────────────────────────────────────────────────────────┤
│  DEAP Dataset (s01-s10)                                             │
│  ├─ Raw: .bdf files (40 trials × 32 channels × 63s @ 512Hz)        │
│  └─ Processed: .npy files (windowed, normalized @ 128Hz)           │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    PREPROCESSING PIPELINE                            │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      TRAINING PIPELINE                               │
├─────────────────────────────────────────────────────────────────────┤
│  Phase 1: Warmup (Classification)                                   │
│  ├─ BiLSTM Encoder + Classification Head                           │
│  ├─ Loss: CrossEntropy                                              │
│  └─ Epochs: 3                                                       │
│                                                                      │
│  Phase 2: Metric Learning                                           │
│  ├─ BiLSTM Encoder (remove classification head)                    │
│  ├─ Loss: ProxyAnchor / Triplet                                    │
│  ├─ Epochs: 20                                                      │
│  └─ Output: L2-normalized 128-dim embeddings                       │
│                                                                      │
│  Phase 3: Prototype Computation                                     │
│  ├─ Extract train embeddings                                        │
│  ├─ K-means clustering (k=2 per user)                              │
│  └─ Save prototypes.npz                                             │
│                                                                      │
│  Phase 4: Spoof Detector Training                                   │
│  ├─ Autoencoder (128→64→32→64→128)                                 │
│  ├─ Train on genuine embeddings only                               │
│  ├─ Compute reconstruction errors                                   │
│  └─ Set threshold (99th percentile)                                │
│                                                                      │
│  Phase 5: Score Calibration                                         │
│  ├─ Compute validation similarities                                 │
│  ├─ Fit Platt scaling (Logistic Regression)                        │
│  └─ Save calibrator.pkl                                             │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     INFERENCE PIPELINE                               │
├─────────────────────────────────────────────────────────────────────┤
│  Input: Probe EEG trial                                             │
│     ↓                                                                │
│  Preprocess (same as training)                                      │
│     ↓                                                                │
│  BiLSTM Encoder → Embedding (128-dim)                               │
│     ↓                                                                │
│  ┌──────────────────┐        ┌──────────────────┐                  │
│  │ Similarity Score │        │ Spoof Detection  │                  │
│  │ vs Prototypes    │        │ (Reconstruction) │                  │
│  │ (Cosine Sim)     │        │ Error Check      │                  │
│  └──────────────────┘        └──────────────────┘                  │
│     ↓                              ↓                                │
│  Calibration                   Threshold Check                      │
│  (Score → Probability)         (Error > Threshold?)                │
│     ↓                              ↓                                │
│  ┌────────────────────────────────────┐                            │
│  │      Authentication Decision        │                            │
│  │  Authenticated = (NOT spoof) AND    │                            │
│  │                  (prob >= 0.5)      │                            │
│  └────────────────────────────────────┘                            │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    EXPLAINABILITY MODULE                             │
├─────────────────────────────────────────────────────────────────────┤
│  Captum Attribution Methods:                                        │
│  ├─ Integrated Gradients                                            │
│  ├─ GradientSHAP                                                    │
│  └─ Saliency Maps                                                   │
│                                                                      │
│  Outputs:                                                            │
│  ├─ Heatmap (channels × time)                                       │
│  ├─ Top 5 important channels                                        │
│  └─ Top 5 important time windows                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Model Architecture

### BiLSTM Encoder

```
Input: (batch, 32 channels, 256 timesteps)
   ↓
Permute: (batch, 256 timesteps, 32 channels)
   ↓
Linear Projection: 32 → 128
   ↓
Bi-LSTM Layer 1: hidden=128, bidirectional
   ↓
Bi-LSTM Layer 2: hidden=128, bidirectional
   ↓  (output: batch × 256 × 256)
   ↓
┌─────────────────────────────────┐
│  Temporal Attention (optional)  │
│  ├─ Linear: 256 → 128           │
│  ├─ Tanh                        │
│  ├─ Linear: 128 → 1             │
│  ├─ Softmax (over time)         │
│  └─ Weighted sum                │
└─────────────────────────────────┘
   ↓  (output: batch × 256)
   ↓
FC Layer 1: 256 → 128
   ↓
ReLU + Dropout(0.2)
   ↓
FC Layer 2: 128 → 128
   ↓
L2 Normalization
   ↓
Output: (batch, 128) embeddings
```

### Spoof Detector (Autoencoder)

```
Input: (batch, 128) embeddings
   ↓
Encoder:
   Linear: 128 → 64
   ReLU
   Linear: 64 → 32
   ReLU
   ↓
Latent: (batch, 32)
   ↓
Decoder:
   Linear: 32 → 64
   ReLU
   Linear: 64 → 128
   ↓
Reconstructed: (batch, 128)

Loss: MSE(input, reconstructed)
Spoof Score: MSE per sample
```

---

## API Architecture

### FastAPI Backend

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Startup:                                                    │
│  ├─ Load BiLSTM encoder                                     │
│  ├─ Load system prototypes                                  │
│  ├─ Load calibrator                                         │
│  ├─ Load spoof detector                                     │
│  └─ Initialize SQLite database                              │
│                                                              │
│  Endpoints:                                                  │
│  ├─ GET  /health          → Health check                    │
│  ├─ POST /register        → User registration               │
│  ├─ POST /auth/login      → Authentication                  │
│  ├─ GET  /explain/{id}    → Explanation heatmap            │
│  └─ GET  /docs            → OpenAPI documentation           │
│                                                              │
│  Middleware:                                                 │
│  ├─ CORS (allow frontend origins)                          │
│  ├─ Request logging                                         │
│  └─ Error handling                                          │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    prototypes_path VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Data Flow

### Registration Flow

```
User → Frontend → API /register
                    ↓
              Receive enrollment trials (.npy files)
                    ↓
              Preprocess each trial
                    ↓
              Extract embeddings (BiLSTM)
                    ↓
              Compute prototypes (k-means, k=2)
                    ↓
              Save prototypes to disk
                    ↓
              Hash password (bcrypt)
                    ↓
              Store user in database
                    ↓
              Return success response
```

### Authentication Flow

```
User → Frontend → API /auth/login
                    ↓
              Verify password (bcrypt)
                    ↓
              Load user prototypes
                    ↓
              Preprocess probe trial
                    ↓
              Extract embedding (BiLSTM)
                    ↓
         ┌────────────────────────┐
         │  Similarity Scoring    │
         │  ├─ Cosine similarity  │
         │  │   vs each prototype │
         │  └─ Take max score     │
         └────────────────────────┘
                    ↓
         ┌────────────────────────┐
         │  Spoof Detection       │
         │  ├─ Autoencoder        │
         │  │   reconstruction    │
         │  └─ Error > threshold? │
         └────────────────────────┘
                    ↓
         ┌────────────────────────┐
         │  Calibration           │
         │  └─ Score → Probability│
         └────────────────────────┘
                    ↓
              Make decision:
              authenticated = (NOT spoof) AND (prob >= 0.5)
                    ↓
              Save probe for explanation
                    ↓
              Return result + explain_id
```

---

## Deployment Architecture

### Docker Compose

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Network                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │   Backend API    │         │   Frontend       │         │
│  │   (FastAPI)      │◄────────│   (React+nginx)  │         │
│  │   Port: 8000     │         │   Port: 3000     │         │
│  └──────────────────┘         └──────────────────┘         │
│          │                                                   │
│          │                                                   │
│  ┌──────────────────┐                                       │
│  │   Database       │                                       │
│  │   (SQLite/PG)    │                                       │
│  │   Port: 5432     │                                       │
│  └──────────────────┘                                       │
│                                                              │
│  Volumes:                                                    │
│  ├─ models/    (shared)                                     │
│  ├─ data/      (shared)                                     │
│  └─ outputs/   (shared)                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Considerations

### Authentication Security

1. **Password Storage**: bcrypt hashing with salt
2. **Database**: SQLAlchemy with parameterized queries (SQL injection prevention)
3. **CORS**: Configurable allowed origins
4. **Rate Limiting**: TODO - implement per-user rate limits
5. **HTTPS**: TODO - add TLS/SSL in production

### Biometric Security

1. **Liveness Detection**: Spoof detector via reconstruction error
2. **Template Protection**: Embeddings are L2-normalized, not raw EEG
3. **Multi-factor**: Password + EEG biometric
4. **Revocability**: Can update prototypes without re-enrollment

---

## Performance Characteristics

### Latency

| Operation | Time (CPU) | Time (GPU) |
|-----------|-----------|-----------|
| Preprocessing | ~100ms | N/A |
| Embedding extraction | ~50ms | ~10ms |
| Similarity scoring | <1ms | <1ms |

### Data Splits

Per subject (40 trials total - using ALL trials for better accuracy):
- **Train:** Trials 0-23 (24 trials, 60%)
- **Validation:** Trials 24-29 (6 trials, 15%)
- **Test:** Trials 30-39 (10 trials, 25%)

**Total across 10 subjects:**
- Training: 240 trials (10 subjects × 24 trials)
- Validation: 60 trials (10 subjects × 6 trials)
- Testing: 100 trials (10 subjects × 10 trials)
- **Grand Total: 400 trials**

### Throughput

- **CPU**: ~6-7 authentications/second
- **GPU**: ~60-70 authentications/second
{{ ... }}
### Storage

- **Model weights**: ~5 MB
- **Prototypes per user**: ~1 KB
- **Database**: ~10 KB per user

---

## Scalability

### Horizontal Scaling

```
                    Load Balancer
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    API Server 1    API Server 2    API Server 3
         │               │               │
         └───────────────┼───────────────┘
                         │
                  Shared Database
                  (PostgreSQL)
```

### Optimization Strategies

1. **Model Serving**: Use ONNX Runtime or TorchServe
2. **Caching**: Cache user prototypes in Redis
3. **Batch Processing**: Batch multiple authentication requests
4. **GPU Pooling**: Share GPU across multiple workers
5. **CDN**: Serve frontend and static assets via CDN

---

## Monitoring & Observability

### Metrics to Track

1. **Performance**:
   - Authentication latency (p50, p95, p99)
   - Throughput (requests/second)
   - Model inference time
   - Memory usage
   - Disk I/O
   - API error rates

### Logging
{{ ... }}
- **Application logs**: INFO level for normal operations
- **Security logs**: All authentication attempts (success/failure)
- **Error logs**: Exceptions and failures
- **Audit logs**: User registration, prototype updates

---

## Future Enhancements

1. **Multi-session enrollment**: Collect trials across multiple sessions
2. **Template update**: Online learning to adapt to user changes
3. **Cross-dataset evaluation**: Test on other EEG datasets
4. **Mobile deployment**: Edge inference on smartphones
5. **Real-time streaming**: Continuous authentication
6. **Federated learning**: Privacy-preserving distributed training

---

**Last Updated**: 2025-10-05
