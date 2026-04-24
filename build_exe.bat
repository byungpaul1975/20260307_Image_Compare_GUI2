@echo off
REM Build script for Image Compare Tool executable
REM This script creates a standalone .exe file

echo ========================================
echo Building Image Compare Tool Executable
echo ========================================

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo.
echo Building executable...
pyinstaller --clean ImageCompareTool.spec

echo.
echo ========================================
if exist "dist\ImageCompareTool.exe" (
    echo Build successful!
    echo Executable location: dist\ImageCompareTool.exe
    echo.
    echo You can distribute the following file:
    echo   - dist\ImageCompareTool.exe
) else (
    echo Build failed! Check the error messages above.
)
echo ========================================

pause
