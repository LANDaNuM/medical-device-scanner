# 📁 Struktura Projektu

## Organizacja Katalogów

```
medical-device-scanner/
├── src/                    # Kod źródłowy Python
│   ├── scanner.py          # Główny moduł skanowania
│   ├── api_server.py       # Serwer API (Flask)
│   ├── dashboard.py        # Dashboard (Streamlit)
│   └── ...
│
├── docs/                   # 📚 Dokumentacja
│   ├── README.md           # (README.md pozostaje w głównym katalogu)
│   ├── FLAGI.md            # Dokumentacja flag CLI
│   ├── GITHUB_KOMENDY.md   # Komendy Git
│   └── ...
│
├── reports/                # 📊 Raporty i skany (JSON)
│   ├── report_*.json       # Raporty skanowania
│   └── scan_*.json         # Surowe dane skanowania
│
├── exports/                # 📤 Eksporty SIEM (JSONL)
│   └── siem_export_*.jsonl # Eksporty do SIEM
│
├── scripts/                # 🔧 Skrypty pomocnicze
│   ├── import_to_splunk.sh # Import do Splunk
│   ├── napraw_splunk.sh    # Naprawa Splunk
│   ├── dodaj_github.sh     # Konfiguracja GitHub
│   └── ...
│
├── data/                   # 💾 Dane (cache, modele ML)
│   ├── cache/              # Cache
│   └── models/             # Modele ML
│
├── rust_scanner/           # 🔧 Skaner Rust (szybki port scanner)
│   └── src/
│
├── .env                    # 🔐 Klucze API (NIE commituj!)
├── .env.example            # Przykładowa konfiguracja
├── requirements.txt        # Zależności Python
├── README.md               # Główny README
└── ...
```

---

## 📂 Opis Katalogów

### `src/`
Kod źródłowy aplikacji:
- **scanner.py** - Główny moduł skanowania urządzeń
- **api_server.py** - REST API (Flask)
- **dashboard.py** - Dashboard (Streamlit)
- **vulnerability_tester.py** - Testy podatności
- **anomaly_detector.py** - Wykrywanie anomalii (ML)
- I inne moduły...

### `docs/`
Wszystka dokumentacja projektu:
- Instrukcje użytkowania
- Dokumentacja funkcjonalności
- Przewodniki konfiguracji
- Komendy Git
- I inne...

### `reports/`
Wygenerowane raporty i skany:
- **report_*.json** - Szczegółowe raporty skanowania
- **scan_*.json** - Surowe dane ze skanowania

**Uwaga:** Katalog `reports/` jest w `.gitignore` - pliki nie są commitowane.

### `exports/`
Eksporty do systemów SIEM:
- **siem_export_*.jsonl** - Eksporty w formacie JSON Lines

**Uwaga:** Katalog `exports/` jest w `.gitignore` - pliki nie są commitowane.

### `scripts/`
Skrypty pomocnicze:
- **import_to_splunk.sh** - Automatyczny import do Splunk
- **napraw_splunk.sh** - Naprawa uprawnień Splunk
- **dodaj_github.sh** - Konfiguracja GitHub remote
- **check_api_keys.py** - Sprawdzanie kluczy API
- I inne...

### `data/`
Dane aplikacji:
- **cache/** - Cache danych
- **models/** - Wytrenowane modele ML

**Uwaga:** Katalog `data/` jest w `.gitignore`.

---

## 🔄 Zmiany w Strukturze

### Przed reorganizacją:
```
medical-device-scanner/
├── *.md (26 plików w głównym katalogu)
├── report_*.json (w głównym katalogu)
├── scan_*.json (w głównym katalogu)
├── siem_export_*.jsonl (w głównym katalogu)
└── *.sh (w głównym katalogu)
```

### Po reorganizacji:
```
medical-device-scanner/
├── docs/ (wszystkie .md)
├── reports/ (wszystkie .json)
├── exports/ (wszystkie .jsonl)
└── scripts/ (wszystkie .sh i skrypty Python)
```

---

## 📝 Uwagi

1. **README.md** pozostaje w głównym katalogu (standard GitHub)
2. **Pliki generowane** (`reports/`, `exports/`) są w `.gitignore`
3. **Wszystkie ścieżki w kodzie** zostały zaktualizowane do nowych katalogów
4. **Skrypty** automatycznie znajdują pliki w nowych lokalizacjach

---

## 🚀 Użycie

### Skanowanie (zapisuje do `reports/` i `exports/`):
```bash
python3 src/scanner.py
```

### Import do Splunk (czyta z `exports/`):
```bash
./scripts/import_to_splunk.sh
```

### API Server (czyta z `reports/`):
```bash
python3 src/scanner.py --api
```

---

**Ostatnia aktualizacja:** 2026-01-27
