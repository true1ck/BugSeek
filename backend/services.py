import os
import uuid
from datetime import datetime
from flask import current_app
from sqlalchemy import or_, and_
from backend.models import db, ErrorLog
from werkzeug.utils import secure_filename

class ErrorLogService:
    """Service class for error log operations."""
    
    @staticmethod
    def create_error_log(data, file_content=None):
        """Create a new error log entry."""
        try:
            # Generate unique ID if not provided
            cr_id = data.get('Cr_ID', str(uuid.uuid4()))
            
            # Create new error log instance
            error_log = ErrorLog(
                Cr_ID=cr_id,
                TeamName=data['TeamName'],
                Module=data['Module'],
                Description=data['Description'],
                Owner=data['Owner'],
                LogFileName=data['LogFileName'],
                ErrorName=data['ErrorName'],
                SolutionPossible=data.get('SolutionPossible', False),
                LogContent=file_content,
                FileSize=len(file_content.encode('utf-8')) if file_content else 0
            )
            
            # Set embedding if provided (placeholder)
            if 'Embedding' in data and data['Embedding']:
                error_log.set_embedding(data['Embedding'])
            
            # Save to database
            db.session.add(error_log)
            db.session.commit()
            
            return {'success': True, 'data': error_log.to_dict(), 'message': 'Error log created successfully'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e), 'message': 'Failed to create error log'}
    
    @staticmethod
    def get_error_logs(filters=None, page=1, per_page=20):
        """Get error logs with optional filtering and pagination."""
        try:
            query = ErrorLog.query
            
            # Apply filters if provided
            if filters:
                if 'TeamName' in filters and filters['TeamName']:
                    query = query.filter(ErrorLog.TeamName.ilike(f"%{filters['TeamName']}%"))
                
                if 'Module' in filters and filters['Module']:
                    query = query.filter(ErrorLog.Module.ilike(f"%{filters['Module']}%"))
                
                if 'ErrorName' in filters and filters['ErrorName']:
                    query = query.filter(ErrorLog.ErrorName.ilike(f"%{filters['ErrorName']}%"))
                
                if 'Owner' in filters and filters['Owner']:
                    query = query.filter(ErrorLog.Owner.ilike(f"%{filters['Owner']}%"))
                
                if 'SolutionPossible' in filters:
                    query = query.filter(ErrorLog.SolutionPossible == filters['SolutionPossible'])
                
                if 'search' in filters and filters['search']:
                    search_term = f"%{filters['search']}%"
                    query = query.filter(
                        or_(
                            ErrorLog.ErrorName.ilike(search_term),
                            ErrorLog.Description.ilike(search_term),
                            ErrorLog.Module.ilike(search_term),
                            ErrorLog.TeamName.ilike(search_term)
                        )
                    )
            
            # Apply pagination
            paginated = query.order_by(ErrorLog.CreatedAt.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return {
                'success': True,
                'data': [log.get_summary() for log in paginated.items],
                'pagination': {
                    'page': paginated.page,
                    'pages': paginated.pages,
                    'per_page': paginated.per_page,
                    'total': paginated.total,
                    'has_next': paginated.has_next,
                    'has_prev': paginated.has_prev
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'message': 'Failed to retrieve error logs'}
    
    @staticmethod
    def get_error_log_by_id(cr_id):
        """Get a specific error log by ID."""
        try:
            error_log = ErrorLog.query.filter_by(Cr_ID=cr_id).first()
            
            if not error_log:
                return {'success': False, 'error': 'Error log not found', 'message': 'Error log not found'}
            
            return {'success': True, 'data': error_log.to_dict()}
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'message': 'Failed to retrieve error log'}
    
    @staticmethod
    def update_error_log(cr_id, data):
        """Update an existing error log."""
        try:
            error_log = ErrorLog.query.filter_by(Cr_ID=cr_id).first()
            
            if not error_log:
                return {'success': False, 'error': 'Error log not found', 'message': 'Error log not found'}
            
            # Update fields
            for key, value in data.items():
                if key == 'Embedding':
                    error_log.set_embedding(value)
                elif hasattr(error_log, key):
                    setattr(error_log, key, value)
            
            error_log.UpdatedAt = datetime.utcnow()
            db.session.commit()
            
            return {'success': True, 'data': error_log.to_dict(), 'message': 'Error log updated successfully'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e), 'message': 'Failed to update error log'}
    
    @staticmethod
    def delete_error_log(cr_id):
        """Delete an error log."""
        try:
            error_log = ErrorLog.query.filter_by(Cr_ID=cr_id).first()
            
            if not error_log:
                return {'success': False, 'error': 'Error log not found', 'message': 'Error log not found'}
            
            db.session.delete(error_log)
            db.session.commit()
            
            return {'success': True, 'message': 'Error log deleted successfully'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e), 'message': 'Failed to delete error log'}
    
    @staticmethod
    def get_statistics():
        """Get basic statistics about error logs."""
        try:
            total_logs = ErrorLog.query.count()
            logs_with_solutions = ErrorLog.query.filter_by(SolutionPossible=True).count()
            
            # Get team statistics
            team_stats = db.session.query(
                ErrorLog.TeamName,
                db.func.count(ErrorLog.Cr_ID).label('count')
            ).group_by(ErrorLog.TeamName).all()
            
            # Get module statistics
            module_stats = db.session.query(
                ErrorLog.Module,
                db.func.count(ErrorLog.Cr_ID).label('count')
            ).group_by(ErrorLog.Module).all()
            
            return {
                'success': True,
                'data': {
                    'total_logs': total_logs,
                    'logs_with_solutions': logs_with_solutions,
                    'solution_rate': (logs_with_solutions / total_logs * 100) if total_logs > 0 else 0,
                    'team_stats': [{'team': t[0], 'count': t[1]} for t in team_stats],
                    'module_stats': [{'module': m[0], 'count': m[1]} for m in module_stats]
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'message': 'Failed to retrieve statistics'}

class FileService:
    """Service class for file operations."""
    
    @staticmethod
    def save_uploaded_file(file, upload_folder='uploads'):
        """Save uploaded file and return file info."""
        try:
            if file and file.filename:
                # Secure the filename
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_filename = f"{timestamp}_{filename}"
                
                # Ensure upload directory exists
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                file_path = os.path.join(upload_folder, unique_filename)
                
                # Save file
                file.save(file_path)
                
                # Read file content for storage
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                return {
                    'success': True,
                    'filename': filename,
                    'unique_filename': unique_filename,
                    'file_path': file_path,
                    'content': content,
                    'size': len(content.encode('utf-8'))
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e), 'message': 'Failed to save uploaded file'}
    
    @staticmethod
    def read_file_content(file_path):
        """Read content from a file path."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return {'success': True, 'content': content}
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'message': 'Failed to read file content'}

# Placeholder services for NLP/GenAI features
class NLPService:
    """Placeholder service for NLP operations."""
    
    @staticmethod
    def generate_embeddings(text):
        """Placeholder for text embedding generation."""
        # TODO: Implement actual NLP embedding generation
        return {
            'success': True,
            'embeddings': [0.1, 0.2, 0.3, 0.4, 0.5],  # Dummy embeddings
            'message': 'Embeddings generated (placeholder)'
        }
    
    @staticmethod
    def find_similar_logs(embeddings, threshold=0.8):
        """Placeholder for similarity search."""
        # TODO: Implement actual similarity search
        return {
            'success': True,
            'similar_logs': [],
            'message': 'Similarity search completed (placeholder)'
        }

class GenAIService:
    """Placeholder service for GenAI operations."""
    
    @staticmethod
    def generate_summary(log_content):
        """Placeholder for AI-generated summaries."""
        # TODO: Implement actual GenAI summary generation
        return {
            'success': True,
            'summary': 'This is a placeholder summary generated by GenAI service.',
            'confidence': 0.85,
            'message': 'Summary generated (placeholder)'
        }
    
    @staticmethod
    def suggest_solutions(error_log):
        """Placeholder for solution suggestions."""
        # TODO: Implement actual solution suggestion logic
        return {
            'success': True,
            'solutions': [
                'Placeholder solution 1: Check configuration files',
                'Placeholder solution 2: Verify dependencies',
                'Placeholder solution 3: Review recent code changes'
            ],
            'confidence': 0.75,
            'message': 'Solutions suggested (placeholder)'
        }
