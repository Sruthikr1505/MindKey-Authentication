#!/usr/bin/env python3
"""
Setup Verification Script
Checks if all dependencies are installed and the environment is ready.
"""

import sys
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("  ⚠ Warning: Python 3.10+ recommended")
        return False
    return True

def check_imports():
    """Check if all required packages can be imported"""
    packages = {
        'torch': 'PyTorch',
        'pytorch_lightning': 'PyTorch Lightning',
        'mne': 'MNE-Python',
        'numpy': 'NumPy',
        'scipy': 'SciPy',
        'sklearn': 'scikit-learn',
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'sqlalchemy': 'SQLAlchemy',
        'bcrypt': 'bcrypt',
        'captum': 'Captum',
        'matplotlib': 'Matplotlib',
    }
    
    # Optional packages
    optional_packages = {
        'onnx': 'ONNX',
        'onnxruntime': 'ONNX Runtime',
    }
    
    all_ok = True
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} - NOT INSTALLED")
            all_ok = False
    
    # Check optional packages
    print("\nOptional packages:")
    for package, name in optional_packages.items():
        try:
            __import__(package)
            print(f"✓ {name} (optional)")
        except ImportError:
            print(f"⚠ {name} - NOT INSTALLED (optional, only needed for ONNX export)")
        except Exception as e:
            print(f"⚠ {name} - ERROR (optional, can be ignored): {str(e)[:50]}")
    
    return all_ok

def check_directories():
    """Check if required directories exist"""
    dirs = [
        'data/raw',
        'src',
        'src/api',
        'src/utils',
        'src/inference',
        'frontend',
        'deployments',
    ]
    
    all_ok = True
    for dir_path in dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/ - NOT FOUND")
            all_ok = False
    
    return all_ok

def check_data_files():
    """Check if DEAP data files exist"""
    data_dir = Path('data/raw')
    if not data_dir.exists():
        print("✗ data/raw/ directory not found")
        return False
    
    bdf_files = list(data_dir.glob('s*.bdf'))
    if len(bdf_files) == 0:
        print("⚠ No .bdf files found in data/raw/")
        print("  Please download DEAP dataset and place s01.bdf - s10.bdf in data/raw/")
        return False
    else:
        print(f"✓ Found {len(bdf_files)} .bdf files in data/raw/")
        return True

def check_cuda():
    """Check CUDA availability"""
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
            return True
        else:
            print("⚠ CUDA not available (CPU mode will be used)")
            return False
    except ImportError:
        return False

def main():
    print("=" * 60)
    print("DEAP BiLSTM Authentication - Setup Verification")
    print("=" * 60)
    print()
    
    print("1. Checking Python version...")
    python_ok = check_python_version()
    print()
    
    print("2. Checking required packages...")
    packages_ok = check_imports()
    print()
    
    print("3. Checking directory structure...")
    dirs_ok = check_directories()
    print()
    
    print("4. Checking data files...")
    data_ok = check_data_files()
    print()
    
    print("5. Checking CUDA availability...")
    cuda_ok = check_cuda()
    print()
    
    print("=" * 60)
    if python_ok and packages_ok and dirs_ok:
        print("✓ Setup verification PASSED")
        print()
        if not data_ok:
            print("⚠ Note: DEAP data files not found")
            print("  Download from: https://www.eecs.qmul.ac.uk/mmv/datasets/deap/")
            print("  Place s01.bdf - s10.bdf in data/raw/")
        print()
        print("Ready to run:")
        print("  ./run_demo.sh")
        print()
        return 0
    else:
        print("✗ Setup verification FAILED")
        print()
        print("Please install missing dependencies:")
        print("  pip install -r requirements.txt")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
