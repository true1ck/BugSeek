# 🚀 BugSeek Quick Setup Guide

**New to BugSeek? Get up and running in 2 minutes!**

## One-Command Setup ⚡

```bash
python setup_project.py
```

That's it! This script will:
- ✅ Check Python 3.8+ compatibility
- 🔧 Set up virtual environment (optional)
- 📦 Install all dependencies
- ⚙️ Create configuration files
- 🗄️ Initialize database with proper schema
- 📊 Add 10 realistic sample error logs
- 🤖 Setup AI features (optional)
- ✅ Test everything works

## Manual Setup (Alternative)

If you prefer step-by-step:

```bash
# 1. Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment
copy .env.template .env  # Windows
# cp .env.template .env  # macOS/Linux

# 4. Initialize database with sample data
python init_database.py
```

## Start BugSeek

```bash
python run.py
```

Then open:
- **Frontend UI**: http://localhost:8080
- **Backend API**: http://localhost:5000
- **API Docs**: http://localhost:5000/api/docs/

## What You Get 📋

Your database will contain **10 realistic error logs** with:

| Team | Module | Error Examples |
|------|--------|----------------|
| Frontend | Authentication | Mobile login timeouts |
| Backend | Database | SQL query performance issues |
| API | Payment | Gateway failures, transaction errors |
| DevOps | Deployment | Docker startup problems |
| QA | Testing | Automated test suite failures |
| Security | Authentication | Suspicious login attempts |
| Infrastructure | Monitoring | Disk space alerts |
| Mobile | Push Notifications | FCM delivery failures |

**Severity Levels**: Critical, High, Medium, Low  
**Environments**: Production, Staging, Development  
**Features**: Search, filtering, analytics, AI analysis ready

## Explore Features 🔍

1. **Upload**: Try uploading your own log files
2. **Search**: Test advanced filtering by team, module, severity
3. **Analytics**: View team performance and error distributions  
4. **Reports**: Generate detailed error analysis reports
5. **AI Features**: Configure OpenAI API key for AI-powered analysis

## Need Help? 📚

- **Full Documentation**: README.md
- **Development Guide**: WARP.md  
- **AI Features**: AI_FEATURES.md
- **OpenAI Setup**: OPENAI_SETUP.md 🤖
- **Interactive Database**: `python database_viewer.py`

## Troubleshooting 🔧

**Python version issues?**
```bash
python --version  # Need 3.8+
```

**Dependencies not installing?**
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Database issues?**
```bash
python test_db.py  # Test connection
python init_database.py  # Recreate with sample data
```

**Can't access the app?**
- Check if ports 5000 and 8080 are available
- Try `python run.py --backend` then `python run.py --frontend` separately

---

**🎉 You're ready to start debugging with BugSeek!**

Happy error hunting! 🐛🔍
