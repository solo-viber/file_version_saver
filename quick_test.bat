@echo off
echo ========================================
echo    File Version Saver - Quick Test
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Python found
) else (
    echo ❌ Python not found. Please install Python 3.7+
    pause
    exit /b 1
)

REM Create a test file
echo Creating test file...
echo This is a test file for File Version Saver > test_file.txt
echo Created at %date% %time% >> test_file.txt

echo.
echo 📄 Created test_file.txt
echo.

REM Test the version saver
echo 🧪 Testing version saver...
python version_saver.py save test_file.txt

echo.
echo 📝 Modifying test file...
echo Additional content added >> test_file.txt

echo.
echo 🧪 Saving another version...
python version_saver.py save test_file.txt

echo.
echo 📋 Current versions:
python version_saver.py view test_file.txt

echo.
echo ✅ Quick test complete!
echo 📁 Check %USERPROFILE%\.versiontracker\test_file.txt\ for saved versions
echo.
echo 🗑️  Cleaning up test file...
del test_file.txt

pause 