# 📚 Spis Treści - Kompletny Przewodnik po Kodzie Python

## ✅ Część 1 - PODSTAWY (Gotowe)
📄 **Plik:** `PRZEWODNIK_PYTHON_CZESC_1.md`

**Zawiera:**
- ✅ Wprowadzenie do przewodnika
- ✅ Mapa zależności między plikami
- ✅ Podstawowe koncepty Python (klasy, pętle, funkcje, warunki)
- ✅ **Plik 1:** `__init__.py` - szczegółowe wyjaśnienie
- ✅ **Plik 2:** `device.py` - szczegółowe wyjaśnienie każdej linii

---

## 📝 Część 2 - SKANERY (W przygotowaniu)
📄 **Plik:** `PRZEWODNIK_PYTHON_CZESC_2.md`

**Będzie zawierać:**
- **Plik 3:** `real_scanner.py` - Skaner BLE (Bluetooth Low Energy)
  - Jak działa skanowanie BLE
  - Jak wykrywa urządzenia
  - Jak analizuje bezpieczeństwo
  - Wyjaśnienie async/await
  - Wyjaśnienie callback functions
  
- **Plik 4:** `wifi_scanner.py` - Skaner WiFi
  - Jak skanuje sieć lokalną
  - Jak używa nmap i scapy
  - Jak wykrywa otwarte porty
  - Wyjaśnienie threading i concurrent.futures
  
- **Plik 5:** `usb_scanner.py` - Skaner USB
  - Jak wykrywa urządzenia USB
  - Jak używa pyusb i pyserial
  - Automatyczne wykrywanie portów i baudrate
  
- **Plik 6:** `nfc_scanner.py` - Skaner NFC
  - Jak skanuje urządzenia NFC
  - Jak używa nfcpy i pyscard

---

## 📝 Część 3 - ANALIZA I BEZPIECZEŃSTWO (W przygotowaniu)
📄 **Plik:** `PRZEWODNIK_PYTHON_CZESC_3.md`

**Będzie zawierać:**
- **Plik 7:** `vulnerability_tester.py` - Testy podatności
  - Jak testuje podatności
  - Wyjaśnienie wszystkich metod testowych
  - Jak używa CVE lookup
  
- **Plik 8:** `anomaly_detector.py` - Wykrywanie anomalii (ML)
  - Jak działa Machine Learning
  - Wyjaśnienie algorytmów ML (Isolation Forest, LOF, SVM)
  - Jak trenuje modele
  - Wyjaśnienie numpy i pandas
  
- **Plik 9:** `encryption_analyzer.py` - Analiza szyfrowania
  - Jak analizuje algorytmy szyfrowania
  - Jak wykrywa słabe algorytmy

---

## 📝 Część 4 - INTEGRACJE (W przygotowaniu)
📄 **Plik:** `PRZEWODNIK_PYTHON_CZESC_4.md`

**Będzie zawierać:**
- **Plik 10:** `api_server.py` - REST API (Flask)
  - Jak działa serwer Flask
  - Wyjaśnienie endpointów
  - Jak obsługuje żądania HTTP
  - Wyjaśnienie threading dla serwera
  
- **Plik 11:** `dashboard.py` - Dashboard (Streamlit)
  - Jak działa Streamlit
  - Jak tworzy interaktywny dashboard
  - Wyjaśnienie plotly (wykresy)
  
- **Plik 12:** `siem_exporter.py` - Eksport do SIEM
  - Jak eksportuje dane do SIEM
  - Formaty eksportu (CEF, JSON Lines, CSV)
  
- **Plik 13:** `threat_intelligence.py` - Threat Intelligence
  - Jak używa zewnętrznych API
  - Jak sprawdza urządzenia w bazach threat intelligence

---

## 📝 Część 5 - GŁÓWNY MODUŁ I POMOCNICZE (W przygotowaniu)
📄 **Plik:** `PRZEWODNIK_PYTHON_CZESC_5.md`

**Będzie zawierać:**
- **Plik 14:** `scanner.py` - GŁÓWNY MODUŁ ⭐
  - Jak łączy wszystkie komponenty
  - Jak zarządza skanowaniem
  - Wyjaśnienie argparse (argumenty wiersza poleceń)
  - Jak zapisuje raporty
  - Wyjaśnienie wszystkich metod
  
- **Plik 15:** `history_db.py` - Baza danych historii
  - Jak używa SQLite
  - Wyjaśnienie SQL queries
  - Jak przechowuje historię skanowań
  
- **Plik 16:** `scheduler.py` - Zaplanowane skanowania
  - Jak używa biblioteki schedule
  - Wyjaśnienie threading dla scheduler
  
- **Plik 17:** `monitor.py` - Monitoring w czasie rzeczywistym
  - Jak monitoruje urządzenia
  - Jak wykrywa zmiany

---

## 📝 Część 6 - POMOCNICZE MODUŁY (W przygotowaniu)
📄 **Plik:** `PRZEWODNIK_PYTHON_CZESC_6.md`

**Będzie zawierać:**
- **Plik 18:** `cve_lookup.py` - Wyszukiwanie CVE
  - Jak używa API NIST NVD
  - Jak wyszukuje podatności
  
- **Plik 19:** `external_apis.py` - Zewnętrzne API
  - Jak używa VirusTotal, Shodan, AbuseIPDB
  
- **Plik 20:** `oui_lookup.py` - Identyfikacja producenta
  - Jak identyfikuje producenta po adresie MAC
  
- **Plik 21:** `rust_scanner_wrapper.py` - Wrapper dla Rust
  - Jak używa kodu Rust z Python
  - Wyjaśnienie FFI (Foreign Function Interface)

---

## 🎯 Jak Używać Przewodnika

### Dla Początkujących:
1. **Zacznij od Części 1** - naucz się podstaw
2. **Przeczytaj Część 2** - zrozum jak działają skanery
3. **Przeczytaj Część 5** - zrozum główny moduł (najważniejszy!)
4. **Potem Części 3, 4, 6** - szczegóły

### Dla Zaawansowanych:
- Użyj jako **referencji** - znajdź konkretny plik który Cię interesuje
- Sprawdź **mapę zależności** w Części 1
- Przeczytaj wyjaśnienia konkretnych funkcji

---

## 📊 Statystyki

- **Łącznie plików .py:** 21
- **Części przewodnika:** 6
- **Szacunkowa długość:** ~500-800 stron (wszystkie części razem)

---

## 🔄 Aktualizacje

Przewodnik będzie aktualizowany wraz z rozwojem projektu. Każda część jest niezależna - możesz czytać w dowolnej kolejności.

---

**Status:** Część 1 ✅ Gotowa | Części 2-6 📝 W przygotowaniu

**Ostatnia aktualizacja:** 2026-01-27
