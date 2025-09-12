# 📚 BugSeek API Documentation

Complete REST API reference for BugSeek error log management system.

## 🚀 Getting Started

### Base URL
```
http://localhost:5000/api/v1
```

### Authentication
BugSeek uses session-based authentication. Access the frontend at `http://localhost:8080` and log in with the hackathon password to establish a session.

### Response Format
All API responses follow this standard format:

```json
{
  "success": boolean,
  "data": object | array,
  "message": string,
  "error_code": string (optional),
  "pagination": object (for paginated results)
}
```

### Status Codes
- `200` - OK: Request successful
- `201` - Created: Resource created successfully
- `400` - Bad Request: Invalid request parameters
- `401` - Unauthorized: Authentication required
- `404` - Not Found: Resource not found
- `500` - Internal Server Error: Server error

---

## 📋 Core API Endpoints

### 1. Error Log Management

#### Upload Error Log
Upload a new error log file with metadata for AI analysis.

**Endpoint:** `POST /logs/upload`

**Content-Type:** `multipart/form-data`

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | Yes | Log file (TXT, LOG, JSON, XML, max 16MB) |
| `TeamName` | String | Yes | Team responsible for the error |
| `Module` | String | Yes | System module/component |
| `Description` | String | Yes | Error description |
| `Owner` | String | Yes | Contact email |
| `SolutionPossible` | Boolean | No | Whether solution is available |

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/v1/logs/upload \
  -F "file=@error.log" \
  -F "TeamName=Backend Team" \
  -F "Module=Authentication Service" \
  -F "Description=User login timeout after 30 seconds" \
  -F "Owner=john.doe@company.com" \
  -F "SolutionPossible=false"
```

**Example Response:**
```json
{
  "success": true,
  "message": "Log uploaded successfully",
  "report_url": "/api/v1/reports/cr_20240312_1234567890",
  "Cr_ID": "cr_20240312_1234567890"
}
```

#### List Error Logs
Retrieve a paginated list of error logs with optional filtering.

**Endpoint:** `GET /logs/`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | Integer | Page number (default: 1) |
| `per_page` | Integer | Items per page (default: 20, max: 100) |
| `TeamName` | String | Filter by team name |
| `Module` | String | Filter by module |
| `Owner` | String | Filter by owner email |
| `SolutionPossible` | Boolean | Filter by solution availability |
| `search` | String | Search in content and descriptions |
| `date_from` | String | Filter from date (YYYY-MM-DD) |
| `date_to` | String | Filter to date (YYYY-MM-DD) |

**Example Request:**
```bash
curl "http://localhost:5000/api/v1/logs/?page=1&per_page=10&TeamName=Backend%20Team&search=timeout"
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "Cr_ID": "cr_20240312_1234567890",
        "TeamName": "Backend Team",
        "Module": "Authentication Service",
        "ErrorName": "LOGIN_TIMEOUT",
        "Description": "User login timeout after 30 seconds",
        "Owner": "john.doe@company.com",
        "LogFileName": "auth_error.log",
        "FileSize": 2048,
        "SolutionPossible": false,
        "Severity": "high",
        "Environment": "production",
        "CreatedAt": "2024-03-12T10:30:00Z",
        "UpdatedAt": "2024-03-12T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total_pages": 5,
      "total_items": 47,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

#### Get Filter Options
Get distinct values for dropdown filters.

**Endpoint:** `GET /logs/options/{kind}`

**Path Parameters:**
| Parameter | Description |
|-----------|-------------|
| `kind` | One of: `teams`, `modules`, `owners` |

**Example Request:**
```bash
curl http://localhost:5000/api/v1/logs/options/teams
```

**Example Response:**
```json
{
  "success": true,
  "data": ["Backend Team", "Frontend Team", "DevOps Team", "QA Team"]
}
```

### 2. Detailed Reports

#### Get Error Log Report
Retrieve comprehensive analysis report for a specific error log.

**Endpoint:** `GET /reports/{cr_id}`

**Path Parameters:**
| Parameter | Description |
|-----------|-------------|
| `cr_id` | Unique Change Request ID |

**Example Request:**
```bash
curl http://localhost:5000/api/v1/reports/cr_20240312_1234567890
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "log_details": {
      "Cr_ID": "cr_20240312_1234567890",
      "TeamName": "Backend Team",
      "Module": "Authentication Service",
      "Description": "User login timeout after 30 seconds",
      "Owner": "john.doe@company.com",
      "Severity": "high",
      "CreatedAt": "2024-03-12T10:30:00Z"
    },
    "ai_summary": {
      "success": true,
      "summary": "Authentication timeout detected in login module. Analysis shows database connection issues causing user login delays.",
      "confidence": 0.85,
      "keywords": ["timeout", "authentication", "database", "login"],
      "severity": "high",
      "root_cause": "Database connection timeout"
    },
    "suggested_solutions": {
      "success": true,
      "solutions": [
        "🔍 Check database connection string and credentials",
        "⚡ Verify database server is running and accessible",
        "🔧 Review and optimize slow database queries",
        "📊 Monitor database connection pool utilization"
      ],
      "confidence": 0.75
    },
    "detected_errors": [
      {
        "line": 23,
        "text": "ERROR: Database connection timeout after 30 seconds",
        "severity": "high",
        "category": "database"
      },
      {
        "line": 45,
        "text": "WARN: Connection pool exhausted, creating new connection",
        "severity": "medium",
        "category": "database"
      }
    ],
    "similar_logs": {
      "success": true,
      "similar_logs": [
        {
          "Cr_ID": "cr_20240310_0987654321",
          "Module": "Authentication Service",
          "TeamName": "Backend Team",
          "SimilarityScore": 0.92,
          "Description": "Database timeout during login process"
        }
      ],
      "total_found": 3,
      "threshold_used": 0.7
    },
    "user_solutions": [
      {
        "Solution_ID": 1,
        "Content": "Increased database connection timeout from 30 to 60 seconds",
        "Author": "john.doe@company.com",
        "IsOfficial": true,
        "CreatedAt": "2024-03-12T11:00:00Z"
      }
    ]
  }
}
```

### 3. File Operations

#### Download Original Log File
Download the original uploaded log file.

**Endpoint:** `GET /logs/{cr_id}/file`

**Path Parameters:**
| Parameter | Description |
|-----------|-------------|
| `cr_id` | Unique Change Request ID |

**Example Request:**
```bash
curl -O http://localhost:5000/api/v1/logs/cr_20240312_1234567890/file
```

**Response:** Binary file download with appropriate headers.

#### Get File Information
Get metadata about the uploaded file.

**Endpoint:** `GET /logs/{cr_id}/file/info`

**Example Response:**
```json
{
  "success": true,
  "data": {
    "File_ID": 123,
    "Cr_ID": "cr_20240312_1234567890",
    "OriginalFileName": "auth_error.log",
    "FileSize": 2048,
    "MimeType": "text/plain",
    "Sha256Hash": "abc123...",
    "CreatedAt": "2024-03-12T10:30:00Z"
  }
}
```

### 4. User Solutions

#### Get User Solutions
Retrieve user-submitted solutions for a specific error log.

**Endpoint:** `GET /logs/{cr_id}/solutions`

**Example Response:**
```json
{
  "success": true,
  "data": [
    {
      "Solution_ID": 1,
      "Cr_ID": "cr_20240312_1234567890",
      "Content": "Increased database connection timeout configuration",
      "Author": "john.doe@company.com",
      "IsOfficial": true,
      "CreatedAt": "2024-03-12T11:00:00Z"
    }
  ]
}
```

#### Submit User Solution
Add a new solution for an error log.

**Endpoint:** `POST /logs/{cr_id}/solutions`

**Request Body:**
```json
{
  "content": "Solution description here",
  "author": "user@company.com",
  "is_official": false
}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "Solution_ID": 2,
    "Cr_ID": "cr_20240312_1234567890",
    "Content": "Solution description here",
    "Author": "user@company.com",
    "IsOfficial": false,
    "CreatedAt": "2024-03-12T12:00:00Z"
  }
}
```

---

## 🤖 AI & Analysis Endpoints

### Trigger AI Analysis
Manually trigger AI analysis for a specific error log.

**Endpoint:** `POST /ai/analyze/{cr_id}`

**Example Request:**
```bash
curl -X POST http://localhost:5000/api/v1/ai/analyze/cr_20240312_1234567890
```

**Example Response:**
```json
{
  "success": true,
  "message": "AI analysis completed",
  "data": {
    "analysis_id": "analysis_456",
    "status": "completed",
    "confidence": 0.87
  }
}
```

### Get AI Analysis Status
Check the status of AI analysis for a specific log.

**Endpoint:** `GET /ai/status/{cr_id}`

**Example Response:**
```json
{
  "success": true,
  "analysis": {
    "Analysis_ID": "analysis_456",
    "Cr_ID": "cr_20240312_1234567890",
    "AnalysisType": "comprehensive",
    "Status": "completed",
    "Summary": "Authentication timeout analysis completed",
    "Confidence": 0.87,
    "CreatedAt": "2024-03-12T10:35:00Z"
  }
}
```

### Check OpenAI Connection
Test the connection to OpenAI services.

**Endpoint:** `GET /openai/status`

**Example Response:**
```json
{
  "success": true,
  "connected": false,
  "message": "AI services using intelligent fallback",
  "fallback_active": true,
  "features_available": [
    "pattern_recognition",
    "intelligent_solutions",
    "similarity_matching"
  ]
}
```

### Test OpenAI Connection
Perform a test request to OpenAI API.

**Endpoint:** `GET /openai/test`

**Example Response:**
```json
{
  "success": false,
  "connected": false,
  "message": "AI services not available - using intelligent fallback",
  "test_result": "fallback_active"
}
```

---

## 📊 Statistics & Analytics

### System Statistics
Get comprehensive system statistics.

**Endpoint:** `GET /statistics`

**Example Response:**
```json
{
  "success": true,
  "data": {
    "total_logs": 245,
    "resolved_count": 189,
    "pending_count": 56,
    "teams_count": 8,
    "modules_count": 12,
    "avg_file_size": 15.7,
    "latest_upload": "2024-03-12T10:30:00Z",
    "top_teams": [
      {"name": "Backend Team", "count": 67},
      {"name": "Frontend Team", "count": 45},
      {"name": "DevOps Team", "count": 38}
    ],
    "top_modules": [
      {"name": "Authentication Service", "count": 34},
      {"name": "Payment Gateway", "count": 28},
      {"name": "User Management", "count": 23}
    ]
  }
}
```

### Analytics Data
Get detailed analytics for dashboards.

**Endpoint:** `GET /analytics`

**Example Response:**
```json
{
  "success": true,
  "data": {
    "upload_trends": {
      "daily": [12, 15, 8, 22, 18, 14, 9],
      "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    },
    "severity_distribution": {
      "critical": 12,
      "high": 45,
      "medium": 123,
      "low": 65
    },
    "team_performance": {
      "Backend Team": {"resolved": 45, "pending": 12},
      "Frontend Team": {"resolved": 32, "pending": 8}
    },
    "resolution_time": {
      "avg_hours": 24.5,
      "median_hours": 18.0,
      "fastest_hours": 2.5,
      "slowest_hours": 168.0
    }
  }
}
```

---

## 🏥 Health & Monitoring

### Health Check
Check overall system health.

**Endpoint:** `GET /health`

**Example Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "statistics": {
    "total_logs": 245,
    "total_teams": 8
  },
  "version": "1.0.0",
  "uptime": "2h 15m 32s"
}
```

---

## 🔧 Automation Endpoints

### Automation Validation
Validate logs through automation frameworks.

**Endpoint:** `POST /automation/validate`

**Request Body:**
```json
{
  "log_content": "Error log content here...",
  "metadata": {
    "source": "automated_test",
    "test_suite": "integration_tests",
    "environment": "staging"
  }
}
```

**Example Response:**
```json
{
  "success": true,
  "message": "Validation completed",
  "report_url": "/api/v1/reports/cr_20240312_1234567890",
  "status": "validated",
  "recommendations": [
    "Review authentication service configuration",
    "Check database connection settings"
  ]
}
```

---

## 🚀 Usage Examples

### Complete Workflow Example

#### 1. Upload a Log File
```javascript
// Using JavaScript fetch API
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('TeamName', 'Backend Team');
formData.append('Module', 'Authentication');
formData.append('Description', 'Login timeout issues');
formData.append('Owner', 'dev@company.com');

fetch('http://localhost:5000/api/v1/logs/upload', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Upload successful:', data.Cr_ID);
  // Get the report
  return fetch(`http://localhost:5000/api/v1/reports/${data.Cr_ID}`);
})
.then(response => response.json())
.then(report => {
  console.log('Analysis complete:', report.data);
});
```

#### 2. Search and Filter Logs
```python
import requests

# Search for authentication-related errors
response = requests.get('http://localhost:5000/api/v1/logs/', params={
    'search': 'authentication timeout',
    'TeamName': 'Backend Team',
    'page': 1,
    'per_page': 20
})

logs = response.json()['data']['logs']
for log in logs:
    print(f"Found: {log['Cr_ID']} - {log['Description']}")
```

#### 3. Get Comprehensive Analysis
```bash
#!/bin/bash

CR_ID="cr_20240312_1234567890"

# Get detailed report
curl -s "http://localhost:5000/api/v1/reports/$CR_ID" | \
  jq '.data.ai_summary.summary'

# Get similar logs  
curl -s "http://localhost:5000/api/v1/reports/$CR_ID" | \
  jq '.data.similar_logs.similar_logs[].Description'

# Download original file
curl -O "http://localhost:5000/api/v1/logs/$CR_ID/file"
```

---

## 🛡️ Error Handling

### Common Error Responses

#### Validation Error (400)
```json
{
  "success": false,
  "message": "Validation failed: TeamName is required",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field": "TeamName",
    "issue": "Required field missing"
  }
}
```

#### Not Found Error (404)
```json
{
  "success": false,
  "message": "Error log not found",
  "error_code": "RESOURCE_NOT_FOUND"
}
```

#### Server Error (500)
```json
{
  "success": false,
  "message": "Internal server error",
  "error_code": "INTERNAL_ERROR"
}
```

---

## 📝 API Best Practices

### Rate Limiting
- No rate limiting currently implemented
- Consider implementing for production use

### File Upload Guidelines
- Maximum file size: 16MB
- Supported formats: TXT, LOG, JSON, XML, OUT, ERR
- Use meaningful file names
- Include comprehensive metadata

### Error Handling
- Always check the `success` field in responses
- Use appropriate HTTP status codes
- Implement retry logic for network issues
- Handle file upload progress for large files

### Performance Tips
- Use pagination for large result sets
- Cache frequently accessed data
- Use specific filters to reduce result sets
- Monitor API response times

---

## 🔄 Webhook Integration

### Future Enhancement: Webhooks
Planning to add webhook support for:
- New log uploads
- Analysis completion
- Critical error detection
- Solution updates

**Planned Endpoint:** `POST /webhooks/register`

```json
{
  "url": "https://your-app.com/webhook",
  "events": ["log.uploaded", "analysis.completed"],
  "secret": "webhook-secret"
}
```

---

This API documentation provides comprehensive coverage of all BugSeek endpoints with practical examples. For interactive testing, use the Swagger UI at `http://localhost:5000/api/docs/`.
