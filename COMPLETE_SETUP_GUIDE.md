# Complete Setup Guide - From Zero to Running System

## 🎯 Using Your Downloaded DEAP Dataset (s01-s10, 40 trials each)

This guide provides **exact step-by-step commands** to set up and run the complete system using your downloaded DEAP .bdf files for maximum accuracy.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- ✅ Downloaded DEAP dataset files: `s01.bdf`, `s02.bdf`, ..., `s10.bdf`
- ✅ macOS system (as per your setup)
- ✅ Python 3.10 or higher installed
- ✅ At least 8GB RAM
- ✅ At least 5GB free disk space
- ✅ Terminal access

---

## Part 1: Initial Setup (10 minutes)

### Step 1.1: Navigate to Project Directory

```bash
cd "/Users/sruthikr/Desktop/Thought Based Authentiction System Using BiLSTM/deap_bilstm_auth"
```

### Step 1.2: Create Data Directory Structure

```bash
# Create the raw data directory
mkdir -p data/raw

# Verify it was created
ls -la data/
```

**Expected output**: You should see a `raw/` directory inside `data/`

### Step 1.3: Copy Your Downloaded DEAP Files

**Important**: Copy your downloaded .bdf files to the `data/raw/` directory.

Based on your screenshot, you have files in Downloads. Copy them:

```bash
# Copy all .bdf files from Downloads to data/raw/
cp ~/Downloads/s*.bdf data/raw/

# Verify all 10 files are copied
ls -lh data/raw/
```

**Expected output**: You should see 10 files:
```
s01.bdf  (285.9 MB)
s02.bdf  (273 MB)
s03.bdf  (286.4 MB)
s04.bdf  (243.4 MB)
s05.bdf  (283.7 MB)
s06.bdf  (284.4 MB)
s07.bdf  (263.3 MB)
s08.bdf  (259.3 MB)
s09.bdf  (277.7 MB)
s10.bdf  (258.9 MB)
```

### Step 1.4: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Verify it was created
ls -la venv/
```

**Expected output**: You should see `bin/`, `lib/`, `include/` directories

### Step 1.5: Activate Virtual Environment

```bash
source venv/bin/activate
```

**Expected output**: Your terminal prompt should now show `(venv)` at the beginning:
```
(venv) sruthikr@MacBook deap_bilstm_auth %
```

### Step 1.6: Upgrade pip

```bash
pip install --upgrade pip
```

### Step 1.7: Install All Dependencies

```bash
pip install -r requirements.txt
```

**Expected time**: 3-5 minutes

**Note**: You may see some warnings - these are normal. Wait for installation to complete.

### Step 1.8: Verify Installation

```bash
./verify_setup.py
```

**Expected output**: All checks should pass with ✓ marks:
```
✓ Python version: 3.10.x
✓ PyTorch
✓ PyTorch Lightning
✓ MNE-Python
...
✓ Found 10 .bdf files in data/raw/
```

---

## Part 2: Data Preprocessing (15-20 minutes)

### Step 2.1: Preprocess All 40 Trials Per Subject

**This is the key step for better accuracy!**

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
- Loads each .bdf file (all 40 trials per subject)
- Applies bandpass filter (1-50 Hz)
- Applies notch filter (50/60 Hz powerline)
- Downsamples from 512 Hz → 128 Hz
- Z-score normalizes each channel
- Saves each trial as a separate .npy file

**Expected time**: 15-20 minutes for all 10 subjects

**Progress**: You'll see output like:
```
INFO - Loading data for subjects: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
Processing subjects: 100%|████████████| 10/10
INFO - Loaded 40 trials with 32 channels and 32256 samples from s01.bdf
INFO - Preprocessed 40 trials: (40, 32, 32256) -> (40, 32, 8064)
INFO - Saved 40 trials for subject 01 to data/processed
...
```

### Step 2.2: Verify Preprocessing Output

```bash
# Count processed files (should be 400: 10 subjects × 40 trials)
ls data/processed/ | wc -l

# Check file sizes
ls -lh data/processed/ | head -20
```

**Expected output**:
```
400
```

You should see files like:
```
s01_trial00.npy
s01_trial01.npy
...
s01_trial39.npy
s02_trial00.npy
...
s10_trial39.npy
```

---

## Part 3: Model Training (30-60 minutes on CPU)

### Step 3.1: Train BiLSTM Model with All 40 Trials

**This uses all 40 trials per subject for maximum accuracy!**

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

**If you have a GPU** (much faster):
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

**Expected time**: 
- CPU: 30-60 minutes
- GPU: 10-15 minutes

**Training phases**:
1. **Warmup (3 epochs)**: Classification training
2. **Metric Learning (20 epochs)**: Embedding space learning
3. **Prototype Computation**: K-means clustering (k=2 per user)
4. **Spoof Detector Training**: Autoencoder training
5. **Calibration**: Platt scaling

**Progress output**:
```
=== Warmup Training (Classification) ===
Epoch 1/3: 100%|████████| loss: 2.145, acc: 0.234
Epoch 2/3: 100%|████████| loss: 1.823, acc: 0.412
Epoch 3/3: 100%|████████| loss: 1.456, acc: 0.567

=== Metric Learning Training (proxyanchor) ===
Epoch 1/20: 100%|████████| metric_loss: 0.234
Epoch 2/20: 100%|████████| metric_loss: 0.198
...

=== Computing Prototypes ===
Computed prototypes for 10 users

=== Training Spoof Detector ===
Epoch 10/30: Loss: 0.0023
...

=== Calibration ===
Validation scores: 15000 (genuine: 1500, impostor: 13500)
```

### Step 3.2: Verify Training Output

```bash
# Check models directory
ls -lh models/

# View model configuration
cat models/config.json
```

**Expected output**: 6 files in `models/` directory:
```
encoder.pth          (5.2 MB)   - BiLSTM model weights
prototypes.npz       (10 KB)    - User prototypes
spoof_model.pth      (67 KB)    - Spoof detector
spoof_threshold.npy  (128 bytes)- Spoof threshold
calibrator.pkl       (2 KB)     - Score calibrator
config.json          (256 bytes)- Model config
```

---

## Part 4: Model Evaluation (3-5 minutes)

### Step 4.1: Evaluate Model Performance

```bash
python src/eval.py \
    --data_dir data/processed \
    --models_dir models \
    --output_dir outputs \
    --batch_size 64 \
    --device cpu \
    --seed 42
```

**Expected time**: 3-5 minutes

**Progress output**:
```
Extracting embeddings: 100%|████████████|
Computing similarity scores: 100%|████████████|

=== Computing Metrics ===
EER: 0.0456 at threshold 0.7234

FAR/FRR at different thresholds:
  Threshold 0.300: FAR=0.2341, FRR=0.0012
  Threshold 0.500: FAR=0.1234, FRR=0.0234
  Threshold 0.700: FAR=0.0456, FRR=0.0456
  Threshold 0.800: FAR=0.0123, FRR=0.0987

Results saved to outputs/eval_results.json
```

### Step 4.2: View Evaluation Results

```bash
# View metrics JSON
cat outputs/eval_results.json | python -m json.tool

# Open visualization plots
open outputs/roc.png
open outputs/det.png
open outputs/score_dist.png
```

**Expected metrics** (with 40 trials):
- **EER**: 3-8%
- **FAR @ 1% FRR**: 1-3%
- **AUC**: > 0.95

---

## Part 5: Backend API Server (2 minutes)

### Step 5.1: Start FastAPI Backend

Open a **new terminal window** and run:

```bash
# Navigate to project
cd "/Users/sruthikr/Desktop/Thought Based Authentiction System Using BiLSTM/deap_bilstm_auth"

# Activate virtual environment
source venv/bin/activate

# Start API server
cd src/api
python main.py
```

**Expected output**:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Encoder model loaded
INFO:     System prototypes loaded for 10 users
INFO:     Calibrator loaded
INFO:     Spoof detector loaded (threshold: 0.012345)
INFO:     Startup complete!
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Server is now running at**: http://localhost:8000

**Keep this terminal open** - the server needs to stay running.

### Step 5.2: Test API Health Check

Open **another new terminal** and run:

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

### Step 5.3: View API Documentation

Open your web browser and visit:

**http://localhost:8000/docs**

You'll see interactive API documentation with all endpoints.

---

## Part 6: Test Backend API (5 minutes)

### Step 6.1: Register a Test User

In your terminal (not the one running the server):

```bash
# Activate environment
cd "/Users/sruthikr/Desktop/Thought Based Authentiction System Using BiLSTM/deap_bilstm_auth"
source venv/bin/activate

# Register user 'alice' with 3 enrollment trials from subject 1
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

### Step 6.2: Test Genuine Authentication

```bash
# Authenticate with a trial from the same subject (genuine)
curl -X POST http://localhost:8000/auth/login \
  -F "username=alice" \
  -F "password=secret123" \
  -F "probe=@data/processed/s01_trial03.npy"
```

**Expected response** (genuine user):
```json
{
  "authenticated": true,
  "score": 0.8734,
  "probability": 0.9234,
  "is_spoof": false,
  "spoof_error": 0.0023,
  "explain_id": "abc123-def456-...",
  "message": "Authentication successful"
}
```

### Step 6.3: Test Impostor Authentication

```bash
# Authenticate with a trial from a different subject (impostor)
curl -X POST http://localhost:8000/auth/login \
  -F "username=alice" \
  -F "password=secret123" \
  -F "probe=@data/processed/s02_trial00.npy"
```

**Expected response** (impostor):
```json
{
  "authenticated": false,
  "score": 0.3421,
  "probability": 0.2134,
  "is_spoof": false,
  "spoof_error": 0.0019,
  "explain_id": "xyz789-abc123-...",
  "message": "Authentication failed: similarity too low"
}
```

### Step 6.4: Get Explanation Heatmap

```bash
# Use the explain_id from the previous response
curl http://localhost:8000/explain/abc123-def456-... -o explanation.png

# Open the image
open explanation.png
```

You'll see a heatmap showing which EEG channels and time windows were important for the decision.

---

## Part 7: Frontend Setup (15 minutes)

### Step 7.1: Install Node.js (if not already installed)

Check if Node.js is installed:

```bash
node --version
npm --version
```

If not installed, download from: https://nodejs.org/ (LTS version)

### Step 7.2: Create React App

```bash
# Navigate to frontend directory
cd frontend

# Create React app with Vite
npm create vite@latest eeg-auth-app -- --template react

# Navigate into the app
cd eeg-auth-app
```

### Step 7.3: Install Dependencies

```bash
# Install base dependencies
npm install

# Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer

# Install additional packages
npm install lucide-react axios
```

### Step 7.4: Configure Tailwind CSS

```bash
# Initialize Tailwind
npx tailwindcss init -p
```

Edit `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Edit `src/index.css` (replace content):

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Step 7.5: Copy Component Files

```bash
# Create components directory
mkdir -p src/components

# Copy skeleton components
cp ../../skeleton/*.jsx src/components/
```

### Step 7.6: Create Main App Component

Edit `src/App.jsx`:

```jsx
import { useState } from 'react'
import UploadEEG from './components/UploadEEG'
import AuthResultCard from './components/AuthResultCard'
import HeatmapDisplay from './components/HeatmapDisplay'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

function App() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [authResult, setAuthResult] = useState(null)
  const [showExplanation, setShowExplanation] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleAuth = async (files) => {
    if (!username || !password) {
      alert('Please enter username and password')
      return
    }

    setLoading(true)
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    formData.append('probe', files[0])

    try {
      const response = await axios.post(`${API_URL}/auth/login`, formData)
      setAuthResult(response.data)
      setShowExplanation(false)
    } catch (error) {
      console.error('Authentication error:', error)
      alert('Authentication failed: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-5xl font-bold text-gray-900 mb-2 text-center">
          🧠 EEG Authentication
        </h1>
        <p className="text-gray-600 text-center mb-8">
          Biometric authentication using brain signals
        </p>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-4">Login Credentials</h2>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <UploadEEG 
            onUpload={handleAuth} 
            label={loading ? "Authenticating..." : "Upload EEG Trial & Authenticate"}
            multiple={false}
          />
        </div>

        {authResult && (
          <div className="space-y-6">
            <AuthResultCard 
              result={authResult} 
              onExplain={() => setShowExplanation(true)}
            />
            
            {showExplanation && authResult.explain_id && (
              <HeatmapDisplay 
                explainId={authResult.explain_id}
                apiUrl={API_URL}
              />
            )}
          </div>
        )}

        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Test with processed trials from data/processed/</p>
          <p>Genuine: Use trials from same subject | Impostor: Use trials from different subject</p>
        </div>
      </div>
    </div>
  )
}

export default App
```

### Step 7.7: Start Frontend Development Server

```bash
npm run dev
```

**Expected output**:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### Step 7.8: Test Frontend

Open your browser and visit: **http://localhost:5173**

You should see the EEG Authentication interface!

**To test**:
1. Enter username: `alice`
2. Enter password: `secret123`
3. Upload a trial file (e.g., `s01_trial04.npy` for genuine or `s02_trial00.npy` for impostor)
4. Click "Upload EEG Trial & Authenticate"
5. View the result card
6. Click "View Explanation" to see the heatmap

---

## Part 8: Complete System Test (5 minutes)

### Test Workflow:

1. **Backend running**: Terminal 1 (`cd src/api && python main.py`)
2. **Frontend running**: Terminal 2 (`cd frontend/eeg-auth-app && npm run dev`)
3. **Browser open**: http://localhost:5173

### Test Scenarios:

#### Scenario 1: Genuine User
- Username: `alice`
- Password: `secret123`
- Upload: `data/processed/s01_trial04.npy`
- **Expected**: ✅ Authentication successful (score > 0.7)

#### Scenario 2: Impostor
- Username: `alice`
- Password: `secret123`
- Upload: `data/processed/s02_trial00.npy`
- **Expected**: ❌ Authentication failed (score < 0.5)

#### Scenario 3: Register New User
Use API directly:
```bash
curl -X POST http://localhost:8000/register \
  -F "username=bob" \
  -F "password=pass456" \
  -F "enrollment_trials=@data/processed/s03_trial00.npy" \
  -F "enrollment_trials=@data/processed/s03_trial01.npy"
```

Then test in frontend with username `bob`.

---

## 📊 Expected Final Results

### With All 40 Trials:

| Metric | Expected Value |
|--------|---------------|
| **EER** | 3-8% |
| **FAR @ 1% FRR** | 1-3% |
| **Genuine Score** | 0.75-0.95 |
| **Impostor Score** | 0.15-0.45 |
| **Inference Time** | < 50ms |

### Files Generated:

```
data/processed/          400 files (10 subjects × 40 trials)
models/                  6 files (encoder, prototypes, etc.)
outputs/                 4 files (metrics, plots)
data/users.db            User database
data/user_prototypes/    User enrollment data
```

---

## 🎉 Success Checklist

- [ ] All 10 .bdf files in `data/raw/`
- [ ] 400 preprocessed files in `data/processed/`
- [ ] 6 model files in `models/`
- [ ] EER < 10% in evaluation
- [ ] Backend API running on port 8000
- [ ] Frontend running on port 5173
- [ ] Successful genuine authentication
- [ ] Successful impostor rejection
- [ ] Explanation heatmap generated

---

## 🔧 Troubleshooting

### Issue: "No .bdf files found"
**Solution**: Copy files from Downloads:
```bash
cp ~/Downloads/s*.bdf data/raw/
```

### Issue: "Out of memory during training"
**Solution**: Reduce batch size:
```bash
python src/train.py --batch_size 32 ...
```

### Issue: "Port 8000 already in use"
**Solution**:
```bash
lsof -ti:8000 | xargs kill -9
```

### Issue: "Frontend can't connect to backend"
**Solution**: Check CORS. Backend should allow `http://localhost:5173`.
Already configured in `src/api/main.py`.

---

## 📞 Quick Reference

| Component | Command | URL |
|-----------|---------|-----|
| **Backend** | `cd src/api && python main.py` | http://localhost:8000 |
| **API Docs** | - | http://localhost:8000/docs |
| **Frontend** | `cd frontend/eeg-auth-app && npm run dev` | http://localhost:5173 |
| **Health Check** | `curl http://localhost:8000/health` | - |

---

**Total Setup Time**: ~60-90 minutes
**Status**: ✅ Complete system ready!
**Last Updated**: 2025-10-05
