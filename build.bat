@echo off
echo Building File Version Saver...

REM Install PyInstaller if not already installed
pip install pyinstaller

REM Build the executable
pyinstaller version_saver.spec --clean

echo.
echo Build complete! Executable created in dist/version_saver.exe
echo.
echo To install the context menu:
echo 1. Copy version_saver.exe to C:\Program Files\FileVersionSaver\
echo 2. Run install_context_menu.reg as administrator
echo.
pause 