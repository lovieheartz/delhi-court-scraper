#!/bin/bash

echo "========================================"
echo "Court Data Fetcher - Installation Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check if Python is installed
echo
echo "[1/8] Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    print_error "Python is not installed or not in PATH"
    echo "Please install Python 3.9+ from https://python.org"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
print_status "Python $PYTHON_VERSION found"

# Check Python version
echo
echo "[2/8] Checking Python version..."
PYTHON_VERSION_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
PYTHON_VERSION_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")

if [ "$PYTHON_VERSION_MAJOR" -lt 3 ] || ([ "$PYTHON_VERSION_MAJOR" -eq 3 ] && [ "$PYTHON_VERSION_MINOR" -lt 9 ]); then
    print_error "Python 3.9+ is required. Found Python $PYTHON_VERSION_MAJOR.$PYTHON_VERSION_MINOR"
    exit 1
fi
print_status "Python version is compatible"

# Install system dependencies
echo
echo "[3/8] Checking system dependencies..."
if command -v apt-get &> /dev/null; then
    echo "Installing system dependencies with apt-get..."
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr tesseract-ocr-eng wget gnupg unzip curl
    
    # Install Chrome
    if ! command -v google-chrome &> /dev/null; then
        echo "Installing Google Chrome..."
        wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google.list
        sudo apt-get update
        sudo apt-get install -y google-chrome-stable
    fi
    print_status "System dependencies installed"
elif command -v brew &> /dev/null; then
    echo "Installing system dependencies with Homebrew..."
    brew install tesseract
    if ! command -v google-chrome &> /dev/null; then
        brew install --cask google-chrome
    fi
    print_status "System dependencies installed"
else
    print_warning "Package manager not found. Please install manually:"
    echo "  - Tesseract OCR"
    echo "  - Google Chrome"
fi

# Create virtual environment
echo
echo "[4/8] Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
else
    $PYTHON_CMD -m venv venv
    if [ $? -eq 0 ]; then
        print_status "Virtual environment created"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo
echo "[5/8] Activating virtual environment..."
source venv/bin/activate
print_status "Virtual environment activated"

# Install Python dependencies
echo
echo "[6/8] Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    print_status "Dependencies installed"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Set up environment variables
echo
echo "[7/8] Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_status "Environment file created (.env)"
    print_warning "Please edit .env file with your configuration"
else
    print_status "Environment file already exists"
fi

# Create necessary directories
echo
echo "[8/8] Creating necessary directories..."
mkdir -p data logs
print_status "Directories created"

echo
echo "========================================"
echo "Installation completed successfully!"
echo "========================================"
echo
echo "To run the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the app: python app.py"
echo "  3. Open browser: http://localhost:5000"
echo
echo "To run demo: python demo.py"
echo "To run tests: python -m pytest tests/"
echo "To run with Docker: docker-compose up"
echo