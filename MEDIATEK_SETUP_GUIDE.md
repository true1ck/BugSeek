# 🚀 BugSeek - MediaTek Environment Setup Guide

Complete setup guide for running BugSeek in the MediaTek development environment with Azure OpenAI integration.

## 📋 Prerequisites

### MediaTek Environment Requirements
- **Access to MediaTek Internal Network**: Required for Azure OpenAI gateway access
- **MediaTek Azure API Key**: Your JWT token for authentication
- **User ID**: Your MediaTek user ID (e.g., `mtk34708`)
- **Python 3.8+**: Available in MediaTek development environment
- **Network Access**: To `https://mlop-azure-gateway.mediatek.inc`

### Verify Your Access
Before starting, ensure you have:
1. ✅ MediaTek network access
2. ✅ Valid Azure API key (JWT token)
3. ✅ Your MediaTek user ID
4. ✅ Python installed and working

---

## ⚡ Quick MediaTek Setup (5 Minutes)

### Step 1: Clone and Setup Project
```bash
# Navigate to your development directory
cd /path/to/your/projects

# If you already have BugSeek, skip to Step 2
# Otherwise, extract the BugSeek project files
cd BugSeek
```

### Step 2: Configure MediaTek Environment
```bash
# Copy MediaTek environment template
cp .env.mediatek .env

# Edit the .env file with your MediaTek credentials
# Use your preferred editor (vim, nano, code, etc.)
code .env  # or vim .env
```

**Update these values in `.env`:**
```bash
# Replace with your actual MediaTek credentials
AZURE_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your_actual_jwt_token_here
USER_ID=your_mtk_user_id
ENDPOINT_URL=https://mlop-azure-gateway.mediatek.inc
MODEL_NAME=aida-gpt-4o-mini
API_VERSION=2024-10-21
```

### Step 3: Install Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install required packages
pip install -r backend/requirements.txt
```

### Step 4: Initialize Database
```bash
# Initialize database with tables
python 1_initialize_database.py

# Load sample data for demo
python 2_load_sample_data.py
```

### Step 5: Test MediaTek AI Connection
```bash
# Test the MediaTek AI service
python -c "
from backend.ai_services import OpenAIService
service = OpenAIService()
result = service.check_connection()
print('Connection Status:', result)
"
```

### Step 6: Start BugSeek
```bash
# Start both backend and frontend
python run.py
```

### Step 7: Access Application
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:5000
- **API Docs**: http://localhost:5000/api/docs/
- **Login Password**: `hackathon2025`

---

## 🔧 Detailed MediaTek Configuration

### MediaTek Environment Variables

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `AZURE_API_KEY` | Your MediaTek JWT token | `eyJhbGciOiJIUzI1NiIs...` |
| `USER_ID` | Your MediaTek user ID | `mtk34708` |
| `ENDPOINT_URL` | MediaTek Azure gateway | `https://mlop-azure-gateway.mediatek.inc` |
| `MODEL_NAME` | AI model to use | `aida-gpt-4o-mini` |
| `API_VERSION` | Azure OpenAI API version | `2024-10-21` |

### MediaTek Network Configuration
```bash
# Ensure network access to MediaTek gateway
curl -I https://mlop-azure-gateway.mediatek.inc

# Expected response: HTTP/2 200 or similar (not 404/403)
```

### MediaTek AI Service Test
Create a test file `test_mediatek_ai.py`:
```python
#!/usr/bin/env python3
import os
import requests
import json

# MediaTek configuration (update with your values)
AZURE_API_KEY = "your_jwt_token_here"
USER_ID = "your_user_id"
ENDPOINT_URL = "https://mlop-azure-gateway.mediatek.inc"
MODEL_NAME = "aida-gpt-4o-mini"
API_VERSION = "2024-10-21"

def test_mediatek_ai():
    """Test MediaTek AI service connection."""
    url = f"{ENDPOINT_URL}/openai/deployments/{MODEL_NAME}/chat/completions?api-version={API_VERSION}"
    
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "api-key": AZURE_API_KEY,
        "X-User-Id": USER_ID,
    }
    
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful log analyzer."},
            {"role": "user", "content": "Analyze this error: Connection timeout"}
        ],
        "max_tokens": 100,
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ MediaTek AI connection successful!")
            print(f"Response: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ Connection failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_mediatek_ai()
    if success:
        print("\n🎉 Your MediaTek environment is ready for BugSeek!")
    else:
        print("\n🔧 Please check your MediaTek credentials and network access.")
```

Run the test:
```bash
python test_mediatek_ai.py
```

---

## 🐛 Troubleshooting MediaTek Issues

### Common Issues and Solutions

#### 1. **Connection Refused / Network Error**
**Symptoms**: `Connection refused`, `Network is unreachable`
**Solution**:
```bash
# Check MediaTek network access
ping mlop-azure-gateway.mediatek.inc

# Check if you're on MediaTek internal network
# Ensure VPN is connected if working remotely
```

#### 2. **Invalid API Key / 401 Unauthorized**
**Symptoms**: `HTTP 401`, `Invalid API key`
**Solution**:
```bash
# Verify your JWT token is correct and not expired
# Check your .env file:
cat .env | grep AZURE_API_KEY

# Update with fresh token if needed
```

#### 3. **Model Not Found / 404 Error**
**Symptoms**: `HTTP 404`, `Model not found`
**Solution**:
```bash
# Verify model name in .env
grep MODEL_NAME .env

# Common MediaTek models:
# - aida-gpt-4o-mini
# - aida-gpt-4o
# Ask your MediaTek admin for available models
```

#### 4. **Timeout Errors**
**Symptoms**: `Request timeout`, `Connection timeout`
**Solution**:
```bash
# Increase timeout in .env
AI_REQUEST_TIMEOUT=60
MTK_GATEWAY_TIMEOUT=45

# Check network latency
ping mlop-azure-gateway.mediatek.inc
```

#### 5. **SSL Certificate Issues**
**Symptoms**: `SSL certificate verify failed`
**Solution**:
```bash
# For development only, add to your Python script:
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Better: Update your certificates or contact IT
```

### Debug Mode
Enable detailed logging:
```bash
# Add to .env
DEBUG=True
MTK_LOG_LEVEL=DEBUG

# Check logs
python run.py --backend 2>&1 | tee debug.log
```

### Network Diagnostics
```bash
# Test MediaTek gateway connectivity
curl -v https://mlop-azure-gateway.mediatek.inc

# Test with your credentials
curl -H "api-key: YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     https://mlop-azure-gateway.mediatek.inc/openai/deployments/aida-gpt-4o-mini/chat/completions?api-version=2024-10-21
```

---

## 🚀 MediaTek Production Deployment

### Production Environment Setup
```bash
# Production environment variables
export FLASK_ENV=production
export DEBUG=False
export AI_REQUEST_TIMEOUT=45
export MTK_GATEWAY_TIMEOUT=60

# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

### MediaTek Security Best Practices
1. **API Key Security**: Store JWT tokens securely, rotate regularly
2. **Network Security**: Use MediaTek internal network only
3. **User ID Management**: Map user IDs to actual MediaTek employees
4. **Logging**: Enable audit logging for AI API calls
5. **Rate Limiting**: Implement rate limiting for production use

### Performance Optimization for MediaTek
```bash
# Optimize for MediaTek network
AI_MAX_RETRIES=2
AI_REQUEST_TIMEOUT=30
MTK_GATEWAY_TIMEOUT=45

# Enable connection pooling
pip install requests[security]
```

---

## 📊 MediaTek Integration Features

### BugSeek + MediaTek Benefits
- 🔐 **Secure AI**: Uses MediaTek's secure Azure gateway
- 🚀 **Enterprise Grade**: Built for MediaTek's production environment
- 🎯 **Optimized**: Tuned for MediaTek network and infrastructure
- 📈 **Scalable**: Ready for MediaTek's development teams
- 🛡️ **Compliant**: Follows MediaTek security guidelines

### Supported MediaTek Models
- `aida-gpt-4o-mini` - Fast, cost-effective (recommended)
- `aida-gpt-4o` - Most capable, higher cost
- Custom models as available in your MediaTek environment

### MediaTek-Specific Features
- **User ID Tracking**: All AI calls logged with MediaTek user ID
- **Gateway Compatibility**: Optimized for MediaTek Azure gateway
- **Network Resilience**: Handles MediaTek network conditions
- **Security Headers**: Proper authentication for MediaTek environment

---

## 🧪 Testing Your MediaTek Setup

### Complete Integration Test
```bash
# 1. Test database
python 4_view_database.py

# 2. Test AI service
python -c "
from backend.ai_services import OpenAIService
service = OpenAIService()
result = service.check_connection()
print('✅ AI Service:', 'Working' if result['success'] else 'Failed')
"

# 3. Test full application
python run.py --backend &
sleep 5
curl http://localhost:5000/api/v1/health

# 4. Test frontend
python run.py --frontend &
sleep 5
curl http://localhost:8080/api/health

# Kill background processes
pkill -f "python run.py"
```

### Upload Test with MediaTek AI
1. Start BugSeek: `python run.py`
2. Open: http://localhost:8080
3. Login with: `hackathon2025`
4. Upload a sample log file
5. Verify AI analysis appears (should use MediaTek AI!)

---

## 📞 MediaTek Support

### Getting Help
1. **Internal Support**: Contact MediaTek IT/DevOps team
2. **API Issues**: Check MediaTek Azure gateway status
3. **Network Issues**: Verify MediaTek network connectivity
4. **Authentication**: Verify JWT token with MediaTek admin

### Useful MediaTek Resources
- MediaTek Azure Gateway Documentation
- Internal AI/ML Platform guides
- MediaTek network configuration docs
- Security policy documentation

---

## ✅ MediaTek Setup Checklist

### Pre-Setup
- [ ] MediaTek network access confirmed
- [ ] Valid JWT token obtained
- [ ] User ID confirmed
- [ ] Python 3.8+ available

### Configuration
- [ ] `.env` file created with MediaTek values
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Database initialized

### Testing
- [ ] MediaTek AI connection test passed
- [ ] Database test passed
- [ ] Application starts successfully
- [ ] Login works with hackathon password
- [ ] File upload and AI analysis working

### Production Ready
- [ ] Security review completed
- [ ] Performance testing done
- [ ] Logging and monitoring configured
- [ ] Backup and recovery tested

---

## 🎉 Success!

If all tests pass, your BugSeek is now running successfully in the MediaTek environment with full AI capabilities!

**Key URLs:**
- 🌐 **Application**: http://localhost:8080
- 🔧 **API**: http://localhost:5000
- 📚 **Docs**: http://localhost:5000/api/docs/
- 🔑 **Password**: `hackathon2025`

**Your MediaTek-powered BugSeek is ready for the hackathon! 🏆**

---

*Last updated: 2025-09-12*  
*MediaTek environment optimized ✅*
