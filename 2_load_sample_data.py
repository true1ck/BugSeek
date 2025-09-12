#!/usr/bin/env python3
"""
2_load_sample_data.py
Load comprehensive sample data into BugSeek database
"""

import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def create_comprehensive_sample_data():
    """Create comprehensive realistic sample data for BugSeek."""
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
        },
        # Additional 5 logs to make it 15 total
        {
            'TeamName': 'Data Science',
            'Module': 'ML Pipeline',
            'Description': 'Machine learning model training job stuck in pending state',
            'Owner': 'dr.alan.turing@company.com',
            'LogFileName': 'ml_training_stuck.log',
            'ErrorName': 'ML_TRAINING_TIMEOUT',
            'LogContent': '''2025-08-31 16:30:45 WARNING [MLPipeline] Training job ID: ml_job_789123 pending for 4 hours
2025-08-31 16:30:45 ERROR [MLPipeline] GPU allocation failed: insufficient resources
2025-08-31 16:30:45 ERROR [MLPipeline] Dataset size: 2.8TB, Memory required: 64GB
2025-08-31 16:30:45 ERROR [MLPipeline] Queue position: 15/20''',
            'FileSize': 3584,
            'SolutionPossible': False,
            'Severity': 'medium',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=11, hours=8)
        },
        {
            'TeamName': 'Network',
            'Module': 'Load Balancer',
            'Description': 'HAProxy load balancer dropping connections during peak traffic',
            'Owner': 'network.ops@company.com',
            'LogFileName': 'haproxy_connection_drops.log',
            'ErrorName': 'LOAD_BALANCER_CONNECTION_DROP',
            'LogContent': '''2025-08-30 19:30:25 ERROR [HAProxy] Server backend1: 504 Gateway Timeout
2025-08-30 19:30:25 ERROR [HAProxy] Connection drops: 1,247 in last 5 minutes
2025-08-30 19:30:25 ERROR [HAProxy] Active connections: 8,924 / 10,000
2025-08-30 19:30:25 WARNING [HAProxy] Backend server response time: 15.2s''',
            'FileSize': 3072,
            'SolutionPossible': True,
            'Severity': 'high',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=12, hours=11)
        },
        {
            'TeamName': 'Platform',
            'Module': 'Microservices',
            'Description': 'Service mesh experiencing cascading failures across multiple services',
            'Owner': 'platform.team@company.com',
            'LogFileName': 'service_mesh_cascade.log',
            'ErrorName': 'SERVICE_MESH_CASCADE_FAILURE',
            'LogContent': '''2025-08-29 22:15:18 ERROR [ServiceMesh] Circuit breaker opened: user-service
2025-08-29 22:15:18 ERROR [ServiceMesh] Downstream failure: payment-service (timeout)
2025-08-29 22:15:18 CRITICAL [ServiceMesh] 7 services affected by cascade failure
2025-08-29 22:15:18 ERROR [ServiceMesh] Recovery ETA: 15-20 minutes''',
            'FileSize': 3840,
            'SolutionPossible': True,
            'Severity': 'critical',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=13, hours=1)
        },
        {
            'TeamName': 'Analytics',
            'Module': 'Data Pipeline',
            'Description': 'Daily data pipeline failing during transformation stage',
            'Owner': 'data.engineer@company.com',
            'LogFileName': 'etl_transform_failure.log',
            'ErrorName': 'ETL_TRANSFORM_FAILURE',
            'LogContent': '''2025-08-28 04:15:33 ERROR [ETLPipeline] Transformation step 3/7 failed
2025-08-28 04:15:33 ERROR [ETLPipeline] Spark job: application_1691234567890_0123
2025-08-28 04:15:33 ERROR [ETLPipeline] OutOfMemoryError: Java heap space
2025-08-28 04:15:33 ERROR [ETLPipeline] Processed: 2.1M/5.8M records''',
            'FileSize': 4608,
            'SolutionPossible': True,
            'Severity': 'high',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=14, hours=20)
        },
        {
            'TeamName': 'Mobile',
            'Module': 'Real-time Sync',
            'Description': 'Mobile app failing to sync data when network connectivity is restored',
            'Owner': 'mobile.dev@company.com',
            'LogFileName': 'mobile_sync_failure.log',
            'ErrorName': 'OFFLINE_SYNC_FAILURE',
            'LogContent': '''2025-08-27 08:45:33 ERROR [SyncManager] Sync attempt failed after 3 retries
2025-08-27 08:45:33 ERROR [SyncManager] Pending operations: 127
2025-08-27 08:45:33 ERROR [SyncManager] Conflict resolution failed for 23 records
2025-08-27 08:45:33 ERROR [SyncManager] Last successful sync: 2025-08-26 14:22:10''',
            'FileSize': 2304,
            'SolutionPossible': False,
            'Severity': 'medium',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=15, hours=15)
        }
    ]
    
    return sample_logs

def load_sample_data():
    """Load comprehensive sample data into the database."""
    print("=" * 60)
    print("BugSeek Sample Data Loader")
    print("=" * 60)
    print(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        from flask import Flask
        from backend.models import db, ErrorLog
        from config.settings import config
        from backend.auth_service import AuthenticationService
        
        # Create Flask app
        app = Flask(__name__)
        app.config.from_object(config['development'])
        db.init_app(app)
        
        with app.app_context():
            print("[INFO] Loading sample data...")
            
            # Clear existing data
            print("[INFO] Clearing existing error logs...")
            ErrorLog.query.delete()
            db.session.commit()
            
            # Get sample data
            sample_data = create_comprehensive_sample_data()
            print(f"[INFO] Prepared {len(sample_data)} sample error logs")
            
            added_count = 0
            for i, log_data in enumerate(sample_data, 1):
                try:
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
                    print(f"   [{i:2d}] Added: {log_data['ErrorName']} ({log_data['TeamName']})")
                    
                except Exception as e:
                    print(f"   [ERROR] Failed to add log {i}: {e}")
            
            # Commit all changes
            db.session.commit()
            
            # Create demo users as part of sample data
            print("\n[INFO] Creating demo users as part of sample data...")
            create_demo_users()
            
            print(f"\n[OK] Successfully added {added_count} sample error logs!")
            return added_count
            
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return 0
    except Exception as e:
        print(f"[ERROR] Failed to load sample data: {e}")
        import traceback
        traceback.print_exc()
        return 0

def create_demo_users():
    """Create demo users for authentication."""
    print("\n" + "=" * 40)
    print("Creating Demo Users")
    print("=" * 40)
    
    demo_users = [
        {"employee_id": "admin", "password": "admin123", "role": "System Administrator", "is_active": True},
        {"employee_id": "developer", "password": "dev123", "role": "Developer User", "is_active": True},
        {"employee_id": "testuser", "password": "test123", "role": "Test User", "is_active": True},
        {"employee_id": "hackathon", "password": "hackathon2025", "role": "Hackathon Participant", "is_active": True},
        {"employee_id": "demo", "password": "demo123", "role": "Demo User", "is_active": True}
    ]
    
    created_count = 0
    for user_data in demo_users:
        try:
            result = AuthenticationService.create_user(
                employee_id=user_data["employee_id"],
                password=user_data["password"],
                role=user_data["role"],
                is_active=user_data["is_active"]
            )
            
            if result["success"]:
                print(f"[OK] Created user: {user_data['employee_id']} ({user_data['role']})")
                created_count += 1
            else:
                print(f"[INFO] User {user_data['employee_id']} already exists")
        except Exception as e:
            print(f"[ERROR] Failed to create user {user_data['employee_id']}: {e}")
    
    print(f"\n[OK] Demo user setup completed. Created: {created_count}/5")
    return created_count

def show_data_summary():
    """Show summary of loaded data."""
    print("\n" + "=" * 40)
    print("Data Summary")
    print("=" * 40)
    
    try:
        from flask import Flask
        from backend.models import db, ErrorLog
        from config.settings import config
        from sqlalchemy import func
        
        app = Flask(__name__)
        app.config.from_object(config['development'])
        db.init_app(app)
        
        with app.app_context():
            # Basic statistics
            total_logs = ErrorLog.query.count()
            teams = db.session.query(ErrorLog.TeamName).distinct().count()
            modules = db.session.query(ErrorLog.Module).distinct().count()
            solved_count = ErrorLog.query.filter_by(SolutionPossible=True).count()
            
            print(f"Total Error Logs: {total_logs}")
            print(f"Unique Teams: {teams}")
            print(f"Unique Modules: {modules}")
            print(f"Solutions Available: {solved_count}")
            print(f"Pending Issues: {total_logs - solved_count}")
            
            # Team distribution
            print(f"\nTeam Distribution:")
            team_stats = db.session.query(
                ErrorLog.TeamName,
                func.count(ErrorLog.Cr_ID).label('count'),
                func.sum(func.cast(ErrorLog.SolutionPossible, db.Integer)).label('solved')
            ).group_by(ErrorLog.TeamName).order_by(func.count(ErrorLog.Cr_ID).desc()).all()
            
            for team, count, solved in team_stats:
                print(f"   {team:15} : {count:2d} logs ({solved or 0} with solutions)")
            
            # Severity distribution
            print(f"\nSeverity Distribution:")
            severity_stats = db.session.query(
                ErrorLog.Severity,
                func.count(ErrorLog.Cr_ID).label('count')
            ).group_by(ErrorLog.Severity).order_by(func.count(ErrorLog.Cr_ID).desc()).all()
            
            for severity, count in severity_stats:
                print(f"   {severity.capitalize():10} : {count:2d} logs")
            
            # Environment distribution
            print(f"\nEnvironment Distribution:")
            env_stats = db.session.query(
                ErrorLog.Environment,
                func.count(ErrorLog.Cr_ID).label('count')
            ).group_by(ErrorLog.Environment).order_by(func.count(ErrorLog.Cr_ID).desc()).all()
            
            for env, count in env_stats:
                print(f"   {env.capitalize():10} : {count:2d} logs")
            
            return True
            
    except Exception as e:
        print(f"[ERROR] Failed to generate summary: {e}")
        return False

def main():
    """Main function to load sample data."""
    print("BugSeek Sample Data Loader")
    print("This script will populate your database with realistic sample data and demo users")
    print()
    
    # Load sample data
    added_count = load_sample_data()
    
    if added_count == 0:
        print("\n[ERROR] No sample data was loaded!")
        return False
    
    # Show summary
    if not show_data_summary():
        print("\n[WARN] Could not generate data summary")
    
    print("\n" + "=" * 60)
    print("SAMPLE DATA LOADING COMPLETE")
    print("=" * 60)
    print(f"[SUCCESS] Loaded {added_count} sample error logs!")
    print("\nDemo users available for login:")
    print("• admin / admin123 (System Administrator)")
    print("• developer / dev123 (Developer User)")
    print("• testuser / test123 (Test User)")
    print("• hackathon / hackathon2025 (Hackathon Participant)")
    print("• demo / demo123 (Demo User)")
    print("\nNext steps:")
    print("1. Run: python 4_view_database.py (to explore the data)")
    print("2. Start the application: python run.py")
    print("3. Open: http://localhost:8080")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n[ERROR] Sample data loading failed! Please check the errors above.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] Sample data is ready for use!")
        sys.exit(0)
