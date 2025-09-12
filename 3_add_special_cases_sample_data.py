#!/usr/bin/env python3
"""
3_add_special_cases_sample_data.py
Add special cases and edge cases sample data to BugSeek database
"""

import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def create_special_cases_data():
    """Create special cases and edge cases sample data for testing."""
    base_time = datetime.now()
    
    special_cases = [
        # Edge Case 1: Very long error messages
        {
            'TeamName': 'Performance',
            'Module': 'Memory Management',
            'Description': 'Memory leak causing gradual performance degradation over 72 hours',
            'Owner': 'performance.team@company.com',
            'LogFileName': 'memory_leak_gradual_72h.log',
            'ErrorName': 'MEMORY_LEAK_GRADUAL_DEGRADATION',
            'LogContent': '''2025-09-01 00:00:15 INFO [MemoryMonitor] Initial memory usage: 2.1GB
2025-09-01 06:15:23 WARNING [MemoryMonitor] Memory usage increased to 3.8GB (+80.9%)
2025-09-01 12:30:45 WARNING [MemoryMonitor] Memory usage increased to 5.2GB (+36.8%)
2025-09-01 18:45:12 ERROR [MemoryMonitor] Memory usage reached 7.1GB - approaching limit
2025-09-02 00:15:33 ERROR [MemoryMonitor] Memory usage: 8.9GB - performance severely degraded
2025-09-02 06:30:22 CRITICAL [MemoryMonitor] Memory usage: 11.2GB - swap file activated
2025-09-02 12:45:18 CRITICAL [MemoryMonitor] Memory usage: 13.8GB - system becoming unresponsive
2025-09-02 18:22:45 FATAL [MemoryMonitor] Memory usage: 15.9GB - out of memory imminent
2025-09-03 01:12:33 FATAL [MemoryMonitor] System crashed due to memory exhaustion - automatic restart initiated
2025-09-03 01:15:22 INFO [MemoryMonitor] System restarted - memory usage reset to 2.1GB''',
            'FileSize': 8192,
            'SolutionPossible': True,
            'Severity': 'critical',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=20, hours=15)
        },
        
        # Edge Case 2: Unicode and special characters
        {
            'TeamName': 'Internationalization',
            'Module': 'Text Processing',
            'Description': 'Unicode encoding issues with multilingual user input causing crashes',
            'Owner': 'i18n.team@company.com',
            'LogFileName': 'unicode_encoding_crash.log',
            'ErrorName': 'UNICODE_ENCODING_ERROR',
            'LogContent': '''2025-08-25 14:22:18 ERROR [TextProcessor] Failed to process input: "Hello 世界! Здравствуй мир! こんにちは!"
2025-08-25 14:22:18 ERROR [TextProcessor] UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff
2025-08-25 14:22:18 ERROR [TextProcessor] Input contained mixed encodings: UTF-8, UTF-16, ISO-8859-1
2025-08-25 14:22:18 ERROR [TextProcessor] Special characters detected: €, ©, ™, ♥, ✓, ★, ✉
2025-08-25 14:22:18 ERROR [TextProcessor] Emoji processing failed: 🔥🚀💻🎯🌟🐛
2025-08-25 14:22:18 CRITICAL [TextProcessor] System unable to handle multilingual content
2025-08-25 14:22:18 FATAL [TextProcessor] Application terminated due to encoding mismatch''',
            'FileSize': 2560,
            'SolutionPossible': True,
            'Severity': 'high',
            'Environment': 'staging',
            'CreatedAt': base_time - timedelta(days=16, hours=3)
        },
        
        # Edge Case 3: Extremely high frequency errors
        {
            'TeamName': 'Rate Limiting',
            'Module': 'Request Processing',
            'Description': 'Rate limiter failing under extreme load - 50,000 requests per second',
            'Owner': 'scalability.team@company.com',
            'LogFileName': 'rate_limiter_extreme_load.log',
            'ErrorName': 'RATE_LIMITER_OVERLOAD',
            'LogContent': '''2025-08-20 16:45:00 WARNING [RateLimiter] Current RPS: 50,247 (limit: 10,000)
2025-08-20 16:45:01 ERROR [RateLimiter] Queue overflow: 45,892 requests pending
2025-08-20 16:45:02 ERROR [RateLimiter] Memory exhausted storing rate limit counters
2025-08-20 16:45:03 CRITICAL [RateLimiter] Circuit breaker activated - dropping all requests
2025-08-20 16:45:04 ERROR [RateLimiter] Redis connection pool exhausted (500/500)
2025-08-20 16:45:05 FATAL [RateLimiter] System unable to process any requests
2025-08-20 16:45:06 INFO [RateLimiter] Emergency shutdown initiated
[... 45,000+ similar entries in 60 seconds ...]
2025-08-20 16:46:00 INFO [RateLimiter] Load decreased to manageable levels: 8,234 RPS''',
            'FileSize': 15728640,  # 15MB log file
            'SolutionPossible': False,
            'Severity': 'critical',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=21, hours=7)
        },
        
        # Edge Case 4: Intermittent network issues
        {
            'TeamName': 'Network',
            'Module': 'Connection Management',
            'Description': 'Intermittent network failures causing random connection drops every 3-7 minutes',
            'Owner': 'network.reliability@company.com',
            'LogFileName': 'intermittent_network_drops.log',
            'ErrorName': 'INTERMITTENT_CONNECTION_DROP',
            'LogContent': '''2025-08-18 10:00:00 INFO [NetworkManager] Connection established: 192.168.1.100
2025-08-18 10:03:22 WARNING [NetworkManager] Latency spike detected: 2.3s (normal: 50ms)
2025-08-18 10:06:45 ERROR [NetworkManager] Connection lost unexpectedly - attempting reconnect
2025-08-18 10:06:47 INFO [NetworkManager] Connection restored: 192.168.1.100
2025-08-18 10:11:12 ERROR [NetworkManager] Connection lost unexpectedly - attempting reconnect
2025-08-18 10:11:15 INFO [NetworkManager] Connection restored: 192.168.1.100
2025-08-18 10:15:33 WARNING [NetworkManager] Packet loss detected: 15% over last 60s
2025-08-18 10:18:44 ERROR [NetworkManager] Connection lost unexpectedly - attempting reconnect
2025-08-18 10:18:46 INFO [NetworkManager] Connection restored: 192.168.1.100
[Pattern repeats every 3-7 minutes for 8 hours]
2025-08-18 18:22:15 INFO [NetworkManager] Network stability restored - no drops in 2+ hours''',
            'FileSize': 12288,
            'SolutionPossible': True,
            'Severity': 'medium',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=23, hours=14)
        },
        
        # Edge Case 5: Null/Empty data handling
        {
            'TeamName': 'Data Validation',
            'Module': 'Input Sanitization',
            'Description': 'Null pointer exceptions when handling empty or malformed API requests',
            'Owner': 'data.validation@company.com',
            'LogFileName': 'null_data_handling.log',
            'ErrorName': 'NULL_DATA_EXCEPTION',
            'LogContent': '''2025-08-15 09:30:15 ERROR [APIValidator] Null pointer exception: request.body is null
2025-08-15 09:30:16 ERROR [APIValidator] Empty string validation failed: ""
2025-08-15 09:30:17 ERROR [APIValidator] Undefined field access: request.user.id = undefined
2025-08-15 09:30:18 ERROR [APIValidator] Zero-length array processing: data.items.length = 0
2025-08-15 09:30:19 ERROR [APIValidator] Missing required field: "timestamp" not found in payload
2025-08-15 09:30:20 ERROR [APIValidator] Malformed JSON: unexpected end of input
2025-08-15 09:30:21 ERROR [APIValidator] SQL injection attempt blocked: "'; DROP TABLE users; --"
2025-08-15 09:30:22 ERROR [APIValidator] XSS attempt blocked: "<script>alert('hack')</script>"
2025-08-15 09:30:23 CRITICAL [APIValidator] Multiple validation failures in single request''',
            'FileSize': 1920,
            'SolutionPossible': True,
            'Severity': 'high',
            'Environment': 'dev',
            'CreatedAt': base_time - timedelta(days=26, hours=20)
        },
        
        # Edge Case 6: Time zone and date issues
        {
            'TeamName': 'Global Operations',
            'Module': 'Time Management',
            'Description': 'Daylight saving time transition causing scheduling conflicts across time zones',
            'Owner': 'global.ops@company.com',
            'LogFileName': 'timezone_dst_conflict.log',
            'ErrorName': 'TIMEZONE_DST_CONFLICT',
            'LogContent': '''2025-03-10 01:59:59 INFO [Scheduler] Preparing for DST transition in 1 second
2025-03-10 03:00:00 WARNING [Scheduler] Clock jumped forward - 2:00:00 AM never occurred
2025-03-10 03:00:01 ERROR [Scheduler] Scheduled task missed: backup_job scheduled for 2:30 AM
2025-03-10 03:00:02 ERROR [Scheduler] Calendar conflict: meeting scheduled for non-existent time
2025-03-10 03:00:03 ERROR [Scheduler] Log timestamps inconsistent: previous=01:59:59, current=03:00:03
2025-03-10 03:00:04 WARNING [Scheduler] UTC offset changed from -05:00 to -04:00
2025-03-10 03:00:05 ERROR [Scheduler] Database query failed: WHERE timestamp BETWEEN '2:00' AND '3:00'
2025-03-10 03:00:06 CRITICAL [Scheduler] Multiple systems showing different times
2025-03-10 03:00:07 INFO [Scheduler] Initiating time synchronization across all services''',
            'FileSize': 2048,
            'SolutionPossible': True,
            'Severity': 'medium',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=30, hours=11)
        },
        
        # Edge Case 7: Concurrent access conflicts
        {
            'TeamName': 'Concurrency',
            'Module': 'Resource Management',
            'Description': 'Database deadlock from concurrent transactions accessing same records',
            'Owner': 'concurrency.team@company.com',
            'LogFileName': 'database_deadlock_concurrent.log',
            'ErrorName': 'DATABASE_DEADLOCK_CONCURRENT',
            'LogContent': '''2025-08-12 14:15:22 INFO [TransactionManager] Starting transaction T1: UPDATE users SET balance = balance - 100 WHERE id = 1001
2025-08-12 14:15:22 INFO [TransactionManager] Starting transaction T2: UPDATE accounts SET balance = balance + 100 WHERE id = 2001
2025-08-12 14:15:23 INFO [TransactionManager] T1 acquired lock on users.id=1001
2025-08-12 14:15:23 INFO [TransactionManager] T2 acquired lock on accounts.id=2001
2025-08-12 14:15:24 WARNING [TransactionManager] T1 waiting for lock on accounts.id=2001 (held by T2)
2025-08-12 14:15:24 WARNING [TransactionManager] T2 waiting for lock on users.id=1001 (held by T1)
2025-08-12 14:15:25 ERROR [TransactionManager] Deadlock detected: T1 ↔ T2
2025-08-12 14:15:25 ERROR [TransactionManager] Rolling back transaction T2 (victim)
2025-08-12 14:15:26 INFO [TransactionManager] T1 completed successfully
2025-08-12 14:15:26 INFO [TransactionManager] T2 will be retried in 100ms''',
            'FileSize': 1536,
            'SolutionPossible': True,
            'Severity': 'medium',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=29, hours=5)
        },
        
        # Edge Case 8: Resource exhaustion
        {
            'TeamName': 'System Resources',
            'Module': 'Resource Monitoring',
            'Description': 'System resources exhausted: CPU 100%, Memory 98%, Disk 95%, Network 90%',
            'Owner': 'system.monitoring@company.com',
            'LogFileName': 'resource_exhaustion_critical.log',
            'ErrorName': 'SYSTEM_RESOURCE_EXHAUSTION',
            'LogContent': '''2025-08-08 20:45:00 WARNING [ResourceMonitor] CPU usage: 85% (warning threshold)
2025-08-08 20:45:30 WARNING [ResourceMonitor] Memory usage: 92% (8GB of 16GB)
2025-08-08 20:46:00 ERROR [ResourceMonitor] CPU usage: 95% - system becoming unresponsive
2025-08-08 20:46:30 ERROR [ResourceMonitor] Memory usage: 98% - swap file heavily used
2025-08-08 20:47:00 CRITICAL [ResourceMonitor] CPU usage: 100% - multiple processes competing
2025-08-08 20:47:30 CRITICAL [ResourceMonitor] Disk I/O: 95% utilization - queue length: 47
2025-08-08 20:48:00 CRITICAL [ResourceMonitor] Network bandwidth: 90% of 1Gbps
2025-08-08 20:48:30 FATAL [ResourceMonitor] System load average: 15.73 (normal: <2.0)
2025-08-08 20:49:00 EMERGENCY [ResourceMonitor] Initiating emergency resource cleanup
2025-08-08 20:49:30 INFO [ResourceMonitor] Non-essential processes terminated
2025-08-08 20:50:00 INFO [ResourceMonitor] System resources stabilized - CPU: 45%, Memory: 78%''',
            'FileSize': 2304,
            'SolutionPossible': True,
            'Severity': 'critical',
            'Environment': 'prod',
            'CreatedAt': base_time - timedelta(days=33, hours=17)
        }
    ]
    
    return special_cases

def add_special_cases_data():
    """Add special cases and edge cases data to the database."""
    print("=" * 60)
    print("BugSeek Special Cases Data Loader")
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
            print("[INFO] Loading special cases and edge cases data...")
            
            # Get special cases data
            special_data = create_special_cases_data()
            print(f"[INFO] Prepared {len(special_data)} special case error logs")
            
            added_count = 0
            for i, log_data in enumerate(special_data, 1):
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
                        Embedding=json.dumps({"vector": [0.9, 0.1, 0.5, 0.7, 0.3], "confidence": 0.75})  # Different embedding for special cases
                    )
                    
                    db.session.add(error_log)
                    added_count += 1
                    print(f"   [{i:2d}] Added: {log_data['ErrorName']} ({log_data['TeamName']})")
                    
                except Exception as e:
                    print(f"   [ERROR] Failed to add special case {i}: {e}")
            
            # Commit all changes
            db.session.commit()
            
            print(f"\n[OK] Successfully added {added_count} special case error logs!")
            return added_count
            
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return 0
    except Exception as e:
        print(f"[ERROR] Failed to load special cases data: {e}")
        import traceback
        traceback.print_exc()
        return 0

def ensure_demo_users():
    """Ensure demo users exist for authentication."""
    print("\n" + "=" * 40)
    print("Ensuring Demo Users Exist")
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
    
    if created_count > 0:
        print(f"\n[OK] Created {created_count} new demo users")
    else:
        print(f"\n[OK] All demo users already exist")
    return created_count

def show_special_cases_summary():
    """Show summary of special cases data."""
    print("\n" + "=" * 40)
    print("Special Cases Summary")
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
            # Get special case error types
            special_error_types = [
                'MEMORY_LEAK_GRADUAL_DEGRADATION',
                'UNICODE_ENCODING_ERROR',
                'RATE_LIMITER_OVERLOAD', 
                'INTERMITTENT_CONNECTION_DROP',
                'NULL_DATA_EXCEPTION',
                'TIMEZONE_DST_CONFLICT',
                'DATABASE_DEADLOCK_CONCURRENT',
                'SYSTEM_RESOURCE_EXHAUSTION'
            ]
            
            special_cases = ErrorLog.query.filter(
                ErrorLog.ErrorName.in_(special_error_types)
            ).all()
            
            print(f"Special Cases Found: {len(special_cases)}")
            
            if special_cases:
                print("\nSpecial Case Types:")
                for case in special_cases:
                    print(f"   • {case.ErrorName}")
                    print(f"     Team: {case.TeamName}, Severity: {case.Severity}")
                    print(f"     Environment: {case.Environment}")
                    print()
                
                # Show file size distribution for special cases
                print("File Size Distribution (Special Cases):")
                size_ranges = [
                    (0, 2048, "Small (<2KB)"),
                    (2048, 8192, "Medium (2-8KB)"),
                    (8192, 1048576, "Large (8KB-1MB)"),
                    (1048576, float('inf'), "Very Large (>1MB)")
                ]
                
                for min_size, max_size, label in size_ranges:
                    # Estimate file size from content length (not exact but representative)
                    count = len([
                        case for case in special_cases 
                        if min_size <= len(case.LogContentPreview or '') < max_size
                    ])
                    if count > 0:
                        print(f"   {label}: {count} logs")
            
            return True
            
    except Exception as e:
        print(f"[ERROR] Failed to generate special cases summary: {e}")
        return False

def main():
    """Main function to add special cases data."""
    print("BugSeek Special Cases Data Loader")
    print("This script adds edge cases and special scenarios to your database")
    print()
    
    # Ensure demo users exist first
    try:
        from flask import Flask
        from backend.models import db
        from config.settings import config
        
        app = Flask(__name__)
        app.config.from_object(config['development'])
        db.init_app(app)
        
        with app.app_context():
            ensure_demo_users()
    except Exception as e:
        print(f"[WARN] Demo user creation failed: {e}")
    
    # Add special cases data
    added_count = add_special_cases_data()
    
    if added_count == 0:
        print("\n[ERROR] No special cases data was added!")
        return False
    
    # Show summary
    if not show_special_cases_summary():
        print("\n[WARN] Could not generate special cases summary")
    
    print("\n" + "=" * 60)
    print("SPECIAL CASES DATA LOADING COMPLETE")
    print("=" * 60)
    print(f"[SUCCESS] Added {added_count} special case error logs!")
    print("\nThese edge cases include:")
    print("• Memory leaks and gradual performance degradation")
    print("• Unicode encoding issues with multilingual content")
    print("• Extreme load scenarios (50K+ requests/second)")
    print("• Intermittent network failures")
    print("• Null data and validation edge cases")
    print("• Time zone and daylight saving conflicts")
    print("• Database deadlocks and concurrent access")
    print("• System resource exhaustion scenarios")
    print("\nDemo users available:")
    print("• admin / admin123 (System Administrator)")
    print("• developer / dev123 (Developer User)")
    print("• testuser / test123 (Test User)")
    print("• hackathon / hackathon2025 (Hackathon Participant)")
    print("• demo / demo123 (Demo User)")
    print("\nNext steps:")
    print("1. Run: python 4_view_database.py (to explore all data)")
    print("2. Start the application: python run.py")
    print("3. Test search/filtering with these edge cases")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n[ERROR] Special cases data loading failed! Please check the errors above.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] Special cases data is ready for testing!")
        sys.exit(0)
