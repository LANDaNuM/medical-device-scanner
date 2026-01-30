#!/bin/bash
# Setup script dla Medical Device Security Scanner

echo "🏥 Medical Device Security Scanner - Setup"
echo "=========================================="
echo ""

# Sprawdź czy Python 3.9+ jest zainstalowany
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 nie jest zainstalowany!"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION znaleziony"

# Utwórz virtual environment
echo ""
echo "📦 Tworzenie virtual environment..."
python3 -m venv venv

# Aktywuj virtual environment
echo "🔧 Aktywacja virtual environment..."
source venv/bin/activate

# Zainstaluj zależności
echo ""
echo "📥 Instalowanie zależności..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup zakończony!"
echo ""
echo "🚀 Aby uruchomić skaner:"
echo "   1. source venv/bin/activate  (aktywuj virtual environment)"
echo "   2. python src/scanner.py     (uruchom skaner)"
echo ""
