#!/usr/bin/env python3
"""
Test script to verify setup_project.py works without Unicode issues
"""

import subprocess
import sys

def test_setup_script():
    """Test the setup script with minimal interaction."""
    print("Testing setup_project.py with automatic responses...")
    
    try:
        # Run setup script with 'n' responses (no to venv, no to deps)
        process = subprocess.Popen(
            [sys.executable, "setup_project.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        # Send 'no' responses to prompts
        stdout, stderr = process.communicate(input="n\nn\n", timeout=60)
        
        print("STDOUT:")
        print(stdout)
        
        if stderr:
            print("STDERR:")
            print(stderr)
        
        if process.returncode == 0:
            print("\n[SUCCESS] Setup script completed successfully!")
            return True
        else:
            print(f"\n[ERROR] Setup script failed with return code: {process.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("[ERROR] Setup script timed out")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to run setup script: {e}")
        return False

if __name__ == "__main__":
    success = test_setup_script()
    sys.exit(0 if success else 1)
