#!/usr/bin/env python3
"""
Quick start script for the admin dashboard
"""

import subprocess
import sys
import os
import time
import requests

def check_api_running():
    """Check if main API is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def start_admin_dashboard():
    """Start the admin dashboard"""
    print("🚀 Starting EEG Authentication Admin Dashboard")
    print("=" * 50)
    
    # Check if main API is running
    if not check_api_running():
        print("⚠️  Main API not detected on port 8000")
        print("   Please start the main API first:")
        print("   cd 'D:\\Thought Based Authentication System Using BiLSTM\\Mindkey-Authentication'")
        print("   venv\\Scripts\\activate")
        print("   python run.py")
        print()
    
    print("📊 Admin Dashboard Features:")
    print("   ✅ Detailed authentication tracking")
    print("   ✅ Enrollment success/failure analysis")
    print("   ✅ Impostor detection with reasoning")
    print("   ✅ Real-time filtering and search")
    print("   ✅ Data export functionality")
    print()
    
    print("🔗 Access Points:")
    print("   👥 User Frontend: http://localhost:5173")
    print("   🔒 Admin Dashboard: http://localhost:9000")
    print("   🔌 API Docs: http://localhost:8000/docs")
    print()
    
    print("🚀 Starting admin dashboard server...")
    
    # Start the admin dashboard
    try:
        subprocess.run([sys.executable, "admin_dashboard_server.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Admin dashboard stopped")
    except FileNotFoundError:
        print("❌ admin_dashboard_server.py not found")
        print("   Make sure you're in the correct directory")
    except Exception as e:
        print(f"❌ Error starting admin dashboard: {e}")

if __name__ == '__main__':
    start_admin_dashboard()
