#!/usr/bin/env python3
"""
BugSeek Database Initialization Script
Creates the database with proper schema and populates it with 10 sample entries.
"""

import os
import sys
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from flask import Flask
from backend.models import db, ErrorLog, User, create_tables
from backend.auth_service import AuthenticationService
from config.settings import config

def init_database():
    """Initialize the BugSeek database with proper schema."""
    print("🔄 Initializing BugSeek Database...")
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configure the app
    app.config.from_object(config['development'])
    
    # Ensure the database URL is set
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bugseek.db'
    
    print(f"📊 Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Initialize SQLAlchemy with the app
    db.init_app(app)
    
    # Create application context and tables
    with app.app_context():
        try:
            # Drop all tables first (for clean slate)
            print("🗑️  Dropping existing tables...")
            db.drop_all()
            
            # Create all tables
            print("📋 Creating tables...")
            db.create_all()
            
            # Verify tables were created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"✅ Database schema created successfully!")
                print(f"📋 Created {len(tables)} table(s): {', '.join(tables)}")
                
                # Show detailed table info
                for table_name in tables:
                    columns = inspector.get_columns(table_name)
                    indexes = inspector.get_indexes(table_name)
                    print(f"   • {table_name}:")
                    print(f"     - Columns: {len(columns)}")
                    print(f"     - Indexes: {len(indexes)}")
                    for idx in indexes:
                        print(f"       * {idx['name']}: {idx['column_names']}")
                
                return app
            else:
                print("❌ No tables were created!")
                return None
                
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            import traceback
            traceback.print_exc()
            return None

def create_sample_data():
    """Create 10 sample error log entries with realistic data."""
    
    # Create varied timestamps over the past 30 days
    base_time = datetime.now()
    
    sample_logs = [
        {
            'TeamName': 'Frontend',
            'Module': 'Authentication',
            'Description': 'User login timeout after 30 seconds on mobile app',
            'Owner': 'john.doe@company.com',
            'LogFileName': 'auth_mobile_timeout_001.log',
            'ErrorName': 'LOGIN_TIMEOUT_MOBILE',
            'LogContent': '''2024-08-15 14:30:22 ERROR [AuthService] Connection timeout to authentication service
2024-08-15 14:30:22 ERROR [AuthService] Retrying connection attempt 1/3
2024-08-15 14:30:52 ERROR [AuthService] Authentication failed after 30s timeout
2024-08-15 14:30:52 ERROR [AuthService] User session terminated: timeout''',
            'FileSize': 2048,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.1, 0.3, 0.8, 0.2, 0.9], "confidence": 0.85}),
            'CreatedAt': base_time - timedelta(days=2, hours=5),
        },
        {
            'TeamName': 'Backend',
            'Module': 'Database',
            'Description': 'SQL query execution timeout on user statistics report',
            'Owner': 'jane.smith@company.com',
            'LogFileName': 'db_stats_query_slow.log',
            'ErrorName': 'SQL_QUERY_TIMEOUT',
            'LogContent': '''2024-08-20 09:15:33 WARNING [DatabaseManager] Query execution time: 45.2 seconds
2024-08-20 09:15:33 WARNING [DatabaseManager] Query: SELECT * FROM users JOIN logs ON...
2024-08-20 09:16:18 ERROR [DatabaseManager] Query timeout after 60 seconds
2024-08-20 09:16:18 ERROR [DatabaseManager] Connection pool exhausted''',
            'FileSize': 1536,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.7, 0.1, 0.4, 0.8, 0.3], "confidence": 0.92}),
            'CreatedAt': base_time - timedelta(days=5, hours=2),
        },
        {
            'TeamName': 'API',
            'Module': 'Payment',
            'Description': 'Payment gateway returning HTTP 500 for credit card transactions',
            'Owner': 'mike.wilson@company.com',
            'LogFileName': 'payment_gateway_500.log',
            'ErrorName': 'PAYMENT_GATEWAY_ERROR',
            'LogContent': '''2024-08-22 16:45:10 ERROR [PaymentService] HTTP 500 from payment gateway
2024-08-22 16:45:10 ERROR [PaymentService] Response: {"error": "Internal server error"}
2024-08-22 16:45:10 ERROR [PaymentService] Transaction ID: TXN_789456123
2024-08-22 16:45:10 ERROR [PaymentService] Card ending in ****1234 declined''',
            'FileSize': 1200,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.3, 0.9, 0.2, 0.6, 0.7], "confidence": 0.78}),
            'CreatedAt': base_time - timedelta(days=1, hours=8),
        },
        {
            'TeamName': 'DevOps',
            'Module': 'Deployment',
            'Description': 'Docker container failing to start on production server',
            'Owner': 'sarah.jones@company.com',
            'LogFileName': 'docker_startup_fail.log',
            'ErrorName': 'CONTAINER_START_FAILURE',
            'LogContent': '''2024-08-23 10:20:15 ERROR [Docker] Container bugseek_backend failed to start
2024-08-23 10:20:15 ERROR [Docker] Exit code: 125
2024-08-23 10:20:15 ERROR [Docker] Port 5000 already in use
2024-08-23 10:20:15 ERROR [Docker] Health check failed: connection refused''',
            'FileSize': 980,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.5, 0.4, 0.9, 0.1, 0.8], "confidence": 0.88}),
            'CreatedAt': base_time - timedelta(hours=12),
        },
        {
            'TeamName': 'Frontend',
            'Module': 'Dashboard',
            'Description': 'Chart rendering failure when loading large datasets',
            'Owner': 'alex.brown@company.com',
            'LogFileName': 'chart_render_error.log',
            'ErrorName': 'CHART_RENDER_MEMORY_ERROR',
            'LogContent': '''2024-08-21 13:25:44 ERROR [ChartComponent] Out of memory rendering 50000+ data points
2024-08-21 13:25:44 ERROR [ChartComponent] Canvas allocation failed
2024-08-21 13:25:44 ERROR [ChartComponent] Browser memory usage: 1.8GB
2024-08-21 13:25:44 ERROR [ChartComponent] Fallback to table view activated''',
            'FileSize': 1856,
            'SolutionPossible': False,
            'Embedding': json.dumps({"vector": [0.2, 0.6, 0.3, 0.9, 0.4], "confidence": 0.71}),
            'CreatedAt': base_time - timedelta(days=3, hours=6),
        },
        {
            'TeamName': 'Backend',
            'Module': 'FileUpload',
            'Description': 'Large file uploads failing with connection reset',
            'Owner': 'david.lee@company.com',
            'LogFileName': 'file_upload_connection_reset.log',
            'ErrorName': 'UPLOAD_CONNECTION_RESET',
            'LogContent': '''2024-08-19 11:40:12 ERROR [UploadService] Connection reset by peer during upload
2024-08-19 11:40:12 ERROR [UploadService] File: large_dataset.csv (450MB)
2024-08-19 11:40:12 ERROR [UploadService] Bytes uploaded: 234,567,890 / 472,186,432
2024-08-19 11:40:12 ERROR [UploadService] Retry attempt 3/3 failed''',
            'FileSize': 3072,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.8, 0.2, 0.7, 0.4, 0.6], "confidence": 0.83}),
            'CreatedAt': base_time - timedelta(days=7, hours=3),
        },
        {
            'TeamName': 'QA',
            'Module': 'Testing',
            'Description': 'Automated test suite failing on new build deployment',
            'Owner': 'lisa.garcia@company.com',
            'LogFileName': 'test_suite_failure.log',
            'ErrorName': 'AUTOMATED_TEST_FAILURE',
            'LogContent': '''2024-08-18 08:15:30 ERROR [TestRunner] 15 out of 234 tests failed
2024-08-18 08:15:30 ERROR [TestRunner] Selenium WebDriver timeout on login test
2024-08-18 08:15:30 ERROR [TestRunner] API endpoint /api/v1/users returning 404
2024-08-18 08:15:30 ERROR [TestRunner] Database seed data missing for test environment''',
            'FileSize': 4096,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.4, 0.7, 0.1, 0.5, 0.9], "confidence": 0.76}),
            'CreatedAt': base_time - timedelta(days=8, hours=10),
        },
        {
            'TeamName': 'API',
            'Module': 'RateLimiting',
            'Description': 'Rate limiting not working properly for high-traffic endpoints',
            'Owner': 'tom.martin@company.com',
            'LogFileName': 'rate_limit_bypass.log',
            'ErrorName': 'RATE_LIMIT_BYPASS',
            'LogContent': '''2024-08-17 19:22:18 WARNING [RateLimiter] Client IP 192.168.1.100 exceeded 1000 req/min
2024-08-17 19:22:18 ERROR [RateLimiter] Rate limit check failed for endpoint /api/v1/search
2024-08-17 19:22:18 ERROR [RateLimiter] Redis connection timeout during rate limit check
2024-08-17 19:22:18 ERROR [RateLimiter] Allowing request through due to limiter failure''',
            'FileSize': 2560,
            'SolutionPossible': False,
            'Embedding': json.dumps({"vector": [0.6, 0.3, 0.8, 0.7, 0.2], "confidence": 0.69}),
            'CreatedAt': base_time - timedelta(days=10, hours=7),
        },
        {
            'TeamName': 'Security',
            'Module': 'Authentication',
            'Description': 'Suspicious login attempts from multiple IP addresses',
            'Owner': 'emma.davis@company.com',
            'LogFileName': 'suspicious_login_attempts.log',
            'ErrorName': 'SUSPICIOUS_LOGIN_PATTERN',
            'LogContent': '''2024-08-16 02:33:45 WARNING [SecurityMonitor] 47 failed login attempts for user admin@company.com
2024-08-16 02:33:45 WARNING [SecurityMonitor] Source IPs: 185.220.101.*, 198.51.100.*
2024-08-16 02:33:45 ERROR [SecurityMonitor] Account locked due to suspicious activity
2024-08-16 02:33:45 ERROR [SecurityMonitor] Possible brute force attack detected''',
            'FileSize': 1728,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.9, 0.8, 0.6, 0.3, 0.5], "confidence": 0.94}),
            'CreatedAt': base_time - timedelta(days=15, hours=18),
        },
        {
            'TeamName': 'Infrastructure',
            'Module': 'Monitoring',
            'Description': 'Disk space alert triggered on main database server',
            'Owner': 'chris.wilson@company.com',
            'LogFileName': 'disk_space_alert.log',
            'ErrorName': 'DISK_SPACE_CRITICAL',
            'LogContent': '''2024-08-14 23:55:12 CRITICAL [DiskMonitor] Disk usage on /var/lib/mysql: 94%
2024-08-14 23:55:12 CRITICAL [DiskMonitor] Available space: 2.3GB of 40GB
2024-08-14 23:55:12 CRITICAL [DiskMonitor] Log rotation failed - insufficient space
2024-08-14 23:55:12 CRITICAL [DiskMonitor] Database backup cancelled due to space constraints''',
            'FileSize': 896,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.7, 0.5, 0.9, 0.8, 0.1], "confidence": 0.91}),
            'CreatedAt': base_time - timedelta(days=20, hours=4),
        },
        # Additional 20 realistic sample entries
        {
            'TeamName': 'Mobile',
            'Module': 'Push Notifications',
            'Description': 'FCM push notifications failing to deliver on Android devices',
            'Owner': 'maria.rodriguez@company.com',
            'LogFileName': 'fcm_delivery_failure.log',
            'ErrorName': 'PUSH_NOTIFICATION_FAILURE',
            'LogContent': '''2024-08-13 11:22:33 ERROR [FCMService] Failed to send notification to token: eJ8x9K2mN...
2024-08-13 11:22:33 ERROR [FCMService] Response: InvalidRegistration
2024-08-13 11:22:33 ERROR [FCMService] Batch size: 1500 notifications
2024-08-13 11:22:33 ERROR [FCMService] Success rate: 45% (675/1500)''',
            'FileSize': 2240,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.4, 0.8, 0.3, 0.7, 0.6], "confidence": 0.84}),
            'CreatedAt': base_time - timedelta(days=22, hours=12),
        },
        {
            'TeamName': 'Data Science',
            'Module': 'ML Pipeline',
            'Description': 'Machine learning model training job stuck in pending state',
            'Owner': 'dr.alan.turing@company.com',
            'LogFileName': 'ml_training_stuck.log',
            'ErrorName': 'ML_TRAINING_TIMEOUT',
            'LogContent': '''2024-08-12 16:30:45 WARNING [MLPipeline] Training job ID: ml_job_789123 pending for 4 hours
2024-08-12 16:30:45 ERROR [MLPipeline] GPU allocation failed: insufficient resources
2024-08-12 16:30:45 ERROR [MLPipeline] Dataset size: 2.8TB, Memory required: 64GB
2024-08-12 16:30:45 ERROR [MLPipeline] Queue position: 15/20''',
            'FileSize': 3584,
            'SolutionPossible': False,
            'Embedding': json.dumps({"vector": [0.9, 0.2, 0.8, 0.1, 0.7], "confidence": 0.77}),
            'CreatedAt': base_time - timedelta(days=25, hours=8),
        },
        {
            'TeamName': 'Frontend',
            'Module': 'Search',
            'Description': 'Search autocomplete showing no results for valid queries',
            'Owner': 'lucy.chen@company.com',
            'LogFileName': 'search_autocomplete_empty.log',
            'ErrorName': 'SEARCH_AUTOCOMPLETE_EMPTY',
            'LogContent': '''2024-08-11 09:45:12 ERROR [SearchComponent] Autocomplete returned empty results
2024-08-11 09:45:12 ERROR [SearchComponent] Query: "machine learning"
2024-08-11 09:45:12 ERROR [SearchComponent] Elasticsearch response time: 8.2s
2024-08-11 09:45:12 ERROR [SearchComponent] Index status: yellow''',
            'FileSize': 1344,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.3, 0.6, 0.4, 0.8, 0.5], "confidence": 0.82}),
            'CreatedAt': base_time - timedelta(days=28, hours=14),
        },
        {
            'TeamName': 'Backend',
            'Module': 'Caching',
            'Description': 'Redis cache cluster experiencing high memory usage and evictions',
            'Owner': 'redis.admin@company.com',
            'LogFileName': 'redis_memory_pressure.log',
            'ErrorName': 'CACHE_MEMORY_PRESSURE',
            'LogContent': '''2024-08-10 21:18:44 WARNING [RedisCluster] Memory usage: 14.2GB / 16GB (89%)
2024-08-10 21:18:44 ERROR [RedisCluster] Evicted keys in last hour: 125,430
2024-08-10 21:18:44 ERROR [RedisCluster] Hit ratio dropped to 67%
2024-08-10 21:18:44 CRITICAL [RedisCluster] OOM prevention triggered''',
            'FileSize': 4096,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.8, 0.4, 0.9, 0.2, 0.6], "confidence": 0.89}),
            'CreatedAt': base_time - timedelta(days=30, hours=2),
        },
        {
            'TeamName': 'DevOps',
            'Module': 'CI/CD',
            'Description': 'Docker build failing due to network timeout during dependency installation',
            'Owner': 'devops.lead@company.com',
            'LogFileName': 'docker_build_timeout.log',
            'ErrorName': 'DOCKER_BUILD_NETWORK_TIMEOUT',
            'LogContent': '''2024-08-09 15:20:30 ERROR [DockerBuild] Step 5/12: RUN npm install
2024-08-09 15:25:30 ERROR [DockerBuild] Network timeout after 300 seconds
2024-08-09 15:25:30 ERROR [DockerBuild] Failed to download: react@18.2.0
2024-08-09 15:25:30 ERROR [DockerBuild] Build terminated with exit code 124''',
            'FileSize': 2048,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.6, 0.7, 0.3, 0.8, 0.4], "confidence": 0.86}),
            'CreatedAt': base_time - timedelta(days=31, hours=9),
        },
        {
            'TeamName': 'API',
            'Module': 'User Management',
            'Description': 'User profile update endpoint returning 422 validation errors',
            'Owner': 'api.team.lead@company.com',
            'LogFileName': 'profile_update_validation.log',
            'ErrorName': 'PROFILE_UPDATE_VALIDATION_ERROR',
            'LogContent': '''2024-08-08 12:33:18 ERROR [UserController] Validation failed for user ID: 123456
2024-08-08 12:33:18 ERROR [UserController] Field: email, Error: invalid format
2024-08-08 12:33:18 ERROR [UserController] Field: phone, Error: country code missing
2024-08-08 12:33:18 ERROR [UserController] Request payload size: 2.1KB''',
            'FileSize': 1536,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.2, 0.9, 0.1, 0.7, 0.8], "confidence": 0.85}),
            'CreatedAt': base_time - timedelta(days=32, hours=16),
        },
        {
            'TeamName': 'Security',
            'Module': 'SSL/TLS',
            'Description': 'SSL certificate renewal failed for production domain',
            'Owner': 'security.ops@company.com',
            'LogFileName': 'ssl_renewal_failure.log',
            'ErrorName': 'SSL_CERT_RENEWAL_FAILED',
            'LogContent': '''2024-08-07 03:00:15 ERROR [CertBot] Challenge failed for domain: api.company.com
2024-08-07 03:00:15 ERROR [CertBot] DNS validation timeout after 60 seconds
2024-08-07 03:00:15 ERROR [CertBot] Current cert expires: 2024-08-15 03:00:00 UTC
2024-08-07 03:00:15 CRITICAL [CertBot] Manual intervention required''',
            'FileSize': 1024,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.9, 0.1, 0.8, 0.6, 0.3], "confidence": 0.93}),
            'CreatedAt': base_time - timedelta(days=33, hours=21),
        },
        {
            'TeamName': 'QA',
            'Module': 'Load Testing',
            'Description': 'Performance test showing degraded response times under high load',
            'Owner': 'qa.performance@company.com',
            'LogFileName': 'load_test_degradation.log',
            'ErrorName': 'PERFORMANCE_DEGRADATION',
            'LogContent': '''2024-08-06 14:45:22 WARNING [LoadTester] Average response time: 2.8s (target: <1s)
2024-08-06 14:45:22 ERROR [LoadTester] 95th percentile: 8.2s
2024-08-06 14:45:22 ERROR [LoadTester] Concurrent users: 500
2024-08-06 14:45:22 ERROR [LoadTester] Error rate: 12.4%''',
            'FileSize': 2816,
            'SolutionPossible': False,
            'Embedding': json.dumps({"vector": [0.5, 0.3, 0.7, 0.9, 0.2], "confidence": 0.73}),
            'CreatedAt': base_time - timedelta(days=35, hours=10),
        },
        {
            'TeamName': 'Mobile',
            'Module': 'Camera',
            'Description': 'iOS camera module crashing when accessing photo library',
            'Owner': 'ios.dev@company.com',
            'LogFileName': 'ios_camera_crash.log',
            'ErrorName': 'IOS_CAMERA_CRASH',
            'LogContent': '''2024-08-05 16:22:17 ERROR [CameraModule] NSInternalInconsistencyException
2024-08-05 16:22:17 ERROR [CameraModule] Reason: Invalid parameter not satisfying: asset != nil
2024-08-05 16:22:17 ERROR [CameraModule] Stack trace: 0x1045e8000 CameraViewController.swift:142
2024-08-05 16:22:17 FATAL [CameraModule] App terminated with SIGABRT''',
            'FileSize': 3200,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.4, 0.8, 0.2, 0.6, 0.9], "confidence": 0.81}),
            'CreatedAt': base_time - timedelta(days=36, hours=7),
        },
        {
            'TeamName': 'Data Science',
            'Module': 'ETL',
            'Description': 'Daily data pipeline failing during transformation stage',
            'Owner': 'data.engineer@company.com',
            'LogFileName': 'etl_transform_failure.log',
            'ErrorName': 'ETL_TRANSFORM_FAILURE',
            'LogContent': '''2024-08-04 04:15:33 ERROR [ETLPipeline] Transformation step 3/7 failed
2024-08-04 04:15:33 ERROR [ETLPipeline] Spark job: application_1691234567890_0123
2024-08-04 04:15:33 ERROR [ETLPipeline] OutOfMemoryError: Java heap space
2024-08-04 04:15:33 ERROR [ETLPipeline] Processed: 2.1M/5.8M records''',
            'FileSize': 4608,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.7, 0.2, 0.9, 0.4, 0.5], "confidence": 0.88}),
            'CreatedAt': base_time - timedelta(days=37, hours=20),
        },
        {
            'TeamName': 'Frontend',
            'Module': 'User Interface',
            'Description': 'React component state update causing infinite re-render loop',
            'Owner': 'react.dev@company.com',
            'LogFileName': 'react_infinite_render.log',
            'ErrorName': 'REACT_INFINITE_RENDER',
            'LogContent': '''2024-08-03 10:30:44 ERROR [ReactProfiler] Component UserDashboard re-rendered 847 times
2024-08-03 10:30:44 ERROR [ReactProfiler] useEffect dependency array issue detected
2024-08-03 10:30:44 ERROR [ReactProfiler] Memory usage increased by 234MB
2024-08-03 10:30:44 WARNING [ReactProfiler] Browser tab becoming unresponsive''',
            'FileSize': 1792,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.3, 0.7, 0.5, 0.8, 0.1], "confidence": 0.79}),
            'CreatedAt': base_time - timedelta(days=38, hours=13),
        },
        {
            'TeamName': 'Backend',
            'Module': 'Message Queue',
            'Description': 'RabbitMQ queue buildup causing memory exhaustion on broker',
            'Owner': 'messaging.team@company.com',
            'LogFileName': 'rabbitmq_queue_buildup.log',
            'ErrorName': 'MESSAGE_QUEUE_BUILDUP',
            'LogContent': '''2024-08-02 18:45:12 WARNING [RabbitMQ] Queue email_notifications: 45,892 messages
2024-08-02 18:45:12 ERROR [RabbitMQ] Consumer lag: 2.3 hours
2024-08-02 18:45:12 ERROR [RabbitMQ] Memory usage: 7.8GB / 8GB (97.5%)
2024-08-02 18:45:12 CRITICAL [RabbitMQ] Flow control activated''',
            'FileSize': 2560,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.8, 0.6, 0.4, 0.7, 0.3], "confidence": 0.87}),
            'CreatedAt': base_time - timedelta(days=39, hours=5),
        },
        {
            'TeamName': 'Infrastructure',
            'Module': 'Load Balancer',
            'Description': 'HAProxy load balancer dropping connections during peak traffic',
            'Owner': 'infrastructure.ops@company.com',
            'LogFileName': 'haproxy_connection_drops.log',
            'ErrorName': 'LOAD_BALANCER_CONNECTION_DROP',
            'LogContent': '''2024-08-01 19:30:25 ERROR [HAProxy] Server backend1: 504 Gateway Timeout
2024-08-01 19:30:25 ERROR [HAProxy] Connection drops: 1,247 in last 5 minutes
2024-08-01 19:30:25 ERROR [HAProxy] Active connections: 8,924 / 10,000
2024-08-01 19:30:25 WARNING [HAProxy] Backend server response time: 15.2s''',
            'FileSize': 3072,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.6, 0.8, 0.7, 0.3, 0.4], "confidence": 0.90}),
            'CreatedAt': base_time - timedelta(days=40, hours=11),
        },
        {
            'TeamName': 'API',
            'Module': 'GraphQL',
            'Description': 'GraphQL resolver causing N+1 query problem with user relationships',
            'Owner': 'graphql.dev@company.com',
            'LogFileName': 'graphql_n_plus_one.log',
            'ErrorName': 'GRAPHQL_N_PLUS_ONE_QUERIES',
            'LogContent': '''2024-07-31 13:15:40 WARNING [GraphQLResolver] Query depth: 8 levels
2024-07-31 13:15:40 ERROR [GraphQLResolver] Database queries executed: 1,547
2024-07-31 13:15:40 ERROR [GraphQLResolver] Query duration: 23.7 seconds
2024-07-31 13:15:40 ERROR [GraphQLResolver] DataLoader not implemented for User.posts field''',
            'FileSize': 1920,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.5, 0.4, 0.8, 0.9, 0.2], "confidence": 0.83}),
            'CreatedAt': base_time - timedelta(days=41, hours=18),
        },
        {
            'TeamName': 'Security',
            'Module': 'WAF',
            'Description': 'Web Application Firewall blocking legitimate API requests',
            'Owner': 'security.waf@company.com',
            'LogFileName': 'waf_false_positive.log',
            'ErrorName': 'WAF_FALSE_POSITIVE',
            'LogContent': '''2024-07-30 11:22:15 BLOCKED [WAF] Rule ID: OWASP_CRS_941_110
2024-07-30 11:22:15 BLOCKED [WAF] Request: POST /api/v1/users/search
2024-07-30 11:22:15 BLOCKED [WAF] Reason: SQL injection attempt detected
2024-07-30 11:22:15 INFO [WAF] Client IP: 203.0.113.45 (whitelisted partner)''',
            'FileSize': 1408,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.9, 0.3, 0.6, 0.5, 0.7], "confidence": 0.86}),
            'CreatedAt': base_time - timedelta(days=42, hours=6),
        },
        {
            'TeamName': 'Mobile',
            'Module': 'Offline Sync',
            'Description': 'Mobile app failing to sync data when network connectivity is restored',
            'Owner': 'mobile.sync@company.com',
            'LogFileName': 'mobile_sync_failure.log',
            'ErrorName': 'OFFLINE_SYNC_FAILURE',
            'LogContent': '''2024-07-29 08:45:33 ERROR [SyncManager] Sync attempt failed after 3 retries
2024-07-29 08:45:33 ERROR [SyncManager] Pending operations: 127
2024-07-29 08:45:33 ERROR [SyncManager] Conflict resolution failed for 23 records
2024-07-29 08:45:33 ERROR [SyncManager] Last successful sync: 2024-07-28 14:22:10''',
            'FileSize': 2304,
            'SolutionPossible': False,
            'Embedding': json.dumps({"vector": [0.4, 0.6, 0.3, 0.8, 0.7], "confidence": 0.75}),
            'CreatedAt': base_time - timedelta(days=43, hours=15),
        },
        {
            'TeamName': 'Data Science',
            'Module': 'Recommendation Engine',
            'Description': 'Recommendation algorithm returning biased results for certain user segments',
            'Owner': 'ml.ethics@company.com',
            'LogFileName': 'recommendation_bias.log',
            'ErrorName': 'RECOMMENDATION_BIAS_DETECTED',
            'LogContent': '''2024-07-28 20:12:55 WARNING [RecEngine] Bias detected in demographic group: age 18-25
2024-07-28 20:12:55 ERROR [RecEngine] Recommendation diversity score: 0.23 (target: >0.7)
2024-07-28 20:12:55 ERROR [RecEngine] Filter bubble detected: 89% similarity in recommendations
2024-07-28 20:12:55 ALERT [RecEngine] Fairness metric threshold breached''',
            'FileSize': 2688,
            'SolutionPossible': False,
            'Embedding': json.dumps({"vector": [0.7, 0.9, 0.2, 0.4, 0.6], "confidence": 0.72}),
            'CreatedAt': base_time - timedelta(days=44, hours=3),
        },
        {
            'TeamName': 'Frontend',
            'Module': 'WebSocket',
            'Description': 'Real-time chat feature experiencing frequent disconnections',
            'Owner': 'frontend.realtime@company.com',
            'LogFileName': 'websocket_disconnections.log',
            'ErrorName': 'WEBSOCKET_FREQUENT_DISCONNECT',
            'LogContent': '''2024-07-27 16:33:22 ERROR [WebSocketClient] Connection closed unexpectedly
2024-07-27 16:33:22 ERROR [WebSocketClient] Close code: 1006 (abnormal closure)
2024-07-27 16:33:22 ERROR [WebSocketClient] Reconnection attempts: 15/15 failed
2024-07-27 16:33:22 ERROR [WebSocketClient] Average session duration: 45 seconds''',
            'FileSize': 1664,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.2, 0.8, 0.6, 0.7, 0.4], "confidence": 0.80}),
            'CreatedAt': base_time - timedelta(days=45, hours=22),
        },
        {
            'TeamName': 'Backend',
            'Module': 'Microservices',
            'Description': 'Service mesh experiencing cascading failures across multiple services',
            'Owner': 'microservices.lead@company.com',
            'LogFileName': 'service_mesh_cascade.log',
            'ErrorName': 'SERVICE_MESH_CASCADE_FAILURE',
            'LogContent': '''2024-07-26 22:15:18 ERROR [ServiceMesh] Circuit breaker opened: user-service
2024-07-26 22:15:18 ERROR [ServiceMesh] Downstream failure: payment-service (timeout)
2024-07-26 22:15:18 CRITICAL [ServiceMesh] 7 services affected by cascade failure
2024-07-26 22:15:18 ERROR [ServiceMesh] Recovery ETA: 15-20 minutes''',
            'FileSize': 3840,
            'SolutionPossible': True,
            'Embedding': json.dumps({"vector": [0.8, 0.1, 0.9, 0.6, 0.3], "confidence": 0.91}),
            'CreatedAt': base_time - timedelta(days=46, hours=1),
        }
    ]
    
    return sample_logs

def populate_database(app):
    """Populate the database with sample data."""
    print("\n🔄 Adding sample data to database...")
    
    sample_data = create_sample_data()
    
    with app.app_context():
        try:
            # Clear existing data
            ErrorLog.query.delete()
            db.session.commit()
            
            added_count = 0
            for log_data in sample_data:
                # Create ErrorLog instance with updated schema
                error_log = ErrorLog(
                    TeamName=log_data['TeamName'],
                    Module=log_data['Module'],
                    Description=log_data['Description'],
                    Owner=log_data['Owner'],
                    LogFileName=log_data['LogFileName'],
                    ErrorName=log_data['ErrorName'],
                    LogContentPreview=log_data['LogContent'][:2048] + '...' if len(log_data['LogContent']) > 2048 else log_data['LogContent'],  # Store as preview
                    SolutionPossible=log_data['SolutionPossible'],
                    Embedding=log_data['Embedding'],
                    CreatedAt=log_data['CreatedAt'],
                    # Set default severity and environment based on content analysis
                    Severity='high' if 'CRITICAL' in log_data['LogContent'] or 'FATAL' in log_data['LogContent'] 
                           else 'medium' if 'ERROR' in log_data['LogContent'] 
                           else 'low',
                    Environment='prod' if 'production' in log_data['Description'].lower() 
                              else 'staging' if 'staging' in log_data['Description'].lower() 
                              else 'dev' if 'development' in log_data['Description'].lower() or 'test' in log_data['Description'].lower() 
                              else 'unknown'
                )
                
                db.session.add(error_log)
                added_count += 1
            
            # Commit all changes
            db.session.commit()
            
            print(f"✅ Successfully added {added_count} sample error logs!")
            
            # Show summary statistics
            print("\n📊 Database Summary:")
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
            print(f"❌ Error populating database: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

def verify_database():
    """Verify the database is properly set up and connected."""
    print("\n🔍 Verifying database setup...")
    
    try:
        from db_connection import DatabaseConnection
        db_conn = DatabaseConnection()
        
        if db_conn.connect():
            print("✅ Database connection successful!")
            
            tables = db_conn.get_tables()
            print(f"📋 Found {len(tables)} tables: {', '.join(tables)}")
            
            for table in tables:
                count = db_conn.get_table_count(table)
                print(f"   • {table}: {count} records")
            
            db_conn.close()
            return True
        else:
            print("❌ Database connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False

def create_demo_users(app):
    """Create demo users for authentication."""
    print("\n👥 Creating demo users...")
    
    # Demo users to create
    demo_users = [
        {
            'EmployeeID': 'admin',
            'FullName': 'System Administrator',
            'Email': 'admin@bugseek.com',
            'Password': 'admin123',
            'Department': 'IT',
            'TeamName': 'System Administration',
            'JobTitle': 'Administrator',
            'IsActive': True,
            'IsAdmin': True
        },
        {
            'EmployeeID': 'developer',
            'FullName': 'John Developer',
            'Email': 'developer@bugseek.com',
            'Password': 'dev123',
            'Department': 'Engineering',
            'TeamName': 'Backend Development',
            'JobTitle': 'Senior Developer',
            'IsActive': True,
            'IsAdmin': False
        },
        {
            'EmployeeID': 'testuser',
            'FullName': 'Jane Tester',
            'Email': 'testuser@bugseek.com',
            'Password': 'test123',
            'Department': 'Quality Assurance',
            'TeamName': 'QA Team',
            'JobTitle': 'QA Engineer',
            'IsActive': True,
            'IsAdmin': False
        },
        {
            'EmployeeID': 'hackathon',
            'FullName': 'Hackathon Participant',
            'Email': 'hackathon@bugseek.com',
            'Password': 'hackathon2025',
            'Department': 'Engineering',
            'TeamName': 'Hackathon Team',
            'JobTitle': 'Participant',
            'IsActive': True,
            'IsAdmin': False
        },
        {
            'EmployeeID': 'demo',
            'FullName': 'Demo User',
            'Email': 'demo@bugseek.com',
            'Password': 'demo123',
            'Department': 'Sales',
            'TeamName': 'Demo Team',
            'JobTitle': 'Demo Specialist',
            'IsActive': True,
            'IsAdmin': False
        }
    ]
    
    with app.app_context():
        try:
            # Clear existing users first
            User.query.delete()
            db.session.commit()
            
            created_users = []
            
            for user_data in demo_users:
                print(f"   Creating user: {user_data['EmployeeID']}")
                
                # Create the user using AuthenticationService
                result = AuthenticationService.create_user(user_data)
                
                if result['success']:
                    print(f"   ✅ User {user_data['EmployeeID']} created successfully!")
                    created_users.append(user_data['EmployeeID'])
                else:
                    print(f"   ❌ Failed to create user {user_data['EmployeeID']}: {result['message']}")
            
            if created_users:
                print(f"\n✅ Successfully created {len(created_users)} demo users!")
                
                # Show user summary
                print("\n👤 Demo User Credentials:")
                for user_data in demo_users:
                    role = "Admin" if user_data['IsAdmin'] else "User"
                    print(f"   • {user_data['EmployeeID']} / {user_data['Password']} ({role} - {user_data['FullName']})")
            else:
                print("\n⚠️  No users were created")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating demo users: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

def main():
    """Main initialization function."""
    print("🔍 BugSeek Database Initializer")
    print("=" * 60)
    
    # Step 1: Initialize database schema
    app = init_database()
    if not app:
        print("❌ Failed to initialize database schema!")
        return False
    
    # Step 2: Create demo users
    users_success = create_demo_users(app)
    if not users_success:
        print("❌ Failed to create demo users!")
        return False
    
    # Step 3: Populate with sample data
    success = populate_database(app)
    if not success:
        print("❌ Failed to populate database!")
        return False
    
    # Step 4: Verify everything is working
    verify_success = verify_database()
    if not verify_success:
        print("❌ Database verification failed!")
        return False
    
    print("\n🎉 Database initialization completed successfully!")
    print("\n🔑 You can now login with these credentials:")
    print("   • admin / admin123 (Administrator)")
    print("   • developer / dev123 (Developer)")
    print("   • demo / demo123 (Demo User)")
    print("   • testuser / test123 (QA Tester)")
    print("   • hackathon / hackathon2025 (Hackathon User)")
    print("\n📋 Next steps:")
    print("   1. Test with: python db_connection.py")
    print("   2. Use CLI: python db_viewer.py")
    print("   3. Start backend: python run.py --backend")
    print("   4. Start frontend: python run.py --frontend")
    print("   5. Login with demo credentials above")
    
    return True

if __name__ == "__main__":
    main()
