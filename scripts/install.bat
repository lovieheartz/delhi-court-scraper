@echo off
echo ========================================
echo Court Data Fetcher - Installation Script
echo ========================================

echo.
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)
echo ✓ Python found

echo.
echo [2/6] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment created

echo.
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [4/6] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed

echo.
echo [5/6] Setting up environment variables...
if not exist .env (
    copy .env.example .env
    echo ✓ Environment file created (.env)
    echo Please edit .env file with your configuration
) else (
    echo ✓ Environment file already exists
)

echo.
echo [6/6] Creating necessary directories...
if not exist data mkdir data
if not exist logs mkdir logs
echo ✓ Directories created

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo To run the application:
echo   1. Activate virtual environment: venv\Scripts\activate.bat
echo   2. Run the app: python app.py
echo   3. Open browser: http://localhost:5000
echo.
echo To run demo: python demo.py
echo To run tests: python -m pytest tests/
echo.
pause