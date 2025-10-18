@echo off
REM Demo script for EEG Authentication System (Windows)
REM This script demonstrates the complete pipeline on CPU with fast mode

echo ==========================================
echo EEG Authentication System - Demo Script
echo ==========================================

REM Step 1: Setup virtual environment
echo.
echo Step 1: Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
call venv\Scripts\activate.bat
echo Virtual environment activated

REM Step 2: Install dependencies
echo.
echo Step 2: Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Dependencies installed

REM Step 3: Data preparation
echo.
echo Step 3: Data preparation
echo Expected data structure:
echo   data\raw\s01.bdf
echo   data\raw\s02.bdf
echo   ...
echo   data\raw\s10.bdf
echo.
echo If you don't have the data, download from DEAP dataset:
echo   https://www.eecs.qmul.ac.uk/mmv/datasets/deap/
echo.
pause

REM Step 4: Preprocessing (fast mode)
echo.
echo Step 4: Preprocessing EEG data (fast mode)...
python src\preprocessing.py --input_dir data\raw --output_dir data\processed --subjects 1 2 3 4 5 6 7 8 9 10 --fast --n_channels 48 --seed 42

echo Preprocessing complete

REM Step 5: Training (demo mode)
echo.
echo Step 5: Training model (demo mode - reduced epochs)...
python src\train.py --data_dir data\processed --subjects 1 2 3 4 5 6 7 8 9 10 --batch_size 32 --warmup_epochs 1 --metric_epochs 2 --lr 0.001 --metric_loss proxyanchor --use_attention --n_channels 48 --device cpu --fast --seed 42

echo Training complete

REM Step 6: Evaluation
echo.
echo Step 6: Evaluating model...
python src\eval.py --data_dir data\processed --checkpoint checkpoints\best.ckpt --prototypes models\prototypes.npz --subjects 1 2 3 4 5 6 7 8 9 10 --batch_size 32 --n_channels 48 --device cpu --output_dir outputs --seed 42

echo Evaluation complete. Results saved to outputs\

REM Step 7: Start backend server
echo.
echo Step 7: Starting FastAPI backend...
echo Backend will run on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
echo API Endpoints:
echo   - POST /register - Register new user
echo   - POST /auth/login - Authenticate user
echo   - GET /explain/{id} - Get explanation
echo   - GET /health - Health check
echo.

python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

echo.
echo ==========================================
echo Demo complete!
echo ==========================================
