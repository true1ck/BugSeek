#!/usr/bin/env python3
"""
Create Demo Users Script for BugSeek
Creates demo users for hackathon demonstration purposes
"""

import os
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import config
from backend.models import db, User, create_tables
from backend.auth_service import AuthenticationService
from flask import Flask

def create_app():
    """Create Flask app for database operations."""
    app = Flask(__name__)
    app.config.from_object(config['development'])
    db.init_app(app)
    return app

def create_demo_users():
    """Create demo users for the hackathon."""
    app = create_app()
    
    with app.app_context():
        # Create tables first
        create_tables(app)
        
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
        
        created_users = []
        
        for user_data in demo_users:
            print(f"Creating user: {user_data['EmployeeID']}")
            
            # Check if user already exists
            existing_user = User.query.filter_by(EmployeeID=user_data['EmployeeID']).first()
            if existing_user:
                print(f"  ✓ User {user_data['EmployeeID']} already exists, skipping...")
                continue
            
            # Create the user using AuthenticationService
            result = AuthenticationService.create_user(user_data)
            
            if result['success']:
                print(f"  ✓ User {user_data['EmployeeID']} created successfully!")
                created_users.append(user_data['EmployeeID'])
            else:
                print(f"  ✗ Failed to create user {user_data['EmployeeID']}: {result['message']}")
        
        if created_users:
            print(f"\n✅ Successfully created {len(created_users)} demo users:")
            for user_id in created_users:
                user_info = next(u for u in demo_users if u['EmployeeID'] == user_id)
                print(f"   - {user_id} / {user_info['Password']} ({user_info['FullName']})")
        else:
            print("\n⚠️  No new users were created (all users already exist)")
            
        print(f"\n📝 You can now use these credentials to log into BugSeek:")
        for user_data in demo_users:
            role = "Admin" if user_data['IsAdmin'] else "User"
            print(f"   Username: {user_data['EmployeeID']} | Password: {user_data['Password']} ({role})")

if __name__ == '__main__':
    try:
        create_demo_users()
        print("\n🎉 Demo users setup completed!")
    except Exception as e:
        print(f"\n❌ Error creating demo users: {e}")
        sys.exit(1)
