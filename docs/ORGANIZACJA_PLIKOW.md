# 📁 Organizacja Plików - Co Gdzie Jest

## ✅ Aktualna Organizacja (Po Optymalizacji)

### 📂 Folder `reports/` - Wszystkie Raporty

**Domyślnie tworzony:**
- ✅ `combined_report_YYYY-MM-DD_HH-MM-SS.json` - **ZALECANY** - Wszystkie dane w jednym pliku

**Opcjonalnie (tylko z `--legacy-reports`):**
- `scan_YYYY-MM-DD_HH-MM-SS.json` - Surowe dane (duplikat z combined_report)
- `report_YYYY-MM-DD_HH-MM-SS.json` - Analiza bezpieczeństwa (duplikat z combined_report)

### 📂 Folder `exports/` - Eksport do SIEM

- `siem_export_YYYYMMDD_HHMMSS.jsonl` - Format JSON Lines dla systemów SIEM

### 📂 Główny Folder - **BRAK PLIKÓW JSON**

- ❌ **Usunięto:** `threat_intel_*.json` (teraz w `combined_report_*.json`)
- ✅ Wszystkie raporty są w `reports/`

---

## 🎯 Zalecane Użycie

### Domyślnie (Zalecane):
```bash
python3 src/scanner.py
```
**Tworzy tylko:**
- ✅ `reports/combined_report_*.json` - wszystko w jednym pliku

### Z Starymi Plikami (Kompatybilność Wsteczna):
```bash
python3 src/scanner.py --legacy-reports
```
**Tworzy:**
- ✅ `reports/combined_report_*.json` - wszystko w jednym pliku
- ✅ `reports/scan_*.json` - surowe dane (duplikat)
- ✅ `reports/report_*.json` - analiza (duplikat)

---

## 📊 Struktura `combined_report_*.json`

```json
{
  "report_timestamp": "...",
  "scan": {
    // Surowe dane ze skanowania (jak scan_*.json)
    "scan_timestamp": "...",
    "total_devices": 11,
    "protocols_scanned": ["ble", "wifi", "usb"],
    "devices": [...]
  },
  "analysis": {
    // Analiza bezpieczeństwa (jak report_*.json)
    "summary": {...},
    "risk_groups": {...},
    "vulnerabilities": {...}
  },
  "threat_intelligence": {
    // Threat intelligence (jak threat_intel_*.json)
    "192.168.1.100": {...}
  },
  "threat_intelligence_summary": {
    "total_ips_checked": 5,
    "threats_found": 0,
    "clean_ips": 5
  }
}
```

---

## 🗑️ Co Zostało Usunięte?

### ❌ Usunięto z Głównego Folderu:
- `threat_intel_*.json` - teraz w `combined_report_*.json`

### ✅ Zostało w `reports/`:
- `combined_report_*.json` - **ZALECANY** - wszystko w jednym pliku
- `scan_*.json` - tylko z `--legacy-reports` (duplikat)
- `report_*.json` - tylko z `--legacy-reports` (duplikat)

---

## 💡 Zalecenia

1. **Używaj `combined_report_*.json`** - zawiera wszystkie dane
2. **Nie używaj `--legacy-reports`** - chyba że potrzebujesz starych plików
3. **Wszystkie raporty są w `reports/`** - łatwa organizacja
4. **Brak plików w głównym folderze** - czysty projekt

---

## 🔄 Migracja Starych Plików

Jeśli masz stare pliki `threat_intel_*.json` w głównym folderze:
```bash
# Usuń je (są już w combined_report_*.json)
rm threat_intel_*.json
```

Stare pliki `scan_*.json` i `report_*.json` w `reports/` możesz zostawić dla historii lub usunąć:
```bash
# Opcjonalnie: usuń stare pliki (jeśli masz combined_report_*.json)
cd reports/
rm scan_*.json report_*.json
```
