import pytest
import os
import sys
import tempfile
import shutil

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.models import db, ErrorLog
from config.settings import config

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    # Create a temporary directory for uploads during testing
    upload_dir = tempfile.mkdtemp()
    app.config['UPLOAD_FOLDER'] = upload_dir
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    # Clean up temporary directory
    shutil.rmtree(upload_dir, ignore_errors=True)

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()

@pytest.fixture
def sample_log_data():
    """Sample log data for testing."""
    return {
        'TeamName': 'Test Team',
        'Module': 'Authentication',
        'Description': 'Test error description',
        'Owner': 'test@example.com',
        'LogFileName': 'test.log',
        'ErrorName': 'Test Error'
    }

@pytest.fixture
def sample_error_log(app, sample_log_data):
    """Create a sample error log in the database."""
    with app.app_context():
        error_log = ErrorLog(**sample_log_data)
        db.session.add(error_log)
        db.session.commit()
        return error_log

@pytest.fixture
def sample_file_content():
    """Sample file content for testing."""
    return """
2023-01-01 10:00:00 ERROR [Authentication] Login failed for user test@example.com
2023-01-01 10:00:01 ERROR [Authentication] Invalid credentials provided
2023-01-01 10:00:02 ERROR [Authentication] Connection timeout to authentication service
Stack trace:
  at login() line 45
  at authenticate() line 23
  at main() line 12
"""

@pytest.fixture
def sample_upload_file(sample_file_content):
    """Create a sample file for upload testing."""
    import io
    return (io.BytesIO(sample_file_content.encode()), 'test.log')

@pytest.fixture
def auth_headers():
    """Sample authorization headers."""
    return {'Content-Type': 'application/json'}

class TestDataFactory:
    """Factory class for creating test data."""
    
    @staticmethod
    def create_error_log(**kwargs):
        """Create an error log with default or provided data."""
        default_data = {
            'TeamName': 'Default Team',
            'Module': 'Default Module',
            'Description': 'Default description',
            'Owner': 'default@example.com',
            'LogFileName': 'default.log',
            'ErrorName': 'Default Error',
            'SolutionPossible': False
        }
        default_data.update(kwargs)
        return ErrorLog(**default_data)
    
    @staticmethod
    def create_multiple_logs(count=5):
        """Create multiple error logs for testing."""
        logs = []
        for i in range(count):
            log_data = {
                'TeamName': f'Team_{i}',
                'Module': f'Module_{i}',
                'Description': f'Error description {i}',
                'Owner': f'user{i}@example.com',
                'LogFileName': f'error_{i}.log',
                'ErrorName': f'Error_{i}',
                'SolutionPossible': i % 2 == 0  # Alternate solution availability
            }
            logs.append(TestDataFactory.create_error_log(**log_data))
        return logs

@pytest.fixture
def test_data_factory():
    """Provide test data factory."""
    return TestDataFactory
