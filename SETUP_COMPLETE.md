
# BugSeek Setup Complete!

Your BugSeek project is now fully set up with sample data.

## Quick Start Commands:

### 1. Activate Virtual Environment (if created):
Windows:   venv\Scripts\activate
macOS/Linux: source venv/bin/activate

### 2. Run the Application:
python run.py                    # Start both backend and frontend
python run.py --backend         # Start only backend (port 5000)
python run.py --frontend        # Start only frontend (port 8080)

### 3. Access the Application:
- Frontend UI: http://localhost:8080
- Backend API: http://localhost:5000
- API Documentation: http://localhost:5000/api/docs/

### 4. Useful Development Commands:
python database_viewer.py       # Interactive database viewer
pytest                          # Run tests
python migrate_ai_tables.py     # Add AI features (optional)

### 5. Sample Data:
Your database now contains 10 realistic error logs with:
- Different teams (Frontend, Backend, API, DevOps, QA, Security, Infrastructure, Mobile)  
- Various severity levels (low, medium, high, critical)
- Different environments (dev, staging, prod)
- Realistic log content and timestamps

### 6. Next Steps:
1. Explore the UI to see the sample data
2. Try uploading your own log files
3. Test the search and filtering features
4. Configure AI features with OpenAI API key (optional)

### 7. Need Help?
- Check README.md for detailed documentation
- Review WARP.md for development guidance  
- Check AI_FEATURES.md for AI integration setup

Happy debugging!
