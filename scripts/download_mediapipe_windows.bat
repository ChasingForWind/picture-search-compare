@echo off
chcp 65001 >nul
echo ========================================
echo   MediaPipe库下载脚本 (Windows CMD)
echo ========================================
echo.
echo 正在执行PowerShell脚本...
echo.

powershell.exe -ExecutionPolicy Bypass -File "%~dp0download_mediapipe_windows.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ 下载失败，错误代码: %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ✅ 下载完成！
pause

