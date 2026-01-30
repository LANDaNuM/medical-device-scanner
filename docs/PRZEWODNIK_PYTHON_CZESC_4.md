# 🐍 Kompletny Przewodnik po Kodzie Python - Część 4: INTEGRACJE

## 📚 Spis Treści Części 4

1. [Wprowadzenie](#wprowadzenie)
2. [Plik 10: `api_server.py` - REST API (Flask)](#plik-10-api_serverpy---rest-api-flask)
3. [Plik 11: `dashboard.py` - Dashboard (Streamlit)](#plik-11-dashboardpy---dashboard-streamlit)
4. [Plik 12: `siem_exporter.py` - Eksport do SIEM](#plik-12-siem_exporterpy---eksport-do-siem)
5. [Plik 13: `threat_intelligence.py` - Threat Intelligence](#plik-13-threat_intelligencepy---threat-intelligence)

---

## Wprowadzenie

Moduły integracji **udostępniają dane** i **eksportują wyniki**:
- **API Server** - REST API (Flask) do pobierania danych przez HTTP
- **Dashboard** - interaktywny dashboard webowy (Streamlit)
- **SIEM Exporter** - eksportuje dane do systemów SIEM
- **Threat Intelligence** - sprawdza IP w bazach zagrożeń

---

## Plik 10: `api_server.py` - REST API (Flask)

### 📍 Lokalizacja: `src/api_server.py`

### 🎯 Cel
Udostępnia **REST API** do pobierania danych o urządzeniach przez HTTP.

### 📝 Kod z Wyjaśnieniami

#### Importy Flask

```python
try:
    from flask import Flask, jsonify, request, render_template_string
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None
```

**Wyjaśnienie:**
- `Flask` - framework do tworzenia serwerów webowych
- `jsonify` - konwertuje dane Python na JSON (dla API)
- `render_template_string` - renderuje HTML z stringa
- `CORS` - Cross-Origin Resource Sharing (pozwala na żądania z innych domen)

#### Konfiguracja Katalogów

```python
project_root = Path(__file__).parent.parent
scans_dir = project_root / "reports"
reports_dir = project_root / "reports"
scans_dir.mkdir(exist_ok=True)
reports_dir.mkdir(exist_ok=True)
```

**Wyjaśnienie:**
- `Path(__file__).parent.parent` - katalog główny projektu (2 poziomy wyżej)
- `project_root / "reports"` - **łączy ścieżki** (niezależne od systemu)
- `.mkdir(exist_ok=True)` - tworzy katalog jeśli nie istnieje (nie rzuca błędu jeśli istnieje)

#### Inicjalizacja Flask App

```python
app = Flask(__name__) if FLASK_AVAILABLE else None
```

**Wyjaśnienie:**
- `Flask(__name__)` - tworzy aplikację Flask
- `__name__` - nazwa modułu (używane przez Flask do znajdowania szablonów)
- Jeśli Flask nie jest dostępny → `app = None`

#### Funkcja: load_latest_scan()

```python
def load_latest_scan() -> Optional[Dict]:
    """Wczytuje najnowszy skan."""
    scan_files = sorted(list(scans_dir.glob("scan_*.json")))
    if not scan_files:
        return None
```

**Wyjaśnienie:**
- `scans_dir.glob("scan_*.json")` - **wyszukuje** pliki pasujące do wzorca
- `glob` - pattern matching (np. `scan_*.json` = wszystkie pliki zaczynające się od "scan_")
- `sorted(list(...))` - sortuje listę plików (alfabetycznie = chronologicznie jeśli nazwa zawiera timestamp)
- `if not scan_files:` - jeśli lista jest pusta → zwróć None

```python
    latest_file = scan_files[-1]
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
```

**Wyjaśnienie:**
- `scan_files[-1]` - **ostatni element** listy (najnowszy plik)
- `with open(...) as f:` - **context manager** - automatycznie zamyka plik
- `encoding='utf-8'` - kodowanie znaków (obsługuje polskie znaki)
- `json.load(f)` - **wczytuje** JSON z pliku i konwertuje na słownik Python

#### Funkcja: filter_devices()

```python
def filter_devices(devices: List[Dict], filters: Dict) -> List[Dict]:
    filtered = devices
    
    # Filtruj po protokole
    if 'protocol' in filters:
        protocol = filters['protocol'].upper()
        filtered = [d for d in filtered if d.get('protocol', '').upper() == protocol]
```

**Wyjaśnienie:**
- **List comprehension** - skrócony sposób filtrowania
- `[d for d in filtered if warunek]` - tworzy nową listę z elementami spełniającymi warunek
- **Równoważne z:**
  ```python
  new_filtered = []
  for d in filtered:
      if d.get('protocol', '').upper() == protocol:
          new_filtered.append(d)
  filtered = new_filtered
  ```

```python
    # Filtruj po security score (min)
    if 'score_min' in filters:
        try:
            score_min = int(filters['score_min'])
            filtered = [d for d in filtered if d.get('security_score', 0) >= score_min]
        except ValueError:
            pass
```

**Wyjaśnienie:**
- `try/except ValueError` - **łapie błąd** jeśli konwersja się nie powiedzie
- `int(filters['score_min'])` - konwertuje string na integer
- Jeśli błąd → `pass` (ignoruj, kontynuuj)
- **Dlaczego try/except?** Użytkownik może podać nieprawidłową wartość (np. "abc")

#### Flask Route: @app.route('/')

```python
@app.route('/')
def index():
    scan_data = load_latest_scan()
    if scan_data:
        return redirect('/dashboard')
    else:
        return render_template_string(WELCOME_HTML)
```

**Wyjaśnienie:**
- `@app.route('/')` - **dekorator** - definiuje endpoint (ścieżkę URL)
- `/` - główna strona (root)
- `def index():` - funkcja obsługująca żądanie
- `redirect('/dashboard')` - **przekierowuje** na inną stronę
- `render_template_string(...)` - renderuje HTML z stringa

#### Flask Route: @app.route('/devices')

```python
@app.route('/devices')
def get_devices():
    scan_data = load_latest_scan()
    if not scan_data:
        return jsonify({'error': 'Brak danych'}), 404
    
    devices = scan_data.get('devices', [])
    
    # Filtry z query parameters
    filters = {
        'protocol': request.args.get('protocol'),
        'score_min': request.args.get('score_min'),
        'score_max': request.args.get('score_max'),
        'has_encryption': request.args.get('has_encryption'),
        'search': request.args.get('search')
    }
```

**Wyjaśnienie:**
- `/devices` - endpoint zwracający listę urządzeń
- `request.args.get('protocol')` - pobiera **query parameter** z URL
- **Przykład:** `/devices?protocol=BLE&score_min=50`
- `request.args` - słownik z parametrami URL (po `?`)

```python
    # Usuń None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    # Filtruj urządzenia
    filtered_devices = filter_devices(devices, filters)
```

**Wyjaśnienie:**
- **Dict comprehension** - usuwa klucze z wartością None
- `{k: v for k, v in filters.items() if v is not None}`
- **Przykład:**
  ```python
  filters = {'protocol': 'BLE', 'score_min': None, 'search': 'test'}
  # Po filtrowaniu: {'protocol': 'BLE', 'search': 'test'}
  ```

```python
    # Sprawdź format żądania
    wants_json = request.headers.get('Accept', '').startswith('application/json') or \
                 request.args.get('format') == 'json'
    
    if wants_json:
        return jsonify(filtered_devices)
    else:
        return render_template_string(DEVICES_HTML, devices=filtered_devices)
```

**Wyjaśnienie:**
- Sprawdza czy klient chce JSON czy HTML
- `request.headers.get('Accept')` - nagłówek HTTP (jakie formaty akceptuje)
- `request.args.get('format')` - query parameter `?format=json`
- `or` - jeśli którykolwiek warunek True → chce JSON
- `jsonify(...)` - konwertuje dane Python na JSON response
- `render_template_string(..., devices=...)` - renderuje HTML z danymi

#### Flask Route: @app.route('/shutdown')

```python
shutdown_event = threading.Event()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_event.set()
    return jsonify({'status': 'shutting down'})
```

**Wyjaśnienie:**
- `threading.Event()` - **sygnał** między wątkami
- `.set()` - **ustawia** event (oznacza że serwer ma się zamknąć)
- `methods=['POST']` - tylko POST requests (nie GET)
- **Dlaczego?** Zamykanie serwera to operacja która powinna być POST (nie GET)

#### JavaScript Auto-Shutdown

```python
    <script>
        window.addEventListener('beforeunload', function() {
            navigator.sendBeacon('/shutdown');
        });
    </script>
```

**Wyjaśnienie:**
- **JavaScript** w HTML - wykonywany w przeglądarce
- `window.addEventListener('beforeunload', ...)` - nasłuchuje **przed zamknięciem** strony
- `navigator.sendBeacon('/shutdown')` - wysyła żądanie POST (nawet gdy strona się zamyka)
- **Dlaczego?** Aby serwer wiedział że przeglądarka się zamknęła

#### Uruchomienie Serwera

```python
def run_api_server(port: int = 5000, host: str = '127.0.0.1'):
    if not FLASK_AVAILABLE:
        raise ImportError("Flask nie jest zainstalowany")
    
    app.run(host=host, port=port, debug=False, threaded=True)
```

**Wyjaśnienie:**
- `app.run(...)` - **uruchamia** serwer Flask
- `host='127.0.0.1'` - tylko lokalne połączenia (nie z Internetu)
- `port=5000` - port serwera
- `threaded=True` - **wielowątkowość** (może obsługiwać wiele żądań jednocześnie)

### 🔗 Kiedy jest używany?
- Gdy uruchamiasz `scanner.py --api`
- Serwer działa w osobnym wątku
- Automatycznie otwiera przeglądarkę

---

## Plik 11: `dashboard.py` - Dashboard (Streamlit)

### 📍 Lokalizacja: `src/dashboard.py`

### 🎯 Cel
Tworzy **interaktywny dashboard webowy** do wizualizacji danych.

### 📝 Kod z Wyjaśnieniami

#### Import Streamlit

```python
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
```

**Wyjaśnienie:**
- `streamlit` - framework do szybkiego tworzenia dashboardów
- **Streamlit** - automatycznie tworzy interfejs webowy z kodu Python

#### Funkcja: main()

```python
def main():
    if not STREAMLIT_AVAILABLE:
        st.error("❌ Streamlit nie jest zainstalowany!")
        return
```

**Wyjaśnienie:**
- `st.error(...)` - wyświetla **czerwony komunikat błędu** w dashboardzie
- Streamlit automatycznie renderuje to w przeglądarce

```python
    st.set_page_config(
        page_title="Medical Device Security Scanner",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
```

**Wyjaśnienie:**
- `st.set_page_config(...)` - konfiguruje stronę
- `page_icon="🏥"` - emoji jako ikona
- `layout="wide"` - szeroki layout (więcej miejsca)

```python
    st.title("🏥 Medical Device Security Scanner")
    st.markdown("**Dashboard do analizy bezpieczeństwa urządzeń medycznych IoT**")
```

**Wyjaśnienie:**
- `st.title(...)` - **duży nagłówek**
- `st.markdown(...)` - renderuje Markdown (może zawierać **bold**, *italic*, itp.)

#### Sidebar (Boczny Panel)

```python
    st.sidebar.title("⚙️ Opcje")
    
    data_source = st.sidebar.radio(
        "Źródło danych:",
        ["Najnowszy skan", "Najnowszy raport", "Nowe skanowanie"]
    )
```

**Wyjaśnienie:**
- `st.sidebar.*` - elementy w **bocznym panelu**
- `st.sidebar.radio(...)` - **przyciski radio** (jeden wybór z listy)
- Zwraca wybraną wartość (string)

#### Wczytywanie Danych

```python
    if data_source == "Najnowszy skan":
        scan_data = load_latest_scan()
        if scan_data:
            devices_data = scan_data.get('devices', [])
        else:
            st.warning("⚠️ Brak dostępnych skanów.")
            return
```

**Wyjaśnienie:**
- `st.warning(...)` - wyświetla **żółty komunikat ostrzegawczy**
- `return` - **kończy** funkcję (nie wyświetla dalej)

#### Statystyki

```python
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Urządzeń", total_devices)
    with col2:
        st.metric("🔴 Wysokie Ryzyko", high_risk)
```

**Wyjaśnienie:**
- `st.columns(4)` - tworzy **4 kolumny** (layout)
- `with col1:` - **context manager** - wszystko w tym bloku idzie do kolumny 1
- `st.metric(...)` - wyświetla **metrykę** (liczba z etykietą)

#### Wykresy (Plotly)

```python
    if PLOTLY_AVAILABLE and PANDAS_AVAILABLE:
        df = devices_to_dataframe(devices_data)
        
        fig_score = px.histogram(
            df,
            x='Security Score',
            nbins=20,
            title='Rozkład Security Score'
        )
        st.plotly_chart(fig_score, use_container_width=True)
```

**Wyjaśnienie:**
- `px.histogram(...)` - tworzy **histogram** (wykres słupkowy)
- `x='Security Score'` - oś X = Security Score
- `nbins=20` - 20 przedziałów (słupków)
- `st.plotly_chart(...)` - wyświetla wykres Plotly w dashboardzie
- `use_container_width=True` - używa pełnej szerokości kontenera

#### Funkcja: devices_to_dataframe()

```python
def devices_to_dataframe(devices: List[Dict]) -> pd.DataFrame:
    data = []
    for device in devices:
        row = {
            'Nazwa': device.get('name', 'Unknown'),
            'MAC Address': device.get('mac_address', ''),
            'Security Score': device.get('security_score', 0),
            # ...
        }
        data.append(row)
    
    return pd.DataFrame(data)
```

**Wyjaśnienie:**
- Konwertuje listę słowników na **DataFrame** (tabela pandas)
- **DataFrame** - struktura danych jak Excel (wiersze i kolumny)
- Używany przez Plotly do tworzenia wykresów

### 🔗 Kiedy jest używany?
- Gdy uruchamiasz `streamlit run src/dashboard.py`
- Otwiera się w przeglądarce automatycznie

---

## Plik 12: `siem_exporter.py` - Eksport do SIEM

### 📍 Lokalizacja: `src/siem_exporter.py`

### 🎯 Cel
Eksportuje dane do systemów **SIEM** (Security Information and Event Management).

### 📝 Kod z Wyjaśnieniami

#### Enum: SIEMFormat

```python
class SIEMFormat(Enum):
    CEF = "cef"
    JSON_LINES = "jsonl"
    SYSLOG = "syslog"
    CSV = "csv"
```

**Wyjaśnienie:**
- Formaty eksportu do różnych systemów SIEM
- **CEF** - Common Event Format (Splunk, ArcSight)
- **JSON Lines** - dla ELK Stack
- **CSV** - uniwersalny format

#### Klasa SIEMExporter - Metoda: export_devices()

```python
    def export_devices(self, devices: List[Device], scan_timestamp: Optional[str] = None) -> str:
        if not scan_timestamp:
            scan_timestamp = datetime.now().isoformat()
        
        if self.format == SIEMFormat.CEF:
            return self._export_cef(devices, scan_timestamp)
        elif self.format == SIEMFormat.JSON_LINES:
            return self._export_json_lines(devices, scan_timestamp)
```

**Wyjaśnienie:**
- Sprawdza format i wywołuje odpowiednią metodę eksportu
- `datetime.now().isoformat()` - aktualna data/czas w formacie ISO (np. "2026-01-27T12:00:00")

#### Metoda: _export_cef() - Format CEF

```python
    def _export_cef(self, devices: List[Device], timestamp: str) -> str:
        lines = []
        
        for device in devices:
            severity = self._calculate_severity(device.security_score)
            
            extension = {
                'src': device.metadata.get('ip_address', 'N/A'),
                'mac': device.mac_address,
                'securityScore': device.security_score,
                # ...
            }
```

**Wyjaśnienie:**
- **CEF Format** - standardowy format dla SIEM
- Format: `CEF:Version|Vendor|Product|Version|Signature|Name|Severity|Extension`
- `extension` - dodatkowe pola (key=value)

```python
            ext_str = ' '.join([f"{k}={self._escape_cef_value(str(v))}" for k, v in extension.items()])
            
            cef_line = (
                f"CEF:0|Medical Device Scanner|Security Scanner|1.0|"
                f"device_scan|{self._escape_cef_value(device.name)}|{severity}|{ext_str}"
            )
            
            lines.append(cef_line)
```

**Wyjaśnienie:**
- **List comprehension** - tworzy listę stringów `["key=value", ...]`
- `' '.join(...)` - **łączy** elementy spacją
- `f"CEF:0|..."` - f-string z formatowaniem
- **Przykład CEF:**
  ```
  CEF:0|Medical Device Scanner|Security Scanner|1.0|device_scan|GlucoSmart|5|src=192.168.1.100 mac=AA:BB:CC securityScore=75
  ```

#### Metoda: _export_json_lines() - Format JSON Lines

```python
    def _export_json_lines(self, devices: List[Device], timestamp: str) -> str:
        lines = []
        
        for device in devices:
            event = {
                '@timestamp': timestamp,
                'event': {
                    'kind': 'event',
                    'category': 'network',
                    'type': 'device_scan',
                    'severity': 'Low' if device.security_score >= 80 else 'Medium' if device.security_score >= 50 else 'High'
                },
                'device': {
                    'name': device.name,
                    'mac_address': device.mac_address,
                    # ...
                }
            }
            lines.append(json.dumps(event, ensure_ascii=False))
```

**Wyjaśnienie:**
- **JSON Lines** - każda linia to osobny JSON (nie jeden duży JSON)
- Format dla **ELK Stack** (Elasticsearch, Logstash, Kibana)
- `json.dumps(...)` - konwertuje słownik Python na string JSON
- `ensure_ascii=False` - zachowuje polskie znaki (nie konwertuje na \uXXXX)

```python
        return self._write_output(lines)
```

**Wyjaśnienie:**
- Zapisuje wszystkie linie do pliku
- Zwraca ścieżkę do pliku

### 🔗 Kiedy jest używany?
- Automatycznie przez `scanner.py` (domyślnie włączony)
- Eksportuje do `exports/siem_export_*.jsonl`

---

## Plik 13: `threat_intelligence.py` - Threat Intelligence

### 📍 Lokalizacja: `src/threat_intelligence.py`

### 🎯 Cel
Sprawdza adresy IP w **bazach threat intelligence** (zagrożeń).

### 📝 Kod z Wyjaśnieniami

#### Cache

```python
CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"
THREAT_CACHE = CACHE_DIR / "threat_intel_cache.json"
```

**Wyjaśnienie:**
- **Cache** - przechowuje wyniki aby nie sprawdzać tego samego IP wiele razy
- Zapisuje do pliku JSON

#### Klasa ThreatIntelligence - Metoda: check_ip()

```python
    def check_ip(self, ip: str) -> Dict[str, Any]:
        # Sprawdź cache
        if ip in self.cache:
            cached_result = self.cache[ip]
            if time.time() - cached_result.get('cached_at', 0) < 86400:
                return cached_result
```

**Wyjaśnienie:**
- Sprawdza czy IP **jest w cache**
- `time.time()` - aktualny czas (Unix timestamp, sekundy od 1970)
- `86400` - 24 godziny w sekundach (cache ważny przez 24h)
- Jeśli cache jest świeży → zwróć z cache (nie sprawdzaj API)

```python
        result = {
            'ip': ip,
            'is_threat': False,
            'sources': {},
            'abuse_score': 0,
            'reputation': 'unknown',
            'checked_at': time.time()
        }
```

**Wyjaśnienie:**
- Tworzy słownik z wynikami
- `is_threat: False` - domyślnie nie jest zagrożeniem
- `sources: {}` - pusty słownik (będzie zawierał wyniki z różnych API)

#### Sprawdzanie AbuseIPDB

```python
        if self.abuseipdb_key and REQUESTS_AVAILABLE:
            abuse_result = self._check_abuseipdb(ip)
            if abuse_result:
                result['sources']['abuseipdb'] = abuse_result
                result['abuse_score'] = abuse_result.get('abuseConfidencePercentage', 0)
                result['is_threat'] = abuse_result.get('abuseConfidencePercentage', 0) > 25
```

**Wyjaśnienie:**
- Sprawdza AbuseIPDB API (jeśli klucz dostępny)
- `abuseConfidencePercentage` - procent pewności że IP jest złośliwe (0-100)
- `> 25` - jeśli >25% → uznaj za zagrożenie

#### Metoda: _check_abuseipdb()

```python
    def _check_abuseipdb(self, ip: str) -> Optional[Dict]:
        # Rate limiting
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
```

**Wyjaśnienie:**
- **Rate limiting** - ogranicza liczbę żądań (aby nie przekroczyć limitu API)
- `time.sleep(...)` - **czeka** określoną liczbę sekund
- **Dlaczego?** AbuseIPDB free tier = 1 request/second

```python
        url = "https://api.abuseipdb.com/api/v2/check"
        headers = {'Key': self.abuseipdb_key}
        params = {'ipAddress': ip, 'maxAgeInDays': 90, 'verbose': ''}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
```

**Wyjaśnienie:**
- `requests.get(...)` - wysyła **GET request** HTTP
- `headers={'Key': ...}` - nagłówek z kluczem API
- `params={...}` - **query parameters** w URL
- `timeout=10` - maksymalny czas czekania (10 sekund)

```python
        if response.status_code == 200:
            data = response.json()
            return {
                'abuseConfidencePercentage': data['data'].get('abuseConfidencePercentage', 0),
                'usageType': data['data'].get('usageType', 'unknown'),
                'country': data['data'].get('countryCode', 'unknown')
            }
```

**Wyjaśnienie:**
- `response.status_code == 200` - sukces (OK)
- `response.json()` - **parsuje** JSON response na słownik Python
- `data['data'].get(...)` - bezpieczne pobranie z zagnieżdżonego słownika

#### Zapisywanie do Cache

```python
        # Zapisz do cache
        self.cache[ip] = result
        self.cache[ip]['cached_at'] = time.time()
        self._save_cache()
```

**Wyjaśnienie:**
- Zapisuje wynik do cache
- `self.cache[ip] = result` - dodaje do słownika cache
- `self._save_cache()` - zapisuje cache do pliku JSON

### 🔗 Kiedy jest używany?
- Automatycznie przez `scanner.py` (domyślnie włączony)
- Sprawdza IP urządzeń WiFi w bazach threat intelligence

---

## 📝 Podsumowanie Części 4

### Co nauczyłeś się:
1. ✅ Jak działa REST API (Flask)
2. ✅ Jak działa Dashboard (Streamlit)
3. ✅ Jak eksportuje dane do SIEM
4. ✅ Jak sprawdza threat intelligence
5. ✅ Koncepty: HTTP requests, JSON, cache, rate limiting

### Kluczowe Koncepty:

**HTTP Requests:**
```python
response = requests.get(url, headers=headers, params=params)
data = response.json()  # Parsuje JSON
```

**Cache:**
```python
if ip in cache:
    return cache[ip]  # Użyj cache
else:
    result = check_api(ip)
    cache[ip] = result  # Zapisz do cache
```

**Rate Limiting:**
```python
time.sleep(1.0)  # Czekaj 1 sekundę między żądaniami
```

---

**Kontynuacja w: PRZEWODNIK_PYTHON_CZESC_5.md** (Główny Moduł: scanner.py)
