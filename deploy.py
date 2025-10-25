#!/usr/bin/env python3
"""
Deployment script for EEG Authentication System
Supports multiple deployment platforms: Docker, Heroku, Railway, Render
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class EEGAuthDeployer:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.frontend_dir = self.root_dir / "frontend" / "eeg-auth-app"
        
    def check_prerequisites(self):
        """Check if required tools are installed"""
        tools = {
            'node': 'Node.js',
            'npm': 'NPM',
            'python': 'Python',
            'pip': 'Pip'
        }
        
        missing = []
        for tool, name in tools.items():
            try:
                subprocess.run([tool, '--version'], capture_output=True, check=True)
                print(f"✅ {name} is installed")
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing.append(name)
                print(f"❌ {name} is not installed")
        
        if missing:
            print(f"\n⚠️  Please install: {', '.join(missing)}")
            return False
        return True
    
    def build_frontend(self):
        """Build the React frontend"""
        print("\n🔨 Building frontend...")
        
        # Install dependencies
        subprocess.run(['npm', 'ci'], cwd=self.frontend_dir, check=True)
        
        # Build for production
        subprocess.run(['npm', 'run', 'build'], cwd=self.frontend_dir, check=True)
        
        print("✅ Frontend built successfully")
    
    def install_backend_deps(self):
        """Install Python backend dependencies"""
        print("\n📦 Installing backend dependencies...")
        
        # Create virtual environment if it doesn't exist
        venv_path = self.root_dir / "venv"
        if not venv_path.exists():
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], cwd=self.root_dir, check=True)
        
        # Install requirements
        if os.name == 'nt':  # Windows
            pip_path = venv_path / "Scripts" / "pip"
        else:  # Unix/Linux/Mac
            pip_path = venv_path / "bin" / "pip"
        
        subprocess.run([str(pip_path), 'install', '-r', 'requirements.txt'], 
                      cwd=self.root_dir, check=True)
        
        print("✅ Backend dependencies installed")
    
    def deploy_docker(self):
        """Deploy using Docker"""
        print("\n🐳 Deploying with Docker...")
        
        # Build Docker image
        subprocess.run(['docker', 'build', '-t', 'eeg-auth-app', '.'], 
                      cwd=self.root_dir, check=True)
        
        # Run with docker-compose
        subprocess.run(['docker-compose', 'up', '-d'], 
                      cwd=self.root_dir, check=True)
        
        print("✅ Docker deployment complete!")
        print("🌐 Access your app at: http://localhost:8000")
    
    def deploy_heroku(self):
        """Deploy to Heroku"""
        print("\n🚀 Deploying to Heroku...")
        
        # Check if Heroku CLI is installed
        try:
            subprocess.run(['heroku', '--version'], capture_output=True, check=True)
        except FileNotFoundError:
            print("❌ Heroku CLI not found. Please install it first.")
            return
        
        # Create Heroku app
        app_name = input("Enter Heroku app name (or press Enter for auto-generated): ").strip()
        
        if app_name:
            subprocess.run(['heroku', 'create', app_name], cwd=self.root_dir)
        else:
            subprocess.run(['heroku', 'create'], cwd=self.root_dir)
        
        # Set environment variables
        env_vars = [
            'PYTHONPATH=/app',
            'MODEL_PATH=/app/models/bilstm_encoder.pth',
            'PROTOTYPES_PATH=/app/data/prototypes.pkl'
        ]
        
        for var in env_vars:
            subprocess.run(['heroku', 'config:set', var], cwd=self.root_dir)
        
        # Deploy
        subprocess.run(['git', 'push', 'heroku', 'main'], cwd=self.root_dir)
        
        print("✅ Heroku deployment complete!")
    
    def deploy_netlify(self):
        """Deploy frontend to Netlify"""
        print("\n🌐 Deploying frontend to Netlify...")
        
        self.build_frontend()
        
        print("Frontend built! To deploy to Netlify:")
        print("1. Go to https://netlify.com")
        print("2. Drag and drop the 'frontend/eeg-auth-app/dist' folder")
        print("3. Or connect your GitHub repository")
        print("4. Update the API URL in the frontend config")
    
    def create_production_config(self):
        """Create production configuration files"""
        print("\n⚙️  Creating production configuration...")
        
        # Create .env.production for frontend
        env_prod = self.frontend_dir / ".env.production"
        with open(env_prod, 'w') as f:
            f.write("VITE_API_BASE_URL=https://your-backend-url.herokuapp.com\n")
            f.write("VITE_NODE_ENV=production\n")
        
        # Create Procfile for Heroku
        procfile = self.root_dir / "Procfile"
        with open(procfile, 'w') as f:
            f.write("web: python -m uvicorn src.api.main:app --host 0.0.0.0 --port $PORT\n")
        
        # Create runtime.txt for Heroku
        runtime = self.root_dir / "runtime.txt"
        with open(runtime, 'w') as f:
            f.write("python-3.9.18\n")
        
        print("✅ Production configuration created")
    
    def run_local_development(self):
        """Run the application locally for development"""
        print("\n🔧 Starting local development servers...")
        
        # Start backend
        print("Starting backend server on port 8000...")
        backend_process = subprocess.Popen(
            [sys.executable, '-m', 'uvicorn', 'src.api.main:app', '--reload', '--host', '0.0.0.0', '--port', '8000'],
            cwd=self.root_dir
        )
        
        # Start frontend
        print("Starting frontend server on port 5173...")
        frontend_process = subprocess.Popen(
            ['npm', 'run', 'dev'],
            cwd=self.frontend_dir
        )
        
        print("\n✅ Development servers started!")
        print("🌐 Frontend: http://localhost:5173")
        print("🔌 Backend API: http://localhost:8000")
        print("📊 API Docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop servers")
        
        try:
            backend_process.wait()
            frontend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping servers...")
            backend_process.terminate()
            frontend_process.terminate()

def main():
    deployer = EEGAuthDeployer()
    
    print("🧠 EEG Authentication System Deployment Tool")
    print("=" * 50)
    
    if not deployer.check_prerequisites():
        return
    
    print("\nSelect deployment option:")
    print("1. Local Development")
    print("2. Docker (Local)")
    print("3. Heroku (Cloud)")
    print("4. Netlify (Frontend only)")
    print("5. Create Production Config")
    print("6. Build Frontend Only")
    print("7. Install Backend Dependencies")
    
    choice = input("\nEnter your choice (1-7): ").strip()
    
    try:
        if choice == '1':
            deployer.run_local_development()
        elif choice == '2':
            deployer.deploy_docker()
        elif choice == '3':
            deployer.deploy_heroku()
        elif choice == '4':
            deployer.deploy_netlify()
        elif choice == '5':
            deployer.create_production_config()
        elif choice == '6':
            deployer.build_frontend()
        elif choice == '7':
            deployer.install_backend_deps()
        else:
            print("❌ Invalid choice")
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Deployment cancelled")

if __name__ == "__main__":
    main()
