@echo off
echo ========================================
echo    File Version Saver - Installation
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as Administrator
) else (
    echo ❌ This script requires Administrator privileges
    echo Please right-click and "Run as Administrator"
    pause
    exit /b 1
)

REM Create installation directory
set INSTALL_DIR=C:\Program Files\FileVersionSaver
echo 📁 Creating installation directory: %INSTALL_DIR%
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Check if executable exists
if not exist "dist\version_saver.exe" (
    echo ❌ version_saver.exe not found in dist\ directory
    echo Please run build.bat first to create the executable
    pause
    exit /b 1
)

REM Copy executable
echo 📋 Copying version_saver.exe...
copy "dist\version_saver.exe" "%INSTALL_DIR%\" >nul
if %errorLevel% == 0 (
    echo ✅ Executable copied successfully
) else (
    echo ❌ Failed to copy executable
    pause
    exit /b 1
)

REM Install context menu
echo 🔧 Installing context menu...
regedit /s install_context_menu.reg
if %errorLevel% == 0 (
    echo ✅ Context menu installed successfully
) else (
    echo ❌ Failed to install context menu
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo ✅ File Version Saver has been installed successfully
echo.
echo 🎯 To use:
echo    1. Right-click any file in Windows Explorer
echo    2. Select "Save Version" to save a version
echo    3. Select "View Versions" to browse saved versions
echo.
echo 📁 Versions are stored in: %USERPROFILE%\.versiontracker\
echo.
echo 🔧 To uninstall:
echo    1. Run uninstall_context_menu.reg as Administrator
echo    2. Delete %INSTALL_DIR%
echo.
pause 