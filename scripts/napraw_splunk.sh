#!/bin/bash
# Naprawa uprawnień Splunk

echo "🔧 Naprawiam uprawnienia Splunk..."

# Sprawdź czy Splunk jest zainstalowany
if [ ! -d "/opt/splunk" ]; then
    echo "❌ Splunk nie jest zainstalowany w /opt/splunk"
    exit 1
fi

echo "📁 Sprawdzam właściciela katalogów..."

# Sprawdź czy użytkownik splunk istnieje
if id "splunk" &>/dev/null; then
    echo "✅ Użytkownik 'splunk' istnieje"
    SPLUNK_USER="splunk"
    SPLUNK_GROUP="splunk"
else
    echo "⚠️  Użytkownik 'splunk' nie istnieje - używam 'root'"
    SPLUNK_USER="root"
    SPLUNK_GROUP="root"
fi

echo "🔐 Ustawiam właściciela na $SPLUNK_USER:$SPLUNK_GROUP..."

# Ustaw właściciela całego katalogu Splunk
sudo chown -R $SPLUNK_USER:$SPLUNK_GROUP /opt/splunk

# Ustaw uprawnienia
sudo chmod -R 755 /opt/splunk

# Upewnij się, że katalogi logów istnieją i mają odpowiednie uprawnienia
sudo mkdir -p /opt/splunk/var/log/splunk
sudo mkdir -p /opt/splunk/var/log/introspection
sudo mkdir -p /opt/splunk/var/log/watchdog
sudo mkdir -p /opt/splunk/var/log/client_events
sudo mkdir -p /opt/splunk/etc/licenses/download-trial

# Ustaw właściciela dla katalogów logów
sudo chown -R $SPLUNK_USER:$SPLUNK_GROUP /opt/splunk/var/log
sudo chown -R $SPLUNK_USER:$SPLUNK_GROUP /opt/splunk/etc/licenses

# Ustaw uprawnienia do zapisu
sudo chmod -R 755 /opt/splunk/var/log
sudo chmod -R 755 /opt/splunk/etc/licenses

echo "✅ Uprawnienia naprawione!"
echo ""
echo "🚀 Teraz możesz uruchomić Splunk:"
echo "   sudo -u splunk /opt/splunk/bin/splunk start --accept-license --answer-yes --no-prompt"
echo ""
echo "   (Uruchom jako użytkownik 'splunk', nie jako root)"
