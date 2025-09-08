import pytest
import json
from datetime import datetime
from backend.models import db, ErrorLog
from backend.services import ErrorLogService, FileService, NLPService, GenAIService

class TestErrorLogModel:
    """Test cases for ErrorLog database model."""
    
    def test_create_error_log(self, app, sample_log_data):
        """Test creating an error log."""
        with app.app_context():
            error_log = ErrorLog(**sample_log_data)
            db.session.add(error_log)
            db.session.commit()
            
            assert error_log.Cr_ID is not None
            assert error_log.TeamName == sample_log_data['TeamName']
            assert error_log.CreatedAt is not None
            assert error_log.UpdatedAt is not None
    
    def test_error_log_to_dict(self, app, sample_log_data):
        """Test converting error log to dictionary."""
        with app.app_context():
            error_log = ErrorLog(**sample_log_data)
            db.session.add(error_log)
            db.session.commit()
            
            log_dict = error_log.to_dict()
            
            assert 'Cr_ID' in log_dict
            assert log_dict['TeamName'] == sample_log_data['TeamName']
            assert log_dict['Module'] == sample_log_data['Module']
            assert 'CreatedAt' in log_dict
    
    def test_error_log_embedding(self, app, sample_log_data):
        """Test embedding functionality."""
        with app.app_context():
            error_log = ErrorLog(**sample_log_data)
            
            # Test setting embedding
            test_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
            error_log.set_embedding(test_embedding)
            
            assert error_log.Embedding is not None
            assert error_log.get_embedding_dict() == test_embedding
    
    def test_error_log_get_summary(self, app, sample_log_data):
        """Test getting error log summary."""
        with app.app_context():
            error_log = ErrorLog(**sample_log_data)
            db.session.add(error_log)
            db.session.commit()
            
            summary = error_log.get_summary()
            
            assert 'Cr_ID' in summary
            assert 'TeamName' in summary
            assert 'LogFileName' in summary
            # Should not include full content
            assert 'LogContent' not in summary

class TestErrorLogService:
    """Test cases for ErrorLogService."""
    
    def test_create_error_log_service(self, app, sample_log_data):
        """Test creating error log through service."""
        with app.app_context():
            result = ErrorLogService.create_error_log(sample_log_data, "test content")
            
            assert result['success'] is True
            assert 'data' in result
            assert result['data']['TeamName'] == sample_log_data['TeamName']
    
    def test_get_error_logs_empty(self, app):
        """Test getting error logs from empty database."""
        with app.app_context():
            result = ErrorLogService.get_error_logs()
            
            assert result['success'] is True
            assert len(result['data']) == 0
            assert result['pagination']['total'] == 0
    
    def test_get_error_logs_with_data(self, app, test_data_factory):
        """Test getting error logs with data."""
        with app.app_context():
            # Create test logs
            logs = test_data_factory.create_multiple_logs(5)
            for log in logs:
                db.session.add(log)
            db.session.commit()
            
            result = ErrorLogService.get_error_logs()
            
            assert result['success'] is True
            assert len(result['data']) == 5
            assert result['pagination']['total'] == 5
    
    def test_get_error_logs_with_filters(self, app, test_data_factory):
        """Test getting error logs with filters."""
        with app.app_context():
            # Create test logs
            logs = test_data_factory.create_multiple_logs(5)
            for log in logs:
                db.session.add(log)
            db.session.commit()
            
            # Test team filter
            filters = {'TeamName': 'Team_0'}
            result = ErrorLogService.get_error_logs(filters)
            
            assert result['success'] is True
            assert len(result['data']) == 1
            assert result['data'][0]['TeamName'] == 'Team_0'
    
    def test_get_error_logs_with_search(self, app, test_data_factory):
        """Test getting error logs with search."""
        with app.app_context():
            # Create test logs
            logs = test_data_factory.create_multiple_logs(5)
            for log in logs:
                db.session.add(log)
            db.session.commit()
            
            # Test search
            filters = {'search': 'Error_1'}
            result = ErrorLogService.get_error_logs(filters)
            
            assert result['success'] is True
            assert len(result['data']) >= 1
    
    def test_get_error_log_by_id(self, app, sample_error_log):
        """Test getting specific error log by ID."""
        with app.app_context():
            log_id = sample_error_log.Cr_ID
            
            result = ErrorLogService.get_error_log_by_id(log_id)
            
            assert result['success'] is True
            assert result['data']['Cr_ID'] == log_id
    
    def test_get_error_log_by_invalid_id(self, app):
        """Test getting error log with invalid ID."""
        with app.app_context():
            result = ErrorLogService.get_error_log_by_id('invalid-id')
            
            assert result['success'] is False
            assert 'not found' in result['message'].lower()
    
    def test_update_error_log(self, app, sample_error_log):
        """Test updating error log."""
        with app.app_context():
            log_id = sample_error_log.Cr_ID
            update_data = {'SolutionPossible': True}
            
            result = ErrorLogService.update_error_log(log_id, update_data)
            
            assert result['success'] is True
            assert result['data']['SolutionPossible'] is True
    
    def test_delete_error_log(self, app, sample_error_log):
        """Test deleting error log."""
        with app.app_context():
            log_id = sample_error_log.Cr_ID
            
            result = ErrorLogService.delete_error_log(log_id)
            
            assert result['success'] is True
            
            # Verify deletion
            deleted_log = ErrorLog.query.filter_by(Cr_ID=log_id).first()
            assert deleted_log is None
    
    def test_get_statistics(self, app, test_data_factory):
        """Test getting statistics."""
        with app.app_context():
            # Create test logs with different teams and modules
            logs = test_data_factory.create_multiple_logs(5)
            for log in logs:
                db.session.add(log)
            db.session.commit()
            
            result = ErrorLogService.get_statistics()
            
            assert result['success'] is True
            data = result['data']
            assert data['total_logs'] == 5
            assert 'logs_with_solutions' in data
            assert 'solution_rate' in data
            assert 'team_stats' in data
            assert 'module_stats' in data

class TestFileService:
    """Test cases for FileService."""
    
    def test_read_file_content_success(self, app, tmp_path):
        """Test reading file content successfully."""
        # Create a temporary file
        test_file = tmp_path / "test.log"
        test_content = "Test log content\nLine 2\nLine 3"
        test_file.write_text(test_content)
        
        with app.app_context():
            result = FileService.read_file_content(str(test_file))
            
            assert result['success'] is True
            assert result['content'] == test_content
    
    def test_read_file_content_not_found(self, app):
        """Test reading non-existent file."""
        with app.app_context():
            result = FileService.read_file_content("nonexistent.log")
            
            assert result['success'] is False
            assert 'error' in result

class TestNLPService:
    """Test cases for NLPService (placeholder)."""
    
    def test_generate_embeddings(self):
        """Test generating embeddings (placeholder)."""
        result = NLPService.generate_embeddings("test content")
        
        assert result['success'] is True
        assert 'embeddings' in result
        assert isinstance(result['embeddings'], list)
    
    def test_find_similar_logs(self):
        """Test finding similar logs (placeholder)."""
        test_embeddings = [0.1, 0.2, 0.3, 0.4, 0.5]
        result = NLPService.find_similar_logs(test_embeddings)
        
        assert result['success'] is True
        assert 'similar_logs' in result

class TestGenAIService:
    """Test cases for GenAIService (placeholder)."""
    
    def test_generate_summary(self):
        """Test generating summary (placeholder)."""
        test_content = "Error occurred in authentication module"
        result = GenAIService.generate_summary(test_content)
        
        assert result['success'] is True
        assert 'summary' in result
        assert 'confidence' in result
    
    def test_suggest_solutions(self):
        """Test suggesting solutions (placeholder)."""
        test_log = {'ErrorName': 'Login Error', 'Module': 'Authentication'}
        result = GenAIService.suggest_solutions(test_log)
        
        assert result['success'] is True
        assert 'solutions' in result
        assert isinstance(result['solutions'], list)
        assert 'confidence' in result

class TestModelValidation:
    """Test cases for model validation and constraints."""
    
    def test_error_log_required_fields(self, app):
        """Test that required fields are enforced."""
        with app.app_context():
            # Try to create error log without required fields
            error_log = ErrorLog()
            db.session.add(error_log)
            
            with pytest.raises(Exception):  # Should raise database constraint error
                db.session.commit()
    
    def test_error_log_field_lengths(self, app):
        """Test field length constraints."""
        with app.app_context():
            # Test with very long strings
            long_string = "x" * 1000
            
            error_log = ErrorLog(
                TeamName=long_string,  # Should be truncated or cause error
                Module="Test Module",
                Description="Test description",
                Owner="test@example.com",
                LogFileName="test.log",
                ErrorName="Test Error"
            )
            
            db.session.add(error_log)
            # Depending on database constraints, this might succeed or fail
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                # Expected if field length validation is enforced

class TestDatabaseIndexes:
    """Test cases for database indexes and performance."""
    
    def test_indexed_fields_performance(self, app, test_data_factory):
        """Test that indexed fields work correctly."""
        with app.app_context():
            # Create many logs for testing
            logs = test_data_factory.create_multiple_logs(100)
            for log in logs:
                db.session.add(log)
            db.session.commit()
            
            # Test queries that should use indexes
            # These should execute quickly due to indexes
            team_logs = ErrorLog.query.filter_by(TeamName='Team_50').all()
            module_logs = ErrorLog.query.filter_by(Module='Module_25').all()
            error_logs = ErrorLog.query.filter_by(ErrorName='Error_75').all()
            
            # Just verify the queries work (performance testing would require more sophisticated setup)
            assert isinstance(team_logs, list)
            assert isinstance(module_logs, list)
            assert isinstance(error_logs, list)
