import os
import uuid
import hashlib
import mimetypes
from datetime import datetime
from flask import current_app
from sqlalchemy import or_, and_
from backend.models import db, ErrorLog, ErrorLogFile
from werkzeug.utils import secure_filename

class ErrorLogService:
    """Service class for error log operations."""
    
    @staticmethod
    def create_error_log(data, content_preview=None, severity='medium', environment='unknown'):
        """Create a new error log entry with new schema."""
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
                ErrorName=data.get('ErrorName', 'Auto-generated'),
                SolutionPossible=data.get('SolutionPossible', False),
                LogContentPreview=content_preview,
                Severity=severity,
                Environment=environment,
                Archived=False
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
        """Get comprehensive statistics for analytics dashboard."""
        try:
            from datetime import datetime, timedelta
            from sqlalchemy import func, and_
            
            total_logs = ErrorLog.query.count()
            logs_with_solutions = ErrorLog.query.filter_by(SolutionPossible=True).count()
            pending_logs = total_logs - logs_with_solutions
            
            # Calculate solution rate percentage
            solution_rate = (logs_with_solutions / total_logs * 100) if total_logs > 0 else 0
            
            # Get team statistics
            team_stats = db.session.query(
                ErrorLog.TeamName,
                func.count(ErrorLog.Cr_ID).label('count'),
                func.sum(func.cast(ErrorLog.SolutionPossible, db.Integer)).label('solved')
            ).group_by(ErrorLog.TeamName).order_by(func.count(ErrorLog.Cr_ID).desc()).all()
            
            # Get module statistics
            module_stats = db.session.query(
                ErrorLog.Module,
                func.count(ErrorLog.Cr_ID).label('count'),
                func.sum(func.cast(ErrorLog.SolutionPossible, db.Integer)).label('solved')
            ).group_by(ErrorLog.Module).order_by(func.count(ErrorLog.Cr_ID).desc()).all()
            
            # Get latest upload timestamp
            latest_log = ErrorLog.query.order_by(ErrorLog.CreatedAt.desc()).first()
            latest_upload = latest_log.CreatedAt if latest_log else None
            
            # Calculate average file size from file metadata
            from sqlalchemy import func
            avg_size_result = db.session.query(
                func.avg(ErrorLogFile.FileSize)
            ).join(ErrorLog).scalar()
            avg_file_size = round(avg_size_result / 1024, 1) if avg_size_result else 0  # Convert to KB
            
            # Get error trends over last 7 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            daily_trends = db.session.query(
                func.date(ErrorLog.CreatedAt).label('date'),
                func.count(ErrorLog.Cr_ID).label('count')
            ).filter(
                and_(ErrorLog.CreatedAt >= start_date, ErrorLog.CreatedAt <= end_date)
            ).group_by(func.date(ErrorLog.CreatedAt)).order_by('date').all()
            
            # Get error type distribution (top error names)
            error_types = db.session.query(
                ErrorLog.ErrorName,
                func.count(ErrorLog.Cr_ID).label('count')
            ).group_by(ErrorLog.ErrorName).order_by(func.count(ErrorLog.Cr_ID).desc()).limit(10).all()
            
            # Get recent activity (last 10 logs)
            recent_logs = ErrorLog.query.order_by(ErrorLog.CreatedAt.desc()).limit(10).all()
            recent_activity = [{
                'id': log.Cr_ID,
                'team': log.TeamName,
                'module': log.Module,
                'error_name': log.ErrorName,
                'solution_possible': log.SolutionPossible,
                'created_at': log.CreatedAt.isoformat(),
                'owner': log.Owner
            } for log in recent_logs]
            
            # Calculate response time estimates (placeholder - would need actual resolution times)
            # For now, calculate based on solution possibility distribution
            avg_response_time = "2.5h" if solution_rate > 70 else "4.2h" if solution_rate > 50 else "6.1h"
            
            return {
                'success': True,
                'data': {
                    # Key metrics
                    'total_logs': total_logs,
                    'resolved_count': logs_with_solutions,
                    'pending_count': pending_logs,
                    'solution_rate': round(solution_rate, 1),
                    'avg_response_time': avg_response_time,
                    'avg_file_size': avg_file_size,
                    'latest_upload': latest_upload.isoformat() if latest_upload else None,
                    
                    # Team performance
                    'teams_count': len(team_stats),
                    'team_stats': [{
                        'team': t[0],
                        'total_errors': t[1],
                        'solved': t[2] or 0,
                        'solution_rate': round((t[2] or 0) / t[1] * 100, 1) if t[1] > 0 else 0
                    } for t in team_stats],
                    
                    # Module breakdown
                    'modules_count': len(module_stats),
                    'module_stats': [{
                        'module': m[0],
                        'total_errors': m[1],
                        'solved': m[2] or 0,
                        'solution_rate': round((m[2] or 0) / m[1] * 100, 1) if m[1] > 0 else 0
                    } for m in module_stats],
                    
                    # Time series data
                    'daily_trends': [{
                        'date': str(trend[0]),
                        'count': trend[1]
                    } for trend in daily_trends],
                    
                    # Error type distribution
                    'error_types': [{
                        'error_name': et[0],
                        'count': et[1]
                    } for et in error_types],
                    
                    # Recent activity
                    'recent_activity': recent_activity,
                    
                    # Legacy fields for backwards compatibility
                    'logs_with_solutions': logs_with_solutions,
                    'top_teams': [{'team': t[0], 'count': t[1]} for t in team_stats[:5]],
                    'top_modules': [{'module': m[0], 'count': m[1]} for m in module_stats[:5]]
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'message': 'Failed to retrieve statistics'}

class FileService:
    """Service class for file operations."""
    
    @staticmethod
    def save_uploaded_file(file, cr_id, upload_folder='uploads'):
        """Save uploaded file with enhanced metadata management and deduplication."""
        try:
            if not file or not file.filename:
                return {'success': False, 'message': 'No file provided'}
            
            # Read file content first to calculate hash
            file_content = file.read()
            file.seek(0)  # Reset file pointer for saving
            
            # Calculate SHA256 hash for deduplication
            sha256_hash = hashlib.sha256(file_content).hexdigest()
            
            # Check if file already exists (deduplication)
            existing_file = ErrorLogFile.find_by_hash(sha256_hash)
            if existing_file:
                # File already exists, create a new record pointing to same file
                new_file_record = ErrorLogFile(
                    Cr_ID=cr_id,
                    OriginalFileName=secure_filename(file.filename),
                    StoredFileName=existing_file.StoredFileName,
                    StoredPath=existing_file.StoredPath,
                    MimeType=existing_file.MimeType,
                    FileSize=existing_file.FileSize,
                    Sha256Hash=sha256_hash
                )
                
                db.session.add(new_file_record)
                db.session.commit()
                
                # Read content for preview (decode properly)
                try:
                    content_str = file_content.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        content_str = file_content.decode('latin-1')
                    except:
                        content_str = str(file_content)[:65536]  # Fallback to string representation
                
                return {
                    'success': True,
                    'file_record': new_file_record,
                    'content': content_str,
                    'content_preview': content_str[:65536],  # First 64KB
                    'deduplicated': True,
                    'message': 'File deduplicated successfully'
                }
            
            # File is new, save it
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            
            # Ensure upload directory exists
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            file_path = os.path.join(upload_folder, unique_filename)
            
            # Save file to disk
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Detect MIME type
            mime_type, _ = mimetypes.guess_type(filename)
            if not mime_type:
                # Fallback MIME type detection based on extension
                ext = filename.lower().split('.')[-1] if '.' in filename else ''
                mime_type = {
                    'log': 'text/plain',
                    'txt': 'text/plain',
                    'json': 'application/json',
                    'xml': 'application/xml',
                    'csv': 'text/csv'
                }.get(ext, 'application/octet-stream')
            
            # Create file metadata record
            file_record = ErrorLogFile(
                Cr_ID=cr_id,
                OriginalFileName=filename,
                StoredFileName=unique_filename,
                StoredPath=file_path,
                MimeType=mime_type,
                FileSize=len(file_content),
                Sha256Hash=sha256_hash
            )
            
            db.session.add(file_record)
            db.session.commit()
            
            # Prepare content for preview (decode properly)
            try:
                content_str = file_content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    content_str = file_content.decode('latin-1')
                except:
                    content_str = str(file_content)[:65536]  # Fallback to string representation
            
            return {
                'success': True,
                'file_record': file_record,
                'content': content_str,
                'content_preview': content_str[:65536],  # First 64KB
                'deduplicated': False,
                'message': 'File saved successfully'
            }
            
        except Exception as e:
            db.session.rollback()
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
    
    @staticmethod
    def get_file_by_cr_id(cr_id):
        """Get file metadata and content for a specific error log."""
        try:
            file_record = ErrorLogFile.query.filter_by(Cr_ID=cr_id).first()
            if not file_record:
                return {'success': False, 'message': 'File not found'}
            
            # Check if file exists on disk
            if not os.path.exists(file_record.StoredPath):
                return {'success': False, 'message': 'File not found on disk'}
            
            return {'success': True, 'file_record': file_record}
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'message': 'Failed to get file'}
    
    @staticmethod
    def cleanup_expired_files():
        """Clean up files that have exceeded their retention period."""
        try:
            expired_files = ErrorLogFile.query.filter(
                ErrorLogFile.RetainUntil < datetime.now()
            ).all()
            
            cleaned_count = 0
            for file_record in expired_files:
                try:
                    # Check if file is used by other records (deduplication)
                    other_records = ErrorLogFile.query.filter(
                        ErrorLogFile.Sha256Hash == file_record.Sha256Hash,
                        ErrorLogFile.File_ID != file_record.File_ID
                    ).count()
                    
                    # Only delete physical file if no other records reference it
                    if other_records == 0 and os.path.exists(file_record.StoredPath):
                        os.remove(file_record.StoredPath)
                    
                    # Remove the file record
                    db.session.delete(file_record)
                    cleaned_count += 1
                    
                except Exception as e:
                    print(f"Error cleaning up file {file_record.File_ID}: {e}")
                    continue
            
            db.session.commit()
            return {'success': True, 'cleaned_count': cleaned_count}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e), 'message': 'Failed to cleanup expired files'}

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
