# Seed Database Script
# Populates the database with example data for demonstration

Write-Host "Seeding WebShield Database with Example Data" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check if backend virtual environment exists
if (-not (Test-Path "backend\venv\Scripts\Activate.ps1")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: cd backend; python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment and run seed script
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
Set-Location backend

try {
    & .\venv\Scripts\Activate.ps1
    Write-Host "Running seed script..." -ForegroundColor Yellow
    Write-Host ""
    
    python seed_data.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "=============================================" -ForegroundColor Cyan
        Write-Host "[SUCCESS] Database seeded successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor White
        Write-Host "  1. Open http://localhost:3000/dashboard" -ForegroundColor Gray
        Write-Host "  2. Explore the populated data" -ForegroundColor Gray
        Write-Host "  3. Navigate through different pages" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "[ERROR] Seeding failed!" -ForegroundColor Red
    }
} catch {
    Write-Host ""
    Write-Host "[ERROR] Failed to run seed script: $_" -ForegroundColor Red
} finally {
    Set-Location ..
}
