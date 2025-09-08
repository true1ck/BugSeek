from datetime import datetime
import uuid
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index

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
    
    # File content storage (for preview functionality)
    LogContent = db.Column(db.Text, nullable=True)
    FileSize = db.Column(db.Integer, nullable=True)
    
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
            'FileSize': self.FileSize,
            'LogContent': self.LogContent[:500] + '...' if self.LogContent and len(self.LogContent) > 500 else self.LogContent
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
        return {
            'Cr_ID': self.Cr_ID,
            'TeamName': self.TeamName,
            'Module': self.Module,
            'ErrorName': self.ErrorName,
            'Owner': self.Owner,
            'LogFileName': self.LogFileName,
            'SolutionPossible': self.SolutionPossible,
            'CreatedAt': self.CreatedAt.isoformat() if self.CreatedAt else None,
            'FileSize': self.FileSize
        }
    
    def __repr__(self):
        """String representation of ErrorLog."""
        return f'<ErrorLog {self.Cr_ID}: {self.ErrorName} - {self.Module}>'

def create_tables(app):
    """Create all database tables."""
    with app.app_context():
        db.create_all()
        
def init_db(app):
    """Initialize database with Flask app."""
    db.init_app(app)
    return db
