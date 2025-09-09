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
    ai_analyses = relationship('AIAnalysisResult', back_populates='error_log', cascade='all, delete-orphan')
    
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


class AIAnalysisResult(db.Model):
    """AI analysis results model for storing GenAI analysis data."""
    
    __tablename__ = 'ai_analysis_results'
    
    # Primary Key
    Analysis_ID = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Key to ErrorLog
    Cr_ID = db.Column(db.String(36), ForeignKey('error_logs.Cr_ID'), nullable=False)
    
    # Analysis Type
    AnalysisType = db.Column(db.String(50), nullable=False)  # 'summary', 'solution', 'similarity'
    
    # AI Analysis Results
    Summary = db.Column(db.Text, nullable=True)  # AI-generated summary
    Confidence = db.Column(db.Float, default=0.0, nullable=False)  # Confidence score (0.0-1.0)
    Keywords = db.Column(db.Text, nullable=True)  # JSON array of extracted keywords
    EstimatedSeverity = db.Column(db.String(20), nullable=True)  # AI-estimated severity
    
    # Solution Suggestions (JSON format)
    SuggestedSolutions = db.Column(db.Text, nullable=True)  # JSON array of solutions
    SolutionCategories = db.Column(db.Text, nullable=True)  # JSON array of solution categories
    
    # Error Pattern Recognition
    ErrorPattern = db.Column(db.String(100), nullable=True)  # Detected error pattern
    ErrorCategory = db.Column(db.String(50), nullable=True)  # Categorized error type
    
    # Processing Status
    Status = db.Column(db.String(20), default='pending', nullable=False)  # pending, processing, completed, failed
    ProcessingStartTime = db.Column(db.DateTime, nullable=True)
    ProcessingEndTime = db.Column(db.DateTime, nullable=True)
    ErrorMessage = db.Column(db.Text, nullable=True)  # Error message if processing failed
    
    # API Usage Tracking
    TokensUsed = db.Column(db.Integer, default=0, nullable=False)  # OpenAI tokens used
    ModelUsed = db.Column(db.String(50), nullable=True)  # AI model used
    ApiCost = db.Column(db.Float, default=0.0, nullable=False)  # Estimated API cost
    
    # Timestamps
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    UpdatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to ErrorLog
    error_log = relationship('ErrorLog', back_populates='ai_analyses')
    
    # Indexes
    __table_args__ = (
        Index('idx_ai_cr_id', 'Cr_ID'),
        Index('idx_ai_analysis_type', 'AnalysisType'),
        Index('idx_ai_status', 'Status'),
        Index('idx_ai_created_at', 'CreatedAt'),
        Index('idx_ai_error_pattern', 'ErrorPattern'),
    )
    
    def __init__(self, **kwargs):
        """Initialize AIAnalysisResult instance."""
        super(AIAnalysisResult, self).__init__(**kwargs)
    
    def to_dict(self):
        """Convert AIAnalysisResult instance to dictionary."""
        return {
            'Analysis_ID': self.Analysis_ID,
            'Cr_ID': self.Cr_ID,
            'AnalysisType': self.AnalysisType,
            'Summary': self.Summary,
            'Confidence': self.Confidence,
            'Keywords': json.loads(self.Keywords) if self.Keywords else [],
            'EstimatedSeverity': self.EstimatedSeverity,
            'SuggestedSolutions': json.loads(self.SuggestedSolutions) if self.SuggestedSolutions else [],
            'SolutionCategories': json.loads(self.SolutionCategories) if self.SolutionCategories else [],
            'ErrorPattern': self.ErrorPattern,
            'ErrorCategory': self.ErrorCategory,
            'Status': self.Status,
            'ProcessingStartTime': self.ProcessingStartTime.isoformat() if self.ProcessingStartTime else None,
            'ProcessingEndTime': self.ProcessingEndTime.isoformat() if self.ProcessingEndTime else None,
            'ErrorMessage': self.ErrorMessage,
            'TokensUsed': self.TokensUsed,
            'ModelUsed': self.ModelUsed,
            'ApiCost': self.ApiCost,
            'CreatedAt': self.CreatedAt.isoformat() if self.CreatedAt else None,
            'UpdatedAt': self.UpdatedAt.isoformat() if self.UpdatedAt else None
        }
    
    def set_keywords(self, keywords_list):
        """Set keywords as JSON string."""
        if keywords_list:
            self.Keywords = json.dumps(keywords_list)
        else:
            self.Keywords = None
    
    def set_solutions(self, solutions_list):
        """Set suggested solutions as JSON string."""
        if solutions_list:
            self.SuggestedSolutions = json.dumps(solutions_list)
        else:
            self.SuggestedSolutions = None
    
    def set_solution_categories(self, categories_list):
        """Set solution categories as JSON string."""
        if categories_list:
            self.SolutionCategories = json.dumps(categories_list)
        else:
            self.SolutionCategories = None
    
    def __repr__(self):
        """String representation of AIAnalysisResult."""
        return f'<AIAnalysisResult {self.Analysis_ID}: {self.AnalysisType} - {self.Status}>'


class OpenAIStatus(db.Model):
    """OpenAI API status and configuration tracking."""
    
    __tablename__ = 'openai_status'
    
    # Primary Key
    Status_ID = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # API Configuration
    ApiKeyHash = db.Column(db.String(64), nullable=True)  # SHA256 hash of API key for tracking
    ApiEndpoint = db.Column(db.String(255), nullable=True)  # OpenAI API endpoint
    ModelVersion = db.Column(db.String(50), nullable=True)  # Model version being used
    
    # Connection Status
    IsConnected = db.Column(db.Boolean, default=False, nullable=False)
    LastConnectionCheck = db.Column(db.DateTime, nullable=True)
    LastSuccessfulCall = db.Column(db.DateTime, nullable=True)
    LastErrorMessage = db.Column(db.Text, nullable=True)
    
    # Usage Statistics
    TotalApiCalls = db.Column(db.Integer, default=0, nullable=False)
    TotalTokensUsed = db.Column(db.Integer, default=0, nullable=False)
    EstimatedTotalCost = db.Column(db.Float, default=0.0, nullable=False)
    
    # Rate Limiting Info
    RequestsPerMinute = db.Column(db.Integer, nullable=True)
    TokensPerMinute = db.Column(db.Integer, nullable=True)
    LastRateLimitHit = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    UpdatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_openai_updated_at', 'UpdatedAt'),
        Index('idx_openai_is_connected', 'IsConnected'),
    )
    
    def __init__(self, **kwargs):
        """Initialize OpenAIStatus instance."""
        super(OpenAIStatus, self).__init__(**kwargs)
    
    def to_dict(self):
        """Convert OpenAIStatus instance to dictionary."""
        return {
            'Status_ID': self.Status_ID,
            'ApiEndpoint': self.ApiEndpoint,
            'ModelVersion': self.ModelVersion,
            'IsConnected': self.IsConnected,
            'LastConnectionCheck': self.LastConnectionCheck.isoformat() if self.LastConnectionCheck else None,
            'LastSuccessfulCall': self.LastSuccessfulCall.isoformat() if self.LastSuccessfulCall else None,
            'LastErrorMessage': self.LastErrorMessage,
            'TotalApiCalls': self.TotalApiCalls,
            'TotalTokensUsed': self.TotalTokensUsed,
            'EstimatedTotalCost': self.EstimatedTotalCost,
            'RequestsPerMinute': self.RequestsPerMinute,
            'TokensPerMinute': self.TokensPerMinute,
            'LastRateLimitHit': self.LastRateLimitHit.isoformat() if self.LastRateLimitHit else None,
            'CreatedAt': self.CreatedAt.isoformat() if self.CreatedAt else None,
            'UpdatedAt': self.UpdatedAt.isoformat() if self.UpdatedAt else None
        }
    
    @staticmethod
    def get_current_status():
        """Get the most recent OpenAI status record."""
        return OpenAIStatus.query.order_by(OpenAIStatus.UpdatedAt.desc()).first()
    
    def update_connection_status(self, is_connected, error_message=None):
        """Update connection status."""
        self.IsConnected = is_connected
        self.LastConnectionCheck = datetime.utcnow()
        if is_connected:
            self.LastSuccessfulCall = datetime.utcnow()
        if error_message:
            self.LastErrorMessage = error_message
        self.UpdatedAt = datetime.utcnow()
    
    def increment_usage(self, tokens_used, estimated_cost):
        """Increment usage statistics."""
        self.TotalApiCalls += 1
        self.TotalTokensUsed += tokens_used
        self.EstimatedTotalCost += estimated_cost
        self.UpdatedAt = datetime.utcnow()
    
    def __repr__(self):
        """String representation of OpenAIStatus."""
        return f'<OpenAIStatus {self.Status_ID}: Connected={self.IsConnected}>'


class SimilarLogMatch(db.Model):
    """Similarity matching results between error logs."""
    
    __tablename__ = 'similar_log_matches'
    
    # Primary Key
    Match_ID = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Source and Target Logs
    Source_Cr_ID = db.Column(db.String(36), ForeignKey('error_logs.Cr_ID'), nullable=False)
    Target_Cr_ID = db.Column(db.String(36), ForeignKey('error_logs.Cr_ID'), nullable=False)
    
    # Similarity Metrics
    SimilarityScore = db.Column(db.Float, nullable=False)  # 0.0 - 1.0 similarity score
    MatchingMethod = db.Column(db.String(50), nullable=False)  # 'tfidf', 'embeddings', 'keywords'
    ConfidenceLevel = db.Column(db.String(20), nullable=False)  # 'low', 'medium', 'high'
    
    # Match Details
    CommonKeywords = db.Column(db.Text, nullable=True)  # JSON array of common keywords
    MatchingPatterns = db.Column(db.Text, nullable=True)  # JSON array of matching patterns
    
    # Timestamps
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    source_log = relationship('ErrorLog', foreign_keys=[Source_Cr_ID])
    target_log = relationship('ErrorLog', foreign_keys=[Target_Cr_ID])
    
    # Indexes
    __table_args__ = (
        Index('idx_similar_source', 'Source_Cr_ID'),
        Index('idx_similar_target', 'Target_Cr_ID'),
        Index('idx_similar_score', 'SimilarityScore'),
        Index('idx_similar_method', 'MatchingMethod'),
    )
    
    def __init__(self, **kwargs):
        """Initialize SimilarLogMatch instance."""
        super(SimilarLogMatch, self).__init__(**kwargs)
    
    def to_dict(self):
        """Convert SimilarLogMatch instance to dictionary."""
        return {
            'Match_ID': self.Match_ID,
            'Source_Cr_ID': self.Source_Cr_ID,
            'Target_Cr_ID': self.Target_Cr_ID,
            'SimilarityScore': self.SimilarityScore,
            'MatchingMethod': self.MatchingMethod,
            'ConfidenceLevel': self.ConfidenceLevel,
            'CommonKeywords': json.loads(self.CommonKeywords) if self.CommonKeywords else [],
            'MatchingPatterns': json.loads(self.MatchingPatterns) if self.MatchingPatterns else [],
            'CreatedAt': self.CreatedAt.isoformat() if self.CreatedAt else None
        }
    
    def set_common_keywords(self, keywords_list):
        """Set common keywords as JSON string."""
        if keywords_list:
            self.CommonKeywords = json.dumps(keywords_list)
        else:
            self.CommonKeywords = None
    
    def set_matching_patterns(self, patterns_list):
        """Set matching patterns as JSON string."""
        if patterns_list:
            self.MatchingPatterns = json.dumps(patterns_list)
        else:
            self.MatchingPatterns = None
    
    def __repr__(self):
        """String representation of SimilarLogMatch."""
        return f'<SimilarLogMatch {self.Match_ID}: {self.SimilarityScore:.2f} ({self.MatchingMethod})>'

def create_tables(app):
    """Create all database tables."""
    with app.app_context():
        db.create_all()
        
def init_db(app):
    """Initialize database with Flask app."""
    db.init_app(app)
    return db
