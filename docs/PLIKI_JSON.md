# 📄 Pliki JSON - Wyjaśnienie Różnic

Skaner generuje **trzy różne typy plików JSON** w różnych lokalizacjach. Ten dokument wyjaśnia różnice między nimi.

---

## 📁 Lokalizacje Plików

### ⭐ **NOWY: `reports/combined_report_*.json` - Kompleksowy Raport (ZALECANY)**
**Lokalizacja:** `reports/combined_report_YYYY-MM-DD_HH-MM-SS.json`

**Kiedy jest tworzony:**
- Automatycznie po każdym skanowaniu
- Funkcja: `generate_combined_report()`

**Zawartość:**
```json
{
  "report_timestamp": "2026-02-04T12:03:00.741897",
  "scan": {
    "scan_timestamp": "...",
    "total_devices": 11,
    "protocols_scanned": ["ble", "wifi", "usb", "nfc"],
    "devices": [...]
  },
  "analysis": {
    "summary": {
      "high_risk_count": 7,
      "medium_risk_count": 4,
      "average_security_score": 34.09,
      "encryption_stats": {...}
    },
    "risk_groups": {
      "high_risk": [...],
      "medium_risk": [...],
      "low_risk": [...]
    },
    "vulnerabilities": {
      "no_encryption": [...],
      "no_pairing": [...]
    }
  },
  "threat_intelligence": {
    "192.168.1.100": {
      "is_threat": false,
      "abuse_score": 0,
      "reputation": "clean"
    }
  },
  "threat_intelligence_summary": {
    "total_ips_checked": 5,
    "threats_found": 0,
    "clean_ips": 5
  }
}
```

**Cel:**
- ✅ **JEDEN plik z wszystkimi danymi** - łatwiejsza analiza
- ✅ Surowe dane ze skanowania (`scan`)
- ✅ Analiza bezpieczeństwa (`analysis`)
- ✅ Threat intelligence (`threat_intelligence`)
- ✅ Podsumowanie threat intelligence
- ✅ Idealny do analizy i raportowania

**Kiedy używać:**
- ✅ **ZALECANY** - użyj tego pliku do analizy
- Gdy potrzebujesz wszystkich danych w jednym miejscu
- Do importu do systemów analitycznych
- Do raportowania i prezentacji

**Różnice vs inne pliki:**
- ✅ Zawiera WSZYSTKIE dane w jednym pliku
- ✅ Łatwiejsza analiza (wszystko w jednym miejscu)
- ✅ Struktura zorganizowana (scan, analysis, threat_intelligence)
- ✅ Podsumowanie threat intelligence

---

### 1. `reports/scan_*.json` - Surowe Dane ze Skanowania
**Lokalizacja:** `reports/scan_YYYY-MM-DD_HH-MM-SS.json`

**Kiedy jest tworzony:**
- Automatycznie po każdym skanowaniu
- Funkcja: `save_scan_results()`

**Zawartość:**
```json
{
  "scan_timestamp": "2026-02-04T12:03:00.737957",
  "total_devices": 11,
  "protocols_scanned": ["ble", "wifi", "usb", "nfc"],
  "devices": [
    {
      "mac_address": "...",
      "name": "...",
      "device_type": "...",
      "protocol": "...",
      "security_score": 0,
      "vulnerabilities": [...],
      "metadata": {...}
    }
  ]
}
```

**Cel:**
- ✅ Surowe dane ze skanowania
- ✅ Wszystkie wykryte urządzenia z pełnymi informacjami
- ✅ Używane do archiwizacji i późniejszej analizy
- ✅ Najprostsza struktura - tylko podstawowe dane

**Kiedy używać:**
- Gdy potrzebujesz surowych danych ze skanowania
- Do importu do innych systemów
- Do analizy historycznej

---

### 2. `reports/report_*.json` - Raport z Analizą Bezpieczeństwa
**Lokalizacja:** `reports/report_YYYY-MM-DD_HH-MM-SS.json`

**Kiedy jest tworzony:**
- Automatycznie po analizie bezpieczeństwa
- Funkcja: `generate_report()`

**Zawartość:**
```json
{
  "report_timestamp": "2026-02-04T12:03:00.741897",
  "summary": {
    "total_devices": 11,
    "high_risk_count": 7,
    "medium_risk_count": 4,
    "low_risk_count": 0,
    "devices_without_encryption": 7,
    "devices_without_pairing": 7,
    "fda_non_compliant": 11,
    "average_security_score": 34.09,
    "encryption_stats": {
      "strong_encryption": 0,
      "moderate_encryption": 0,
      "weak_encryption": 4,
      "no_encryption": 7
    }
  },
  "devices": [...],
  "risk_groups": {
    "high_risk": [...],
    "medium_risk": [...],
    "low_risk": [...]
  },
  "vulnerabilities": {
    "no_encryption": [...],
    "no_pairing": [...],
    "fda_non_compliant": [...]
  }
}
```

**Cel:**
- ✅ Szczegółowa analiza bezpieczeństwa
- ✅ Statystyki i podsumowania
- ✅ Grupowanie urządzeń według ryzyka
- ✅ Lista podatności pogrupowana według typu
- ✅ Używane do raportowania i prezentacji

**Kiedy używać:**
- Gdy potrzebujesz szczegółowej analizy bezpieczeństwa
- Do raportów dla zarządu/klientów
- Do wizualizacji danych
- Do analizy trendów bezpieczeństwa

**Różnice vs `scan_*.json`:**
- ✅ Dodatkowe sekcje: `summary`, `risk_groups`, `vulnerabilities`
- ✅ Statystyki i agregacje
- ✅ Grupowanie urządzeń według ryzyka
- ✅ Większa struktura danych

---

### 3. `threat_intel_*.json` - Threat Intelligence
**Lokalizacja:** `threat_intel_YYYYMMDD_HHMMSS.json` (w głównym folderze)

**Kiedy jest tworzony:**
- Automatycznie po skanowaniu (jeśli włączone)
- Funkcja: `_check_threat_intelligence()`
- Tylko jeśli masz skonfigurowany `ABUSEIPDB_API_KEY` w `.env`

**Zawartość:**
```json
{
  "192.168.1.100": {
    "ip": "192.168.1.100",
    "is_threat": false,
    "abuse_score": 0,
    "reputation": "clean",
    "sources": {
      "abuseipdb": {
        "abuseConfidencePercentage": 0,
        "usageType": "Residential",
        "isp": "..."
      }
    }
  }
}
```

**Cel:**
- ✅ Sprawdzanie IP urządzeń w bazach threat intelligence
- ✅ Wykrywanie podejrzanych adresów IP
- ✅ Reputacja IP (clean/malicious)
- ✅ Używane do dodatkowej analizy bezpieczeństwa

**Kiedy używać:**
- Gdy chcesz sprawdzić czy IP urządzeń są podejrzane
- Do analizy zagrożeń
- Do wykrywania potencjalnych ataków

**Różnice vs inne pliki:**
- ✅ Zawiera tylko dane threat intelligence (nie urządzenia)
- ✅ Klucz to adres IP (nie MAC)
- ✅ Zawiera reputację i score z AbuseIPDB
- ✅ Tworzony w głównym folderze (nie w `reports/`)

---

## 📊 Porównanie Plików

| Właściwość | `combined_report_*.json` ⭐ | `scan_*.json` | `report_*.json` | `threat_intel_*.json` |
|------------|----------------------------|---------------|-----------------|----------------------|
| **Lokalizacja** | `reports/` | `reports/` | `reports/` | Główny folder |
| **Nazwa** | `combined_report_*.json` | `scan_*.json` | `report_*.json` | `threat_intel_*.json` |
| **Zawartość** | **WSZYSTKO** | Surowe dane | Analiza bezpieczeństwa | Threat intelligence |
| **Struktura** | Złożona (3 sekcje) | Prosta | Złożona | Prosta |
| **Statystyki** | ✅ Tak | ❌ Nie | ✅ Tak | ❌ Nie |
| **Grupowanie** | ✅ Tak (ryzyko) | ❌ Nie | ✅ Tak (ryzyko) | ❌ Nie |
| **Urządzenia** | ✅ Wszystkie + grupowane | ✅ Wszystkie | ✅ Wszystkie + grupowane | ❌ Nie |
| **IP Threat Intel** | ✅ Tak | ❌ Nie | ❌ Nie | ✅ Tak |
| **Rozmiar** | Największy | Średni | Duży | Mały |
| **Zalecenie** | ⭐ **UŻYJ TEGO** | Archiwum | Archiwum | Archiwum |

---

## 🎯 Który Plik Użyć?

### ⭐ **ZALECANY: Kompleksowy Raport**
```bash
# Użyj combined_report_*.json - zawiera WSZYSTKO!
cat reports/combined_report_2026-02-04_12-03-00.json | jq '.analysis.summary'
cat reports/combined_report_2026-02-04_12-03-00.json | jq '.scan.devices[]'
cat reports/combined_report_2026-02-04_12-03-00.json | jq '.threat_intelligence'
```

### Do Analizy Surowej
```bash
# Z kompleksowego raportu:
cat reports/combined_report_2026-02-04_12-03-00.json | jq '.scan.devices[]'

# Lub ze starego pliku (jeśli istnieje):
cat reports/scan_2026-02-04_12-03-00.json | jq '.devices[]'
```

### Do Raportowania
```bash
# Z kompleksowego raportu:
cat reports/combined_report_2026-02-04_12-03-00.json | jq '.analysis.summary'

# Lub ze starego pliku (jeśli istnieje):
cat reports/report_2026-02-04_12-03-00.json | jq '.summary'
```

### Do Analizy Zagrożeń
```bash
# Z kompleksowego raportu:
cat reports/combined_report_2026-02-04_12-03-00.json | jq '.threat_intelligence | to_entries[] | select(.value.is_threat == true)'

# Lub ze starego pliku (jeśli istnieje):
cat threat_intel_20260204_120303.json | jq '.[] | select(.is_threat == true)'
```

---

## 💡 Przykłady Użycia

### 1. Znajdź Wszystkie Urządzenia Wysokiego Ryzyka

**Z `report_*.json`:**
```bash
cat reports/report_2026-02-04_12-03-00.json | jq '.risk_groups.high_risk[]'
```

**Z `scan_*.json`:**
```bash
cat reports/scan_2026-02-04_12-03-00.json | jq '.devices[] | select(.security_score < 50)'
```

### 2. Sprawdź Statystyki

**Tylko z `report_*.json`:**
```bash
cat reports/report_2026-02-04_12-03-00.json | jq '.summary'
```

### 3. Sprawdź Threat Intelligence

**Tylko z `threat_intel_*.json`:**
```bash
cat threat_intel_20260204_120303.json | jq '.[] | select(.is_threat == true)'
```

---

## 🔄 Relacje Między Plikami

```
Skanowanie
    ↓
scan_*.json (surowe dane)
    ↓
Analiza Bezpieczeństwa
    ↓
report_*.json (raport z analizą)
    ↓
Threat Intelligence (opcjonalnie)
    ↓
threat_intel_*.json (threat intel)
```

**Uwaga:** Wszystkie pliki mają ten sam timestamp, więc łatwo je powiązać:
- `scan_2026-02-04_12-03-00.json`
- `report_2026-02-04_12-03-00.json`
- `threat_intel_20260204_120303.json` (format: YYYYMMDD_HHMMSS)

---

## 📝 Podsumowanie

1. **⭐ `combined_report_*.json`** - **ZALECANY** - Wszystkie dane w jednym pliku (scan + analysis + threat_intel)
2. **`scan_*.json`** - Surowe dane, prosta struktura, wszystkie urządzenia (archiwum)
3. **`report_*.json`** - Analiza bezpieczeństwa, złożona struktura, statystyki, grupowanie (archiwum)
4. **`threat_intel_*.json`** - Threat intelligence, tylko IP, reputacja (archiwum)

**Zalecenie:** 
- ✅ **Używaj `combined_report_*.json`** - zawiera wszystkie dane w jednym miejscu, idealny do analizy
- Stare pliki (`scan_*.json`, `report_*.json`, `threat_intel_*.json`) są nadal tworzone dla kompatybilności wstecznej, ale `combined_report_*.json` jest zalecany do analizy
