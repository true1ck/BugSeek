# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## System Architecture

BugSeek is a professional error log management system built with a multi-service architecture:

**Core Services:**
- **Backend**: Flask REST API with SQLAlchemy ORM (`backend/app.py`)
- **Frontend**: Streamlit UI with fast Flask alternative (`frontend/app.py`, `frontend/fast_app.py`)
- **Database**: SQLite with migration support (upgradeable to PostgreSQL)
- **Background Processing**: Celery + Redis for async tasks (`backend/tasks.py`)
- **AI Integration**: OpenAI/Azure OpenAI services for log analysis (`backend/ai_services.py`)

**Architecture Pattern:**
- Flask-RESTx for API with automatic Swagger documentation
- Service layer pattern with dedicated services (`backend/services.py`)
- Database models with relationships and proper indexing (`backend/models.py`)
- Configuration management with environment-based settings (`config/settings.py`)

## Development Commands

### First-Time Setup (New Users)

**Comprehensive project setup (RECOMMENDED for new clones):**
```bash
python setup_project.py
```

This automated script will:
- ✅ Check Python version compatibility (3.8+)
- 🔄 Optionally create virtual environment
- 📦 Install all dependencies from requirements.txt
- ⚙️ Create .env file from template with proper paths
- 📁 Create necessary directories (backend/instance, uploads, etc.)
- 🗄️ Initialize database with proper schema
- 🤖 Run AI table migrations (if available)
- 📊 Populate database with 10 realistic sample error logs
- 🔍 Test database connection
- 📋 Create SETUP_COMPLETE.md with next steps

**Quick verification after setup:**
```bash
python test_db.py  # Test database connection
python run.py      # Start the application
```

## Complete Setup Guide for New Machine

### Prerequisites

- **Python 3.8+** (verify with `python --version`)
- **Git** (for cloning the repository)
- **Redis Server** (optional, for background tasks)

### Step 1: Clone and Setup Environment

**Clone the repository:**
```bash
git clone <repository-url>
cd BugSeek
```

**Create and activate a virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

**Install dependencies:**
```bash
# Install all dependencies (recommended)
pip install -r requirements.txt

# Backend only (minimal setup)
pip install -r backend/requirements.txt
```

### Step 2: Configure Environment

**Create environment configuration:**
```bash
# Copy the environment template
copy .env.template .env  # Windows
cp .env.template .env    # macOS/Linux
```

**Edit `.env` file with minimum required settings:**
```bash
# Database Configuration
DATABASE_URL=sqlite:///backend/instance/bugseek.db

# API Configuration
BACKEND_API_URL=http://localhost:5000

# Redis (optional - for background tasks)
REDIS_URL=redis://localhost:6379/0

# OpenAI (optional - for AI features)
OPENAI_API_KEY=your-api-key-here
AI_ANALYSIS_ENABLED=True
```

### Step 3: Initialize Database with Sample Data

**Option A: Full Initialization (Recommended)**
```bash
# Initialize database schema and populate with 30+ realistic sample logs
python init_database.py
```

This script will:
- Create all database tables with proper schema
- Generate 30+ realistic error logs with:
  - Varied teams (Frontend, Backend, API, DevOps, Security, etc.)
  - Different modules (Authentication, Database, Payment, etc.)
  - Realistic error content and timestamps
  - AI embeddings and solution flags
  - Proper severity levels and environments

**Option B: Manual Database Setup**
```bash
# Create database schema only
python -c "from backend.app import create_app; from backend.models import create_tables; app = create_app(); create_tables(app)"

# Then manually add data via the UI
```

**Option C: Setup with AI Tables (for AI features)**
```bash
# First initialize basic database
python init_database.py

# Then add AI analysis tables
python migrate_ai_tables.py
```

### Step 4: Verify Database Setup

**Check database and sample data:**
```bash
# Use the interactive database viewer
python db_viewer.py
```

In the database viewer:
1. Select option **1** (Database Overview) to see all tables
2. Select option **2** (Browse Tables) → **1** (error_logs) to view sample data
3. Select option **9** (Error Log Analytics) for team and module statistics

**Quick verification:**
```bash
# Test database connection
python -c "from db_connection import DatabaseConnection; db = DatabaseConnection(); print('✅ Connected!' if db.connect() else '❌ Connection failed'); db.close()"
```

### Step 5: Start the Application

**Option A: Start Both Services (Recommended)**
```bash
# Starts both backend (port 5000) and frontend (port 8080)
python run.py
```

**Option B: Start Services Individually**
```bash
# Terminal 1: Start Backend API
python run.py --backend
# Or manually: cd backend && python app.py

# Terminal 2: Start Frontend
python run.py --frontend
# Or manually: cd frontend && streamlit run app.py
# Or Flask alternative: cd frontend && python fast_app.py
```

**Option C: With Background Worker (Full Stack)**
```bash
# Terminal 1: Backend
python run.py --backend

# Terminal 2: Frontend  
python run.py --frontend

# Terminal 3: Celery Worker (optional)
cd backend && celery -A celery_worker.celery worker --loglevel=info
```

### Step 6: Access and Verify

**Application URLs:**
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api/docs/
- **Frontend UI**: http://localhost:8501 (Streamlit) or http://localhost:8080 (Flask)
- **Health Check**: http://localhost:5000/api/v1/health

**Verify Sample Data:**
1. Open the frontend URL
2. Navigate to **Search** section
3. Click **"🔍 Search"** without filters to see all 30+ sample logs
4. Check **Dashboard** for statistics showing:
   - Total logs: 30+
   - Multiple teams and modules
   - Mix of solved/unsolved issues

### Sample Data Overview

The initialization script creates realistic error logs including:

**Teams Represented:**
- Frontend (React, UI, WebSocket)
- Backend (Database, Microservices, Caching)
- API (Payment, GraphQL, Rate Limiting)
- DevOps (Docker, CI/CD, Deployment)
- Security (Authentication, SSL, WAF)
- QA (Testing, Load Testing)
- Mobile (iOS, Android, Push Notifications)
- Data Science (ML Pipeline, ETL, Recommendations)
- Infrastructure (Monitoring, Load Balancer)

**Error Types:**
- Authentication timeouts
- Database query issues
- Payment gateway errors
- Container deployment failures
- Memory/performance issues
- Network connectivity problems
- Security incidents
- And many more realistic scenarios

**Data Features:**
- Timestamps spanning the last 45 days
- Realistic error messages and stack traces
- Various file sizes and content types
- Mixed solution availability (solved/pending)
- AI embeddings for similarity matching
- Proper severity levels (low/medium/high/critical)
- Environment categorization (dev/staging/prod)

### Viewing Tables and Data

**Database Tables Created:**
1. **error_logs** - Main error log entries
2. **error_log_files** - File metadata (if AI features enabled)
3. **ai_analysis_results** - AI analysis results (if AI features enabled)
4. **openai_status** - OpenAI connection tracking (if AI features enabled)
5. **similar_log_matches** - Log similarity relationships (if AI features enabled)

**Interactive Database Exploration:**
```bash
# Launch database viewer for exploration
python db_viewer.py

# Options available:
# 1. Database Overview - See all tables and counts
# 2. Browse Tables - Interactive table selection
# 3. Table Inspector - Deep dive into table structure
# 4. Search Data - Search across all tables
# 5. Execute Custom Query - Run SQL queries
# 6. Common Queries - Pre-built analytics queries
# 7. Export Data - Export results to CSV/JSON
# 8. Database Statistics - Comprehensive analytics
# 9. Error Log Analytics - BugSeek-specific analysis
```

### Database Operations

**Quick database initialization (for development):**
```bash
# Create empty database schema
python -c "from backend.app import create_app; from backend.models import create_tables; app = create_app(); create_tables(app)"
```

**Full database setup with sample data:**
```bash
# Initialize with 30+ realistic sample logs (recommended for new setup)
python init_database.py
```

**AI features setup:**
```bash
# Add AI analysis tables
python migrate_ai_tables.py
python migrate_ai_tables.py --check  # Check migration status
```

**Database exploration:**
```bash
# Interactive database viewer with analytics
python db_viewer.py
```

> **Note**: For complete setup instructions including sample data, see the "Complete Setup Guide for New Machine" section above.
```

**Database viewer (interactive CLI):**
```bash
python database_viewer.py   # Interactive database explorer
python db_viewer.py         # Alternative database viewer
```

### Running the Application

**Start both services (recommended):**
```bash
python run.py
```

**Start individual services:**
```bash
python run.py --backend    # Flask API on port 5000
python run.py --frontend   # Frontend on port 8080
```

**Manual service startup:**
```bash
# Backend
cd backend && python app.py

# Frontend (Streamlit)
cd frontend && streamlit run app.py

# Frontend (Fast Flask alternative)
cd frontend && python fast_app.py
```

**Background worker:**
```bash
cd backend && celery -A celery_worker.celery worker --loglevel=info
```

### Testing

**Run all tests:**
```bash
pytest
```

**Run specific test categories:**
```bash
pytest tests/test_api.py      # API endpoint tests
pytest tests/test_models.py   # Database and model tests
pytest -m unit               # Unit tests only
pytest -m integration        # Integration tests only
```

**Run tests with coverage:**
```bash
pytest --cov=backend --cov-report=html
```

**Run a single test file:**
```bash
pytest tests/test_api.py::TestLogUploadAPI::test_upload_log_success -v
```

## Key Architectural Concepts

### Database Schema Design

The system uses a modern multi-table approach:

1. **ErrorLog**: Main error log metadata with text preview
2. **ErrorLogFile**: Full file storage with integrity checks (SHA256)
3. **AIAnalysisResult**: AI analysis results and caching
4. **OpenAIStatus**: API usage tracking and status
5. **SimilarLogMatch**: Similarity relationships between logs

**Key Relationships:**
- ErrorLog 1:N ErrorLogFile (supports multiple files per error)
- ErrorLog 1:N AIAnalysisResult (supports multiple AI analyses)
- ErrorLog N:N SimilarLogMatch (similarity graph)

### Service Architecture

- **ErrorLogService**: CRUD operations, filtering, statistics
- **FileService**: File upload, storage, integrity checking
- **NLPService**: Text embeddings, similarity matching (placeholder for full implementation)
- **GenAIService**: AI summary generation, solution suggestions (placeholder)
- **AIAnalysisService**: Full AI analysis pipeline with OpenAI integration
- **OpenAIService**: OpenAI/Azure OpenAI API integration with retry logic

### API Design Patterns

- RESTful endpoints with consistent JSON responses
- Swagger/OpenAPI 3.0 documentation at `/api/docs/`
- Standardized error handling with success/error response format
- Request validation using Flask-RESTx parsers
- Pagination for list endpoints

### Configuration Management

The application uses a three-tier configuration system:
1. **Environment variables** (`.env` file)
2. **Config classes** (`config/settings.py`) 
3. **Runtime overrides** (Flask app config)

**Environment Types:**
- `development`: Default, debug enabled
- `production`: Debug disabled, optimized settings  
- `testing`: In-memory SQLite for tests

### Background Task System

Uses Celery with Redis broker for:
- **Log processing**: NLP embeddings, content analysis
- **Report generation**: Comprehensive AI-powered reports  
- **Bulk operations**: Processing multiple logs
- **Maintenance**: File cleanup, health checks

### AI Integration Architecture

**OpenAI Service Features:**
- Azure OpenAI gateway support (MediaTek endpoint pre-configured)
- Automatic retry with exponential backoff
- Usage tracking and cost estimation
- Connection health monitoring
- Graceful fallback to pattern-based analysis

**AI Analysis Pipeline:**
1. Content preprocessing and truncation
2. Pattern recognition (regex-based fallback)
3. OpenAI API calls for analysis
4. Results caching in database
5. Similarity matching using TF-IDF or embeddings

## Important File Locations

**Configuration:**
- `.env` / `.env.template` - Environment configuration
- `config/settings.py` - Application configuration classes

**Database:**  
- `backend/models.py` - SQLAlchemy models and relationships
- `migrate_ai_tables.py` - AI feature database migration
- `backend/instance/bugseek.db` - SQLite database file

**API Layer:**
- `backend/app.py` - Flask application factory and API routes
- `backend/services.py` - Business logic services

**Frontend:**
- `frontend/app.py` - Streamlit UI application
- `frontend/fast_app.py` - Alternative Flask frontend
- `frontend/templates/` - HTML templates for Flask frontend
- `frontend/static/` - CSS, JavaScript, and other static assets

**Background Processing:**
- `backend/celery_worker.py` - Celery configuration
- `backend/tasks.py` - Background task definitions

**AI Services:**
- `backend/ai_services.py` - OpenAI integration and AI analysis
- `AI_FEATURES.md` - AI features documentation

## Development Guidelines

### Database Operations

**Always use the service layer** for database operations rather than direct model access:
```python
# Good
result = ErrorLogService.create_error_log(data)

# Avoid
error_log = ErrorLog(**data)
db.session.add(error_log)
```

### API Response Format

All API endpoints return consistent JSON format:
```python
{
    "success": true/false,
    "message": "Human readable message", 
    "data": {...},  # On success
    "error": "Error details"  # On failure
}
```

### Error Handling

The application uses structured exception handling:
- Service layer catches exceptions and returns structured responses
- API layer validates inputs and handles service responses
- Database operations use transactions with rollback

### AI Features Integration

When working with AI features:
- Check `AI_SERVICES_AVAILABLE` flag before using AI services
- Always provide fallback behavior for when OpenAI is unavailable
- Use the pattern-based analysis as fallback
- Respect rate limits and token usage

## Environment Variables

**Required Environment Variables:**
- `DATABASE_URL`: SQLite path or PostgreSQL connection
- `SECRET_KEY`: Flask secret key for sessions
- `OPENAI_API_KEY`: OpenAI/Azure OpenAI API key (for AI features)

**Optional but Recommended:**
- `REDIS_URL`: Redis connection for background tasks
- `BACKEND_API_URL`: Frontend-to-backend communication
- `AI_ANALYSIS_ENABLED`: Enable/disable AI features

**MediaTek-specific Configuration:**
Pre-configured for MediaTek Azure OpenAI gateway:
- Endpoint: `https://mlop-azure-gateway.mediatek.inc`
- Model: `aida-gpt-4o-mini`
- API Version: `2024-10-21`

## API Documentation

The BugSeek API documentation is available at the Swagger UI endpoint:
```
http://localhost:5000/api/docs/
```

### Core Endpoints

**Upload Log:**
```http
POST /api/v1/logs/upload
Content-Type: multipart/form-data
```

**List Logs:**
```http
GET /api/v1/logs/
Parameters: page, per_page, TeamName, Module, ErrorName, Owner, SolutionPossible, search
```

**Get Report:**
```http
GET /api/v1/reports/{cr_id}
```

**Health Check:**
```http
GET /api/v1/health/
```

**Statistics:**
```http
GET /api/v1/statistics
```

### AI Endpoints

**OpenAI Status:**
```http
GET /api/v1/openai/status
```

**AI Analysis:**
```http
POST /api/v1/ai/analyze/{cr_id}
```

## Troubleshooting

### Common Issues

**Connection Refused Error:**
- Ensure Flask backend is running on port 5000
- Check `BACKEND_API_URL` in `.env` file

**Database Lock Errors:**
- Close any database connections
- Restart the application
- Check file permissions on SQLite database

**File Upload Issues:**
- Verify `uploads/` directory exists and is writable
- Check file size limits (16MB default)
- Ensure supported file formats (TXT, LOG, JSON, XML)

**Redis Connection Errors:**
- Install and start Redis server
- Update `REDIS_URL` in `.env`
- Skip Celery worker for basic functionality

**OpenAI Connection Issues:**
- Verify API key is set correctly in `.env`
- Check network connectivity to Azure endpoint
- Verify API key permissions and quotas

### Debug Mode

Enable debug logging:
```bash
# In .env file
FLASK_DEBUG=True

# Run with verbose logging
python backend/app.py --debug
```

## Testing and Quality Assurance

### Testing Strategy

- **Unit tests**: Individual functions and methods (`pytest tests/test_models.py`)
- **Integration tests**: Service interactions and database operations  
- **API tests**: Full HTTP request/response cycles (`pytest tests/test_api.py`)
- **Fixtures**: Use `tests/conftest.py` for test setup and sample data

### Test Coverage

The project maintains 95%+ test coverage. Key test areas:
- All API endpoints with success and error cases
- Database model operations and relationships
- Service layer business logic
- File upload and validation
- AI integration with mocked responses

### Performance Benchmarks

- **API Response Time**: < 200ms average
- **File Upload**: Supports up to 16MB files
- **Database Queries**: Optimized with proper indexing
- **Search Performance**: Sub-second response for 10k+ records

## Development Workflow

This architecture supports rapid development while maintaining code quality and system reliability. The modular design allows for easy extension and modification of individual components.

### Adding New Features

1. **Database Changes**: Update models in `backend/models.py`
2. **Service Layer**: Add business logic to appropriate service class
3. **API Layer**: Add endpoints with proper documentation in `backend/app.py`
4. **Frontend**: Update UI components in frontend files
5. **Tests**: Add comprehensive tests for new functionality

### Code Quality Standards

- Follow PEP 8 Python style guidelines
- Use type hints where helpful
- Maintain comprehensive docstrings
- Ensure all new code has corresponding tests
- Use the service layer pattern for business logic

## Quick Reference

### For New Developers

**Complete setup with data:**
```bash
git clone <repo> && cd BugSeek
python -m venv venv && venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.template .env  # Edit DATABASE_URL if needed
python init_database.py
python run.py
```

**Verify setup:**
```bash
# Check database
python db_viewer.py  # Option 1 for overview

# Check API
curl http://localhost:5000/api/v1/health

# Check frontend
# Visit http://localhost:8501 or http://localhost:8080
```

### For Daily Development

**Start development environment:**
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
python run.py
```

**Common database tasks:**
```bash
# View all data
python db_viewer.py  # Interactive menu

# Reset with fresh sample data
python init_database.py

# Add AI tables
python migrate_ai_tables.py
```

**Testing:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test
pytest tests/test_api.py::TestLogUploadAPI::test_upload_log_success -v
```

### For Production Deployment

**Environment setup:**
```bash
# Use production config
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@host:port/dbname

# Install production dependencies only
pip install -r backend/requirements.txt
```

**Database migration:**
```bash
# Create schema (without sample data)
python -c "from backend.app import create_app; from backend.models import create_tables; app = create_app('production'); create_tables(app)"
```

This comprehensive guide ensures anyone can clone the repository and have a fully functional BugSeek system with realistic sample data within minutes.
- `backend/tasks.py` - Background task definitions

**AI Services:**
- `backend/ai_services.py` - OpenAI integration and AI analysis
- `AI_FEATURES.md` - AI features documentation

## Development Guidelines

### Database Operations

**Always use the service layer** for database operations rather than direct model access:
```python
# Good
result = ErrorLogService.create_error_log(data)

# Avoid
error_log = ErrorLog(**data)
db.session.add(error_log)
```

### API Response Format

All API endpoints return consistent JSON format:
```python
{
    "success": true/false,
    "message": "Human readable message", 
    "data": {...},  # On success
    "error": "Error details"  # On failure
}
```

### Error Handling

The application uses structured exception handling:
- Service layer catches exceptions and returns structured responses
- API layer validates inputs and handles service responses
- Database operations use transactions with rollback

### AI Features Integration

When working with AI features:
- Check `AI_SERVICES_AVAILABLE` flag before using AI services
- Always provide fallback behavior for when OpenAI is unavailable
- Use the pattern-based analysis as fallback
- Respect rate limits and token usage

### Testing Strategy

- **Unit tests**: Individual functions and methods
- **Integration tests**: Service interactions and database operations  
- **API tests**: Full HTTP request/response cycles
- **Fixtures**: Use `tests/conftest.py` for test setup

### Performance Considerations

- Database queries use proper indexes (defined in models)
- File uploads are streamed and validated
- Large log files are truncated for preview display
- Background processing for expensive operations
- Caching of AI analysis results

## Environment Setup Notes

**Required Environment Variables:**
- `DATABASE_URL`: SQLite path or PostgreSQL connection
- `SECRET_KEY`: Flask secret key for sessions
- `OPENAI_API_KEY`: OpenAI/Azure OpenAI API key (for AI features)

**Optional but Recommended:**
- `REDIS_URL`: Redis connection for background tasks
- `BACKEND_API_URL`: Frontend-to-backend communication
- `AI_ANALYSIS_ENABLED`: Enable/disable AI features

**MediaTek-specific Configuration:**
Pre-configured for MediaTek Azure OpenAI gateway:
- Endpoint: `https://mlop-azure-gateway.mediatek.inc`
- Model: `aida-gpt-4o-mini`
- API Version: `2024-10-21`

## Sample Data Structure

When using `setup_project.py` or `init_database.py`, the database is populated with realistic sample data:

**Sample Data Includes:**
- **Teams**: Frontend, Backend, API, DevOps, QA, Security, Infrastructure, Mobile
- **Modules**: Authentication, Database, Payment, Deployment, Dashboard, FileUpload, Testing, Monitoring, Push Notifications
- **Severity Levels**: low, medium, high, critical
- **Environments**: dev, staging, prod, unknown
- **Realistic log content** with proper timestamps and error messages
- **Solution status** indicating which errors have known solutions
- **File metadata** including realistic file sizes and names

**Sample Log Examples:**
- Login timeouts on mobile apps
- SQL query performance issues
- Payment gateway failures
- Docker container startup problems
- Chart rendering memory errors
- Security incidents and monitoring alerts

This sample data provides a comprehensive foundation for testing all BugSeek features including search, filtering, analytics, and AI analysis capabilities.

## Common Development Tasks

### Adding New Error Log Fields

1. Update `ErrorLog` model in `backend/models.py`
2. Create database migration (manual SQL or Alembic if added)
3. Update `ErrorLogService` methods
4. Update API request parsers and response models
5. Update frontend forms and display logic

### Adding New AI Analysis Features

1. Extend `AIAnalysisService` in `backend/ai_services.py`
2. Update `AIAnalysisResult` model if new fields needed
3. Add new background tasks in `backend/tasks.py`
4. Update API endpoints for new analysis types
5. Update frontend to display new analysis results

### Extending Search and Filtering

1. Add new filter parameters in `ErrorLogService.get_error_logs()`
2. Update API request parsers for new filter fields
3. Add corresponding frontend filter controls
4. Consider adding database indexes for new searchable fields

### Custom Report Generation

1. Create new task in `backend/tasks.py`
2. Add service methods for data aggregation
3. Create API endpoint for report generation
4. Add frontend UI for report configuration and display

This architecture supports rapid development while maintaining code quality and system reliability. The modular design allows for easy extension and modification of individual components.
