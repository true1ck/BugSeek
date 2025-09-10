#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BugSeek Project Setup Script
Comprehensive setup for new users who clone the project
"""

import os
import sys
import json
import uuid
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("[ERROR] Python 3.8 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    print(f"[OK] Python version: {sys.version.split()[0]}")
    return True

def create_virtual_environment():
    """Create virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("[OK] Virtual environment already exists")
        return True
    
    try:
        print("[INFO] Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("[OK] Virtual environment created successfully")
        
        # Provide activation instructions
        if os.name == 'nt':  # Windows
            activate_script = "venv\\Scripts\\activate"
            pip_path = "venv\\Scripts\\pip"
        else:  # Unix/Linux/macOS
            activate_script = "source venv/bin/activate"
            pip_path = "venv/bin/pip"
            
        print(f"\n[NOTE] To activate virtual environment:")
        print(f"   {activate_script}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to create virtual environment: {e}")
        return False

def install_dependencies():
    """Install project dependencies."""
    print("[INFO] Installing dependencies...")
    
    # Determine pip path
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip" if Path("venv").exists() else "pip"
        python_path = "venv\\Scripts\\python" if Path("venv").exists() else "python"
    else:  # Unix/Linux/macOS
        pip_path = "venv/bin/pip" if Path("venv").exists() else "pip"
        python_path = "venv/bin/python" if Path("venv").exists() else "python"
    
    try:
        # Check if requirements.txt exists
        if not Path("requirements.txt").exists():
            print("[ERROR] requirements.txt not found!")
            return False
            
        # Install dependencies
        subprocess.run([python_path, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([python_path, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("[OK] Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install dependencies: {e}")
        return False

def setup_environment_file():
    """Create .env file from template."""
    env_path = Path(".env")
    template_path = Path(".env.template")
    example_path = Path(".env.example")
    
    if env_path.exists():
        print("[OK] .env file already exists")
        return True
    
    # Try to copy from template or example
    source_file = None
    if template_path.exists():
        source_file = template_path
    elif example_path.exists():
        source_file = example_path
    else:
        print("[ERROR] No .env template found!")
        return False
    
    try:
        shutil.copy(source_file, env_path)
        print(f"[OK] Created .env file from {source_file}")
        
        # Update database URL to use absolute path
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update database URL to use absolute path
        project_root = Path.cwd()
        db_path = project_root / "backend" / "instance" / "bugseek.db"
        db_uri = f"sqlite:///{str(db_path).replace(os.sep, '/')}"
        
        content = content.replace("DATABASE_URL=sqlite:///bugseek.db", f"DATABASE_URL={db_uri}")
        
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[NOTE] Database configured to: {db_uri}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to create .env file: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = [
        "backend/instance",
        "uploads", 
        "logs",
        "exports"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"[OK] Created directory: {directory}")
        else:
            print(f"[OK] Directory exists: {directory}")

def initialize_database():
    """Initialize database with proper schema."""
    print("\n[INFO] Initializing database...")
    
    # Add project root to path
    sys.path.insert(0, str(Path.cwd()))
    
    try:
        from flask import Flask
        from backend.models import db, ErrorLog, ErrorLogFile, create_tables
        from config.settings import config
        
        # Create Flask app
        app = Flask(__name__)
        app.config.from_object(config['development'])
        
        # Initialize SQLAlchemy
        db.init_app(app)
        
        with app.app_context():
            print("[INFO] Creating database tables...")
            create_tables(app)
            
            # Verify tables were created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"[OK] Created {len(tables)} table(s): {', '.join(tables)}")
                return app
            else:
                print("[ERROR] No tables were created!")
                return None
                
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def migrate_ai_tables():
    """Run AI tables migration if available."""
    if Path("migrate_ai_tables.py").exists():
        print("[INFO] Running AI tables migration...")
        try:
            subprocess.run([sys.executable, "migrate_ai_tables.py"], check=True)
            print("[OK] AI tables migration completed")
        except subprocess.CalledProcessError as e:
            print(f"[WARN] AI tables migration failed: {e}")
            print("   This is optional - basic functionality will still work")

def create_comprehensive_sample_data():
    """Create comprehensive realistic sample data."""
    base_time = datetime.now()
    
    sample_logs = [
        {
            'TeamName': 'Frontend',
            'Module': 'Authentication', 
            'Description': 'User login timeout after 30 seconds on mobile app',
            'Owner': 'john.doe@company.com',
            'LogFileName': 'auth_mobile_timeout.log',
            'ErrorName': 'LOGIN_TIMEOUT_MOBILE',
            'LogContent': '''2025-09-10 14:30:22 ERROR [AuthService] Connection timeout to authentication service
2025-09-10 14:30:22 ERROR [AuthService] Retrying connection attempt 1/3  
2025-09-10 14:30:52 ERROR [AuthService] Authentication failed after 30s timeout
2025-09-10 14:30:52 ERROR [AuthService] User session terminated: timeout
2025-09-10 14:30:52 INFO [AuthService] Redirecting to login page''',
            'FileSize': 2048,
            'SolutionPossible': True,
            'Severity': 'medium',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=1, hours=5)
        },
        {
            'TeamName': 'Backend',
            'Module': 'Database',
            'Description': 'SQL query execution timeout on user statistics report',
            'Owner': 'jane.smith@company.com',
            'LogFileName': 'db_stats_query_timeout.log',
            'ErrorName': 'SQL_QUERY_TIMEOUT',
            'LogContent': '''2025-09-09 09:15:33 WARNING [DatabaseManager] Query execution time: 45.2 seconds
2025-09-09 09:15:33 WARNING [DatabaseManager] Query: SELECT * FROM users JOIN logs ON...
2025-09-09 09:16:18 ERROR [DatabaseManager] Query timeout after 60 seconds
2025-09-09 09:16:18 ERROR [DatabaseManager] Connection pool exhausted
2025-09-09 09:16:18 CRITICAL [DatabaseManager] Database performance degraded''',
            'FileSize': 1536,
            'SolutionPossible': True,
            'Severity': 'high',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=2, hours=8)
        },
        {
            'TeamName': 'API',
            'Module': 'Payment',
            'Description': 'Payment gateway returning HTTP 500 for credit card transactions',
            'Owner': 'mike.wilson@company.com',
            'LogFileName': 'payment_gateway_error.log',
            'ErrorName': 'PAYMENT_GATEWAY_ERROR',
            'LogContent': '''2025-09-08 16:45:10 ERROR [PaymentService] HTTP 500 from payment gateway
2025-09-08 16:45:10 ERROR [PaymentService] Response: {"error": "Internal server error"}
2025-09-08 16:45:10 ERROR [PaymentService] Transaction ID: TXN_789456123
2025-09-08 16:45:10 ERROR [PaymentService] Card ending in ****1234 declined
2025-09-08 16:45:10 WARNING [PaymentService] Retrying payment in 30 seconds''',
            'FileSize': 1200,
            'SolutionPossible': True,
            'Severity': 'critical',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=3, hours=12)
        },
        {
            'TeamName': 'DevOps',
            'Module': 'Deployment',
            'Description': 'Docker container failing to start on production server',
            'Owner': 'sarah.jones@company.com',
            'LogFileName': 'docker_startup_failure.log',
            'ErrorName': 'CONTAINER_START_FAILURE',
            'LogContent': '''2025-09-07 10:20:15 ERROR [Docker] Container bugseek_backend failed to start
2025-09-07 10:20:15 ERROR [Docker] Exit code: 125
2025-09-07 10:20:15 ERROR [Docker] Port 5000 already in use
2025-09-07 10:20:15 ERROR [Docker] Health check failed: connection refused
2025-09-07 10:20:15 INFO [Docker] Attempting automatic port reassignment''',
            'FileSize': 980,
            'SolutionPossible': True,
            'Severity': 'high',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=4, hours=3)
        },
        {
            'TeamName': 'Frontend',
            'Module': 'Dashboard',
            'Description': 'Chart rendering failure when loading large datasets',
            'Owner': 'alex.brown@company.com',
            'LogFileName': 'chart_render_memory_error.log',
            'ErrorName': 'CHART_RENDER_MEMORY_ERROR',
            'LogContent': '''2025-09-06 13:25:44 ERROR [ChartComponent] Out of memory rendering 50000+ data points
2025-09-06 13:25:44 ERROR [ChartComponent] Canvas allocation failed
2025-09-06 13:25:44 ERROR [ChartComponent] Browser memory usage: 1.8GB
2025-09-06 13:25:44 ERROR [ChartComponent] Fallback to table view activated
2025-09-06 13:25:44 WARNING [ChartComponent] Consider implementing data pagination''',
            'FileSize': 1856,
            'SolutionPossible': True,
            'Severity': 'medium',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=5, hours=10)
        },
        {
            'TeamName': 'Backend',
            'Module': 'FileUpload',
            'Description': 'Large file uploads failing with connection reset',
            'Owner': 'david.lee@company.com',
            'LogFileName': 'file_upload_connection_reset.log',
            'ErrorName': 'UPLOAD_CONNECTION_RESET',
            'LogContent': '''2025-09-05 11:40:12 ERROR [UploadService] Connection reset by peer during upload
2025-09-05 11:40:12 ERROR [UploadService] File: large_dataset.csv (450MB)
2025-09-05 11:40:12 ERROR [UploadService] Bytes uploaded: 234,567,890 / 472,186,432
2025-09-05 11:40:12 ERROR [UploadService] Retry attempt 3/3 failed
2025-09-05 11:40:12 INFO [UploadService] File upload cancelled by user''',
            'FileSize': 3072,
            'SolutionPossible': True,
            'Severity': 'medium',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=6, hours=14)
        },
        {
            'TeamName': 'QA',
            'Module': 'Testing',
            'Description': 'Automated test suite failing on new build deployment',
            'Owner': 'lisa.garcia@company.com',
            'LogFileName': 'test_suite_failure.log',
            'ErrorName': 'AUTOMATED_TEST_FAILURE',
            'LogContent': '''2025-09-04 08:15:30 ERROR [TestRunner] 15 out of 234 tests failed
2025-09-04 08:15:30 ERROR [TestRunner] Selenium WebDriver timeout on login test
2025-09-04 08:15:30 ERROR [TestRunner] API endpoint /api/v1/users returning 404
2025-09-04 08:15:30 ERROR [TestRunner] Database seed data missing for test environment
2025-09-04 08:15:30 WARNING [TestRunner] Test execution time: 45 minutes''',
            'FileSize': 4096,
            'SolutionPossible': True,
            'Severity': 'medium',
            'Environment': 'dev',
            'CreatedAt': base_time - timedelta(days=7, hours=6)
        },
        {
            'TeamName': 'Security',
            'Module': 'Authentication',
            'Description': 'Suspicious login attempts from multiple IP addresses',
            'Owner': 'emma.davis@company.com',
            'LogFileName': 'suspicious_login_attempts.log',
            'ErrorName': 'SUSPICIOUS_LOGIN_PATTERN',
            'LogContent': '''2025-09-03 02:33:45 WARNING [SecurityMonitor] 47 failed login attempts for user admin@company.com
2025-09-03 02:33:45 WARNING [SecurityMonitor] Source IPs: 185.220.101.*, 198.51.100.*
2025-09-03 02:33:45 ERROR [SecurityMonitor] Account locked due to suspicious activity
2025-09-03 02:33:45 ERROR [SecurityMonitor] Possible brute force attack detected
2025-09-03 02:33:45 CRITICAL [SecurityMonitor] Security incident logged''',
            'FileSize': 1728,
            'SolutionPossible': True,
            'Severity': 'critical',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=8, hours=18)
        },
        {
            'TeamName': 'Infrastructure',
            'Module': 'Monitoring',
            'Description': 'Disk space alert triggered on main database server',
            'Owner': 'chris.wilson@company.com',
            'LogFileName': 'disk_space_critical.log',
            'ErrorName': 'DISK_SPACE_CRITICAL',
            'LogContent': '''2025-09-02 23:55:12 CRITICAL [DiskMonitor] Disk usage on /var/lib/mysql: 94%
2025-09-02 23:55:12 CRITICAL [DiskMonitor] Available space: 2.3GB of 40GB
2025-09-02 23:55:12 CRITICAL [DiskMonitor] Log rotation failed - insufficient space
2025-09-02 23:55:12 CRITICAL [DiskMonitor] Database backup cancelled due to space constraints
2025-09-02 23:55:12 ALERT [DiskMonitor] Immediate action required''',
            'FileSize': 896,
            'SolutionPossible': True,
            'Severity': 'critical',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=9, hours=22)
        },
        {
            'TeamName': 'Mobile',
            'Module': 'Push Notifications',
            'Description': 'FCM push notifications failing to deliver on Android devices',
            'Owner': 'maria.rodriguez@company.com',
            'LogFileName': 'fcm_delivery_failure.log',
            'ErrorName': 'PUSH_NOTIFICATION_FAILURE',
            'LogContent': '''2025-09-01 11:22:33 ERROR [FCMService] Failed to send notification to token: eJ8x9K2mN...
2025-09-01 11:22:33 ERROR [FCMService] Response: InvalidRegistration
2025-09-01 11:22:33 ERROR [FCMService] Batch size: 1500 notifications
2025-09-01 11:22:33 ERROR [FCMService] Success rate: 45% (675/1500)
2025-09-01 11:22:33 WARNING [FCMService] Updating device token registry''',
            'FileSize': 2240,
            'SolutionPossible': True,
            'Severity': 'medium',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=10, hours=4)
        }
    ]
    
    return sample_logs

def populate_sample_data(app):
    """Populate database with comprehensive sample data."""
    print("\n[INFO] Adding sample data to database...")
    
    sample_data = create_comprehensive_sample_data()
    
    try:
        from backend.models import db, ErrorLog
        
        with app.app_context():
            # Clear existing data
            ErrorLog.query.delete()
            db.session.commit()
            
            added_count = 0
            for log_data in sample_data:
                error_log = ErrorLog(
                    Cr_ID=str(uuid.uuid4()),
                    TeamName=log_data['TeamName'],
                    Module=log_data['Module'],
                    Description=log_data['Description'],
                    Owner=log_data['Owner'],
                    LogFileName=log_data['LogFileName'],
                    ErrorName=log_data['ErrorName'],
                    LogContentPreview=log_data['LogContent'][:2048] if len(log_data['LogContent']) > 2048 else log_data['LogContent'],
                    SolutionPossible=log_data['SolutionPossible'],
                    Severity=log_data['Severity'],
                    Environment=log_data['Environment'],
                    CreatedAt=log_data['CreatedAt'],
                    Embedding=json.dumps({"vector": [0.1, 0.3, 0.8, 0.2, 0.9], "confidence": 0.85})
                )
                
                db.session.add(error_log)
                added_count += 1
            
            db.session.commit()
            
            print(f"[OK] Successfully added {added_count} sample error logs!")
            
            # Show summary
            print("\n[INFO] Database Summary:")
            total_logs = ErrorLog.query.count()
            teams = db.session.query(ErrorLog.TeamName).distinct().count()
            modules = db.session.query(ErrorLog.Module).distinct().count()
            solved_count = ErrorLog.query.filter_by(SolutionPossible=True).count()
            
            print(f"   • Total Error Logs: {total_logs}")
            print(f"   • Unique Teams: {teams}")
            print(f"   • Unique Modules: {modules}")
            print(f"   • Solutions Available: {solved_count}")
            print(f"   • Pending Issues: {total_logs - solved_count}")
            
            return True
            
    except Exception as e:
        print(f"[ERROR] Error adding sample data: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection and display summary."""
    print("\n[INFO] Testing database connection...")
    
    try:
        from flask import Flask
        from backend.models import db, ErrorLog
        from config.settings import config
        
        app = Flask(__name__)
        app.config.from_object(config['development'])
        db.init_app(app)
        
        with app.app_context():
            # Test basic query
            total_logs = ErrorLog.query.count()
            print(f"[OK] Database connection successful!")
            print(f"📋 Found {total_logs} error logs in database")
            
            if total_logs > 0:
                # Show sample data
                latest_log = ErrorLog.query.order_by(ErrorLog.CreatedAt.desc()).first()
                print(f"   Latest log: {latest_log.ErrorName} from {latest_log.TeamName}")
                
                # Show team distribution
                from sqlalchemy import func
                team_stats = db.session.query(
                    ErrorLog.TeamName,
                    func.count(ErrorLog.Cr_ID)
                ).group_by(ErrorLog.TeamName).all()
                
                print("   Team distribution:")
                for team, count in team_stats:
                    print(f"     • {team}: {count} logs")
            
            return True
            
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False

def create_startup_instructions():
    """Create a file with startup instructions."""
    instructions = """
# BugSeek Setup Complete!

Your BugSeek project is now fully set up with sample data.

## Quick Start Commands:

### 1. Activate Virtual Environment (if created):
Windows:   venv\\Scripts\\activate
macOS/Linux: source venv/bin/activate

### 2. Run the Application:
python run.py                    # Start both backend and frontend
python run.py --backend         # Start only backend (port 5000)
python run.py --frontend        # Start only frontend (port 8080)

### 3. Access the Application:
- Frontend UI: http://localhost:8080
- Backend API: http://localhost:5000
- API Documentation: http://localhost:5000/api/docs/

### 4. Useful Development Commands:
python database_viewer.py       # Interactive database viewer
pytest                          # Run tests
python migrate_ai_tables.py     # Add AI features (optional)

### 5. Sample Data:
Your database now contains 10 realistic error logs with:
- Different teams (Frontend, Backend, API, DevOps, QA, Security, Infrastructure, Mobile)  
- Various severity levels (low, medium, high, critical)
- Different environments (dev, staging, prod)
- Realistic log content and timestamps

### 6. Next Steps:
1. Explore the UI to see the sample data
2. Try uploading your own log files
3. Test the search and filtering features
4. Configure AI features with OpenAI API key (optional)

### 7. Need Help?
- Check README.md for detailed documentation
- Review WARP.md for development guidance  
- Check AI_FEATURES.md for AI integration setup

Happy debugging!
"""
    
    with open("SETUP_COMPLETE.md", "w", encoding='utf-8') as f:
        f.write(instructions)
    
    print("[OK] Created SETUP_COMPLETE.md with startup instructions")

def main():
    """Main setup function."""
    print("BugSeek Project Setup")
    print("=" * 50)
    print("Setting up BugSeek for first-time use...")
    print()
    
    # Step 1: Check Python version
    if not check_python_version():
        return False
    
    # Step 2: Create virtual environment (optional but recommended)
    create_venv = input("Create virtual environment? [Y/n]: ").strip().lower()
    if create_venv in ['', 'y', 'yes']:
        if not create_virtual_environment():
            print("[WARN] Virtual environment creation failed, continuing without it...")
    
    # Step 3: Install dependencies
    install_deps = input("Install dependencies? [Y/n]: ").strip().lower()
    if install_deps in ['', 'y', 'yes']:
        if not install_dependencies():
            print("[ERROR] Dependency installation failed!")
            return False
    
    # Step 4: Setup environment file
    if not setup_environment_file():
        return False
    
    # Step 5: Create directories
    create_directories()
    
    # Step 6: Initialize database
    app = initialize_database()
    if not app:
        return False
    
    # Step 7: Run AI migration (optional)
    migrate_ai_tables()
    
    # Step 8: Add sample data
    if not populate_sample_data(app):
        return False
    
    # Step 9: Test database connection
    if not test_database_connection():
        return False
    
    # Step 10: Create startup instructions
    create_startup_instructions()
    
    print("\n[SUCCESS] BugSeek setup completed successfully!")
    print("\n[NOTE] Next steps:")
    print("   1. Read SETUP_COMPLETE.md for startup commands")
    print("   2. Run: python run.py")
    print("   3. Open: http://localhost:8080")
    print("   4. Enjoy your fully configured BugSeek system!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n[ERROR] Setup failed! Please check the errors above and try again.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] Setup successful! You're ready to use BugSeek.")
        sys.exit(0)
