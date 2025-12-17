@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   Xingchen Reminder - Windows Installer
echo ========================================
echo.

:: Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo       Python found!

:: Get script directory
set "SCRIPT_DIR=%~dp0"
set "INSTALL_DIR=%USERPROFILE%\.xingchen-reminder"

echo.
echo [2/5] Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INSTALL_DIR%\sounds" mkdir "%INSTALL_DIR%\sounds"

:: Copy files
echo [3/5] Copying files...
copy /Y "%SCRIPT_DIR%src\*.py" "%INSTALL_DIR%\" >nul
copy /Y "%SCRIPT_DIR%assets\*" "%INSTALL_DIR%\" >nul 2>&1

:: Create data file
if not exist "%INSTALL_DIR%\reminders.json" (
    echo {"reminders": [], "settings": {"default_sound": true}, "last_check": null} > "%INSTALL_DIR%\reminders.json"
)

:: Install dependencies
echo [4/5] Installing Python dependencies...
pip install -q winotify pygame pillow
if errorlevel 1 (
    echo WARNING: Some dependencies may not have installed correctly.
)

:: Create scheduled task
echo [5/5] Setting up background service...
set "PYTHON_PATH="
for /f "delims=" %%i in ('where python') do (
    set "PYTHON_PATH=%%i"
    goto :found_python
)
:found_python

:: Replace python.exe with pythonw.exe for silent execution
set "PYTHONW_PATH=!PYTHON_PATH:python.exe=pythonw.exe!"

:: Delete existing task
schtasks /delete /tn "XingchenReminder" /f >nul 2>&1

:: Create task XML
echo ^<?xml version="1.0" encoding="UTF-16"?^> > "%INSTALL_DIR%\task.xml"
echo ^<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^> >> "%INSTALL_DIR%\task.xml"
echo   ^<RegistrationInfo^> >> "%INSTALL_DIR%\task.xml"
echo     ^<Description^>Xingchen Reminder - Background checker^</Description^> >> "%INSTALL_DIR%\task.xml"
echo   ^</RegistrationInfo^> >> "%INSTALL_DIR%\task.xml"
echo   ^<Triggers^> >> "%INSTALL_DIR%\task.xml"
echo     ^<TimeTrigger^> >> "%INSTALL_DIR%\task.xml"
echo       ^<Repetition^>^<Interval^>PT1M^</Interval^>^<StopAtDurationEnd^>false^</StopAtDurationEnd^>^</Repetition^> >> "%INSTALL_DIR%\task.xml"
echo       ^<StartBoundary^>2025-01-01T00:00:00^</StartBoundary^> >> "%INSTALL_DIR%\task.xml"
echo       ^<Enabled^>true^</Enabled^> >> "%INSTALL_DIR%\task.xml"
echo     ^</TimeTrigger^> >> "%INSTALL_DIR%\task.xml"
echo   ^</Triggers^> >> "%INSTALL_DIR%\task.xml"
echo   ^<Settings^> >> "%INSTALL_DIR%\task.xml"
echo     ^<MultipleInstancesPolicy^>IgnoreNew^</MultipleInstancesPolicy^> >> "%INSTALL_DIR%\task.xml"
echo     ^<DisallowStartIfOnBatteries^>false^</DisallowStartIfOnBatteries^> >> "%INSTALL_DIR%\task.xml"
echo     ^<StopIfGoingOnBatteries^>false^</StopIfGoingOnBatteries^> >> "%INSTALL_DIR%\task.xml"
echo     ^<ExecutionTimeLimit^>PT30S^</ExecutionTimeLimit^> >> "%INSTALL_DIR%\task.xml"
echo     ^<Hidden^>true^</Hidden^> >> "%INSTALL_DIR%\task.xml"
echo   ^</Settings^> >> "%INSTALL_DIR%\task.xml"
echo   ^<Actions^> >> "%INSTALL_DIR%\task.xml"
echo     ^<Exec^> >> "%INSTALL_DIR%\task.xml"
echo       ^<Command^>!PYTHONW_PATH!^</Command^> >> "%INSTALL_DIR%\task.xml"
echo       ^<Arguments^>"%INSTALL_DIR%\reminder_checker.py"^</Arguments^> >> "%INSTALL_DIR%\task.xml"
echo       ^<WorkingDirectory^>%INSTALL_DIR%^</WorkingDirectory^> >> "%INSTALL_DIR%\task.xml"
echo     ^</Exec^> >> "%INSTALL_DIR%\task.xml"
echo   ^</Actions^> >> "%INSTALL_DIR%\task.xml"
echo ^</Task^> >> "%INSTALL_DIR%\task.xml"

schtasks /create /tn "XingchenReminder" /xml "%INSTALL_DIR%\task.xml" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Could not create scheduled task. You may need to run as Administrator.
) else (
    echo       Background service installed!
)

:: Create desktop shortcut
echo.
echo Creating desktop shortcut...
set "SHORTCUT_VBS=%TEMP%\create_shortcut.vbs"
echo Set WshShell = CreateObject("WScript.Shell") > "%SHORTCUT_VBS%"
echo Set oShellLink = WshShell.CreateShortcut(WshShell.SpecialFolders("Desktop") ^& "\Xingchen Reminder.lnk") >> "%SHORTCUT_VBS%"
echo oShellLink.TargetPath = "!PYTHONW_PATH!" >> "%SHORTCUT_VBS%"
echo oShellLink.Arguments = """%INSTALL_DIR%\reminder_gui.py""" >> "%SHORTCUT_VBS%"
echo oShellLink.WorkingDirectory = "%INSTALL_DIR%" >> "%SHORTCUT_VBS%"
echo oShellLink.Description = "Xingchen Reminder" >> "%SHORTCUT_VBS%"
if exist "%INSTALL_DIR%\icon.ico" (
    echo oShellLink.IconLocation = "%INSTALL_DIR%\icon.ico, 0" >> "%SHORTCUT_VBS%"
)
echo oShellLink.Save >> "%SHORTCUT_VBS%"
cscript //nologo "%SHORTCUT_VBS%"
del "%SHORTCUT_VBS%"

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Installation directory: %INSTALL_DIR%
echo Desktop shortcut created: Xingchen Reminder
echo.
echo You can now:
echo   1. Double-click the desktop shortcut to open the GUI
echo   2. The background service will check reminders every minute
echo.
pause
