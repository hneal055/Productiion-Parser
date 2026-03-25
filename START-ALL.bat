@echo off
REM ============================================================
REM  Scene Reader Studio Technologies — Launch All Apps
REM ============================================================
cd /d "%~dp0"

echo.
echo  ============================================================
echo   [1m[92mScene Reader Studio Technologies[0m
echo   Launching all three apps...
echo  ============================================================
echo.

REM ── Contract Review Tool  (port 5001) ────────────────────────
echo  [96m[1/3][0m Contract Review Tool    ^>  http://localhost:5001
start "Contract Review Tool" cmd /k "cd /d "%~dp0contract-review-tool" && call START.bat"

timeout /t 2 /nobreak >nul

REM ── ScreenFlow AURA  (port 8083) ─────────────────────────────
echo  [96m[2/3][0m ScreenFlow AURA         ^>  http://localhost:8083
start "ScreenFlow AURA" cmd /k "cd /d "%~dp0screenflow-aura" && call START.bat"

timeout /t 2 /nobreak >nul

REM ── Production Budget Parser  (port 8082) ────────────────────
echo  [96m[3/3][0m Production Budget Parser ^>  http://localhost:8082
start "Budget Parser" cmd /k "cd /d "%~dp0production-budget-parser" && call START.bat"

echo.
echo  [92mAll apps launched.[0m
echo.
echo  Open dashboards manually:
echo    Contract Review Tool    ^>  http://localhost:5001
echo    ScreenFlow AURA         ^>  http://localhost:8083
echo    Production Budget Parser ^>  http://localhost:8082
echo.
echo  Press any key to close this window.
echo  ============================================================
pause >nul
