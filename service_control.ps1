# Ethereum Balance Hunter Service Control Script

# Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================================" -ForegroundColor Green
Write-Host "Ethereum Balance Hunter Service Control Panel" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "Python Version: $pythonVersion" -ForegroundColor Yellow
} catch {
    Write-Host "Error: Python not found, please ensure Python is installed and added to PATH" -ForegroundColor Red
    Read-Host "Press any key to exit..."
    exit 1
}

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Check required files
if (-not (Test-Path "service_manager.py")) {
    Write-Host "Error: service_manager.py file not found" -ForegroundColor Red
    Read-Host "Press any key to exit..."
    exit 1
}

if (-not (Test-Path "install_service.py")) {
    Write-Host "Error: install_service.py file not found" -ForegroundColor Red
    Read-Host "Press any key to exit..."
    exit 1
}

function Show-Menu {
    Write-Host ""
    Write-Host "Please select an operation:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Install Service" -ForegroundColor White
    Write-Host "2. Uninstall Service" -ForegroundColor White
    Write-Host "3. Start Service" -ForegroundColor White
    Write-Host "4. Stop Service" -ForegroundColor White
    Write-Host "5. Restart Service" -ForegroundColor White
    Write-Host "6. Check Service Status" -ForegroundColor White
    Write-Host "7. View Service Info" -ForegroundColor White
    Write-Host "8. View Logs" -ForegroundColor White
    Write-Host "9. Exit" -ForegroundColor White
    Write-Host ""
}

function Execute-Command {
    param(
        [string]$Command,
        [string]$Description
    )
    
    Write-Host ""
    Write-Host $Description -ForegroundColor Yellow
    Write-Host ""
    
    try {
        Invoke-Expression $Command
    } catch {
        Write-Host "Error executing command: $_" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Press any key to return to menu..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

do {
    Show-Menu
    $choice = Read-Host "Enter choice (1-9)"
    
    switch ($choice) {
        "1" {
            Execute-Command "python install_service.py install" "Installing service... (Administrator privileges required)"
        }
        "2" {
            Execute-Command "python install_service.py uninstall" "Uninstalling service... (Administrator privileges required)"
        }
        "3" {
            Execute-Command "python service_manager.py start" "Starting service..."
        }
        "4" {
            Execute-Command "python service_manager.py stop" "Stopping service..."
        }
        "5" {
            Execute-Command "python service_manager.py restart" "Restarting service..."
        }
        "6" {
            Execute-Command "python service_manager.py status" "Checking service status..."
        }
        "7" {
            Execute-Command "python service_manager.py info" "Viewing service info..."
        }
        "8" {
            Execute-Command "python service_manager.py logs" "Viewing logs..."
        }
        "9" {
            Write-Host ""
            Write-Host "Exiting..." -ForegroundColor Green
            exit 0
        }
        default {
            Write-Host "Invalid choice, please try again" -ForegroundColor Red
        }
    }
} while ($true)