# WebShield Health Check Script (PowerShell)
# This script verifies all components are working correctly

Write-Host "WebShield Health Check" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host ""

function Test-Service {
    param($Name, $Url)
    try {
        $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK] $Name is healthy" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "[FAIL] $Name is NOT responding" -ForegroundColor Red
        return $false
    }
}

# Check Docker containers
Write-Host "Checking Docker Containers..." -ForegroundColor Yellow
$containers = docker ps --format "{{.Names}}"

if ($containers -match "webshield-postgres") {
    Write-Host "[OK] PostgreSQL container is running" -ForegroundColor Green
} else {
    Write-Host "[FAIL] PostgreSQL container is NOT running" -ForegroundColor Red
}

if ($containers -match "webshield-redis") {
    Write-Host "[OK] Redis container is running" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Redis container is NOT running" -ForegroundColor Red
}
Write-Host ""

# Check Backend
Write-Host "Checking Backend API..." -ForegroundColor Yellow
$backendHealthy = Test-Service "Backend API" "http://localhost:8000/health"

if ($backendHealthy) {
    Write-Host "  Testing admin endpoints..." -ForegroundColor Gray
    
    try {
        $providers = Invoke-WebRequest -Uri "http://localhost:8000/admin/providers" -Method Get -TimeoutSec 5 -UseBasicParsing
        Write-Host "  [OK] Providers endpoint working" -ForegroundColor Green
    } catch {
        Write-Host "  [FAIL] Providers endpoint failed" -ForegroundColor Red
    }
    
    try {
        $webhooks = Invoke-WebRequest -Uri "http://localhost:8000/admin/webhooks" -Method Get -TimeoutSec 5 -UseBasicParsing
        Write-Host "  [OK] Webhooks endpoint working" -ForegroundColor Green
    } catch {
        Write-Host "  [FAIL] Webhooks endpoint failed" -ForegroundColor Red
    }
    
    try {
        $logs = Invoke-WebRequest -Uri "http://localhost:8000/admin/logs" -Method Get -TimeoutSec 5 -UseBasicParsing
        Write-Host "  [OK] Security logs endpoint working" -ForegroundColor Green
    } catch {
        Write-Host "  [FAIL] Security logs endpoint failed" -ForegroundColor Red
    }
}
Write-Host ""

# Check Frontend
Write-Host "Checking Frontend..." -ForegroundColor Yellow
Test-Service "Frontend" "http://localhost:3000" | Out-Null
Write-Host ""

# Check Database Connection
Write-Host "Checking Database..." -ForegroundColor Yellow
try {
    $dbCheck = docker exec webshield-postgres pg_isready -U webhook_user -d webhook_gateway 2>&1
    if ($dbCheck -match "accepting connections") {
        Write-Host "[OK] Database is accepting connections" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Database connection failed" -ForegroundColor Red
    }
} catch {
    Write-Host "[FAIL] Database check failed" -ForegroundColor Red
}
Write-Host ""

# Check Redis Connection
Write-Host "Checking Redis..." -ForegroundColor Yellow
try {
    $redisCheck = docker exec webshield-redis redis-cli ping 2>&1
    if ($redisCheck -match "PONG") {
        Write-Host "[OK] Redis is responding" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Redis connection failed" -ForegroundColor Red
    }
} catch {
    Write-Host "[FAIL] Redis check failed" -ForegroundColor Red
}
Write-Host ""

# Get some stats
Write-Host "Quick Stats..." -ForegroundColor Yellow
try {
    $statsResponse = Invoke-RestMethod -Uri "http://localhost:8000/admin/webhooks/stats" -Method Get -TimeoutSec 5
    Write-Host "  Total Webhooks: $($statsResponse.total)" -ForegroundColor Cyan
    Write-Host "  Successful: $($statsResponse.successful)" -ForegroundColor Green
    Write-Host "  Failed: $($statsResponse.failed)" -ForegroundColor Red
    Write-Host "  Pending: $($statsResponse.pending)" -ForegroundColor Yellow
} catch {
    Write-Host "  Could not fetch webhook stats" -ForegroundColor Gray
}
Write-Host ""

# Summary
Write-Host "======================" -ForegroundColor Cyan
Write-Host "Health Check Summary" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services Status:" -ForegroundColor White
Write-Host "  - Backend API: http://localhost:8000" -ForegroundColor Gray
Write-Host "  - Frontend: http://localhost:3000" -ForegroundColor Gray
Write-Host "  - Database: PostgreSQL on port 5434" -ForegroundColor Gray
Write-Host "  - Cache: Redis on port 6380" -ForegroundColor Gray
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor White
Write-Host "  1. Open http://localhost:3000 in your browser" -ForegroundColor Gray
Write-Host "  2. Navigate to Dashboard to see stats" -ForegroundColor Gray
Write-Host "  3. Create a provider in Providers page" -ForegroundColor Gray
Write-Host "  4. Send test webhooks" -ForegroundColor Gray
Write-Host ""
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
