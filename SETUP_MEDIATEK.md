# MediaTek BugSeek Setup Guide

## ✅ FIXED: Complete Environment Configuration

The **`.env.mediatek`** file has been **completely fixed** with all necessary API configurations for both backend and frontend to work properly.

## 🚀 Quick Setup

### 1. Copy Environment Configuration
```powershell
Copy-Item ".env.mediatek" ".env"
```

### 2. Verify Setup
```powershell
python verify_setup.py
```

### 3. Edit API Credentials
Edit `.env` file and update these two critical values:
```bash
# Get these from MediaTek hackathon organizer
AZURE_API_KEY=your_actual_jwt_token_from_mediatek_here
USER_ID=your_mtk_employee_id_here  # Example: mtk34708
```

### 4. Test API Connection
```powershell
python test_mediatek_api.py
```

### 5. Start Application
```powershell
python run.py
```

## 📋 What's Fixed in .env.mediatek

### ✅ Database Configuration
- **Fixed absolute path**: `sqlite:///G:/Projects/Hackathon/Problem2/BugSeek/instance/bugseek.db`
- **SQLAlchemy settings**: Proper tracking configuration

### ✅ API Configuration (Critical)
- **API_VERSION**: `v1`
- **CORS_ORIGINS**: `*` (allows frontend-backend communication)
- **BACKEND_API_URL**: `http://localhost:5000`

### ✅ Flask Configuration
- **FLASK_DEBUG**: `True`
- **SECRET_KEY**: Secure key for sessions
- **All debugging settings**: Properly configured

### ✅ MediaTek Azure OpenAI
- **ENDPOINT_URL**: `https://mlop-azure-gateway.mediatek.inc`
- **MODEL_NAME**: `aida-gpt-4o-mini`
- **API_VERSION**: `2024-10-21`
- **Enhanced timeout**: `45` seconds for MediaTek gateway

### ✅ File Upload Settings
- **UPLOAD_FOLDER**: `uploads`
- **MAX_CONTENT_LENGTH**: `16777216` (16MB)

### ✅ AI Service Configuration
- **AI_ANALYSIS_ENABLED**: `True`
- **AI_MAX_RETRIES**: `3`
- **AI_REQUEST_TIMEOUT**: `45` (increased for MediaTek)
- **AI_BATCH_SIZE**: `10`

### ✅ Optional Services
- **Redis/Celery**: Configured for async processing
- **Streamlit**: Port configuration
- **Logging**: Proper log file paths

## 🔑 Getting Your API Key

According to the requirements document:

> **Q3: How can I get GenAI Services?**  
> **A:** You can get the Key from me offline in Teams chat. Attached the GenAI.txt which is a Python Script which has the sample script.

### Steps:
1. **Contact the hackathon organizer** via Teams chat
2. **Request the GenAI.txt file** with API credentials
3. **Copy the JWT token** to `AZURE_API_KEY` in `.env`
4. **Add your employee ID** to `USER_ID` in `.env`

## 🌐 Application URLs

When running, access these URLs:
- **Frontend**: http://localhost:8080
- **Backend**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api/docs/

## 🔍 Troubleshooting

### If APIs stop working after copying .env.mediatek to .env:

✅ **FIXED!** The new `.env.mediatek` includes all necessary configurations:
- Database path (absolute path for Windows)
- API configuration for frontend-backend communication  
- CORS settings for cross-origin requests
- All Flask and upload settings
- Complete MediaTek AI service configuration

### Verification Commands:
```powershell
# 1. Verify setup
python verify_setup.py

# 2. Test API connection  
python test_mediatek_api.py

# 3. Start application
python run.py
```

### Common Issues Fixed:
- ❌ Database path issues → ✅ Fixed with absolute path
- ❌ Frontend-backend API communication → ✅ Fixed with proper API_VERSION and BACKEND_API_URL
- ❌ CORS errors → ✅ Fixed with CORS_ORIGINS=*
- ❌ File upload failures → ✅ Fixed with proper UPLOAD_FOLDER and MAX_CONTENT_LENGTH
- ❌ AI service timeouts → ✅ Fixed with increased timeout values for MediaTek gateway

## 🎯 System Status

All APIs will work correctly once you:
1. Copy `.env.mediatek` to `.env` ✅ 
2. Add your actual MediaTek API credentials ⏳
3. Run the application ⏳

The environment configuration is now **complete and fixed** for the MediaTek hackathon setup!
