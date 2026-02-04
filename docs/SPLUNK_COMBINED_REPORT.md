# 📊 Używanie combined_report_*.json w Splunk

## ❓ Pytanie

**Czy mogę używać plików `combined_report_*.json` w Splunk?**

**Odpowiedź:** Tak, ale **nie bezpośrednio**. Splunk lepiej działa z formatem **JSON Lines** (`siem_export_*.jsonl`).

---

## 🔍 Różnice

### 1. `combined_report_*.json` - Pełny Raport
- **Format:** Jeden duży plik JSON z wszystkimi danymi
- **Struktura:** Zagnieżdżona (scan, analysis, threat_intelligence)
- **Zawartość:** Wszystkie dane w jednym pliku
- **Dla Splunk:** Wymaga konwersji lub specjalnej konfiguracji

### 2. `siem_export_*.jsonl` - JSON Lines (ZALECANY dla Splunk)
- **Format:** JSON Lines (każda linia = jeden event)
- **Struktura:** Płaska, jeden event na linię
- **Zawartość:** Tylko dane urządzeń (bez analizy)
- **Dla Splunk:** Idealny format, automatycznie parsowany

---

## ✅ Zalecane: Użyj `siem_export_*.jsonl`

**Skaner automatycznie tworzy plik `siem_export_*.jsonl` dla Splunk!**

### Jak użyć:

```bash
# 1. Uruchom skaner (automatycznie tworzy siem_export_*.jsonl)
python3 src/scanner.py

# 2. Zaimportuj do Splunk
./scripts/import_to_splunk.sh

# LUB ręcznie przez Splunk Web UI:
# http://localhost:8000 → Settings → Add Data → Upload → wybierz siem_export_*.jsonl
```

**Format `siem_export_*.jsonl`:**
```jsonl
{"@timestamp":"2026-02-04T16:01:11","event":{"kind":"event","category":"network","type":"device_scan","severity":"High"},"device":{"name":"192.168.1.5","mac_address":"00:00:01:05:00:00","ip_address":"192.168.1.5","type":"unknown","protocol":"WiFi","security_score":25,"vulnerabilities":[...]},"scan":{"timestamp":"2026-02-04T16:01:11","scanner":"Medical Device Security Scanner"}}
{"@timestamp":"2026-02-04T16:01:11","event":{"kind":"event","category":"network","type":"device_scan","severity":"Medium"},"device":{"name":"192.168.1.1","mac_address":"00:00:01:01:00:00","ip_address":"192.168.1.1","type":"unknown","protocol":"WiFi","security_score":75,"vulnerabilities":[...]},"scan":{"timestamp":"2026-02-04T16:01:11","scanner":"Medical Device Security Scanner"}}
```

**Zalety:**
- ✅ Automatycznie parsowany przez Splunk
- ✅ Jeden event na linię = łatwe przetwarzanie
- ✅ Format standardowy dla SIEM
- ✅ Automatycznie generowany przy każdym skanowaniu

---

## 🔧 Opcja: Użyj `combined_report_*.json` w Splunk

Jeśli chcesz użyć `combined_report_*.json`, masz **3 opcje**:

### Opcja 1: Konwertuj do JSON Lines (ZALECANE)

**Stwórz skrypt konwertujący:**

```bash
#!/bin/bash
# convert_combined_to_jsonl.sh

COMBINED_REPORT="reports/combined_report_2026-02-04_16-01-11.json"
OUTPUT="exports/combined_report_2026-02-04_16-01-11.jsonl"

# Konwertuj urządzenia z combined_report do JSON Lines
jq -c '.scan.devices[] | {
  "@timestamp": .first_seen,
  "event": {
    "kind": "event",
    "category": "network",
    "type": "device_scan",
    "severity": (if .security_score >= 80 then "Low" elif .security_score >= 50 then "Medium" elif .security_score >= 30 then "High" else "Critical" end)
  },
  "device": {
    "name": .display_name // .name,
    "mac_address": .mac_address,
    "ip_address": .ip_address,
    "type": .device_type,
    "protocol": .protocol,
    "manufacturer": .manufacturer,
    "security_score": .security_score,
    "has_encryption": .has_encryption,
    "encryption_type": .encryption_type,
    "requires_pairing": .requires_pairing,
    "vulnerabilities": .vulnerabilities,
    "vulnerability_count": (.vulnerabilities | length),
    "threat_intelligence": .threat_intelligence
  },
  "scan": {
    "timestamp": .first_seen,
    "scanner": "Medical Device Security Scanner"
  }
}' "$COMBINED_REPORT" > "$OUTPUT"

echo "✅ Skonwertowano: $OUTPUT"
```

**Użycie:**
```bash
chmod +x convert_combined_to_jsonl.sh
./convert_combined_to_jsonl.sh
./scripts/import_to_splunk.sh  # Zaimportuj do Splunk
```

---

### Opcja 2: Importuj bezpośrednio jako JSON (wymaga konfiguracji)

**W Splunk Web UI:**

1. Otwórz: http://localhost:8000
2. **Settings** → **Add Data** → **Upload**
3. Wybierz plik: `combined_report_*.json`
4. **Source type:** Wybierz `_json` lub utwórz custom source type
5. **Preview** → Sprawdź czy dane są poprawnie parsowane
6. **Next** → **Review** → **Submit**

**Problem:** Splunk może mieć problemy z zagnieżdżoną strukturą (scan.devices[]).

**Rozwiązanie:** Użyj custom source type:

1. **Settings** → **Source types** → **New**
2. **Name:** `medical_device_scanner`
3. **Category:** `Custom`
4. **Definition:**
   ```
   SHOULD_LINEMERGE = false
   KV_MODE = json
   ```
5. **Save**

---

### Opcja 3: Użyj Splunk REST API (zaawansowane)

```bash
#!/bin/bash
# import_combined_to_splunk.sh

SPLUNK_HOST="localhost"
SPLUNK_PORT="8000"
SPLUNK_USER="admin"
SPLUNK_PASS="twoje_haslo"
COMBINED_REPORT="reports/combined_report_2026-02-04_16-01-11.json"

# Konwertuj do JSON Lines i wyślij przez API
jq -c '.scan.devices[]' "$COMBINED_REPORT" | while read -r device_json; do
  curl -k -u "$SPLUNK_USER:$SPLUNK_PASS" \
    "https://$SPLUNK_HOST:$SPLUNK_PORT/services/receivers/simple?source=medical_device_scanner&sourcetype=json" \
    -d "$device_json"
done

echo "✅ Zaimportowano do Splunk"
```

---

## 📊 Porównanie

| Właściwość | `combined_report_*.json` | `siem_export_*.jsonl` |
|------------|-------------------------|----------------------|
| **Format** | Jeden plik JSON | JSON Lines (jeden event/linia) |
| **Struktura** | Zagnieżdżona | Płaska |
| **Zawartość** | Wszystko (scan + analysis + threat_intel) | Tylko urządzenia |
| **Dla Splunk** | Wymaga konwersji | ✅ Automatycznie parsowany |
| **Generowanie** | Automatyczne | Automatyczne |
| **Rozmiar** | Duży (wszystkie dane) | Mniejszy (tylko urządzenia) |
| **Zalecane dla Splunk** | ❌ Nie | ✅ Tak |

---

## 💡 Rekomendacja

### ✅ **Użyj `siem_export_*.jsonl`** (ZALECANE)

**Dlaczego:**
- ✅ Automatycznie generowany
- ✅ Format idealny dla Splunk
- ✅ Automatycznie parsowany
- ✅ Jeden event na linię = łatwe przetwarzanie
- ✅ Gotowy do użycia od razu

**Jak:**
```bash
python3 src/scanner.py  # Automatycznie tworzy siem_export_*.jsonl
./scripts/import_to_splunk.sh  # Automatyczny import
```

### ⚠️ **Użyj `combined_report_*.json`** (tylko jeśli potrzebujesz)

**Kiedy:**
- Potrzebujesz wszystkich danych (analiza, threat intel, statystyki)
- Chcesz zrobić własną analizę
- Potrzebujesz pełnego raportu

**Jak:**
- Konwertuj do JSON Lines (Opcja 1) - **ZALECANE**
- Lub importuj bezpośrednio (Opcja 2) - wymaga konfiguracji
- Lub użyj REST API (Opcja 3) - zaawansowane

---

## 🎯 Szybki Start

### Dla Splunk (ZALECANE):

```bash
# 1. Uruchom skaner
python3 src/scanner.py

# 2. Zaimportuj automatycznie
./scripts/import_to_splunk.sh

# 3. Otwórz Splunk
# http://localhost:8000
```

**Gotowe!** Splunk automatycznie przetworzy plik `siem_export_*.jsonl`.

---

## 📝 Podsumowanie

**Pytanie:** Czy mogę używać `combined_report_*.json` w Splunk?

**Odpowiedź:**
- ✅ **Tak**, ale wymaga konwersji lub specjalnej konfiguracji
- ✅ **Lepiej użyj `siem_export_*.jsonl`** - automatycznie generowany, idealny format dla Splunk
- ✅ **Oba pliki są tworzone automatycznie** przy każdym skanowaniu

**Zalecenie:** Użyj `siem_export_*.jsonl` dla Splunk - to jest format zaprojektowany specjalnie dla SIEM!
