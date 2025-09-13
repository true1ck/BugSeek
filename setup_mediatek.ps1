# MediaTek BugSeek Setup Script
# This script sets up the complete environment for MediaTek hackathon

Write-Host "=================================================================" -ForegroundColor Green
Write-Host "🔧 BugSeek MediaTek Environment Setup" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green

# Step 1: Copy environment configuration
Write-Host "📋 Step 1: Setting up environment configuration..." -ForegroundColor Yellow
Copy-Item ".env.mediatek" ".env" -Force
Write-Host "✅ Copied .env.mediatek to .env" -ForegroundColor Green

# Step 2: Create necessary directories
Write-Host "📁 Step 2: Creating necessary directories..." -ForegroundColor Yellow
$directories = @("uploads", "instance", "logs")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ Created directory: $dir" -ForegroundColor Green
    } else {
        Write-Host "✅ Directory already exists: $dir" -ForegroundColor Green
    }
}

# Step 3: Check current .env configuration
Write-Host "🔍 Step 3: Checking environment configuration..." -ForegroundColor Yellow
$envFile = Get-Content ".env"
$requiredVars = @(
    "DATABASE_URL",
    "AZURE_API_KEY", 
    "USER_ID",
    "ENDPOINT_URL",
    "MODEL_NAME",
    "API_VERSION",
    "BACKEND_API_URL",
    "SECRET_KEY"
)

Write-Host "📊 Environment Variables Status:" -ForegroundColor Cyan
foreach ($var in $requiredVars) {
    $line = $envFile | Where-Object { $_ -like "$var=*" }
    if ($line) {
        $value = ($line -split "=", 2)[1]
        if ($value -and $value -ne "" -and $value -notlike "*your_*" -and $value -notlike "*here*") {
            Write-Host "✅ $var = configured" -ForegroundColor Green
        } else {
            Write-Host "⚠️  $var = NEEDS CONFIGURATION" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ $var = MISSING" -ForegroundColor Red
    }
}

# Step 4: Show configuration instructions
Write-Host ""
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "📝 CONFIGURATION INSTRUCTIONS" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green

Write-Host "🔑 REQUIRED: Update these values in .env file:" -ForegroundColor Yellow
Write-Host "1. AZURE_API_KEY=your_actual_jwt_token_from_mediatek_organizer" -ForegroundColor White
Write-Host "2. USER_ID=your_mtk_employee_id (e.g., mtk34708)" -ForegroundColor White
Write-Host ""
Write-Host "📞 How to get API Key:" -ForegroundColor Cyan
Write-Host "   - Contact the hackathon organizer via Teams chat" -ForegroundColor White
Write-Host "   - Request the GenAI.txt file with API credentials" -ForegroundColor White
Write-Host "   - Replace placeholder values in .env file" -ForegroundColor White

# Step 5: Test script availability
Write-Host ""
Write-Host "🧪 TESTING:" -ForegroundColor Yellow
if (Test-Path "test_mediatek_api.py") {
    Write-Host "✅ API test script available: test_mediatek_api.py" -ForegroundColor Green
    Write-Host "   Run: python test_mediatek_api.py" -ForegroundColor White
} else {
    Write-Host "⚠️  API test script not found" -ForegroundColor Yellow
}

# Step 6: Show startup instructions
Write-Host ""
Write-Host "🚀 STARTUP INSTRUCTIONS:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your actual MediaTek credentials" -ForegroundColor White
Write-Host "2. Test API connection: python test_mediatek_api.py" -ForegroundColor White
Write-Host "3. Start the application: python run.py" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Application URLs:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:8080" -ForegroundColor White
Write-Host "   Backend:  http://localhost:5000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:5000/api/docs/" -ForegroundColor White

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "✅ MediaTek setup complete!" -ForegroundColor Green
Write-Host "Edit .env file with your credentials, then run: python run.py" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green
