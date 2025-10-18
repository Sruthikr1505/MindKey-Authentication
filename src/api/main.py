"""
FastAPI backend for EEG authentication system.
"""

import os
import sys
import uuid
import logging
from pathlib import Path
from typing import Optional
import numpy as np
import torch
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import BiLSTMEncoder
from prototypes import load_prototypes, add_user_prototype, save_prototypes, compute_user_prototypes
from calibration import load_calibrator, apply_calibration
from spoof_detector import load_spoof_model
from inference_utils import score_vs_prototypes
from preprocessing import preprocess_trials
from captum_attrib import explain_trial
from api.auth_utils import UserStore
from api.auth_logger import AuthLogger
from api.security import (
    SecurityValidator, RateLimiter, rate_limit_middleware,
    add_security_headers, sanitize_html
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize auth logger
AUTH_LOGGER = AuthLogger('auth_logs.db')

# Security validator
security = SecurityValidator()

# Initialize FastAPI app
app = FastAPI(
    title="EEG Authentication API",
    version="1.0.0",
    description="Brain-based authentication system using BiLSTM and EEG signals",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware (restrict origins in production)
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://localhost:8000",  # Allow Swagger UI
    "http://127.0.0.1:8000",  # Allow Swagger UI
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Restricted to specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],  # Allow all headers for Swagger UI
    max_age=3600,
)

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Global variables for loaded models
MODEL = None
PROTOTYPES = None
CALIBRATOR = None
SPOOF_MODEL = None
SPOOF_THRESHOLD = None
USER_STORE = None
DEVICE = 'cpu'

# Paths
MODEL_PATH = 'checkpoints/best.ckpt'
PROTOTYPES_PATH = 'models/prototypes.npz'
CALIBRATOR_PATH = 'models/calibrator.pkl'
SPOOF_MODEL_PATH = 'models/spoof_model.pth'
DB_PATH = 'auth.db'
TEMP_DIR = 'temp_uploads'
EXPLANATIONS_DIR = 'outputs/explanations'


class AuthResponse(BaseModel):
    """Authentication response model."""
    authenticated: bool
    username: str
    score: float
    calibrated_prob: float
    spoof_score: float
    is_spoof: bool
    explain_id: Optional[str] = None
    message: str


class RegisterResponse(BaseModel):
    """Registration response model."""
    success: bool
    username: str
    message: str


@app.on_event("startup")
async def startup_event():
    """Load models on startup."""
    global MODEL, PROTOTYPES, CALIBRATOR, SPOOF_MODEL, SPOOF_THRESHOLD, USER_STORE, DEVICE
    
    logger.info("Loading models...")
    
    # Create directories
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(EXPLANATIONS_DIR, exist_ok=True)
    
    # Initialize user store
    USER_STORE = UserStore(DB_PATH)
    
    # Check if models exist
    if not os.path.exists(MODEL_PATH):
        logger.warning(f"Model not found at {MODEL_PATH}. Please train the model first.")
        return
    
    # Load encoder model
    try:
        MODEL = BiLSTMEncoder(
            n_channels=48,
            hidden_size=128,
            num_layers=2,
            embedding_size=128,
            use_attention=True,
            num_classes=10
        )
        checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)
        # Filter out metric_loss_fn keys if present
        model_state = {k: v for k, v in checkpoint.items() if not k.startswith('metric_loss_fn.')}
        MODEL.load_state_dict(model_state, strict=False)
        MODEL.eval()
        MODEL.to(DEVICE)
        logger.info("Loaded encoder model")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
    
    # Load prototypes
    try:
        if os.path.exists(PROTOTYPES_PATH):
            PROTOTYPES = load_prototypes(PROTOTYPES_PATH)
            logger.info(f"Loaded prototypes for {len(PROTOTYPES)} users")
        else:
            PROTOTYPES = {}
            logger.warning("Prototypes file not found, starting with empty prototypes")
    except Exception as e:
        logger.error(f"Error loading prototypes: {e}")
        PROTOTYPES = {}
    
    # Load calibrator
    try:
        if os.path.exists(CALIBRATOR_PATH):
            CALIBRATOR = load_calibrator(CALIBRATOR_PATH)
            logger.info("Loaded calibrator")
    except Exception as e:
        logger.error(f"Error loading calibrator: {e}")
    
    # Load spoof detector
    try:
        if os.path.exists(SPOOF_MODEL_PATH):
            SPOOF_MODEL, SPOOF_THRESHOLD = load_spoof_model(SPOOF_MODEL_PATH, DEVICE, weights_only=False)
            logger.info(f"Loaded spoof detector (threshold: {SPOOF_THRESHOLD:.6f})")
    except Exception as e:
        logger.error(f"Error loading spoof detector: {e}")
    
    logger.info("Startup complete")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "EEG Authentication API", "status": "running"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": MODEL is not None,
        "prototypes_loaded": PROTOTYPES is not None,
        "calibrator_loaded": CALIBRATOR is not None,
        "spoof_detector_loaded": SPOOF_MODEL is not None
    }


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
    
    Returns:
        Registration response
    """
    try:
        # Validate username
        is_valid, error_msg = security.validate_username(username)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Validate password
        is_valid, error_msg = security.validate_password(password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Sanitize username
        username = sanitize_html(username)
        
        logger.info(f"Registration request for user: {username}")
        
        # Check if user already exists
        if USER_STORE.get_user(username) is not None:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Load and preprocess enrollment trials
        trial_embeddings = []
        
        for trial_file in enrollment_trials:
            # Validate file
            file_size = 0
            content = await trial_file.read()
            file_size = len(content)
            await trial_file.seek(0)  # Reset file pointer
            
            is_valid, error_msg = security.validate_file_upload(trial_file.filename, file_size)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)
            
            # Sanitize filename
            safe_filename = security.sanitize_filename(trial_file.filename)
            
            # Save uploaded file
            temp_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.npy")
            with open(temp_path, 'wb') as f:
                content = await trial_file.read()
                f.write(content)
            
            # Load trial
            trial_data = np.load(temp_path)
            
            # Preprocess if needed (assume already preprocessed)
            # trial_data shape: (n_channels, n_samples)
            
            # Convert to tensor and get embedding
            trial_tensor = torch.FloatTensor(trial_data).unsqueeze(0).to(DEVICE)
            
            with torch.no_grad():
                embedding = MODEL(trial_tensor).cpu().numpy()
            
            trial_embeddings.append(embedding[0])
            
            # Cleanup
            os.remove(temp_path)
        
        trial_embeddings = np.array(trial_embeddings)
        logger.info(f"Computed {len(trial_embeddings)} embeddings for {username}")
        
        # Compute user prototypes
        user_id = len(PROTOTYPES) + 1  # Simple ID assignment
        user_prototypes = compute_user_prototypes({user_id: trial_embeddings}, k=2)
        
        # Add to global prototypes
        PROTOTYPES[user_id] = user_prototypes[user_id]
        
        # Save prototypes
        save_prototypes(PROTOTYPES, PROTOTYPES_PATH)
        
        # Register user in database
        prototypes_path = f"user_{user_id}_prototypes"
        success = USER_STORE.register_user(username, password, prototypes_path)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to register user")
        
        # Log enrollment
        enrollment_files = ", ".join([f.filename for f in enrollment_trials])
        AUTH_LOGGER.log_enrollment(username, password, enrollment_files, True, user_id)
        logger.info(f"Registered user {username}")
        
        return RegisterResponse(
            success=True,
            username=username,
            message=f"User registered successfully with {len(trial_embeddings)} enrollment trials"
        )
    
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/login", response_model=AuthResponse)
async def authenticate(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    probe_trial: UploadFile = File(...)
):
    """
    Authenticate user with probe trial.
    
    Args:
        request: FastAPI request object
        username: Username
        password: Password
        probe_trial: .npy file containing probe EEG trial
    
    Returns:
        Authentication response
    """
    try:
        # Get client IP
        client_ip = request.client.host
        
        # Check rate limiting for login attempts
        is_allowed, lockout_until = RateLimiter.check_login_attempts(username, client_ip)
        if not is_allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Too many failed login attempts. Account locked until {lockout_until.strftime('%H:%M:%S')}"
            )
        
        # Validate and sanitize username
        is_valid, error_msg = security.validate_username(username)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        username = sanitize_html(username)
        
        # Validate file
        content = await probe_trial.read()
        file_size = len(content)
        await probe_trial.seek(0)
        
        is_valid, error_msg = security.validate_file_upload(probe_trial.filename, file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        logger.info(f"Authentication request for user: {username}")
        
        # Authenticate password
        user = USER_STORE.authenticate_user(username, password)
        if user is None:
            # Record failed login attempt
            RateLimiter.record_failed_login(username, client_ip)
            
            return AuthResponse(
                authenticated=False,
                username=username,
                score=0.0,
                calibrated_prob=0.0,
                spoof_score=0.0,
                is_spoof=False,
                message="Invalid username or password"
            )
        
        # Find user ID from prototypes
        user_id = None
        for uid in PROTOTYPES.keys():
            if f"user_{uid}_prototypes" == user.prototypes_path:
                user_id = uid
                break
        
        if user_id is None or user_id not in PROTOTYPES:
            raise HTTPException(status_code=404, detail="User prototypes not found")
        
        # Save uploaded probe trial
        temp_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.npy")
        with open(temp_path, 'wb') as f:
            content = await probe_trial.read()
            f.write(content)
        
        # Load and process probe trial
        probe_data = np.load(temp_path)
        probe_tensor = torch.FloatTensor(probe_data).unsqueeze(0).to(DEVICE)
        
        # Get embedding
        with torch.no_grad():
            probe_embedding = MODEL(probe_tensor).cpu().numpy()[0]
        
        # Compute similarity score
        score = score_vs_prototypes(probe_embedding, PROTOTYPES[user_id], aggregation='max')
        
        # Compute calibrated probability
        calibrated_prob = 0.5
        if CALIBRATOR is not None:
            calibrated_prob = float(apply_calibration(CALIBRATOR, np.array([score]))[0])
        
        # Compute spoof score
        spoof_score = 0.0
        is_spoof = False
        if SPOOF_MODEL is not None:
            probe_tensor_emb = torch.FloatTensor(probe_embedding).unsqueeze(0).to(DEVICE)
            spoof_error = SPOOF_MODEL.get_reconstruction_error(probe_tensor_emb).item()
            spoof_score = float(spoof_error)
            is_spoof = spoof_error > SPOOF_THRESHOLD
        
        # Make authentication decision
        auth_threshold = 0.5  # Configurable
        authenticated = (calibrated_prob >= auth_threshold) and (not is_spoof)
        
        # Handle authentication result
        if authenticated:
            # Clear failed login attempts on successful authentication
            RateLimiter.clear_failed_logins(username, client_ip)
        else:
            # Record failed authentication
            RateLimiter.record_failed_login(username, client_ip)
        
        # Generate explanation ID
        explain_id = None
        if authenticated:
            explain_id = str(uuid.uuid4())
            # Save trial for explanation
            explain_path = os.path.join(EXPLANATIONS_DIR, f"{explain_id}.npy")
            np.save(explain_path, probe_data)
        
        # Cleanup
        os.remove(temp_path)
        
        message = "Authentication successful" if authenticated else \
                  "Authentication failed: " + ("spoof detected" if is_spoof else "low confidence")
        
        # Log authentication attempt
        AUTH_LOGGER.log_authentication(
            username=username,
            auth_file=probe_trial.filename,
            score=float(score),
            calibrated_prob=float(calibrated_prob),
            spoof_score=spoof_score,
            is_spoof=is_spoof,
            authenticated=authenticated,
            message=message
        )
        
        return AuthResponse(
            authenticated=authenticated,
            username=username,
            score=float(score),
            calibrated_prob=float(calibrated_prob),
            spoof_score=spoof_score,
            is_spoof=is_spoof,
            explain_id=explain_id,
            message=message
        )
    
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/explain/{explain_id}")
async def get_explanation(explain_id: str):
    """
    Get explanation for authenticated trial.
    
    Args:
        explain_id: Explanation ID from authentication response
    
    Returns:
        Explanation image
    """
    try:
        trial_path = os.path.join(EXPLANATIONS_DIR, f"{explain_id}.npy")
        
        if not os.path.exists(trial_path):
            raise HTTPException(status_code=404, detail="Explanation not found")
        
        # Generate explanation
        results = explain_trial(
            checkpoint_path=MODEL_PATH,
            trial_path=trial_path,
            methods=['integrated_gradients'],
            n_channels=48,
            device=DEVICE,
            output_dir=EXPLANATIONS_DIR
        )
        
        # Return heatmap image
        heatmap_path = results['methods']['integrated_gradients']['heatmap_path']
        
        return FileResponse(heatmap_path, media_type="image/png")
    
    except Exception as e:
        logger.error(f"Explanation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
