from datetime import datetime, timedelta
import uuid
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, ForeignKey, text
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
    
    # Detected errors with line numbers (JSON array of {line, text, severity})
    DetectedIssues = db.Column(db.Text, nullable=True)
    
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
            'DetectedIssues': json.loads(self.DetectedIssues) if self.DetectedIssues else [],
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
    """Create all database tables and ensure new columns exist."""
    with app.app_context():
        db.create_all()
        # Ensure new column DetectedIssues exists for AIAnalysisResult (SQLite-safe)
        try:
            engine_name = db.engine.dialect.name
            if engine_name == 'sqlite':
                rows = db.session.execute(text("PRAGMA table_info(ai_analysis_results)")).fetchall()
                cols = [r[1] for r in rows]
                if 'DetectedIssues' not in cols:
                    db.session.execute(text("ALTER TABLE ai_analysis_results ADD COLUMN DetectedIssues TEXT"))
                    db.session.commit()
        except Exception as e:
            # Non-fatal; log if needed
            print(f"Warning: could not ensure DetectedIssues column: {e}")
        
def init_db(app):
    """Initialize database with Flask app."""
    db.init_app(app)
    return db

class User(db.Model):
    """User authentication model for proper user management."""
    __tablename__ = 'users'

    # Primary Key - Employee ID
    EmployeeID = db.Column(db.String(50), primary_key=True)
    
    # User Information
    FullName = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(100), nullable=False, unique=True)
    Department = db.Column(db.String(100), nullable=True)
    TeamName = db.Column(db.String(100), nullable=True)
    JobTitle = db.Column(db.String(100), nullable=True)
    
    # Authentication
    PasswordHash = db.Column(db.String(128), nullable=False)  # bcrypt hash
    
    # User Status and Permissions
    IsActive = db.Column(db.Boolean, default=True, nullable=False)
    IsAdmin = db.Column(db.Boolean, default=False, nullable=False)
    
    # Login Tracking
    LastLogin = db.Column(db.DateTime, nullable=True)
    LoginCount = db.Column(db.Integer, default=0, nullable=False)
    
    # Account Management
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    UpdatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    CreatedBy = db.Column(db.String(50), nullable=True)  # Employee ID of creator
    
    # Session Management
    SessionToken = db.Column(db.String(128), nullable=True, unique=True)
    SessionExpiry = db.Column(db.DateTime, nullable=True)
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_user_email', 'Email'),
        Index('idx_user_department', 'Department'),
        Index('idx_user_team', 'TeamName'),
        Index('idx_user_is_active', 'IsActive'),
        Index('idx_user_session', 'SessionToken'),
    )
    
    def __init__(self, **kwargs):
        """Initialize User instance."""
        super(User, self).__init__(**kwargs)
    
    def to_dict(self, include_sensitive=False):
        """Convert User instance to dictionary for JSON serialization."""
        user_dict = {
            'EmployeeID': self.EmployeeID,
            'FullName': self.FullName,
            'Email': self.Email,
            'Department': self.Department,
            'TeamName': self.TeamName,
            'JobTitle': self.JobTitle,
            'IsActive': self.IsActive,
            'IsAdmin': self.IsAdmin,
            'LastLogin': self.LastLogin.isoformat() if self.LastLogin else None,
            'LoginCount': self.LoginCount,
            'CreatedAt': self.CreatedAt.isoformat() if self.CreatedAt else None,
            'UpdatedAt': self.UpdatedAt.isoformat() if self.UpdatedAt else None,
            'CreatedBy': self.CreatedBy
        }
        
        if include_sensitive:
            user_dict.update({
                'SessionToken': self.SessionToken,
                'SessionExpiry': self.SessionExpiry.isoformat() if self.SessionExpiry else None
            })
        
        return user_dict
    
    def set_password(self, password):
        """Set password hash using bcrypt."""
        try:
            import bcrypt
            self.PasswordHash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        except ImportError:
            # Fallback to SHA256 if bcrypt not available (not recommended for production)
            import hashlib
            import secrets
            salt = secrets.token_hex(16)
            self.PasswordHash = hashlib.sha256((password + salt).encode()).hexdigest() + ':' + salt
    
    def check_password(self, password):
        """Check if provided password matches the stored hash."""
        try:
            import bcrypt
            return bcrypt.checkpw(password.encode('utf-8'), self.PasswordHash.encode('utf-8'))
        except ImportError:
            # Fallback for SHA256 hashes
            if ':' in self.PasswordHash:
                stored_hash, salt = self.PasswordHash.split(':')
                import hashlib
                test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                return test_hash == stored_hash
            return False
    
    def generate_session_token(self, expires_in_hours=24):
        """Generate a new session token."""
        import secrets
        self.SessionToken = secrets.token_urlsafe(64)
        self.SessionExpiry = datetime.utcnow() + timedelta(hours=expires_in_hours)
        return self.SessionToken
    
    def is_session_valid(self):
        """Check if current session is valid."""
        if not self.SessionToken or not self.SessionExpiry:
            return False
        return datetime.utcnow() < self.SessionExpiry
    
    def update_last_login(self):
        """Update last login timestamp and increment login count."""
        self.LastLogin = datetime.utcnow()
        self.LoginCount += 1
        self.UpdatedAt = datetime.utcnow()
    
    def clear_session(self):
        """Clear session token and expiry."""
        self.SessionToken = None
        self.SessionExpiry = None
        self.UpdatedAt = datetime.utcnow()
    
    @staticmethod
    def find_by_employee_id(employee_id):
        """Find user by employee ID."""
        return User.query.filter_by(EmployeeID=employee_id).first()
    
    @staticmethod
    def find_by_email(email):
        """Find user by email address."""
        return User.query.filter_by(Email=email).first()
    
    @staticmethod
    def find_by_session_token(token):
        """Find user by session token."""
        return User.query.filter_by(SessionToken=token).first()
    
    def __repr__(self):
        """String representation of User."""
        return f'<User {self.EmployeeID}: {self.FullName} ({self.Email})>'


class UserSolution(db.Model):
    """User-submitted solutions for an error log."""
    __tablename__ = 'user_solutions'

    Solution_ID = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    Cr_ID = db.Column(db.String(36), ForeignKey('error_logs.Cr_ID'), nullable=False)
    Author = db.Column(db.String(100), nullable=True)  # user identifier or email
    Content = db.Column(db.Text, nullable=False)
    IsOfficial = db.Column(db.Boolean, default=False, nullable=False)
    Upvotes = db.Column(db.Integer, default=0, nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    UpdatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_solution_cr_id', 'Cr_ID'),
        Index('idx_solution_created_at', 'CreatedAt'),
    )

    def to_dict(self):
        return {
            'Solution_ID': self.Solution_ID,
            'Cr_ID': self.Cr_ID,
            'Author': self.Author,
            'Content': self.Content,
            'IsOfficial': self.IsOfficial,
            'Upvotes': self.Upvotes,
            'CreatedAt': self.CreatedAt.isoformat() if self.CreatedAt else None,
            'UpdatedAt': self.UpdatedAt.isoformat() if self.UpdatedAt else None,
        }
