# Xingchen Reminder - PowerShell Installer
# For Windows 10/11

param(
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

# Configuration
$AppName = "Xingchen Reminder"
$InstallDir = "$env:USERPROFILE\.xingchen-reminder"
$TaskName = "XingchenReminder"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Write-Header {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  $AppName - Installer" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Install-App {
    Write-Header

    # Check Python
    Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "       Found: $pythonVersion" -ForegroundColor Green
        $pythonPath = (Get-Command python).Source
        $pythonwPath = $pythonPath -replace "python\.exe$", "pythonw.exe"
    } catch {
        Write-Host "ERROR: Python not found. Please install Python first." -ForegroundColor Red
        exit 1
    }

    # Create directories
    Write-Host "[2/5] Creating directories..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
    New-Item -ItemType Directory -Force -Path "$InstallDir\sounds" | Out-Null
    Write-Host "       Created: $InstallDir" -ForegroundColor Green

    # Copy files
    Write-Host "[3/5] Copying files..." -ForegroundColor Yellow
    Copy-Item "$ScriptDir\src\*.py" $InstallDir -Force
    if (Test-Path "$ScriptDir\assets\*") {
        Copy-Item "$ScriptDir\assets\*" $InstallDir -Force
    }

    # Create data file if not exists
    $dataFile = "$InstallDir\reminders.json"
    if (-not (Test-Path $dataFile)) {
        '{"reminders": [], "settings": {"default_sound": true}, "last_check": null}' | Out-File -FilePath $dataFile -Encoding UTF8
    }
    Write-Host "       Files copied successfully" -ForegroundColor Green

    # Install dependencies
    Write-Host "[4/5] Installing dependencies..." -ForegroundColor Yellow
    pip install -q winotify pygame pillow
    Write-Host "       Dependencies installed" -ForegroundColor Green

    # Create scheduled task
    Write-Host "[5/5] Setting up background service..." -ForegroundColor Yellow

    # Remove existing task
    schtasks /delete /tn $TaskName /f 2>$null | Out-Null

    # Create task
    $taskXml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Xingchen Reminder Background Checker</Description>
  </RegistrationInfo>
  <Triggers>
    <TimeTrigger>
      <Repetition>
        <Interval>PT1M</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <StartBoundary>2025-01-01T00:00:00</StartBoundary>
      <Enabled>true</Enabled>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT30S</ExecutionTimeLimit>
    <Hidden>true</Hidden>
  </Settings>
  <Actions>
    <Exec>
      <Command>$pythonwPath</Command>
      <Arguments>"$InstallDir\reminder_checker.py"</Arguments>
      <WorkingDirectory>$InstallDir</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

    $taskXml | Out-File -FilePath "$InstallDir\task.xml" -Encoding Unicode
    schtasks /create /tn $TaskName /xml "$InstallDir\task.xml" 2>$null | Out-Null

    if ($LASTEXITCODE -eq 0) {
        Write-Host "       Background service installed" -ForegroundColor Green
    } else {
        Write-Host "       Warning: Could not create scheduled task (may need admin rights)" -ForegroundColor Yellow
    }

    # Create desktop shortcut
    Write-Host ""
    Write-Host "Creating desktop shortcut..." -ForegroundColor Yellow
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Xingchen Reminder.lnk")
    $Shortcut.TargetPath = $pythonwPath
    $Shortcut.Arguments = "`"$InstallDir\reminder_gui.py`""
    $Shortcut.WorkingDirectory = $InstallDir
    $Shortcut.Description = "Xingchen Reminder"
    if (Test-Path "$InstallDir\icon.ico") {
        $Shortcut.IconLocation = "$InstallDir\icon.ico, 0"
    }
    $Shortcut.Save()
    Write-Host "       Desktop shortcut created" -ForegroundColor Green

    # Done
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Installation Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Installation directory: $InstallDir"
    Write-Host "Desktop shortcut: Xingchen Reminder"
    Write-Host ""
}

function Uninstall-App {
    Write-Header
    Write-Host "Uninstalling $AppName..." -ForegroundColor Yellow

    # Remove scheduled task
    schtasks /delete /tn $TaskName /f 2>$null | Out-Null
    Write-Host "  - Removed scheduled task" -ForegroundColor Green

    # Remove desktop shortcut
    $shortcutPath = "$env:USERPROFILE\Desktop\Xingchen Reminder.lnk"
    if (Test-Path $shortcutPath) {
        Remove-Item $shortcutPath -Force
        Write-Host "  - Removed desktop shortcut" -ForegroundColor Green
    }

    # Remove installation directory
    if (Test-Path $InstallDir) {
        Remove-Item $InstallDir -Recurse -Force
        Write-Host "  - Removed installation directory" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "Uninstallation complete!" -ForegroundColor Green
}

# Main
if ($Uninstall) {
    Uninstall-App
} else {
    Install-App
}
