import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Compute project root (one level up from this config directory)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DEFAULT_SQLITE_PATH = os.path.join(PROJECT_ROOT, 'bugseek.db')
# Ensure Windows paths are normalized for SQLAlchemy URI
DEFAULT_SQLITE_URI = f"sqlite:///{DEFAULT_SQLITE_PATH.replace('\\\\', '/').replace('\\', '/')}"

class Config:
    """Base configuration class."""
    
    # Database Configuration - prefer env var, else absolute sqlite path in project root
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', DEFAULT_SQLITE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False').lower() == 'true'
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Celery Configuration
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # API Configuration
    API_VERSION = os.getenv('API_VERSION', 'v1')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    # Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Streamlit Configuration
    STREAMLIT_SERVER_PORT = int(os.getenv('STREAMLIT_SERVER_PORT', '8501'))
    BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:5000')
    
    # OpenAI/Azure Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT', 'https://mlop-azure-gateway.mediatek.inc')
    AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-10-21')
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'aida-gpt-4o-mini')
    
    # AI Analysis Configuration
    AI_ANALYSIS_ENABLED = os.getenv('AI_ANALYSIS_ENABLED', 'True').lower() == 'true'
    AI_MAX_RETRIES = int(os.getenv('AI_MAX_RETRIES', '3'))
    AI_REQUEST_TIMEOUT = int(os.getenv('AI_REQUEST_TIMEOUT', '30'))
    AI_BATCH_SIZE = int(os.getenv('AI_BATCH_SIZE', '10'))

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
