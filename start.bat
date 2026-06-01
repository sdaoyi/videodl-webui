@echo off
cd /d D:\projects\videodl-webui

:: Kill any process on port 9999
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":9999.*LISTENING" 2^>nul') do (
    taskkill /F /PID %%a >nul 2>nul
)

echo ========================================
echo   videodl WebUI
echo   Output: %cd%\videodl_outputs
echo   Logs:   %cd%\logs
echo   URL:    http://localhost:9999
echo ========================================

D:\envs\videodl\Scripts\python -X utf8 D:\projects\videodl-webui\server.py
pause
