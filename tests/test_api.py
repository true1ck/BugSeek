import pytest
import json
import io
from backend.models import db, ErrorLog
from backend.services import ErrorLogService

class TestLogUploadAPI:
    """Test cases for log upload API endpoint."""
    
    def test_upload_log_success(self, client, sample_file_content):
        """Test successful log upload."""
        data = {
            'TeamName': 'Test Team',
            'Module': 'Authentication',
            'Description': 'Test error description',
            'Owner': 'test@example.com',
            'ErrorName': 'Login Error',
            'SolutionPossible': True
        }
        
        data['file'] = (io.BytesIO(sample_file_content.encode()), 'test.log')
        
        response = client.post('/api/v1/logs/upload', data=data)
        
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert 'Cr_ID' in response_data
        assert 'report_url' in response_data
    
    def test_upload_log_missing_required_fields(self, client):
        """Test upload with missing required fields."""
        data = {
            'TeamName': 'Test Team',
            # Missing other required fields
        }
        
        response = client.post('/api/v1/logs/upload', data=data)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
    
    def test_upload_log_missing_file(self, client):
        """Test upload without file."""
        data = {
            'TeamName': 'Test Team',
            'Module': 'Authentication',
            'Description': 'Test error description',
            'Owner': 'test@example.com',
            'ErrorName': 'Login Error'
        }
        
        response = client.post('/api/v1/logs/upload', data=data)
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False

class TestLogListAPI:
    """Test cases for log list API endpoint."""
    
    def test_get_logs_empty_database(self, client):
        """Test getting logs from empty database."""
        response = client.get('/api/v1/logs/')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert len(response_data['data']) == 0
    
    def test_get_logs_with_data(self, client, app, test_data_factory):
        """Test getting logs with sample data."""
        with app.app_context():
            # Create test logs
            logs = test_data_factory.create_multiple_logs(3)
            for log in logs:
                db.session.add(log)
            db.session.commit()
        
        response = client.get('/api/v1/logs/')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert len(response_data['data']) == 3
        assert 'pagination' in response_data
    
    def test_get_logs_with_filters(self, client, app, test_data_factory):
        """Test getting logs with filters."""
        with app.app_context():
            # Create test logs
            logs = test_data_factory.create_multiple_logs(5)
            for log in logs:
                db.session.add(log)
            db.session.commit()
        
        # Test team name filter
        response = client.get('/api/v1/logs/?TeamName=Team_0')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert len(response_data['data']) == 1
        assert response_data['data'][0]['TeamName'] == 'Team_0'
    
    def test_get_logs_pagination(self, client, app, test_data_factory):
        """Test log pagination."""
        with app.app_context():
            # Create test logs
            logs = test_data_factory.create_multiple_logs(10)
            for log in logs:
                db.session.add(log)
            db.session.commit()
        
        # Test first page
        response = client.get('/api/v1/logs/?page=1&per_page=3')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert len(response_data['data']) == 3
        assert response_data['pagination']['page'] == 1
        assert response_data['pagination']['pages'] == 4  # 10 logs / 3 per page = 4 pages

class TestReportAPI:
    """Test cases for report API endpoint."""
    
    def test_get_report_success(self, client, app, sample_error_log):
        """Test successful report retrieval."""
        with app.app_context():
            log_id = sample_error_log.Cr_ID
        
        response = client.get(f'/api/v1/reports/{log_id}')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert 'data' in response_data
        assert 'log_details' in response_data['data']
        assert response_data['data']['log_details']['Cr_ID'] == log_id
    
    def test_get_report_not_found(self, client):
        """Test report retrieval with invalid ID."""
        response = client.get('/api/v1/reports/invalid-id')
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['success'] is False

class TestHealthAPI:
    """Test cases for health check API endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/v1/health/')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'status' in response_data
        assert 'database' in response_data
        assert 'version' in response_data

class TestAutomationAPI:
    """Test cases for automation API endpoint."""
    
    def test_automation_validate(self, client):
        """Test automation validation endpoint."""
        data = {
            'TeamName': 'Test Team',
            'Module': 'Test Module',
            'Description': 'Test description',
            'Owner': 'test@example.com',
            'ErrorName': 'Test Error'
        }
        
        response = client.post('/api/v1/automation/validate', json=data)
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert 'status' in response_data

class TestStatisticsAPI:
    """Test cases for statistics API endpoint."""
    
    def test_get_statistics_empty(self, client):
        """Test statistics with no data."""
        response = client.get('/api/v1/statistics')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['data']['total_logs'] == 0
    
    def test_get_statistics_with_data(self, client, app, test_data_factory):
        """Test statistics with sample data."""
        with app.app_context():
            # Create test logs with some having solutions
            logs = test_data_factory.create_multiple_logs(5)
            for log in logs:
                db.session.add(log)
            db.session.commit()
        
        response = client.get('/api/v1/statistics')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['data']['total_logs'] == 5
        assert 'solution_rate' in response_data['data']
        assert 'team_stats' in response_data['data']
        assert 'module_stats' in response_data['data']

class TestErrorHandling:
    """Test cases for error handling."""
    
    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/api/v1/nonexistent-endpoint')
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'message' in response_data
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON data."""
        response = client.post(
            '/api/v1/automation/validate',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code in [400, 500]  # Either bad request or server error
