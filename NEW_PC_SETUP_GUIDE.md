# 🚀 BugSeek - Complete Setup Guide for New PC

This guide will help you set up the BugSeek Error Log Management System on a new computer from scratch.

## 📋 Prerequisites

### Required Software
- **Python 3.8 or higher** - [Download from python.org](https://python.org/downloads)
- **Git** - [Download from git-scm.com](https://git-scm.com/downloads)
- **Web Browser** with JavaScript enabled
- **Windows PowerShell** (Windows) or **Terminal** (macOS/Linux)

### System Requirements
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space
- **Network**: Internet connection for initial setup

## 🛠️ Step-by-Step Setup

### Step 1: Verify Prerequisites

```powershell
# Check Python version (must be 3.8+)
python --version

# Check Git installation
git --version

# Check if pip is available
python -m pip --version
```

### Step 2: Clone or Copy the Project

**Option A: From Git Repository**
```powershell
git clone <repository-url>
cd BugSeek
```

**Option B: From Project Files**
```powershell
# Copy the BugSeek folder to your desired location
cd path\to\BugSeek
```

### Step 3: Create Virtual Environment (Recommended)

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
venv\Scripts\Activate.ps1

# Windows Command Prompt:
venv\Scripts\activate.bat

# macOS/Linux:
source venv/bin/activate
```

If you get execution policy errors on Windows:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 4: Install Dependencies

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**If requirements.txt is missing, install manually:**
```powershell
pip install flask flask-restx flask-cors flask-sqlalchemy sqlalchemy python-dotenv requests celery redis streamlit pandas plotly pytest
```

### Step 5: Configure Environment

**Create or update the `.env` file:**

```powershell
# Windows
Copy-Item .env.template .env

# macOS/Linux
cp .env.template .env
```

**Edit `.env` file with these critical settings:**
```env
# Database Configuration (IMPORTANT: Use absolute path)
DATABASE_URL=sqlite:///C:/path/to/your/BugSeek/instance/bugseek.db

# Flask Configuration
FLASK_DEBUG=True
FLASK_ENV=development

# Backend API Configuration
BACKEND_API_URL=http://localhost:5000

# CORS Configuration
CORS_ORIGINS=*

# Upload Configuration
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=16777216

# AI Analysis Configuration
AI_ANALYSIS_ENABLED=True

# OpenAI Configuration (optional)
OPENAI_API_KEY=your-api-key-here
```

### Step 6: Initialize Database and Load Sample Data

```powershell
# Create required directories
New-Item -ItemType Directory -Force -Path "instance"
New-Item -ItemType Directory -Force -Path "uploads"

# Initialize database with schema
python 1_initialize_database.py

# Load sample data (23 realistic error logs)
python 2_load_sample_data.py

# Optional: Add special test cases
python 3_add_special_cases_sample_data.py
```

### Step 7: Verify Database Setup

```powershell
# Check database contents
python 4_view_database.py

# Or run a quick test
python -c "from backend.models import db, ErrorLog; from backend.app import create_app; app=create_app(); app.app_context().push(); print(f'Records in database: {ErrorLog.query.count()}')"
```

You should see **23 error logs** if everything is set up correctly.

### Step 8: Start the Application

**Option A: Start Both Services Together (Recommended)**
```powershell
python run.py
```

**Option B: Start Services Separately**
```powershell
# Terminal 1 - Backend
python run.py --backend

# Terminal 2 - Frontend
python run.py --frontend
```

### Step 9: Access the Application

Once started, open your web browser and navigate to:

- **Frontend UI**: http://localhost:8080
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api/docs/

**Default Login (if prompted):**
- Password: `hackathon2025`

## 🧪 Testing the Setup

### 1. Test Backend API
```powershell
# Windows
Invoke-WebRequest -Uri "http://localhost:5000/api/v1/health/" -UseBasicParsing

# Should return status 200 with JSON response
```

### 2. Test Database Connection
```powershell
python test_db.py
```

### 3. Test Search Functionality
1. Go to http://localhost:8080/search
2. Click "Search Logs" (without filters)
3. You should see 23 sample error logs

## 🔧 Configuration Details

### Database Configuration
The most critical configuration is the database path in `.env`:

```env
# ❌ Wrong (relative path - causes issues)
DATABASE_URL=sqlite:///bugseek.db

# ✅ Correct (absolute path)
DATABASE_URL=sqlite:///C:/full/path/to/BugSeek/instance/bugseek.db
```

### Port Configuration
Default ports:
- Backend: `5000`
- Frontend: `8080`

If ports are in use, the application will suggest alternatives.

## 🚨 Troubleshooting

### Common Issues and Solutions

#### "Python not found"
```powershell
# Check if Python is in PATH
python --version
# If not found, add Python to system PATH or use full path
C:\Users\YourName\AppData\Local\Programs\Python\Python39\python.exe
```

#### "Module not found" errors
```powershell
# Ensure virtual environment is activated
venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

#### "Database not found" errors
1. Check `.env` file has correct absolute path to database
2. Ensure `instance` directory exists
3. Run database initialization again:
   ```powershell
   python 1_initialize_database.py
   python 2_load_sample_data.py
   ```

#### "Port already in use"
```powershell
# Check what's using the ports
netstat -an | findstr "5000 8080"

# Kill processes or restart your computer
# The application will suggest alternative ports
```

#### "JavaScript not working"
1. Ensure JavaScript is enabled in your browser
2. Check browser console for errors (F12)
3. Verify both backend and frontend are running
4. Check CORS settings in `.env`

#### "No data showing in search"
1. Verify database has data:
   ```powershell
   python check_tables.py
   ```
2. Test API directly:
   ```powershell
   Invoke-WebRequest -Uri "http://localhost:5000/api/v1/logs/?page=1&per_page=5" -UseBasicParsing
   ```
3. Restart both backend and frontend services

### Debug Commands
```powershell
# Test database connection
python debug_api.py

# Check all processes
Get-Process | Where-Object {$_.ProcessName -eq "python"}

# View logs in real-time (if implemented)
python backend/app.py  # Shows Flask debug output
```

## 📁 Expected Project Structure

After setup, your directory should look like:

```
BugSeek/
├── run.py                    # Main startup script
├── .env                      # Environment configuration
├── requirements.txt          # Python dependencies
├── backend/
│   ├── app.py               # Flask API server
│   ├── models.py            # Database models
│   ├── services.py          # Business logic
│   └── requirements.txt     # Backend dependencies
├── frontend/
│   ├── fast_app.py          # Frontend server
│   ├── templates/           # HTML templates
│   └── static/             # CSS/JS files
├── config/
│   └── settings.py         # Configuration
├── instance/
│   └── bugseek.db          # Database file (auto-created)
├── uploads/                # Uploaded files directory
├── venv/                   # Virtual environment
└── tests/                  # Test files
```

## 🎯 Verification Checklist

Before considering setup complete, verify:

- [ ] Python 3.8+ installed and accessible
- [ ] Virtual environment created and activated
- [ ] All dependencies installed without errors
- [ ] `.env` file configured with correct absolute database path
- [ ] Database initialized and contains 23 sample records
- [ ] Backend starts without errors (port 5000)
- [ ] Frontend starts without errors (port 8080)
- [ ] Health check returns 200: http://localhost:5000/api/v1/health/
- [ ] Search page loads: http://localhost:8080/search
- [ ] Search returns data (click "Search Logs" button)
- [ ] API documentation accessible: http://localhost:5000/api/docs/

## 🚀 Sample Data Overview

The setup includes 23 realistic error logs across:

### Teams
- Frontend (2 logs)
- Backend (2 logs)
- API (1 log)
- DevOps (1 log)
- QA (1 log)
- Security (1 log)
- Infrastructure (1 log)
- Mobile (2 logs)
- Data Science (1 log)
- Network (1 log)
- Platform (1 log)
- Analytics (1 log)

### Severities
- Critical (4 logs)
- High (4 logs)
- Medium (7 logs)

### Features to Test
- **Search & Filter**: By team, module, owner, severity
- **Analytics Dashboard**: Team performance metrics
- **Detailed Reports**: Individual log analysis
- **File Upload**: Add your own log files
- **AI Features**: If OpenAI API key is configured

## 📞 Support

If you encounter issues during setup:

1. **Check this troubleshooting guide** first
2. **Verify all prerequisites** are met
3. **Check console output** for specific error messages
4. **Validate configuration** files (especially `.env`)
5. **Test individual components** using debug commands

## ✅ Success Indicators

Setup is successful when:
- ✅ Both services start without errors
- ✅ Search page shows 23 sample error logs
- ✅ Filtering and pagination work correctly
- ✅ API endpoints respond correctly
- ✅ No JavaScript errors in browser console

---

**Happy Bug Hunting with BugSeek! 🐛🔍**
