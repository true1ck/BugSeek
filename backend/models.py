from datetime import datetime, timedelta
import uuid
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class ErrorLog(db.Model):
    """Error log model representing the error_logs table."""
    
    __tablename__ = 'error_logs'
    
    # Primary Key - Using UUID for better uniqueness
    Cr_ID = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Metadata fields
    TeamName = db.Column(db.String(100), nullable=False)
    Module = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.Text, nullable=False)
    Owner = db.Column(db.String(100), nullable=False)
    LogFileName = db.Column(db.String(255), nullable=False)
    ErrorName = db.Column(db.String(200), nullable=False)
    
    # Placeholder for NLP/GenAI features
    Embedding = db.Column(db.Text, nullable=True)  # JSON field for vector embeddings
    SolutionPossible = db.Column(db.Boolean, default=False)
    
    # Timestamps
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    UpdatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # File content preview (first 64KB only for quick display)
    LogContentPreview = db.Column(db.Text, nullable=True)
    
    # New fields for better categorization and management
    Severity = db.Column(db.String(20), default='medium', nullable=False)  # low, medium, high, critical
    Environment = db.Column(db.String(20), default='unknown', nullable=False)  # dev, staging, prod, unknown
    Archived = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    files = relationship('ErrorLogFile', back_populates='error_log', cascade='all, delete-orphan')
    
    # Indexes for fast search (defined as class attributes)
    __table_args__ = (
        Index('idx_error_name', 'ErrorName'),
        Index('idx_module', 'Module'),
        Index('idx_team_name', 'TeamName'),
        Index('idx_created_at', 'CreatedAt'),
        Index('idx_owner', 'Owner'),
    )
    
    def __init__(self, **kwargs):
        """Initialize ErrorLog instance."""
        super(ErrorLog, self).__init__(**kwargs)
    
    def to_dict(self):
        """Convert ErrorLog instance to dictionary for JSON serialization."""
        return {
            'Cr_ID': self.Cr_ID,
            'TeamName': self.TeamName,
            'Module': self.Module,
            'Description': self.Description,
            'Owner': self.Owner,
            'LogFileName': self.LogFileName,
            'ErrorName': self.ErrorName,
            'Embedding': self.get_embedding_dict(),
            'SolutionPossible': self.SolutionPossible,
            'CreatedAt': self.CreatedAt.isoformat() if self.CreatedAt else None,
            'UpdatedAt': self.UpdatedAt.isoformat() if self.UpdatedAt else None,
            'LogContentPreview': self.LogContentPreview[:500] + '...' if self.LogContentPreview and len(self.LogContentPreview) > 500 else self.LogContentPreview,
            'Severity': self.Severity,
            'Environment': self.Environment,
            'Archived': self.Archived,
            'Files': [file.to_dict() for file in self.files] if self.files else []
        }
    
    def get_embedding_dict(self):
        """Parse embedding JSON field."""
        if self.Embedding:
            try:
                return json.loads(self.Embedding)
            except (json.JSONDecodeError, TypeError):
                return None
        return None
    
    def set_embedding(self, embedding_data):
        """Set embedding data as JSON string."""
        if embedding_data:
            self.Embedding = json.dumps(embedding_data)
        else:
            self.Embedding = None
    
    def get_summary(self):
        """Get a summary of the error log for list views."""
        # Get total file size from all associated files
        total_file_size = sum(file.FileSize for file in self.files) if self.files else 0
        
        return {
            'Cr_ID': self.Cr_ID,
            'TeamName': self.TeamName,
            'Module': self.Module,
            'ErrorName': self.ErrorName,
            'Owner': self.Owner,
            'LogFileName': self.LogFileName,
            'SolutionPossible': self.SolutionPossible,
            'CreatedAt': self.CreatedAt.isoformat() if self.CreatedAt else None,
            'FileSize': total_file_size,
            'Severity': self.Severity,
            'Environment': self.Environment,
            'Archived': self.Archived,
            'FileCount': len(self.files) if self.files else 0
        }
    
    def __repr__(self):
        """String representation of ErrorLog."""
        return f'<ErrorLog {self.Cr_ID}: {self.ErrorName} - {self.Module}>'


class ErrorLogFile(db.Model):
    """File metadata model for uploaded log files."""
    
    __tablename__ = 'error_log_files'
    
    # Primary Key
    File_ID = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Key to ErrorLog
    Cr_ID = db.Column(db.String(36), ForeignKey('error_logs.Cr_ID'), nullable=False)
    
    # File metadata
    OriginalFileName = db.Column(db.String(255), nullable=False)
    StoredFileName = db.Column(db.String(255), nullable=False)
    StoredPath = db.Column(db.String(512), nullable=False)  # Relative or absolute path
    MimeType = db.Column(db.String(100), nullable=True)
    FileSize = db.Column(db.BigInteger, nullable=False)
    
    # File integrity and deduplication
    Sha256Hash = db.Column(db.String(64), nullable=False)
    
    # File lifecycle management
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    RetainUntil = db.Column(db.DateTime, nullable=True)  # For automatic cleanup
    
    # Relationship back to ErrorLog
    error_log = relationship('ErrorLog', back_populates='files')
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_cr_id', 'Cr_ID'),
        Index('idx_sha256', 'Sha256Hash'),
        Index('idx_created_at_file', 'CreatedAt'),
        Index('idx_retain_until', 'RetainUntil'),
        Index('idx_original_filename', 'OriginalFileName'),
    )
    
    def __init__(self, **kwargs):
        """Initialize ErrorLogFile instance."""
        super(ErrorLogFile, self).__init__(**kwargs)
        
        # Set default retention period (30 days from creation)
        if not self.RetainUntil:
            self.RetainUntil = datetime.utcnow() + timedelta(days=30)
    
    def to_dict(self):
        """Convert ErrorLogFile instance to dictionary."""
        return {
            'File_ID': self.File_ID,
            'Cr_ID': self.Cr_ID,
            'OriginalFileName': self.OriginalFileName,
            'StoredFileName': self.StoredFileName,
            'StoredPath': self.StoredPath,
            'MimeType': self.MimeType,
            'FileSize': self.FileSize,
            'Sha256Hash': self.Sha256Hash,
            'CreatedAt': self.CreatedAt.isoformat() if self.CreatedAt else None,
            'RetainUntil': self.RetainUntil.isoformat() if self.RetainUntil else None
        }
    
    def is_expired(self):
        """Check if file has exceeded retention period."""
        if self.RetainUntil:
            return datetime.utcnow() > self.RetainUntil
        return False
    
    def get_file_size_formatted(self):
        """Get human-readable file size."""
        if not self.FileSize:
            return '0 B'
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.FileSize < 1024:
                return f'{self.FileSize:.1f} {unit}'
            self.FileSize /= 1024
        return f'{self.FileSize:.1f} TB'
    
    @staticmethod
    def find_by_hash(sha256_hash):
        """Find existing file by SHA256 hash for deduplication."""
        return ErrorLogFile.query.filter_by(Sha256Hash=sha256_hash).first()
    
    def __repr__(self):
        """String representation of ErrorLogFile."""
        return f'<ErrorLogFile {self.File_ID}: {self.OriginalFileName} ({self.get_file_size_formatted()})>'

def create_tables(app):
    """Create all database tables."""
    with app.app_context():
        db.create_all()
        
def init_db(app):
    """Initialize database with Flask app."""
    db.init_app(app)
    return db
