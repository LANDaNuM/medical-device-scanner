#!/bin/bash
# Setup script for Medical Device Security Scanner

echo "🏥 Medical Device Security Scanner - Setup"
echo "=========================================="
echo ""

# Check if Python 3.9+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION found"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To run the scanner:"
echo "   1. source venv/bin/activate  (activate virtual environment)"
echo "   2. python src/scanner.py     (run scanner)"
echo ""
