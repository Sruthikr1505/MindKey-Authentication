from fastapi import FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="MindKey Authentication",
    description="EEG-based Authentication System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

# Serve static files
static_dirs = [
    Path("frontend/eeg-auth-app/dist"),  # Development build
    Path("static"),  # Production build
    Path("frontend/eeg-auth-app/public")  # Fallback
]

static_dir = None
for dir_path in static_dirs:
    if dir_path.exists():
        static_dir = dir_path
        logger.info(f"Using static files from: {static_dir}")
        break

if static_dir:
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
else:
    logger.error("No static files directory found! Frontend will not be served.")

# Serve the main page for any route that doesn't match API routes
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    index_path = static_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend files not found")
    return FileResponse(index_path)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "service": "MindKey Authentication",
        "version": "1.0.0"
    }

# Add your authentication endpoints here
@app.post("/api/authenticate")
async def authenticate_user():
    # Add your authentication logic here
    return {"status": "authentication_endpoint", "message": "Authentication endpoint"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
