"""
FastAPI Backend for EEG Authentication
Endpoints: /register, /auth/login, /explain/{id}, /health
"""

import os
import json
import uuid
from pathlib import Path
from typing import Optional
import numpy as np
import torch
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import logging

# Add parent directory to path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from model import BiLSTMEncoder
from prototypes import compute_user_prototypes, save_prototypes, load_prototypes
from calibration import load_calibrator
from spoof_detector import load_spoof_model, compute_reconstruction_errors
from inference_utils import score_vs_prototypes, calibrated_probability, make_decision
from preprocessing import preprocess_trials
from captum_attrib import explain_trial
from auth_utils import UserDatabase

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EEG Authentication API",
    description="Hardware-free EEG authentication using BiLSTM",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
class AppState:
    def __init__(self):
        self.model = None
        self.config = None
        self.prototypes = None
        self.calibrator = None
        self.spoof_model = None
        self.spoof_threshold = None
        self.db = None
        self.device = 'cpu'
        self.models_dir = Path('models')
        self.data_dir = Path('data')
        self.explanations_dir = Path('outputs/explanations')
        self.user_prototypes_dir = Path('data/user_prototypes')
        
        # Create directories
        self.explanations_dir.mkdir(parents=True, exist_ok=True)
        self.user_prototypes_dir.mkdir(parents=True, exist_ok=True)

state = AppState()


@app.on_event("startup")
async def startup_event():
    """Load models and initialize database on startup"""
    logger.info("Starting up EEG Authentication API...")
    
    try:
        # Initialize database
        state.db = UserDatabase(db_path='data/users.db')
        logger.info("Database initialized")
        
        # Check if models exist
        if not (state.models_dir / 'config.json').exists():
            logger.warning("Models not found. Please train the model first.")
            return
        
        # Load config
        with open(state.models_dir / 'config.json', 'r') as f:
            state.config = json.load(f)
        logger.info(f"Config loaded: {state.config}")
        
        # Load encoder model
        state.model = BiLSTMEncoder(
            n_channels=state.config['n_channels'],
            hidden_size=state.config['hidden_size'],
            embedding_size=state.config['embedding_size'],
            num_layers=state.config['num_layers'],
            use_attention=state.config.get('use_attention', True),
            num_classes=state.config['num_classes']
        )
        state.model.load_state_dict(torch.load(state.models_dir / 'encoder.pth', map_location=state.device))
        state.model.eval()
        state.model.to(state.device)
        logger.info("Encoder model loaded")
        
        # Load prototypes (system prototypes from training)
        if (state.models_dir / 'prototypes.npz').exists():
            state.prototypes = load_prototypes(str(state.models_dir / 'prototypes.npz'))
            logger.info(f"System prototypes loaded for {len(state.prototypes)} users")
        
        # Load calibrator
        if (state.models_dir / 'calibrator.pkl').exists():
            state.calibrator = load_calibrator(str(state.models_dir / 'calibrator.pkl'))
            logger.info("Calibrator loaded")
        
        # Load spoof detector
        if (state.models_dir / 'spoof_model.pth').exists():
            state.spoof_model = load_spoof_model(
                str(state.models_dir / 'spoof_model.pth'),
                embedding_dim=state.config['embedding_size'],
                device=state.device
            )
            state.spoof_threshold = float(np.load(state.models_dir / 'spoof_threshold.npy'))
            logger.info(f"Spoof detector loaded (threshold: {state.spoof_threshold:.6f})")
        
        logger.info("Startup complete!")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")


def preprocess_uploaded_trial(file_bytes: bytes, fs_in: int = 512, fs_out: int = 128) -> np.ndarray:
    """Preprocess uploaded EEG trial"""
    # Save temporarily
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.npy', delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    
    try:
        # Load trial
        trial = np.load(tmp_path)
        
        # Ensure correct shape (channels, samples)
        if trial.ndim == 1:
            raise ValueError("Trial must be 2D (channels, samples)")
        
        # Preprocess
        trials = trial[np.newaxis, ...]  # Add trial dimension
        processed = preprocess_trials(trials, fs_in=fs_in, fs_out=fs_out, do_ica=False, seed=42)
        
        return processed[0]  # Return first trial
    finally:
        os.unlink(tmp_path)


def compute_embedding(trial: np.ndarray) -> np.ndarray:
    """Compute embedding for a trial"""
    # Convert to tensor
    trial_tensor = torch.from_numpy(trial).float().unsqueeze(0).to(state.device)
    
    # Compute embedding
    with torch.no_grad():
        embedding = state.model(trial_tensor)
    
    return embedding.cpu().numpy()[0]


# Pydantic models
class RegisterResponse(BaseModel):
    success: bool
    message: str
    username: str


class AuthResponse(BaseModel):
    authenticated: bool
    score: float
    probability: float
    is_spoof: bool
    spoof_error: Optional[float]
    explain_id: Optional[str]
    message: str


class HealthResponse(BaseModel):
    status: str
    models_loaded: bool
    database_connected: bool


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        models_loaded=state.model is not None,
        database_connected=state.db is not None
    )


@app.post("/register", response_model=RegisterResponse)
async def register(
    username: str = Form(...),
    password: str = Form(...),
    enrollment_trials: list[UploadFile] = File(...)
):
    """
    Register a new user with enrollment trials.
    
    Args:
        username: Username
        password: Password
        enrollment_trials: List of .npy files containing EEG trials
    """
    try:
        logger.info(f"Registration request for username: {username}")
        
        if state.model is None:
            raise HTTPException(status_code=503, detail="Models not loaded. Please train the model first.")
        
        # Check if user already exists
        if state.db.get_user(username):
            raise HTTPException(status_code=400, detail=f"Username '{username}' already exists")
        
        # Process enrollment trials
        embeddings = []
        for trial_file in enrollment_trials:
            # Read file
            file_bytes = await trial_file.read()
            
            # Preprocess
            trial = preprocess_uploaded_trial(file_bytes)
            
            # Compute embedding
            embedding = compute_embedding(trial)
            embeddings.append(embedding)
        
        embeddings = np.array(embeddings)
        logger.info(f"Computed {len(embeddings)} enrollment embeddings")
        
        # Compute prototypes (k=2)
        user_prototypes = compute_user_prototypes(
            {0: embeddings},
            k=min(2, len(embeddings)),
            seed=42
        )[0]
        
        # Save prototypes
        prototypes_path = state.user_prototypes_dir / f"{username}_prototypes.npy"
        np.save(str(prototypes_path), user_prototypes)
        logger.info(f"Saved prototypes to {prototypes_path}")
        
        # Register user in database
        user = state.db.register_user(
            username=username,
            password=password,
            prototypes_path=str(prototypes_path)
        )
        
        logger.info(f"User '{username}' registered successfully")
        
        return RegisterResponse(
            success=True,
            message=f"User '{username}' registered successfully with {len(embeddings)} enrollment trials",
            username=username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/login", response_model=AuthResponse)
async def authenticate(
    username: str = Form(...),
    password: str = Form(...),
    probe: UploadFile = File(...)
):
    """
    Authenticate user with probe EEG trial.
    
    Args:
        username: Username
        password: Password
        probe: .npy file containing probe EEG trial
    """
    try:
        logger.info(f"Authentication request for username: {username}")
        
        if state.model is None:
            raise HTTPException(status_code=503, detail="Models not loaded")
        
        # Authenticate password
        user = state.db.authenticate_user(username, password)
        if not user:
            return AuthResponse(
                authenticated=False,
                score=0.0,
                probability=0.0,
                is_spoof=False,
                spoof_error=None,
                explain_id=None,
                message="Invalid username or password"
            )
        
        # Load user prototypes
        user_prototypes = np.load(user.prototypes_path)
        logger.info(f"Loaded prototypes for user '{username}'")
        
        # Process probe trial
        probe_bytes = await probe.read()
        probe_trial = preprocess_uploaded_trial(probe_bytes)
        
        # Compute probe embedding
        probe_embedding = compute_embedding(probe_trial)
        
        # Compute similarity score
        score = score_vs_prototypes(probe_embedding, user_prototypes, aggregation='max')
        
        # Compute calibrated probability
        probability = calibrated_probability(score, state.calibrator) if state.calibrator else score
        
        # Spoof detection
        spoof_error = None
        is_spoof = False
        if state.spoof_model is not None:
            spoof_errors = compute_reconstruction_errors(
                state.spoof_model,
                probe_embedding[np.newaxis, :],
                device=state.device
            )
            spoof_error = float(spoof_errors[0])
            is_spoof = spoof_error > state.spoof_threshold
        
        # Make decision (threshold = 0.5 for calibrated probability)
        decision_threshold = 0.5
        authenticated = (not is_spoof) and (probability >= decision_threshold)
        
        # Generate explanation ID
        explain_id = str(uuid.uuid4())
        
        # Save probe trial for explanation
        explain_trial_path = state.explanations_dir / f"{explain_id}_probe.npy"
        np.save(str(explain_trial_path), probe_trial)
        
        logger.info(f"Authentication result for '{username}': authenticated={authenticated}, score={score:.3f}, prob={probability:.3f}, spoof={is_spoof}")
        
        # Log authentication attempt
        state.db.log_authentication(
            username=username,
            authenticated=authenticated,
            score=float(score),
            probability=float(probability),
            is_spoof=is_spoof
        )
        
        message = "Authentication successful" if authenticated else \
                  "Spoof detected" if is_spoof else \
                  "Authentication failed: similarity too low"
        
        return AuthResponse(
            authenticated=authenticated,
            score=float(score),
            probability=float(probability),
            is_spoof=is_spoof,
            spoof_error=spoof_error,
            explain_id=explain_id,
            message=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/explain/{explain_id}")
async def get_explanation(explain_id: str):
    """
    Get explanation for an authentication attempt.
    
    Args:
        explain_id: Explanation ID from authentication response
    """
    try:
        # Check if trial exists
        trial_path = state.explanations_dir / f"{explain_id}_probe.npy"
        if not trial_path.exists():
            raise HTTPException(status_code=404, detail="Explanation not found")
        
        # Generate explanation
        explanation = explain_trial(
            checkpoint_path=str(state.models_dir / 'encoder.pth'),
            trial_path=str(trial_path),
            config=state.config,
            methods=['integrated_gradients'],
            output_dir=str(state.explanations_dir),
            device=state.device
        )
        
        # Return heatmap image
        heatmap_path = Path(explanation['heatmap_path'])
        if heatmap_path.exists():
            return FileResponse(
                str(heatmap_path),
                media_type="image/png",
                filename=f"explanation_{explain_id}.png"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to generate explanation")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Explanation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {
        "message": "EEG Authentication API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "register": "/register (POST)",
            "login": "/auth/login (POST)",
            "explain": "/explain/{explain_id} (GET)",
            "logs": "/admin/logs (GET)",
            "stats": "/admin/stats (GET)"
        }
    }


@app.get("/admin/logs")
async def get_logs(username: Optional[str] = None, limit: int = 50):
    """Get authentication logs"""
    if state.db is None:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    logs = state.db.get_auth_logs(username=username, limit=limit)
    
    return {
        "total": len(logs),
        "logs": [
            {
                "id": log.id,
                "username": log.username,
                "authenticated": log.authenticated,
                "score": log.score,
                "probability": log.probability,
                "is_spoof": log.is_spoof,
                "timestamp": log.timestamp.isoformat()
            }
            for log in logs
        ]
    }


@app.get("/admin/stats")
async def get_statistics():
    """Get authentication statistics"""
    if state.db is None:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    stats = state.db.get_statistics()
    users = state.db.list_users()
    
    return {
        "statistics": stats,
        "total_users": len(users),
        "users": [{"username": u.username, "created_at": u.created_at.isoformat()} for u in users]
    }


@app.get("/samples/list")
async def list_sample_eegs():
    """List available sample EEG files for demo mode"""
    samples = [
        {"id": "s01_trial00", "name": "Subject 1 - Trial 0 (Relaxed)", "subject": 1, "description": "Use for enrollment"},
        {"id": "s01_trial01", "name": "Subject 1 - Trial 1 (Focused)", "subject": 1, "description": "Use for genuine authentication"},
        {"id": "s01_trial02", "name": "Subject 1 - Trial 2 (Active)", "subject": 1, "description": "Use for genuine authentication"},
        {"id": "s02_trial00", "name": "Subject 2 - Trial 0", "subject": 2, "description": "Use to test impostor detection"},
        {"id": "s02_trial01", "name": "Subject 2 - Trial 1", "subject": 2, "description": "Use to test impostor detection"},
        {"id": "s03_trial00", "name": "Subject 3 - Trial 0", "subject": 3, "description": "Use to test impostor detection"},
    ]
    return {"samples": samples}


@app.get("/samples/{sample_id}")
async def get_sample_eeg(sample_id: str):
    """Get a sample EEG file for demo mode"""
    sample_path = state.data_dir / "processed" / f"{sample_id}.npy"
    
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail=f"Sample '{sample_id}' not found")
    
    return FileResponse(
        path=str(sample_path),
        media_type="application/octet-stream",
        filename=f"{sample_id}.npy"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
