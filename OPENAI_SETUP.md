# 🤖 OpenAI API Key Setup Guide

## Where to Add Your OpenAI API Key

### 📁 File Location: `.env`

Open the `.env` file in the root directory of BugSeek and find this line:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

**Replace `your-openai-api-key-here` with your actual OpenAI API key.**

## 🔑 Getting Your API Key

### Option 1: MediaTek Users (Pre-configured)
If you're using MediaTek's Azure OpenAI gateway:
1. Go to the MediaTek Azure portal
2. Navigate to your OpenAI service
3. Copy your API key
4. The endpoint is already configured: `https://mlop-azure-gateway.mediatek.inc`

### Option 2: Direct OpenAI Account
1. Go to https://platform.openai.com/
2. Sign in to your OpenAI account
3. Go to "API Keys" section
4. Create a new API key or use an existing one
5. Copy the key (starts with `sk-`)

**For direct OpenAI, you may need to update the endpoint:**
```bash
# Comment out MediaTek endpoint and use OpenAI directly
# AZURE_OPENAI_ENDPOINT=https://mlop-azure-gateway.mediatek.inc
AZURE_OPENAI_ENDPOINT=https://api.openai.com
```

## 📝 Example Configuration

### MediaTek Configuration (Default)
```bash
# OpenAI/Azure OpenAI Configuration  
OPENAI_API_KEY=1a2b3c4d5e6f7g8h9i0j...your-actual-key-here

# Azure OpenAI specific settings (for MediaTek)
AZURE_OPENAI_ENDPOINT=https://mlop-azure-gateway.mediatek.inc
AZURE_OPENAI_API_VERSION=2024-10-21
AZURE_OPENAI_DEPLOYMENT_NAME=aida-gpt-4o-mini

# AI Analysis Configuration
AI_ANALYSIS_ENABLED=True
AI_MAX_RETRIES=3
AI_REQUEST_TIMEOUT=30
AI_BATCH_SIZE=10
```

### Direct OpenAI Configuration
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-1a2b3c4d5e6f7g8h9i0j...your-actual-openai-key

# OpenAI specific settings
AZURE_OPENAI_ENDPOINT=https://api.openai.com
AZURE_OPENAI_API_VERSION=2024-10-21
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini

# AI Analysis Configuration
AI_ANALYSIS_ENABLED=True
AI_MAX_RETRIES=3
AI_REQUEST_TIMEOUT=30
AI_BATCH_SIZE=10
```

## ⚙️ Step-by-Step Setup

### 1. Open the `.env` file
```bash
# Windows
notepad .env

# macOS/Linux
nano .env
# or
code .env  # if using VS Code
```

### 2. Find the OpenAI section
Look for this section in the file:
```bash
# OpenAI/Azure OpenAI Configuration
# IMPORTANT: Get your API key from the MediaTek Azure portal or your OpenAI account
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Replace with your actual API key
```bash
# Before (example)
OPENAI_API_KEY=your-openai-api-key-here

# After (with your real key)
OPENAI_API_KEY=1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t
```

### 4. Save the file
- **Windows Notepad**: Ctrl+S
- **VS Code**: Ctrl+S
- **Nano**: Ctrl+X, then Y, then Enter

### 5. Restart BugSeek
```bash
# Stop the application (Ctrl+C if running)
# Then restart
python run.py
```

## 🧪 Test Your API Key

### Method 1: Use the Built-in Test
```bash
python -c "from backend.ai_services import OpenAIService; service = OpenAIService(); print(service.check_connection())"
```

### Method 2: Check via Web Interface
1. Start BugSeek: `python run.py`
2. Open http://localhost:8080
3. Look at the sidebar - you should see:
   - 🟢 OpenAI Connected (if working)
   - 🟠 OpenAI Disconnected (if not working)

### Method 3: Run AI Analysis Migration
```bash
python migrate_ai_tables.py
```

## 🔧 Troubleshooting

### "OpenAI Disconnected" in UI
**Check:**
1. API key is correctly copied (no extra spaces)
2. API key has the right permissions
3. You have remaining quota/credits
4. Network connection is working

### "Connection timeout" errors
**Solutions:**
1. Increase timeout in `.env`:
   ```bash
   AI_REQUEST_TIMEOUT=60  # Increase from 30 to 60 seconds
   ```
2. Check your network/firewall settings
3. Try a different endpoint if using MediaTek gateway

### "Invalid API key" errors
**Solutions:**
1. Double-check the API key is copied correctly
2. Make sure there are no quotes around the key:
   ```bash
   # Wrong
   OPENAI_API_KEY="your-key-here"
   
   # Correct
   OPENAI_API_KEY=your-key-here
   ```
3. Verify the API key hasn't expired
4. Check if you need to use Azure OpenAI vs regular OpenAI endpoint

### Test API Connection
```bash
# Test the AI services
python -c "
from backend.ai_services import OpenAIService
service = OpenAIService()
result = service.check_connection()
print('Connection Status:', result)
"
```

## 🎯 What AI Features You'll Get

Once configured, you'll have access to:

1. **AI Error Analysis**
   - Automatic error summarization
   - Severity level detection
   - Root cause analysis
   - Technical keyword extraction

2. **Solution Suggestions**
   - AI-generated solutions
   - Step-by-step instructions
   - Risk assessments
   - Implementation difficulty ratings

3. **Pattern Recognition**
   - Similar error detection
   - Error categorization
   - Trend analysis

4. **Smart Reports**
   - Comprehensive error reports
   - AI-powered insights
   - Actionable recommendations

## 🔒 Security Notes

- **Never commit your API key to git**
- The `.env` file is already in `.gitignore`
- Keep your API key secure and don't share it
- Monitor your API usage and costs
- The system will show usage statistics in the UI

---

**🎉 That's it! Your BugSeek system now has AI superpowers!**

Try uploading a log file and click "Start AI Analysis" to see the magic happen! ✨
