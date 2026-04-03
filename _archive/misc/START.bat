@echo off
REM ============================================================================
REM Budget Analysis App (Database Edition) - Startup Script
REM ============================================================================

chcp 65001 >nul 2>&1

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

cls
echo.
echo ================================================================================
echo                    BUDGET ANALYSIS APP - STARTING
echo ================================================================================
echo.

echo [1/4] Checking app files...
if not exist "web_app_WITH_DATABASE.py" (
    echo [ERROR] Cannot find web_app_WITH_DATABASE.py
    echo         Make sure you are running this from the correct folder.
    echo         Expected location: %CD%
    echo.
    pause
    exit /b 1
)
echo       [OK] Found app file
echo.

echo [2/4] Checking virtual environment...
if exist "venv\Scripts\activate.bat" (
    echo       [OK] Found venv - activating...
    call venv\Scripts\activate.bat
) else (
    echo       [WARN] No venv found - using system Python
)
echo.

echo [3/4] Checking Python packages...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo       Installing missing packages...
    pip install Flask pandas openpyxl reportlab flask-sqlalchemy
    if errorlevel 1 (
        echo [ERROR] Failed to install packages. Run: pip install -r requirements.txt
        pause
        exit /b 1
    )
)
echo       [OK] Packages ready
echo.

echo [4/4] Starting app...
echo.
echo ================================================================================
echo   App URL : http://localhost:8080
echo   Stop    : Ctrl+C
echo   Stats   : python database_utils.py stats
echo ================================================================================
echo.

python web_app_WITH_DATABASE.py

if errorlevel 1 (
    echo.
    echo [ERROR] App stopped with an error. Check the output above.
    echo.
    echo Common fixes:
    echo   - Port 8080 in use: close other apps or change port
    echo   - Missing packages: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo Server stopped normally.
pause
