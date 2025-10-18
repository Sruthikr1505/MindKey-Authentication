@echo off
REM ==========================================
REM CPU Training Pipeline for Windows 11
REM Target: 97.28% Accuracy (EER ~2.72%)
REM ==========================================

echo.
echo ==========================================
echo EEG Authentication System - CPU Training
echo ==========================================
echo.
echo Configuration:
echo - Subjects: 10 (s01-s10)
echo - Channels: 48
echo - Trials per subject: 40
echo - Epochs: 30 (3 warmup + 30 metric)
echo - Device: CPU
echo - Target Accuracy: 97.28%%
echo.
echo NOTE: CPU training will take 8-10 hours
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Check if data files exist
echo.
echo Checking for DEAP .bdf files...
if not exist "data\raw\s01.bdf" (
    echo ERROR: DEAP .bdf files not found in data\raw\
    echo Please place s01.bdf through s10.bdf in data\raw\
    pause
    exit /b 1
)

REM Count .bdf files
for /f %%A in ('dir /b data\raw\*.bdf 2^>nul ^| find /c /v ""') do set BDF_COUNT=%%A
echo Found %BDF_COUNT% .bdf files

if %BDF_COUNT% LSS 10 (
    echo WARNING: Expected 10 .bdf files, found %BDF_COUNT%
    echo Continuing with available files...
)

REM ==========================================
REM STEP 1: PREPROCESSING
REM ==========================================
echo.
echo ==========================================
echo STEP 1: Preprocessing EEG Data
echo ==========================================
echo.
echo Processing all 40 trials per subject with 48 channels...
echo This will take approximately 15-20 minutes...
echo.

python src\preprocessing.py ^
    --input_dir data\raw ^
    --output_dir data\processed ^
    --subjects 1 2 3 4 5 6 7 8 9 10 ^
    --n_channels 48 ^
    --seed 42

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Preprocessing failed!
    pause
    exit /b 1
)

REM Verify preprocessing output
echo.
echo Verifying preprocessing output...
for /f %%A in ('dir /b data\processed\*.npy 2^>nul ^| find /c /v ""') do set NPY_COUNT=%%A
echo Found %NPY_COUNT% processed files

if %NPY_COUNT% LSS 100 (
    echo WARNING: Expected ~400 files, found %NPY_COUNT%
    echo Continuing anyway...
)

echo.
echo Preprocessing complete!
echo.

REM ==========================================
REM STEP 2: CPU TRAINING (30 EPOCHS)
REM ==========================================
echo.
echo ==========================================
echo STEP 2: Training on CPU
echo ==========================================
echo.
echo Training configuration:
echo - Warmup epochs: 3 (classification)
echo - Metric epochs: 30 (ProxyAnchor)
echo - Batch size: 32 (optimized for CPU)
echo - Learning rate: 0.001
echo - Device: CPU
echo.
echo Expected time: 8-10 hours on CPU
echo You can leave this running overnight
echo.
echo Starting training...
echo.

python src\train.py ^
    --data_dir data\processed ^
    --subjects 1 2 3 4 5 6 7 8 9 10 ^
    --batch_size 32 ^
    --warmup_epochs 3 ^
    --metric_epochs 30 ^
    --lr 0.001 ^
    --metric_loss proxyanchor ^
    --use_attention ^
    --n_channels 48 ^
    --device cpu ^
    --seed 42

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Training failed!
    pause
    exit /b 1
)

echo.
echo Training complete!
echo.

REM ==========================================
REM STEP 3: EVALUATION
REM ==========================================
echo.
echo ==========================================
echo STEP 3: Evaluating Model Performance
echo ==========================================
echo.
echo Computing FAR, FRR, EER metrics...
echo Generating ROC and DET curves...
echo.

python src\eval.py ^
    --data_dir data\processed ^
    --checkpoint checkpoints\best.ckpt ^
    --prototypes models\prototypes.npz ^
    --subjects 1 2 3 4 5 6 7 8 9 10 ^
    --batch_size 32 ^
    --n_channels 48 ^
    --device cpu ^
    --output_dir outputs ^
    --seed 42

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Evaluation failed!
    pause
    exit /b 1
)

echo.
echo Evaluation complete!
echo.

REM ==========================================
REM DISPLAY RESULTS
REM ==========================================
echo.
echo ==========================================
echo TRAINING COMPLETE!
echo ==========================================
echo.
echo Generated Files:
echo - Model: checkpoints\best.ckpt
echo - Prototypes: models\prototypes.npz
echo - Calibrator: models\calibrator.pkl
echo - Spoof Detector: models\spoof_model.pth
echo.
echo Evaluation Results:
echo - Metrics: outputs\eval_results.json
echo - ROC Curve: outputs\roc.png
echo - DET Curve: outputs\det.png
echo - Score Distribution: outputs\score_distribution.png
echo.

REM Display evaluation results if available
if exist "outputs\eval_results.json" (
    echo Results Summary:
    echo.
    type outputs\eval_results.json
    echo.
)

echo.
echo ==========================================
echo NEXT STEPS
echo ==========================================
echo.
echo 1. Check evaluation results in outputs\eval_results.json
echo    Target: EER ~2.72%% (97.28%% accuracy)
echo.
echo 2. Start the backend server:
echo    python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
echo.
echo 3. Setup frontend (if not already done):
echo    cd frontend
echo    npm install
echo    npm start
echo.
echo 4. Access the system:
echo    - Backend API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo    - Frontend: http://localhost:3000
echo.
echo ==========================================
echo.

pause
