"""
Authentication Service Module
Provides user authentication and session management for the BugSeek application.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import db, User
from config.settings import Config

class AuthenticationService:
    """Service class for handling user authentication and session management."""
    
    @staticmethod
    def authenticate_user(employee_id: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user with employee ID and password.
        
        Args:
            employee_id: Employee ID or username
            password: Plain text password
            
        Returns:
            Dict containing authentication result and user data
        """
        try:
            # Find user by employee ID
            user = User.find_by_employee_id(employee_id.strip())
            
            if not user:
                return {
                    'success': False,
                    'message': 'Invalid employee ID or password.',
                    'error_code': 'INVALID_CREDENTIALS'
                }
            
            # Check if user is active
            if not user.IsActive:
                return {
                    'success': False,
                    'message': 'Account is deactivated. Please contact your administrator.',
                    'error_code': 'ACCOUNT_DEACTIVATED'
                }
            
            # Verify password
            if not user.check_password(password):
                return {
                    'success': False,
                    'message': 'Invalid employee ID or password.',
                    'error_code': 'INVALID_CREDENTIALS'
                }
            
            # Generate session token
            session_token = user.generate_session_token(expires_in_hours=24)
            
            # Update last login
            user.update_last_login()
            
            # Save changes
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Authentication successful',
                'user': user.to_dict(include_sensitive=True),
                'session_token': session_token
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': 'Authentication failed due to system error.',
                'error_code': 'SYSTEM_ERROR',
                'error': str(e)
            }
    
    @staticmethod
    def validate_session(session_token: str) -> Dict[str, Any]:
        """
        Validate a session token and return user information.
        
        Args:
            session_token: Session token to validate
            
        Returns:
            Dict containing validation result and user data
        """
        try:
            if not session_token:
                return {
                    'success': False,
                    'message': 'No session token provided.',
                    'error_code': 'NO_TOKEN'
                }
            
            # Find user by session token
            user = User.find_by_session_token(session_token)
            
            if not user:
                return {
                    'success': False,
                    'message': 'Invalid session token.',
                    'error_code': 'INVALID_SESSION'
                }
            
            # Check if session is still valid
            if not user.is_session_valid():
                # Clear expired session
                user.clear_session()
                db.session.commit()
                
                return {
                    'success': False,
                    'message': 'Session has expired. Please login again.',
                    'error_code': 'SESSION_EXPIRED'
                }
            
            # Check if user is still active
            if not user.IsActive:
                return {
                    'success': False,
                    'message': 'Account has been deactivated.',
                    'error_code': 'ACCOUNT_DEACTIVATED'
                }
            
            return {
                'success': True,
                'message': 'Session is valid',
                'user': user.to_dict()
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': 'Session validation failed.',
                'error_code': 'SYSTEM_ERROR',
                'error': str(e)
            }
    
    @staticmethod
    def logout_user(session_token: str) -> Dict[str, Any]:
        """
        Logout a user by clearing their session.
        
        Args:
            session_token: Session token to invalidate
            
        Returns:
            Dict containing logout result
        """
        try:
            if not session_token:
                return {
                    'success': True,
                    'message': 'No active session to logout.'
                }
            
            # Find user by session token
            user = User.find_by_session_token(session_token)
            
            if user:
                # Clear session
                user.clear_session()
                db.session.commit()
            
            return {
                'success': True,
                'message': 'Logout successful'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': 'Logout failed.',
                'error_code': 'SYSTEM_ERROR',
                'error': str(e)
            }
    
    @staticmethod
    def create_user(user_data: Dict[str, Any], creator_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new user account.
        
        Args:
            user_data: Dictionary containing user information
            creator_id: Employee ID of the user creating this account
            
        Returns:
            Dict containing creation result
        """
        try:
            required_fields = ['EmployeeID', 'FullName', 'Email', 'Password']
            
            # Validate required fields
            for field in required_fields:
                if not user_data.get(field):
                    return {
                        'success': False,
                        'message': f'{field} is required.',
                        'error_code': 'MISSING_FIELD'
                    }
            
            # Check if employee ID already exists
            if User.find_by_employee_id(user_data['EmployeeID']):
                return {
                    'success': False,
                    'message': 'Employee ID already exists.',
                    'error_code': 'DUPLICATE_EMPLOYEE_ID'
                }
            
            # Check if email already exists
            if User.find_by_email(user_data['Email']):
                return {
                    'success': False,
                    'message': 'Email address already exists.',
                    'error_code': 'DUPLICATE_EMAIL'
                }
            
            # Create new user
            user = User(
                EmployeeID=user_data['EmployeeID'],
                FullName=user_data['FullName'],
                Email=user_data['Email'],
                Department=user_data.get('Department'),
                TeamName=user_data.get('TeamName'),
                JobTitle=user_data.get('JobTitle'),
                IsActive=user_data.get('IsActive', True),
                IsAdmin=user_data.get('IsAdmin', False),
                CreatedBy=creator_id
            )
            
            # Set password
            user.set_password(user_data['Password'])
            
            # Save user
            db.session.add(user)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'User created successfully',
                'user': user.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': 'Failed to create user.',
                'error_code': 'SYSTEM_ERROR',
                'error': str(e)
            }
    
    @staticmethod
    def update_user(employee_id: str, updates: Dict[str, Any], updater_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Update user information.
        
        Args:
            employee_id: Employee ID of user to update
            updates: Dictionary containing fields to update
            updater_id: Employee ID of the user making the update
            
        Returns:
            Dict containing update result
        """
        try:
            user = User.find_by_employee_id(employee_id)
            
            if not user:
                return {
                    'success': False,
                    'message': 'User not found.',
                    'error_code': 'USER_NOT_FOUND'
                }
            
            # Update allowed fields
            updatable_fields = ['FullName', 'Email', 'Department', 'TeamName', 'JobTitle', 'IsActive', 'IsAdmin']
            
            for field, value in updates.items():
                if field in updatable_fields:
                    setattr(user, field, value)
                elif field == 'Password' and value:
                    user.set_password(value)
            
            # Update timestamps
            user.UpdatedAt = datetime.utcnow()
            
            # Save changes
            db.session.commit()
            
            return {
                'success': True,
                'message': 'User updated successfully',
                'user': user.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': 'Failed to update user.',
                'error_code': 'SYSTEM_ERROR',
                'error': str(e)
            }
    
    @staticmethod
    def get_user_by_id(employee_id: str) -> Dict[str, Any]:
        """
        Get user information by employee ID.
        
        Args:
            employee_id: Employee ID to search for
            
        Returns:
            Dict containing user information
        """
        try:
            user = User.find_by_employee_id(employee_id)
            
            if not user:
                return {
                    'success': False,
                    'message': 'User not found.',
                    'error_code': 'USER_NOT_FOUND'
                }
            
            return {
                'success': True,
                'user': user.to_dict()
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': 'Failed to get user information.',
                'error_code': 'SYSTEM_ERROR',
                'error': str(e)
            }
    
    @staticmethod
    def list_users(filters: Optional[Dict[str, Any]] = None, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        List users with optional filtering and pagination.
        
        Args:
            filters: Optional dictionary of filters
            page: Page number for pagination
            per_page: Number of items per page
            
        Returns:
            Dict containing user list and pagination info
        """
        try:
            query = User.query
            
            # Apply filters
            if filters:
                if filters.get('Department'):
                    query = query.filter(User.Department == filters['Department'])
                if filters.get('TeamName'):
                    query = query.filter(User.TeamName == filters['TeamName'])
                if filters.get('IsActive') is not None:
                    query = query.filter(User.IsActive == filters['IsActive'])
                if filters.get('IsAdmin') is not None:
                    query = query.filter(User.IsAdmin == filters['IsAdmin'])
            
            # Get paginated results
            pagination = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            users = [user.to_dict() for user in pagination.items]
            
            return {
                'success': True,
                'users': users,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': 'Failed to list users.',
                'error_code': 'SYSTEM_ERROR',
                'error': str(e)
            }

    @staticmethod
    def create_default_admin(employee_id: str = "admin", password: str = "admin123", email: str = "admin@company.com") -> Dict[str, Any]:
        """
        Create a default admin user for initial setup.
        
        Args:
            employee_id: Admin employee ID
            password: Admin password
            email: Admin email
            
        Returns:
            Dict containing creation result
        """
        try:
            # Check if admin already exists
            existing_admin = User.find_by_employee_id(employee_id)
            if existing_admin:
                return {
                    'success': False,
                    'message': 'Admin user already exists.',
                    'error_code': 'ADMIN_EXISTS'
                }
            
            # Create admin user
            admin = User(
                EmployeeID=employee_id,
                FullName="System Administrator",
                Email=email,
                Department="IT",
                TeamName="System Administration",
                JobTitle="Administrator",
                IsActive=True,
                IsAdmin=True
            )
            
            admin.set_password(password)
            
            db.session.add(admin)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Default admin user created successfully',
                'user': admin.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': 'Failed to create default admin.',
                'error_code': 'SYSTEM_ERROR',
                'error': str(e)
            }
