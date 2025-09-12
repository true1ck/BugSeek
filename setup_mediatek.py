#!/usr/bin/env python3
"""
MediaTek Environment Setup Script for BugSeek
=============================================

This script helps set up BugSeek for the MediaTek environment by:
1. Checking system requirements
2. Setting up environment variables
3. Installing dependencies
4. Initializing database
5. Testing AI service connectivity
6. Validating the complete setup

Usage:
    python setup_mediatek.py [--interactive] [--test-only]
    
Options:
    --interactive  : Ask for user input to configure MediaTek credentials
    --test-only    : Only run tests, don't modify anything
    --force        : Force setup even if files exist
    --help         : Show this help message

Requirements:
    - Python 3.8+
    - Access to MediaTek internal network
    - Valid MediaTek Azure API credentials
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
import argparse
from typing import Dict, List, Tuple, Optional

# Colors for console output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class MediaTekSetup:
    """Main setup class for MediaTek environment configuration."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_dir = self.root_dir / 'backend'
        self.env_file = self.root_dir / '.env'
        self.env_template = self.root_dir / '.env.mediatek'
        self.success_count = 0
        self.total_steps = 8
    
    def print_header(self):
        """Print setup script header."""
        print(f"""
{Colors.CYAN}{Colors.BOLD}🚀 BugSeek MediaTek Environment Setup{Colors.END}
{'='*60}
This script will configure BugSeek for MediaTek environment
{'='*60}
""")
    
    def print_success(self, message: str):
        """Print success message and increment counter."""
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
        self.success_count += 1
    
    def print_error(self, message: str):
        """Print error message."""
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    
    def print_warning(self, message: str):
        """Print warning message."""
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
    
    def print_info(self, message: str):
        """Print info message."""
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")
    
    def print_step(self, step: int, title: str):
        """Print step header."""
        print(f"\n{Colors.BOLD}{step}/{self.total_steps}. {title}{Colors.END}")
        print("-" * 50)
    
    def check_python_version(self) -> bool:
        """Check if Python version is compatible."""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.print_success(f"Python {version.major}.{version.minor}.{version.micro} - Compatible")
            return True
        else:
            self.print_error(f"Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
            return False
    
    def check_system_requirements(self) -> bool:
        """Check system requirements and dependencies."""
        self.print_step(1, "Checking System Requirements")
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Check if we're in the right directory
        if not self.backend_dir.exists():
            self.print_error("Backend directory not found. Run from BugSeek root directory.")
            return False
        else:
            self.print_success("BugSeek directory structure verified")
        
        # Check for required files
        required_files = ['.env.mediatek', 'backend/app.py', 'backend/models.py']
        for file_path in required_files:
            if (self.root_dir / file_path).exists():
                self.print_success(f"Found {file_path}")
            else:
                self.print_error(f"Missing {file_path}")
                return False
        
        return True
    
    def setup_environment_variables(self, interactive: bool = False) -> bool:
        """Set up environment variables for MediaTek."""
        self.print_step(2, "Setting up Environment Variables")
        
        # Check if .env already exists
        if self.env_file.exists() and not interactive:
            self.print_warning(".env file already exists")
            user_input = input("Overwrite existing .env file? (y/N): ").lower()
            if user_input != 'y':
                self.print_info("Keeping existing .env file")
                return True
        
        # Copy template
        if self.env_template.exists():
            shutil.copy2(self.env_template, self.env_file)
            self.print_success("Created .env from MediaTek template")
        else:
            # Create basic .env if template doesn't exist
            self.create_basic_env_file()
            self.print_warning("Created basic .env file (MediaTek template not found)")
        
        if interactive:
            self.interactive_env_setup()
        
        # Validate environment
        return self.validate_environment_variables()
    
    def create_basic_env_file(self):
        """Create a basic .env file with MediaTek defaults."""
        env_content = """# MediaTek Environment Configuration for BugSeek
# Update these values with your MediaTek credentials

# MediaTek Azure OpenAI Configuration
AZURE_API_KEY=your_mediatek_jwt_token_here
USER_ID=your_mediatek_user_id
ENDPOINT_URL=https://mlop-azure-gateway.mediatek.inc
MODEL_NAME=aida-gpt-4o-mini
API_VERSION=2024-10-21

# Flask Configuration
FLASK_ENV=development
DEBUG=True
SECRET_KEY=bugseek-hackathon-mediatek-2025

# Database Configuration
DATABASE_URL=sqlite:///instance/bugseek.db
SQLALCHEMY_TRACK_MODIFICATIONS=False

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# AI Service Configuration
AI_ANALYSIS_ENABLED=True
AI_MAX_RETRIES=3
AI_REQUEST_TIMEOUT=30

# CORS Configuration
CORS_ORIGINS=["http://localhost:8080", "http://127.0.0.1:8080"]

# MediaTek Specific
MTK_ENVIRONMENT=True
MTK_GATEWAY_TIMEOUT=45

# Hackathon Configuration
HACKATHON_MODE=True
HACKATHON_PASSWORD=hackathon2025
DEMO_DATA_ENABLED=True
"""
        with open(self.env_file, 'w') as f:
            f.write(env_content)
    
    def interactive_env_setup(self):
        """Interactive environment variable setup."""
        self.print_info("Interactive MediaTek credentials setup")
        
        # Read current .env
        env_vars = {}
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        env_vars[key] = value
        
        # Ask for MediaTek credentials
        print("\nEnter your MediaTek credentials:")
        
        # API Key
        current_key = env_vars.get('AZURE_API_KEY', '')
        if 'your_' in current_key or not current_key:
            current_key = ''
        
        api_key = input(f"Azure API Key [{current_key[:10]}...]: ").strip()
        if api_key:
            env_vars['AZURE_API_KEY'] = api_key
        
        # User ID
        current_user = env_vars.get('USER_ID', '')
        user_id = input(f"MediaTek User ID [{current_user}]: ").strip()
        if user_id:
            env_vars['USER_ID'] = user_id
        
        # Write updated .env
        self.write_env_file(env_vars)
        self.print_success("Updated .env with your credentials")
    
    def write_env_file(self, env_vars: Dict[str, str]):
        """Write environment variables to .env file."""
        with open(self.env_file, 'w') as f:
            f.write("# MediaTek Environment Configuration for BugSeek\n")
            f.write("# Generated by setup_mediatek.py\n\n")
            
            # Group variables
            groups = {
                'MediaTek Azure OpenAI': ['AZURE_API_KEY', 'USER_ID', 'ENDPOINT_URL', 'MODEL_NAME', 'API_VERSION'],
                'Flask Application': ['FLASK_ENV', 'DEBUG', 'SECRET_KEY'],
                'Database': ['DATABASE_URL', 'SQLALCHEMY_TRACK_MODIFICATIONS'],
                'File Upload': ['UPLOAD_FOLDER', 'MAX_CONTENT_LENGTH'],
                'AI Service': ['AI_ANALYSIS_ENABLED', 'AI_MAX_RETRIES', 'AI_REQUEST_TIMEOUT'],
                'CORS': ['CORS_ORIGINS'],
                'MediaTek Specific': ['MTK_ENVIRONMENT', 'MTK_GATEWAY_TIMEOUT'],
                'Hackathon': ['HACKATHON_MODE', 'HACKATHON_PASSWORD', 'DEMO_DATA_ENABLED']
            }
            
            for group_name, keys in groups.items():
                f.write(f"# {group_name}\n")
                for key in keys:
                    value = env_vars.get(key, '')
                    f.write(f"{key}={value}\n")
                f.write("\n")
    
    def validate_environment_variables(self) -> bool:
        """Validate that required environment variables are set."""
        self.print_info("Validating environment variables...")
        
        # Load .env file
        if not self.env_file.exists():
            self.print_error(".env file not found")
            return False
        
        # Check required variables
        required_vars = ['AZURE_API_KEY', 'USER_ID', 'ENDPOINT_URL', 'MODEL_NAME']
        missing_vars = []
        
        with open(self.env_file, 'r') as f:
            env_content = f.read()
            
            for var in required_vars:
                if var not in env_content or f'{var}=your_' in env_content:
                    missing_vars.append(var)
        
        if missing_vars:
            self.print_error(f"Missing or placeholder values: {', '.join(missing_vars)}")
            self.print_warning("Please update .env with your actual MediaTek credentials")
            return False
        
        self.print_success("Environment variables validated")
        return True
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies."""
        self.print_step(3, "Installing Dependencies")
        
        requirements_file = self.backend_dir / 'requirements.txt'
        
        if not requirements_file.exists():
            self.print_warning("requirements.txt not found, installing basic dependencies")
            basic_deps = [
                'flask', 'flask-cors', 'flask-sqlalchemy', 'flask-restx',
                'requests', 'python-dotenv', 'sqlalchemy', 'werkzeug'
            ]
            
            for dep in basic_deps:
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                                 check=True, capture_output=True)
                    self.print_success(f"Installed {dep}")
                except subprocess.CalledProcessError:
                    self.print_error(f"Failed to install {dep}")
                    return False
        else:
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)], 
                             check=True, capture_output=True)
                self.print_success("Installed dependencies from requirements.txt")
            except subprocess.CalledProcessError as e:
                self.print_error(f"Failed to install dependencies: {e}")
                return False
        
        return True
    
    def initialize_database(self) -> bool:
        """Initialize the database."""
        self.print_step(4, "Initializing Database")
        
        try:
            # Create instance directory
            instance_dir = self.root_dir / 'instance'
            instance_dir.mkdir(exist_ok=True)
            self.print_success("Created instance directory")
            
            # Check if initialization scripts exist
            init_scripts = [
                '1_initialize_database.py',
                '2_load_sample_data.py'
            ]
            
            for script in init_scripts:
                script_path = self.root_dir / script
                if script_path.exists():
                    try:
                        subprocess.run([sys.executable, str(script_path)], 
                                     check=True, capture_output=True, cwd=self.root_dir)
                        self.print_success(f"Executed {script}")
                    except subprocess.CalledProcessError as e:
                        self.print_error(f"Failed to execute {script}: {e}")
                        return False
                else:
                    self.print_warning(f"{script} not found, skipping")
            
            return True
            
        except Exception as e:
            self.print_error(f"Database initialization failed: {e}")
            return False
    
    def test_mediatek_connectivity(self) -> bool:
        """Test MediaTek AI service connectivity."""
        self.print_step(5, "Testing MediaTek AI Connectivity")
        
        try:
            # Run the test script if it exists
            test_script = self.root_dir / 'test_mediatek_ai.py'
            if test_script.exists():
                result = subprocess.run([sys.executable, str(test_script)], 
                                      capture_output=True, text=True, cwd=self.root_dir)
                if result.returncode == 0:
                    self.print_success("MediaTek AI connectivity test passed")
                    return True
                else:
                    self.print_error("MediaTek AI connectivity test failed")
                    self.print_info("You can run 'python test_mediatek_ai.py' manually for details")
                    return False
            else:
                # Basic connectivity test
                import requests
                from dotenv import load_dotenv
                
                load_dotenv(self.env_file)
                
                endpoint = os.getenv('ENDPOINT_URL', 'https://mlop-azure-gateway.mediatek.inc')
                
                try:
                    response = requests.get(endpoint, timeout=10)
                    self.print_success(f"MediaTek gateway reachable (HTTP {response.status_code})")
                    return True
                except Exception as e:
                    self.print_error(f"Cannot reach MediaTek gateway: {e}")
                    return False
                    
        except Exception as e:
            self.print_error(f"Connectivity test failed: {e}")
            return False
    
    def validate_application_structure(self) -> bool:
        """Validate application file structure."""
        self.print_step(6, "Validating Application Structure")
        
        required_paths = [
            'backend/app.py',
            'backend/models.py',
            'backend/services.py',
            'backend/ai_services.py',
            'frontend/app.py',
            'run.py'
        ]
        
        missing_files = []
        for path in required_paths:
            if not (self.root_dir / path).exists():
                missing_files.append(path)
        
        if missing_files:
            self.print_error(f"Missing files: {', '.join(missing_files)}")
            return False
        
        self.print_success("Application structure validated")
        return True
    
    def create_upload_directory(self) -> bool:
        """Create upload directory with proper permissions."""
        self.print_step(7, "Setting up Upload Directory")
        
        upload_dir = self.root_dir / 'uploads'
        upload_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        subdirs = ['logs', 'temp', 'processed']
        for subdir in subdirs:
            (upload_dir / subdir).mkdir(exist_ok=True)
        
        self.print_success("Upload directories created")
        return True
    
    def run_final_validation(self) -> bool:
        """Run final validation tests."""
        self.print_step(8, "Final Validation")
        
        try:
            # Test basic imports
            sys.path.insert(0, str(self.backend_dir))
            
            try:
                from app import create_app
                self.print_success("Backend imports working")
            except ImportError as e:
                self.print_error(f"Backend import failed: {e}")
                return False
            
            try:
                from models import db, ErrorLog
                self.print_success("Database models loading")
            except ImportError as e:
                self.print_error(f"Models import failed: {e}")
                return False
            
            try:
                from ai_services import OpenAIService
                self.print_success("AI services available")
            except ImportError as e:
                self.print_warning(f"AI services import failed: {e}")
                # This is not critical, fallback will work
            
            self.print_success("Final validation passed")
            return True
            
        except Exception as e:
            self.print_error(f"Final validation failed: {e}")
            return False
    
    def print_summary(self):
        """Print setup summary and next steps."""
        print(f"\n{Colors.BOLD}📊 Setup Summary{Colors.END}")
        print("="*50)
        
        success_rate = (self.success_count / self.total_steps) * 100
        
        if success_rate == 100:
            print(f"{Colors.GREEN}🎉 SETUP COMPLETE! ({self.success_count}/{self.total_steps} steps){Colors.END}")
            print(f"\n{Colors.BOLD}✅ Your BugSeek is ready for MediaTek environment!{Colors.END}")
        elif success_rate >= 80:
            print(f"{Colors.YELLOW}⚠️  PARTIAL SETUP ({self.success_count}/{self.total_steps} steps){Colors.END}")
            print(f"\n{Colors.BOLD}🔧 BugSeek should work but may have limited features{Colors.END}")
        else:
            print(f"{Colors.RED}❌ SETUP INCOMPLETE ({self.success_count}/{self.total_steps} steps){Colors.END}")
            print(f"\n{Colors.BOLD}🚨 Please fix the issues above before using BugSeek{Colors.END}")
        
        print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")
        if success_rate >= 80:
            print("1. 🚀 Start BugSeek:")
            print("   python run.py")
            print("\n2. 🌐 Open in browser:")
            print("   http://localhost:8080")
            print("\n3. 🔑 Login with password:")
            print("   hackathon2025")
            print("\n4. 🧪 Test with sample log files")
        else:
            print("1. 🔧 Fix configuration issues")
            print("2. 🔄 Run setup again:")
            print("   python setup_mediatek.py")
            print("3. 📖 Check MediaTek setup guide:")
            print("   MEDIATEK_SETUP_GUIDE.md")
        
        print(f"\n{Colors.BOLD}Troubleshooting:{Colors.END}")
        print("• Test connectivity: python test_mediatek_ai.py")
        print("• Check logs: tail -f debug.log")
        print("• Manual setup: MEDIATEK_SETUP_GUIDE.md")
        
        print(f"\n{Colors.CYAN}MediaTek BugSeek Setup Complete! 🏆{Colors.END}")

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(
        description='MediaTek Environment Setup for BugSeek',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python setup_mediatek.py                    # Basic setup
    python setup_mediatek.py --interactive      # Interactive credential setup
    python setup_mediatek.py --test-only        # Only run tests
        """
    )
    
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive setup with credential prompts')
    parser.add_argument('--test-only', action='store_true',
                       help='Only run tests, don\'t modify anything')
    parser.add_argument('--force', action='store_true',
                       help='Force setup even if files exist')
    
    args = parser.parse_args()
    
    setup = MediaTekSetup()
    setup.print_header()
    
    if args.test_only:
        # Run validation tests only
        setup.print_info("Running validation tests only...")
        setup.test_mediatek_connectivity()
        setup.run_final_validation()
        return
    
    # Run full setup
    steps = [
        setup.check_system_requirements,
        lambda: setup.setup_environment_variables(args.interactive),
        setup.install_dependencies,
        setup.initialize_database,
        setup.test_mediatek_connectivity,
        setup.validate_application_structure,
        setup.create_upload_directory,
        setup.run_final_validation
    ]
    
    for step in steps:
        if not step():
            setup.print_error("Setup failed. Check errors above.")
            break
    
    setup.print_summary()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Setup interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Setup failed: {e}{Colors.END}")
        sys.exit(1)
