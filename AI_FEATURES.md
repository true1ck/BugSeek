# BugSeek AI Features Documentation

## Overview
BugSeek now includes advanced AI-powered error analysis capabilities using OpenAI/Azure OpenAI integration. These features provide intelligent log analysis, pattern recognition, similarity matching, and solution suggestions.

## Features Implemented

### 1. AI-Powered Error Analysis
- **Automatic Summary Generation**: AI generates concise summaries of error logs
- **Severity Estimation**: Intelligent severity level detection (low, medium, high, critical)
- **Keyword Extraction**: Automatic extraction of important technical terms
- **Root Cause Analysis**: AI attempts to identify the root cause of errors

### 2. Error Pattern Recognition
- **Linux/Android Error Patterns**: Recognizes common patterns including:
  - Kernel panics
  - Segmentation faults
  - Out of memory errors
  - Buffer overflows
  - Device errors
  - I/O errors
  - Permission issues
  - Network errors
  - Watchdog timeouts
  - Android ANR (Application Not Responding)
  - Java exceptions

### 3. Solution Suggestions
- **AI-Generated Solutions**: Provides practical, actionable solutions
- **Categorized Solutions**: Solutions categorized by type (configuration, code, infrastructure, etc.)
- **Step-by-Step Instructions**: Detailed implementation steps
- **Risk Assessment**: Each solution includes difficulty and risk levels

### 4. Similarity Analysis
- **Log Comparison**: Finds similar error logs in the database
- **TF-IDF Based Matching**: Uses text analysis for similarity scoring
- **Pattern-Based Matching**: Considers error patterns, modules, and teams

### 5. OpenAI Status Monitoring
- **Connection Status**: Real-time OpenAI API connection status
- **Usage Tracking**: Monitors API calls, tokens used, and estimated costs
- **Error Handling**: Graceful fallback to pattern-based analysis when AI is unavailable

## Setup Instructions

### 1. Configuration
Create a `.env` file in the project root with your OpenAI API key:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your-api-key-here
```

For MediaTek users, the Azure OpenAI endpoint is pre-configured:
- Endpoint: `https://mlop-azure-gateway.mediatek.inc`
- Model: `aida-gpt-4o-mini`

### 2. Database Migration
Run the migration script to add AI analysis tables:

```bash
python migrate_ai_tables.py

# Check migration status
python migrate_ai_tables.py --check
```

### 3. Start the Application
```bash
# Start both backend and frontend
python run.py

# Or start individually
python run.py --backend
python run.py --frontend
```

## API Endpoints

### OpenAI Status
- `GET /api/v1/openai/status` - Check OpenAI connection status
- `GET /api/v1/openai/test` - Test OpenAI connection

### AI Analysis
- `POST /api/v1/ai/analyze/<cr_id>` - Trigger AI analysis for a specific log
- `GET /api/v1/ai/status/<cr_id>` - Get AI analysis status for a log

## Usage Guide

### 1. Uploading Logs with AI Analysis
When you upload a new error log:
1. The system automatically generates text embeddings
2. AI analysis is triggered in the background
3. Pattern recognition identifies known error types
4. Similar logs are found and linked

### 2. Viewing AI Analysis Results
In the report view:
1. Click on any uploaded log to view its report
2. AI Analysis section shows:
   - Analysis status (pending, processing, completed, failed)
   - AI-generated summary
   - Detected error patterns
   - Suggested solutions with confidence scores
3. Click "Start AI Analysis" if analysis hasn't been performed yet

### 3. Dashboard OpenAI Status
The sidebar shows:
- API connection status (green = connected, orange = disconnected)
- Total API calls made
- Tokens used and estimated costs

## Database Schema

### New Tables Added

#### ai_analysis_results
Stores AI analysis results for each error log:
- Summary and confidence scores
- Keywords and severity estimates
- Suggested solutions
- Error patterns and categories
- Processing status and timing
- Token usage and costs

#### openai_status
Tracks OpenAI API status and usage:
- Connection status
- API configuration
- Usage statistics
- Rate limiting information

#### similar_log_matches
Stores similarity relationships between logs:
- Source and target log IDs
- Similarity scores
- Matching methods
- Common keywords and patterns

## Fallback Mechanisms

When OpenAI is unavailable, the system falls back to:
1. **Pattern-based analysis**: Uses regex patterns to identify error types
2. **Rule-based solutions**: Provides generic solutions based on error categories
3. **TF-IDF similarity**: Uses text analysis for finding similar logs

## Performance Considerations

- AI analysis is performed asynchronously to avoid blocking uploads
- Content is limited to 10,000 characters to manage token usage
- Results are cached in the database to avoid repeated API calls
- Batch processing can be configured via `AI_BATCH_SIZE` setting

## Troubleshooting

### OpenAI Connection Issues
1. Verify API key is set correctly in `.env`
2. Check network connectivity to Azure endpoint
3. Verify API key permissions and quotas
4. Check the OpenAI status page for service issues

### AI Analysis Not Starting
1. Check if `AI_ANALYSIS_ENABLED=True` in `.env`
2. Verify database migration completed successfully
3. Check backend logs for error messages
4. Manually trigger analysis via API or UI

### High API Costs
1. Monitor usage in the OpenAI status section
2. Adjust `AI_MAX_RETRIES` to reduce retry attempts
3. Limit content size in analysis requests
4. Use pattern-based analysis for simple errors

## Security Notes

- API keys are never logged or displayed in the UI
- API key hash is stored for tracking, not the actual key
- All API communications use HTTPS
- Sensitive log content can be redacted before analysis

## Future Enhancements

Potential improvements for future versions:
1. Celery integration for better async processing
2. Custom fine-tuned models for specific error types
3. Automated solution execution
4. Integration with ticketing systems
5. Trend analysis and predictive alerts
6. Multi-language support for error logs

## Support

For issues or questions:
1. Check the API status at `/api/v1/openai/status`
2. Review backend logs for detailed error messages
3. Run migration status check: `python migrate_ai_tables.py --check`
4. Ensure all dependencies are installed: `pip install -r requirements.txt`
