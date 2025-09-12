# 🚀 BugSeek - Quick Setup Guide

Get BugSeek up and running in minutes! This guide covers everything from installation to your first error log analysis.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: 2GB minimum (4GB recommended)
- **Storage**: 500MB free space
- **Internet**: Required for AI features (optional for basic functionality)

### Check Python Installation
```bash
python --version
# or
python3 --version
```

If Python is not installed, download from [python.org](https://python.org/downloads)

## ⚡ Quick Start (3-Minute Setup)

### 1. Download and Extract
```bash
# If you have the project files, navigate to the directory
cd BugSeek

# Or clone from repository (if available)
git clone <repository-url>
cd BugSeek
```

### 2. Install Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r backend/requirements.txt
```

### 3. Initialize Database
```bash
# Run the database setup script
python 1_initialize_database.py
```

### 4. Start the Application
```bash
# Start both frontend and backend
python run.py

# Or start individually:
# Backend: python run.py --backend
# Frontend: python run.py --frontend
```

### 5. Access BugSeek
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api/docs/

### 6. Login
- **Password**: `hackathon2025`

**🎉 You're ready to go!**

---

## 🔧 Detailed Setup Instructions

### Step 1: Environment Setup

#### Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv bugseek-env

# Activate it
# Windows Command Prompt:
bugseek-env\Scripts\activate.bat

# Windows PowerShell:
bugseek-env\Scripts\Activate.ps1

# macOS/Linux:
source bugseek-env/bin/activate
```

#### Install Dependencies
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install backend dependencies
pip install -r backend/requirements.txt

# If requirements.txt is missing, install manually:
pip install flask flask-restx flask-cors sqlalchemy python-dotenv

# Optional: Install AI dependencies (if using OpenAI)
pip install openai
```

### Step 2: Database Configuration

#### Initialize Database
```bash
# Initialize the database with tables
python 1_initialize_database.py

# Load sample data (optional)
python 2_load_sample_data.py

# Add special test cases (optional)
python 3_add_special_cases_sample_data.py
```

#### Verify Database Setup
```bash
# Check database contents
python 4_view_database.py
```

### Step 3: Configuration

#### Create Environment File (Optional)
```bash
# Create .env file for configuration
touch .env

# Add the following content:
DEBUG=True
FLASK_ENV=development
UPLOAD_FOLDER=./uploads
DATABASE_URL=sqlite:///instance/bugseek.db
AI_ANALYSIS_ENABLED=True
```

#### Configure AI Services (Optional)
If you have OpenAI API access:
```bash
# Add to .env file
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

### Step 4: File Structure Verification

Ensure your directory structure looks like this:
```
BugSeek/
├── run.py                          # Main application runner
├── backend/
│   ├── app.py                      # Backend API server
│   ├── models.py                   # Database models
│   ├── services.py                 # Business logic
│   ├── ai_services.py             # AI integration
│   └── requirements.txt           # Dependencies
├── frontend/
│   ├── fast_app.py                # Frontend server
│   ├── templates/                 # HTML templates
│   └── static/                    # CSS/JS files
├── config/
│   └── settings.py               # Configuration
├── instance/                     # Database files
├── uploads/                      # Uploaded files
└── README.md
```

### Step 5: Start Services

#### Option 1: Start Both Services (Recommended)
```bash
python run.py
```

#### Option 2: Start Services Separately
```bash
# Terminal 1 - Backend
python run.py --backend

# Terminal 2 - Frontend
python run.py --frontend
```

#### Option 3: Manual Start
```bash
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend
cd frontend
python fast_app.py
```

---

## 🌐 Accessing the Application

### Web Interface
1. Open browser and go to: http://localhost:8080
2. Enter password: `hackathon2025`
3. Start uploading error logs!

### API Documentation
- Swagger UI: http://localhost:5000/api/docs/
- API Base URL: http://localhost:5000/api/v1/

### Health Check
```bash
# Check if services are running
curl http://localhost:5000/api/v1/health
curl http://localhost:8080/api/health
```

---

## 📁 Sample Usage

### 1. Upload Your First Log

#### Via Web Interface:
1. Go to Upload page
2. Select a log file (TXT, LOG, JSON, XML)
3. Fill in metadata:
   - Team Name: "Backend Team"
   - Module: "Authentication"
   - Owner: "your.email@company.com"
   - Description: "Login timeout issues"
4. Click "Upload & Analyze Log"

#### Via API:
```bash
curl -X POST http://localhost:5000/api/v1/logs/upload \
  -F "file=@error.log" \
  -F "TeamName=Backend Team" \
  -F "Module=Authentication" \
  -F "Owner=test@example.com" \
  -F "Description=Sample error log"
```

### 2. View Analysis Report
- The system will redirect you to the report page
- Or access via: http://localhost:8080/report/{CR_ID}

### 3. Search and Filter Logs
- Use the Search page to find specific logs
- Filter by team, module, owner, or content

---

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `False` |
| `FLASK_ENV` | Flask environment | `production` |
| `DATABASE_URL` | Database connection | `sqlite:///instance/bugseek.db` |
| `UPLOAD_FOLDER` | File upload directory | `./uploads` |
| `MAX_CONTENT_LENGTH` | Max file size | `16MB` |
| `AI_ANALYSIS_ENABLED` | Enable AI features | `True` |
| `OPENAI_API_KEY` | OpenAI API key | `None` |

### Application Settings

Edit `config/settings.py` to modify:
- Database configuration
- File upload limits
- AI service settings
- CORS origins
- Security settings

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using the port
netstat -an | findstr :8080    # Windows
lsof -i :8080                  # macOS/Linux

# Kill the process or use different port
python run.py  # Will show available ports
```

#### 2. Database Connection Error
```bash
# Reinitialize database
python 1_initialize_database.py

# Check database file exists
ls instance/bugseek.db
```

#### 3. Module Not Found Error
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r backend/requirements.txt
```

#### 4. File Upload Issues
```bash
# Check upload folder exists and is writable
mkdir -p uploads
chmod 755 uploads
```

#### 5. AI Services Not Working
- AI features will use intelligent fallbacks
- Check `backend/ai_services.py` exists
- For real AI: Add OpenAI API key to `.env`

### Log Files
- Backend logs: Console output
- Database issues: Check `instance/` directory
- File uploads: Check `uploads/` directory

### Getting Help
1. Check console output for error messages
2. Verify all prerequisites are met
3. Try the manual setup steps
4. Check file permissions
5. Ensure all required files are present

---

## 🚀 Production Deployment

### Prerequisites for Production
- Production-grade database (PostgreSQL/MySQL)
- Web server (Nginx/Apache)
- Process manager (Gunicorn/uWSGI)
- SSL certificate
- Monitoring tools

### Quick Production Setup
```bash
# Install production dependencies
pip install gunicorn psycopg2-binary

# Set production environment
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@localhost/bugseek

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

### Security Checklist
- [ ] Change default passwords
- [ ] Use HTTPS in production
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Enable logging and monitoring
- [ ] Update environment variables
- [ ] Use secrets management

---

## 📋 Development Setup

### For Developers

#### Additional Dependencies
```bash
# Development tools
pip install pytest pytest-cov black flake8 mypy

# Database tools
pip install sqlite-utils

# Optional: Testing tools
pip install requests-mock
```

#### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=backend

# Run specific test
python -m pytest tests/test_api.py
```

#### Code Quality
```bash
# Format code
black backend/ frontend/

# Lint code
flake8 backend/ frontend/

# Type checking
mypy backend/
```

---

## 📚 Next Steps

### Learn More
1. **System Design**: Read `SYSTEM_DESIGN.md` for architecture details
2. **API Documentation**: Visit http://localhost:5000/api/docs/
3. **User Guide**: Check the Documentation page in the web interface

### Extend the System
1. Add custom error patterns
2. Integrate with your monitoring tools
3. Customize AI analysis prompts
4. Add team-specific features
5. Implement custom dashboards

### Support
- Check existing documentation
- Review sample data and test cases
- Examine the codebase for examples
- Use the built-in help and documentation features

**Happy Bug Hunting! 🐛🔍**
