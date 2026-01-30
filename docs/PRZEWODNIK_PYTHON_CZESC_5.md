# 🐍 Kompletny Przewodnik po Kodzie Python - Część 5: GŁÓWNY MODUŁ

## 📚 Spis Treści Części 5

1. [Wprowadzenie](#wprowadzenie)
2. [Plik 14: `scanner.py` - GŁÓWNY MODUŁ ⭐](#plik-14-scannerpy---główny-moduł-)
3. [Plik 15: `history_db.py` - Baza Danych Historii](#plik-15-history_dbpy---baza-danych-historii)
4. [Plik 16: `scheduler.py` - Zaplanowane Skanowania](#plik-16-schedulerpy---zaplanowane-skanowania)
5. [Plik 17: `monitor.py` - Monitoring w Czasie Rzeczywistym](#plik-17-monitorpy---monitoring-w-czasie-rzeczywistym)

---

## Wprowadzenie

**Część 5** to najważniejsza część - zawiera **główny moduł** `scanner.py` który **łączy wszystkie komponenty** i **zarządza całym procesem skanowania**.

---

## Plik 14: `scanner.py` - GŁÓWNY MODUŁ ⭐

### 📍 Lokalizacja: `src/scanner.py`

### 🎯 Cel
**Główny moduł** który:
- Łączy wszystkie skanery (BLE, WiFi, USB, NFC)
- Zarządza procesem skanowania
- Analizuje bezpieczeństwo
- Generuje raporty
- Obsługuje argumenty wiersza poleceń

### 📝 Kod z Wyjaśnieniami

#### Importy i Konfiguracja

```python
#!/usr/bin/env python3
import sys
import os
import json
import csv
import time
from datetime import datetime
import asyncio
from pathlib import Path
```

**Wyjaśnienie:**
- Wszystkie podstawowe moduły Python
- `asyncio` - dla asynchronicznego skanowania BLE
- `Path` - do pracy ze ścieżkami (niezależne od systemu)

```python
try:
    from dotenv import load_dotenv
    project_dir = Path(__file__).parent.parent
    env_file = project_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass
```

**Wyjaśnienie:**
- `dotenv` - ładuje zmienne środowiskowe z pliku `.env`
- `Path(__file__).parent.parent` - katalog główny projektu
- `load_dotenv(env_file)` - ładuje klucze API z `.env`

#### Import Skanerów

```python
try:
    from real_scanner import RealBLEScanner
    BLE_SCANNER_AVAILABLE = True
except ImportError:
    BLE_SCANNER_AVAILABLE = False
    RealBLEScanner = None
```

**Wyjaśnienie:**
- **Try/except** dla każdego skanera
- Jeśli import się nie powiedzie → ustaw flagę `False`
- **Dlaczego?** Nie wszystkie biblioteki mogą być zainstalowane

#### Klasa MedicalDeviceScanner - Konstruktor

```python
class MedicalDeviceScanner:
    def __init__(self, protocols: List[str] = None):
        self.scanners = {}
        
        if protocols is None:
            protocols = ['ble', 'wifi', 'usb', 'nfc']
```

**Wyjaśnienie:**
- `self.scanners = {}` - słownik przechowujący skanery
- **Klucz:** nazwa protokołu ('ble', 'wifi', ...)
- **Wartość:** obiekt skanera (RealBLEScanner, WiFiScanner, ...)
- `protocols = ['ble', ...]` - domyślnie wszystkie protokoły

```python
        # BLE Scanner
        if 'ble' in protocols:
            if BLE_SCANNER_AVAILABLE:
                try:
                    self.scanners['ble'] = RealBLEScanner()
                    console.print("[green]✅ Skaner BLE gotowy[/green]")
                except ImportError as e:
                    console.print(f"[yellow]⚠️  Skaner BLE niedostępny: {e}[/yellow]")
```

**Wyjaśnienie:**
- Sprawdza czy BLE jest w liście protokołów
- Sprawdza czy biblioteka jest dostępna
- Tworzy obiekt `RealBLEScanner()` i zapisuje do słownika
- `self.scanners['ble']` - dostęp do skanera BLE

#### Metoda: scan_all() - Główna Metoda Skanowania

```python
    def scan_all(self) -> List[Device]:
        console.print("[bold blue]🔍 Rozpoczynam kompleksowe skanowanie...[/bold blue]\n")
        
        all_devices = []
```

**Wyjaśnienie:**
- Główna metoda która **uruchamia wszystkie skanery**
- `all_devices = []` - lista wszystkich wykrytych urządzeń

```python
        # Skanuj BLE
        if 'ble' in self.scanners:
            console.print(Panel.fit("📡 Skanowanie Bluetooth Low Energy (BLE)", style="cyan"))
            ble_devices = self._scan_ble_async(duration=10)
            all_devices.extend(ble_devices)
```

**Wyjaśnienie:**
- Sprawdza czy skaner BLE jest dostępny
- `Panel.fit(...)` - wyświetla ładny panel (z biblioteki rich)
- `self._scan_ble_async(duration=10)` - skanuje przez 10 sekund
- `all_devices.extend(ble_devices)` - **dodaje wszystkie** urządzenia BLE do listy

```python
        # Skanuj WiFi
        if 'wifi' in self.scanners:
            wifi_devices = self.scanners['wifi'].scan_wifi_devices()
            all_devices.extend(wifi_devices)
```

**Wyjaśnienie:**
- Pobiera skaner WiFi ze słownika
- `self.scanners['wifi']` - obiekt `WiFiScanner`
- `.scan_wifi_devices()` - wywołuje metodę skanowania
- **Każdy skaner ma swoją metodę:** `scan_ble_devices()`, `scan_wifi_devices()`, itd.

#### Metoda: _scan_ble_async() - Wrapper dla Async

```python
    def _scan_ble_async(self, duration: int = 10) -> List[Device]:
        if platform.system() == "Windows":
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.scanners['ble'].scan_ble_devices(duration))
            finally:
                loop.close()
        else:
            return asyncio.run(self.scanners['ble'].scan_ble_devices(duration))
```

**Wyjaśnienie:**
- **Wrapper** - konwertuje async na sync
- Windows wymaga **nowego event loop**
- Linux/Mac może użyć `asyncio.run()` bezpośrednio
- `loop.run_until_complete(...)` - **czeka** na zakończenie funkcji async
- `finally:` - **zawsze** wykonuje się (nawet jeśli błąd)

#### Metoda: analyze_security() - Analiza Bezpieczeństwa

```python
    def analyze_security(self, run_vulnerability_tests: bool = False):
        console.print("[bold blue]🔒 Analizuję bezpieczeństwo urządzeń...[/bold blue]\n")
        
        for device in self.devices:
            # Oblicz wynik bezpieczeństwa
            device.calculate_security_score()
```

**Wyjaśnienie:**
- Iteruje przez **wszystkie** wykryte urządzenia
- `device.calculate_security_score()` - oblicza wynik (0-100)

```python
            # Sprawdź zgodność z FDA guidelines
            self._check_fda_compliance(device)
            
            # Wzbogać dane zewnętrznymi API
            if self.external_apis:
                self._enrich_device_with_external_apis(device)
            
            # Analizuj szyfrowanie
            if self.encryption_analyzer:
                self._analyze_encryption(device)
            
            # Wykonaj testy podatności jeśli włączone
            if run_vulnerability_tests and self.vulnerability_tester:
                self._run_vulnerability_tests(device)
```

**Wyjaśnienie:**
- **Kolejność analizy:**
  1. Oblicz security score
  2. Sprawdź zgodność z FDA
  3. Wzbogać danymi z API (VirusTotal, Shodan)
  4. Analizuj szyfrowanie
  5. Testuj podatności (jeśli `--audit`)

```python
        # Wykryj anomalie używając ML (zawsze włączone)
        if self.anomaly_detector and len(self.devices) > 0:
            self._detect_anomalies()
```

**Wyjaśnienie:**
- **ML wykrywanie anomalii** - zawsze włączone (jeśli dostępne)
- `len(self.devices) > 0` - sprawdza czy są urządzenia

#### Metoda: save_scan_results() - Zapis Wyników

```python
    def save_scan_results(self) -> str:
        if not self.devices:
            return ""
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"scan_{timestamp}.json"
        filepath = self.scans_dir / filename
```

**Wyjaśnienie:**
- Tworzy nazwę pliku z **timestampem**
- Format: `scan_2026-01-27_12-00-00.json`
- `self.scans_dir / filename` - łączy ścieżki (niezależne od systemu)

```python
        scan_data = {
            "scan_timestamp": datetime.now().isoformat(),
            "total_devices": len(self.devices),
            "protocols_scanned": list(self.scanners.keys()),
            "devices": [device.to_dict() for device in self.devices]
        }
```

**Wyjaśnienie:**
- Tworzy słownik z danymi skanowania
- `list(self.scanners.keys())` - lista protokołów (['ble', 'wifi', ...])
- `[device.to_dict() for device in self.devices]` - **list comprehension**
- Konwertuje wszystkie obiekty Device na słowniki

```python
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(scan_data_serializable, f, indent=2, ensure_ascii=False)
```

**Wyjaśnienie:**
- `json.dump(...)` - zapisuje słownik do pliku JSON
- `indent=2` - wcięcia (ładne formatowanie)
- `ensure_ascii=False` - zachowuje polskie znaki

#### Funkcja: main() - Główna Funkcja Programu

```python
def main():
    parser = argparse.ArgumentParser(
        description='Medical Device Security Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
```

**Wyjaśnienie:**
- `argparse` - moduł do parsowania argumentów wiersza poleceń
- `ArgumentParser` - tworzy parser argumentów
- **Przykład:** `python scanner.py --ble --wifi --audit`

```python
    parser.add_argument('--ble', action='store_true', help='Skanuj tylko BLE')
    parser.add_argument('--wifi', action='store_true', help='Skanuj tylko WiFi')
    parser.add_argument('--usb', action='store_true', help='Skanuj tylko USB')
    parser.add_argument('--nfc', action='store_true', help='Skanuj tylko NFC')
```

**Wyjaśnienie:**
- `action='store_true'` - jeśli flaga jest podana → `True`, jeśli nie → `False`
- **Przykład:**
  ```bash
  python scanner.py --ble  # args.ble = True
  python scanner.py        # args.ble = False
  ```

```python
    parser.add_argument('--audit', action='store_true', help='Pełny audyt bezpieczeństwa')
    parser.add_argument('--api', action='store_true', help='Uruchom API server')
    parser.add_argument('--api-port', type=int, default=5000, help='Port dla API')
```

**Wyjaśnienie:**
- `--audit` - włącza testy podatności
- `--api` - uruchamia serwer API
- `type=int` - konwertuje argument na integer
- `default=5000` - domyślna wartość jeśli nie podano

```python
    args = parser.parse_args()
```

**Wyjaśnienie:**
- **Parsuje** argumenty z wiersza poleceń
- Zwraca obiekt `args` z wszystkimi wartościami

```python
    # Określ protokoły do skanowania
    protocols = []
    if args.ble:
        protocols.append('ble')
    if args.wifi:
        protocols.append('wifi')
```

**Wyjaśnienie:**
- Tworzy listę protokołów na podstawie argumentów
- `protocols.append('ble')` - **dodaje** protokół do listy

```python
    # Jeśli nie wybrano żadnego protokołu, skanuj wszystkie
    if not protocols:
        protocols = ['ble', 'usb', 'nfc']
        if not args.no_wifi:
            protocols.append('wifi')
```

**Wyjaśnienie:**
- Jeśli użytkownik **nie wybrał** protokołów → skanuj wszystkie
- `if not protocols:` - sprawdza czy lista jest pusta
- `if not args.no_wifi:` - jeśli nie wyłączono WiFi → dodaj WiFi

```python
    # Utwórz skaner
    scanner = MedicalDeviceScanner(protocols=protocols)
    
    # Skanuj urządzenia
    devices = scanner.scan_all()
```

**Wyjaśnienie:**
- Tworzy obiekt skanera z wybranymi protokołami
- `scanner.scan_all()` - uruchamia skanowanie wszystkich protokołów

```python
    if not devices:
        console.print("[yellow]⚠️  Nie znaleziono żadnych urządzeń[/yellow]")
    else:
        # Analizuj bezpieczeństwo
        scanner.analyze_security(run_vulnerability_tests=run_vulnerability_tests)
        
        # Wyświetl wyniki
        scanner.display_results()
```

**Wyjaśnienie:**
- Sprawdza czy znaleziono urządzenia
- Jeśli tak → analizuj i wyświetl wyniki
- `run_vulnerability_tests=args.audit` - włącza testy jeśli `--audit`

#### Funkcja: perform_scan() - Dla Scheduler/Monitor

```python
        def perform_scan():
            """Wykonuje pełne skanowanie - używane przez scheduler/monitor"""
            scan_scanner = MedicalDeviceScanner(protocols=protocols)
            scan_devices = scan_scanner.scan_all()
            
            if scan_devices:
                scan_scanner.analyze_security(run_vulnerability_tests=run_vulnerability_tests)
                
                # Zapisz do historii
                try:
                    from history_db import HistoryDB
                    scan_history_db = HistoryDB()
                    scan_history_db.save_scan(scan_devices, protocols)
                except Exception:
                    pass
            
            return scan_devices
```

**Wyjaśnienie:**
- **Funkcja zagnieżdżona** (definiowana wewnątrz `main()`)
- Używana przez scheduler i monitor
- Tworzy **nowy skaner** dla każdego skanowania (świeże dane)
- Zapisuje do historii automatycznie

#### Scheduler (--schedule)

```python
        if args.schedule:
            try:
                from scheduler import ScanScheduler
                scheduler = ScanScheduler()
                scheduler.add_schedule(args.schedule, perform_scan)
                scheduler.start()
```

**Wyjaśnienie:**
- Jeśli użytkownik podał `--schedule` → uruchom scheduler
- `scheduler.add_schedule(...)` - dodaje zaplanowane skanowanie
- `scheduler.start()` - uruchamia scheduler w tle

```python
                # Czekaj w nieskończoność
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    scheduler.stop()
                    return
```

**Wyjaśnienie:**
- `while True:` - **nieskończona pętla**
- `time.sleep(1)` - czeka 1 sekundę (nie obciąża CPU)
- `except KeyboardInterrupt:` - **łapie** Ctrl+C
- `scheduler.stop()` - zatrzymuje scheduler

#### Monitor (--monitor)

```python
        if args.monitor:
            from monitor import RealTimeMonitor
            monitor = RealTimeMonitor(
                scan_function=perform_scan,
                interval=args.interval,
                alert_on_new=True,
                alert_on_risk_change=True,
                history_db=monitor_history_db
            )
            monitor.start(email_recipients=[])
```

**Wyjaśnienie:**
- Uruchamia monitoring w czasie rzeczywistym
- `scan_function=perform_scan` - przekazuje funkcję skanowania
- `interval=args.interval` - interwał skanowania (domyślnie 300s = 5 min)

#### API Server (--api)

```python
        if args.api:
            from api_server import app, shutdown_event
            import threading
            import webbrowser
            
            def run_server():
                app.run(host='0.0.0.0', port=args.api_port, debug=False, use_reloader=False)
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            time.sleep(2)
            webbrowser.open(f'http://localhost:{args.api_port}')
```

**Wyjaśnienie:**
- Uruchamia serwer Flask w **osobnym wątku**
- `threading.Thread(target=run_server, daemon=True)` - wątek daemon (kończy się z programem)
- `webbrowser.open(...)` - **otwiera przeglądarkę** automatycznie
- `time.sleep(2)` - czeka 2 sekundy (na uruchomienie serwera)

```python
            # Czekaj na zamknięcie przeglądarki
            while not shutdown_event.is_set():
                time.sleep(0.5)
            
            console.print("\n[yellow]⏹️  Zamykam serwer...[/yellow]")
            return
```

**Wyjaśnienie:**
- `shutdown_event.is_set()` - sprawdza czy event jest ustawiony
- Czeka aż przeglądarka wyśle żądanie `/shutdown`
- Gdy event jest ustawiony → kończy program

### 🔗 Kiedy jest używany?
- **Zawsze!** To jest główny punkt wejścia programu
- Uruchamiasz: `python src/scanner.py`

---

## Plik 15: `history_db.py` - Baza Danych Historii

### 📍 Lokalizacja: `src/history_db.py`

### 🎯 Cel
Przechowuje **historię skanowań** w bazie danych SQLite.

### 📝 Kod z Wyjaśnieniami

#### SQLite Connection

```python
import sqlite3

conn = sqlite3.connect(self.db_path)
cursor = conn.cursor()
```

**Wyjaśnienie:**
- `sqlite3` - moduł do pracy z bazą danych SQLite
- `connect(...)` - **łączy się** z bazą (tworzy jeśli nie istnieje)
- `cursor` - obiekt do wykonywania zapytań SQL

#### Tworzenie Tabel

```python
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_devices INTEGER NOT NULL,
                high_risk_count INTEGER NOT NULL,
                avg_security_score REAL NOT NULL
            )
        """)
```

**Wyjaśnienie:**
- **SQL** - język zapytań do baz danych
- `CREATE TABLE IF NOT EXISTS` - tworzy tabelę jeśli nie istnieje
- `INTEGER PRIMARY KEY AUTOINCREMENT` - automatycznie zwiększający się ID
- `TEXT`, `INTEGER`, `REAL` - typy danych SQL

```python
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                mac_address TEXT NOT NULL,
                FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
            )
        """)
```

**Wyjaśnienie:**
- **FOREIGN KEY** - klucz obcy (łączy z inną tabelą)
- `REFERENCES scans(id)` - odniesienie do tabeli `scans`
- `ON DELETE CASCADE` - jeśli usuniesz skanowanie, usuń też urządzenia

#### Metoda: save_scan() - Zapis Skanowania

```python
    def save_scan(self, devices: List[Device], protocols: List[str]) -> int:
        timestamp = datetime.now().isoformat()
        total_devices = len(devices)
        
        high_risk = len([d for d in devices if d.security_score < 50])
```

**Wyjaśnienie:**
- Oblicza statystyki przed zapisem
- **List comprehension** - zlicza urządzenia wysokiego ryzyka

```python
        cursor.execute("""
            INSERT INTO scans (timestamp, total_devices, high_risk_count, ...)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, total_devices, high_risk, ...))
```

**Wyjaśnienie:**
- **SQL INSERT** - dodaje rekord do tabeli
- `?` - **placeholders** (zapobiega SQL injection)
- `(timestamp, ...)` - wartości do wstawienia

```python
        scan_id = cursor.lastrowid
        
        # Zapisz urządzenia
        for device in devices:
            device_dict = device.to_dict()
            cursor.execute("""
                INSERT INTO scan_devices (scan_id, mac_address, name, ...)
                VALUES (?, ?, ?, ...)
            """, (scan_id, device.mac_address, device.name, ...))
```

**Wyjaśnienie:**
- `cursor.lastrowid` - **ID ostatnio wstawionego rekordu**
- Dla każdego urządzenia → zapisz do tabeli `scan_devices`
- `scan_id` - łączy urządzenie ze skanowaniem

```python
        conn.commit()
        conn.close()
```

**Wyjaśnienie:**
- `conn.commit()` - **zapisuje** zmiany (bez tego nie są zapisane!)
- `conn.close()` - zamyka połączenie z bazą

#### Metoda: get_recent_scans() - Pobieranie Historii

```python
    def get_recent_scans(self, limit: int = 10) -> List[ScanHistory]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM scans
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
```

**Wyjaśnienie:**
- **SQL SELECT** - pobiera dane z tabeli
- `ORDER BY timestamp DESC` - sortuje od najnowszych
- `LIMIT ?` - tylko N najnowszych rekordów

```python
        rows = cursor.fetchall()
        
        scans = []
        for row in rows:
            scan_id, timestamp, total_devices, ... = row
            scans.append(ScanHistory(...))
        
        return scans
```

**Wyjaśnienie:**
- `cursor.fetchall()` - **pobiera wszystkie** wyniki zapytania
- `row` - krotka (tuple) z wartościami kolumn
- **Unpacking:** `scan_id, timestamp, ... = row` - przypisuje wartości do zmiennych

### 🔗 Kiedy jest używany?
- Automatycznie przez `scanner.py` (zapisuje każdy skan)
- Używany przez scheduler i monitor

---

## Plik 16: `scheduler.py` - Zaplanowane Skanowania

### 📍 Lokalizacja: `src/scheduler.py`

### 🎯 Cel
Umożliwia **zaplanowane skanowania** (np. codziennie o 9:00).

### 📝 Kod z Wyjaśnieniami

#### Import Schedule

```python
import schedule
import time
import threading
```

**Wyjaśnienie:**
- `schedule` - biblioteka do planowania zadań (cron-like)
- `threading` - do uruchomienia scheduler w tle

#### Klasa ScanScheduler - Metoda: add_schedule()

```python
    def add_schedule(self, schedule_str: str, scan_function: Callable):
        if schedule_str.startswith("daily"):
            parts = schedule_str.split()
            time_str = parts[1]  # "09:00"
            schedule.every().day.at(time_str).do(self._run_scheduled_scan)
```

**Wyjaśnienie:**
- Parsuje string schedule (np. "daily 09:00")
- `schedule.every().day.at("09:00")` - **planuje** zadanie codziennie o 9:00
- `.do(self._run_scheduled_scan)` - funkcja do wywołania

```python
        elif schedule_str == "hourly":
            schedule.every().hour.do(self._run_scheduled_scan)
        
        elif schedule_str.startswith("every"):
            parts = schedule_str.split()
            interval = int(parts[1])  # "30"
            unit = parts[2].lower()  # "minutes"
            
            if unit.startswith("minute"):
                schedule.every(interval).minutes.do(self._run_scheduled_scan)
```

**Wyjaśnienie:**
- Różne formaty schedule
- `schedule.every(30).minutes` - co 30 minut
- `schedule.every().hour` - co godzinę

#### Metoda: start() - Uruchomienie Scheduler

```python
    def start(self):
        self.running = True
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
```

**Wyjaśnienie:**
- `run_scheduler()` - funkcja wewnętrzna (wykonuje się w pętli)
- `while self.running:` - pętla dopóki scheduler działa
- `schedule.run_pending()` - **sprawdza** czy są zadania do wykonania
- `time.sleep(1)` - czeka 1 sekundę (nie obciąża CPU)
- `threading.Thread(..., daemon=True)` - wątek daemon (kończy się z programem)

### 🔗 Kiedy jest używany?
- Gdy uruchamiasz `scanner.py --schedule "daily 09:00"`

---

## Plik 17: `monitor.py` - Monitoring w Czasie Rzeczywistym

### 📍 Lokalizacja: `src/monitor.py`

### 🎯 Cel
**Monitoruje** urządzenia w czasie rzeczywistym (ciągłe skanowanie).

### 📝 Kod z Wyjaśnieniami

#### Klasa RealTimeMonitor - Metoda: start()

```python
    def start(self, email_recipients: Optional[List[str]] = None):
        self.running = True
        
        def run_monitor():
            scan_count = 0
            while self.running:
                scan_count += 1
                console.print(f"\n[cyan]🔍 Monitor: Skanowanie #{scan_count}[/cyan]")
                
                # Wykonaj skanowanie
                devices = self.scan_function()
```

**Wyjaśnienie:**
- `run_monitor()` - funkcja wewnętrzna (wykonuje się w pętli)
- `scan_count` - licznik skanowań
- `self.scan_function()` - wywołuje funkcję skanowania (przekazaną w konstruktorze)

```python
                if devices:
                    # Sprawdź nowe urządzenia
                    if self.alert_on_new:
                        new_devices = self._detect_new_devices(devices)
                        if new_devices:
                            self._handle_new_devices(new_devices)
```

**Wyjaśnienie:**
- Sprawdza czy są **nowe urządzenia** (nie widziane wcześniej)
- Jeśli tak → wyświetla alert

```python
                # Czekaj na następne skanowanie
                for _ in range(self.interval):
                    if not self.running:
                        break
                    time.sleep(1)
```

**Wyjaśnienie:**
- Czeka `self.interval` sekund (np. 300 = 5 minut)
- `for _ in range(self.interval):` - pętla N razy
- `_` - zmienna której nie używamy (konwencja Python)
- `time.sleep(1)` - czeka 1 sekundę w każdej iteracji
- **Dlaczego nie `time.sleep(self.interval)`?** Bo możemy przerwać wcześniej (`if not self.running`)

#### Metoda: _detect_new_devices()

```python
    def _detect_new_devices(self, current_devices: List[Device]) -> List[Device]:
        if not self.known_devices:
            # Pierwsze skanowanie - wszystkie są nowe, ale nie alertujemy
            for device in current_devices:
                self.known_devices.add(device.mac_address)
            return []
        
        new_devices = [d for d in current_devices if d.mac_address not in self.known_devices]
        return new_devices
```

**Wyjaśnienie:**
- `self.known_devices` - **zbiór** (Set) znanych adresów MAC
- `if not self.known_devices:` - pierwsze skanowanie (nie ma znanych urządzeń)
- **List comprehension:** `[d for d in current_devices if d.mac_address not in self.known_devices]`
- Zwraca tylko **nowe** urządzenia (nie widziane wcześniej)

#### Metoda: _detect_risk_changes()

```python
    def _detect_risk_changes(self, current_devices: List[Device]) -> List[dict]:
        changes = []
        
        for device in current_devices:
            mac = device.mac_address
            current_score = device.security_score
            previous_score = self.device_scores.get(mac)
            
            if previous_score is not None:
                if abs(current_score - previous_score) >= 20:
                    if current_score < previous_score:
                        changes.append({
                            'device': device,
                            'previous_score': previous_score,
                            'current_score': current_score,
                            'change': current_score - previous_score
                        })
        
        return changes
```

**Wyjaśnienie:**
- Sprawdza **zmiany** w security score
- `abs(current_score - previous_score)` - **wartość bezwzględna** różnicy
- `>= 20` - znacząca zmiana (więcej niż 20 punktów)
- `if current_score < previous_score:` - tylko jeśli **spadł** (gorzej)

### 🔗 Kiedy jest używany?
- Gdy uruchamiasz `scanner.py --monitor --interval 300`

---

## 📝 Podsumowanie Części 5

### Co nauczyłeś się:
1. ✅ Jak działa główny moduł scanner.py
2. ✅ Jak łączy wszystkie komponenty
3. ✅ Jak obsługuje argumenty wiersza poleceń (argparse)
4. ✅ Jak używa SQLite do przechowywania historii
5. ✅ Jak działa scheduler i monitor
6. ✅ Koncepty: threading, async/sync, SQL, argparse

### Kluczowe Koncepty:

**Argparse:**
```python
parser.add_argument('--ble', action='store_true')
args = parser.parse_args()
if args.ble:  # True jeśli --ble było podane
```

**Threading:**
```python
thread = threading.Thread(target=function, daemon=True)
thread.start()  # Uruchamia w tle
```

**SQL:**
```python
cursor.execute("SELECT * FROM table WHERE id = ?", (id,))
rows = cursor.fetchall()
```

**Async/Sync:**
```python
# Async → Sync
result = asyncio.run(async_function())
# Lub dla Windows:
loop = asyncio.new_event_loop()
result = loop.run_until_complete(async_function())
```

---

**Kontynuacja w: PRZEWODNIK_PYTHON_CZESC_6.md** (Pomocnicze Moduły)
