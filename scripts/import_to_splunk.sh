#!/bin/bash
# Automatyczny import danych do Splunk

echo "🔍 Szukam plików siem_export_*.jsonl..."

# Znajdź najnowszy plik w katalogu exports/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
EXPORTS_DIR="$PROJECT_ROOT/exports"

LATEST_FILE=$(ls -t "$EXPORTS_DIR"/siem_export_*.jsonl 2>/dev/null | head -1)

if [ -z "$LATEST_FILE" ]; then
    echo "❌ Nie znaleziono plików siem_export_*.jsonl w katalogu exports/"
    echo "   Uruchom najpierw: python3 src/scanner.py"
    exit 1
fi

echo "📤 Znaleziono: $LATEST_FILE"

# Sprawdź czy Splunk jest zainstalowany
if [ ! -f "/opt/splunk/bin/splunk" ]; then
    echo "❌ Splunk nie jest zainstalowany"
    echo ""
    echo "📥 Zainstaluj Splunk Free:"
    echo "   1. Pobierz z: https://www.splunk.com/en_us/download/splunk-enterprise.html"
    echo "      (Wybierz: Linux, 64-bit, Debian Package)"
    echo "   2. Zainstaluj: sudo dpkg -i splunk*.deb"
    echo "   3. Uruchom: sudo /opt/splunk/bin/splunk start --accept-license"
    echo ""
    echo "   Zobacz: SPLUNK_INSTRUKCJA.md"
    exit 1
fi

# Sprawdź czy Splunk działa
if ! /opt/splunk/bin/splunk status >/dev/null 2>&1; then
    echo "⚠️  Splunk nie działa. Uruchamiam..."
    sudo /opt/splunk/bin/splunk start --accept-license --answer-yes --no-prompt >/dev/null 2>&1
    sleep 3
fi

echo "✅ Splunk działa"

# Metoda 1: Przez API (wymaga tokenu - skomplikowane)
# Metoda 2: Przez katalog monitorowany (prostsze)

SPLUNK_MONITOR_DIR="/opt/splunk/var/spool/splunk"

if [ -d "$SPLUNK_MONITOR_DIR" ]; then
    echo "📥 Kopiuję plik do katalogu monitorowanego Splunk..."
    sudo cp "$LATEST_FILE" "$SPLUNK_MONITOR_DIR/" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Plik skopiowany!"
        echo ""
        echo "🌐 Otwórz Splunk w przeglądarce:"
        echo "   http://localhost:8000"
        echo ""
        echo "💡 Wyszukaj urządzenia:"
        echo "   index=main device.name=*"
        echo ""
        echo "💡 Splunk automatycznie przetworzy plik w ciągu kilku sekund"
    else
        echo "⚠️  Nie udało się skopiować automatycznie"
        echo ""
        echo "📤 Zaimportuj ręcznie przez Splunk Web UI:"
        echo "   1. Otwórz: http://localhost:8000"
        echo "   2. Settings → Add Data → Upload"
        echo "   3. Wybierz plik: $LATEST_FILE"
        echo "   4. Next → Review → Submit"
    fi
else
    echo "⚠️  Katalog monitorowany nie istnieje"
    echo ""
    echo "📤 Zaimportuj ręcznie przez Splunk Web UI:"
    echo "   1. Otwórz: http://localhost:8000"
    echo "   2. Settings → Add Data → Upload"
    echo "   3. Wybierz plik: $LATEST_FILE"
    echo "   4. Next → Review → Submit"
    echo ""
    echo "💡 Lub skonfiguruj automatyczny import:"
    echo "   Settings → Data inputs → Files & Directories"
    echo "   Path: $EXPORTS_DIR"
    echo "   Pattern: siem_export_*.jsonl"
fi
