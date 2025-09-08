#!/usr/bin/env python3
"""
BugSeek Startup Script

Simple script to start both backend and frontend services.
Usage:
    python run.py              # Start both services
    python run.py --backend    # Start only backend
    python run.py --frontend   # Start only frontend
"""

import os
import sys
import subprocess
import threading
import time
import argparse
from pathlib import Path

def start_backend():
    """Start Flask backend server."""
    print("🚀 Starting Flask Backend...")
    backend_path = Path(__file__).parent / "backend"
    os.chdir(backend_path)
    
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n⏹️ Backend server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend failed to start: {e}")

def start_frontend():
    """Start Fast Flask frontend."""
    print("🎨 Starting Fast Flask Frontend...")
    frontend_path = Path(__file__).parent / "frontend"
    
    try:
        subprocess.run([
            sys.executable, 
            str(frontend_path / "fast_app.py")
        ], check=True)
    except KeyboardInterrupt:
        print("\n⏹️ Frontend server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend failed to start: {e}")

def main():
    """Main startup function."""
    parser = argparse.ArgumentParser(description="BugSeek Startup Script")
    parser.add_argument("--backend", action="store_true", help="Start only backend")
    parser.add_argument("--frontend", action="store_true", help="Start only frontend")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔍 BugSeek - Error Log Management System")
    print("=" * 60)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and sys.base_prefix == sys.prefix:
        print("⚠️  Warning: Virtual environment not detected")
        print("   Consider activating venv: source venv/bin/activate")
        print()
    
    # Start services based on arguments
    if args.backend:
        start_backend()
    elif args.frontend:
        start_frontend()
    else:
        # Start both services
        print("🚀 Starting both Backend and Frontend services...")
        print("   Backend: http://localhost:5000")
        print("   Frontend: http://localhost:8080")
        print("   API Docs: http://localhost:5000/api/docs/")
        print()
        print("Press Ctrl+C to stop all services")
        print("-" * 60)
        
        # Start backend in a separate thread
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        
        # Wait a moment for backend to start
        time.sleep(3)
        
        # Start frontend in main thread
        try:
            start_frontend()
        except KeyboardInterrupt:
            print("\n⏹️ Shutting down all services...")
            sys.exit(0)

if __name__ == "__main__":
    main()
