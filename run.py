
import os
import signal
import sys
import uvicorn
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.absolute()))

def handle_signal(signum, frame):
    print("\n🛑 Received shutdown signal. Exiting gracefully...")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    # Configure and run server
    config = uvicorn.Config(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    
    try:
        print("🚀 Starting MindKey Authentication API...")
        print("📚 API Documentation: http://localhost:8000/docs")
        server.run()
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
