#!/bin/bash
# Synchronizuje raporty (exports/) z Raspberry Pi na główny PC przez rsync.
# Uruchom na Pi. Wymaga: SSH z Pi do PC (klucz bez hasła) i rsync na obu maszynach.
#
# Przed użyciem ustaw poniżej: PC_USER, PC_IP, PC_PATH

set -e

# === USTAW NA SWOJE (adres i użytkownik na PC, folder docelowy) ===
PC_USER="${PC_USER:-janek}"
PC_IP="${PC_IP:-192.168.1.10}"
PC_PATH="${PC_PATH:-splunk_import}"

# Ścieżka do exports na Pi
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
EXPORTS_DIR="$PROJECT_ROOT/exports"

if [ ! -d "$EXPORTS_DIR" ]; then
    echo "Katalog exports nie istnieje: $EXPORTS_DIR"
    exit 1
fi

DEST="${PC_USER}@${PC_IP}:${PC_PATH}/"

echo "Synchronizuję $EXPORTS_DIR -> $DEST"
rsync -avz --progress \
    --include='siem_export_*.jsonl' \
    --include='combined_report_*.json' \
    --include='*/' \
    --exclude='*' \
    "$EXPORTS_DIR/" "$DEST"

echo "Gotowe. Raporty na PC w: $PC_PATH"
