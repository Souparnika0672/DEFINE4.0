# EmergencyPass Localhost Quick Launch Script
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  EmergencyPass — Localhost Web Application" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan

Set-Location -Path $PSScriptRoot

Write-Host "`nLaunching server on: http://localhost:5000" -ForegroundColor Green
Write-Host "Demo Driver:    driver@emergency.org    / DemoUser123!" -ForegroundColor White
Write-Host "Demo Hospital:  hospital@emergency.org  / DemoHospital123!" -ForegroundColor White
Write-Host "Demo Police:    police@emergency.org    / DemoPolice123!" -ForegroundColor White
Write-Host "Demo Admin:     admin@emergency.org     / DemoAdmin123!`n" -ForegroundColor White

# Auto-open browser
Start-Process "http://localhost:5000"

# Run Flask app
py app.py
