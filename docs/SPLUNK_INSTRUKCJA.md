# 🚀 Splunk - Prosta Instrukcja (NAJŁATWIEJSZE!)

## ✅ Dlaczego Splunk?

**Splunk Free - Najprostsze rozwiązanie SIEM:**
- ✅ **Nie wymaga OpenSearch/Elasticsearch** - działa samodzielnie
- ✅ **Gotowy dashboard** - działa od razu po instalacji
- ✅ **Prosta instalacja** - jeden plik .deb/.rpm
- ✅ **Darmowy limit:** 500MB/dzień (wystarczy dla skanowania)
- ✅ **Bardzo dobry interfejs** - profesjonalny dashboard

---

## 🚀 Instalacja Splunk (5 minut)

### Krok 1: Pobierz Splunk Free

**Metoda 1: Pobierz z oficjalnej strony (ZALECANE)**

1. Otwórz w przeglądarce: https://www.splunk.com/en_us/download/splunk-enterprise.html
2. Kliknij "Free Download" lub "Try Free"
3. Utwórz konto (darmowe) lub zaloguj się
4. Wybierz:
   - **Platform:** Linux
   - **Architecture:** 64-bit
   - **Package Type:** Debian Package (.deb)
5. Pobierz plik `.deb` na swój komputer

**Metoda 2: Pobierz przez wget (jeśli masz link)**

```bash
# UWAGA: Link może być nieaktualny - lepiej pobrać z oficjalnej strony
# Jeśli masz aktualny link, użyj:
cd /tmp
wget -O splunk.deb "TWÓJ_LINK_DO_SPLUNK.deb"
```

**Aktualna wersja:** Splunk Enterprise 10.2.0 (sprawdź na stronie pobierania)

### Krok 2: Zainstaluj

```bash
sudo dpkg -i splunk*.deb
sudo apt-get install -f  # Napraw zależności jeśli potrzeba
```

### Krok 2.5: Napraw Uprawnienia (WAŻNE!)

**Jeśli widzisz błędy o braku uprawnień do katalogów, uruchom:**

```bash
# Użyj automatycznego skryptu:
./napraw_splunk.sh

# Lub ręcznie:
sudo chown -R root:root /opt/splunk
sudo chmod -R 755 /opt/splunk
sudo mkdir -p /opt/splunk/var/log/{splunk,introspection,watchdog,client_events}
sudo mkdir -p /opt/splunk/etc/licenses/download-trial
```

### Krok 3: Uruchom Splunk

**WAŻNE:** Splunk zaleca uruchamianie jako użytkownik `splunk`, nie jako root.

```bash
# Najpierw napraw uprawnienia (jeśli jeszcze nie):
./napraw_splunk.sh

# Uruchom jako użytkownik splunk (ZALECANE):
sudo -u splunk /opt/splunk/bin/splunk start --accept-license --answer-yes --no-prompt

# LUB jeśli chcesz uruchomić jako root (niezalecane, ale działa):
# sudo /opt/splunk/bin/splunk start --accept-license --answer-yes --no-prompt --run-as-root

# Ustaw hasło admina (wymagane)
sudo -u splunk /opt/splunk/bin/splunk edit user admin -password TWOJE_HASLO -auth admin:changeme

# Uruchom przy starcie systemu (jako użytkownik splunk)
sudo -u splunk /opt/splunk/bin/splunk enable boot-start -user splunk
```

### Krok 4: Otwórz Splunk

```
http://localhost:8000
```

**Login:** `admin`  
**Hasło:** (to które ustawiłeś w kroku 3)

---

## 📤 Import Danych ze Skanera

**Ważne:** W **Upload** (Add Data → Upload) Splunk przyjmuje **tylko jeden plik** na raz. Żeby dodać **wiele plików albo cały folder** (np. `~/splunk_import` z raportami z Pi), użyj **monitorowanego katalogu** – patrz [Metoda 3: Monitorowany katalog (wiele plików / cały folder)](#metoda-3-monitorowany-katalog-wiele-plików--cały-folder).

---

### Metoda 1: Upload jednego pliku (Web UI)

Skaner tworzy plik `siem_export_*.jsonl`. W UI możesz wgrać **jeden** taki plik:

```bash
# 1. Uruchom skaner
python3 src/scanner.py

# 2. Zaimportuj do Splunk (przez web UI)
```

**W Splunk Web UI:**
1. Otwórz: http://localhost:8000
2. Kliknij: **Settings** → **Add Data**
3. Wybierz: **Upload** → **Select File**
4. Wybierz **jeden** plik: `siem_export_*.jsonl`
5. Kliknij: **Next** → **Review** → **Submit**

### Metoda 2: Przez API (Automatycznie)

```bash
# Użyj skryptu do automatycznego importu
./import_to_splunk.sh
```

### Metoda 3: Monitorowany katalog (wiele plików / cały folder)

Żeby Splunk indeksował **wszystkie** pliki `siem_export_*.jsonl` z danego folderu (np. po zgraniu raportów z Pi do `~/splunk_import`), dodaj **Files & Directories** i wskaż **katalog** oraz **wzorzec**:

1. **Settings** (lub **Settings** → **Data**) → **Data inputs** → **Files & Directories**
2. **Add new** / **New**
3. **File or Directory:** ścieżka do **folderu**, np.:
   - `C:\Users\TwojaNazwa\splunk_import` (Windows)
   - `/home/twoja_nazwa/splunk_import` (Linux)
   - katalog z projektem, np. `/home/pi/medical-device-scanner-main/exports`
4. **File pattern (optional):** `siem_export_*.jsonl` – wtedy Splunk bierze tylko te pliki z folderu
5. **Source type:** `_json` (albo zostaw auto)
6. **Save**

Splunk **przeskanuje folder** i zindeksuje wszystkie pasujące pliki. Nowe pliki dopisane do tego folderu też będą automatycznie brane przy następnym skanowaniu (w zależności od ustawień inputu). Dzięki temu masz „cały folder” i wiele plików za jednym razem.

---

### Skaner na Raspberry Pi – raporty na główny PC

Jeśli skaner działa na Pi, a Splunk na PC, raporty trzeba przenieść z Pi na PC. Szybkie opcje: **scp/rsync z PC** (PC pobiera), **skrypt na Pi** (Pi wysyła po skanie) lub **udział Samba**. Pełna instrukcja: **[RAPORTY_PI_NA_PC.md](RAPORTY_PI_NA_PC.md)**. Po zgraniu do folderu na PC użyj **Metody 3** (monitorowany katalog), żeby Splunk zindeksował wszystkie pliki z tego folderu.

---

## 🔍 Jak Zobaczyć Wyniki w Splunk?

### 1. Otwórz Splunk Dashboard

```
http://localhost:8000
```

### 2. Wyszukaj Urządzenia

W polu wyszukiwania wpisz:
```
index=main device.name=*
```

### 3. Zobacz Wszystkie Urządzenia

```
index=main event.type="device_scan" | stats count by device.name, device.type
```

### 4. Zobacz Urządzenia Wysokiego Ryzyka

```
index=main event.severity="High" OR event.severity="Critical" | table device.name, device.security_score, device.vulnerabilities
```

---

## 🎯 Przykładowe Zapytania

### Wszystkie urządzenia:
```
index=main event.type="device_scan"
```

### Urządzenia z podatnościami:
```
index=main device.vulnerability_count > 0
```

### Urządzenia według protokołu:
```
index=main | stats count by device.protocol
```

### Urządzenia według bezpieczeństwa:
```
index=main | stats avg(device.security_score) by device.name
```

---

## 📊 Jak stworzyć dashboard w Splunk

1. **Wejdź w Splunk:** http://localhost:8000 → zaloguj się.
2. **Utwórz dashboard:**  
   **Create** → **Dashboard** (albo **Apps** → **Search & Reporting** → **Dashboards** → **Create New Dashboard**).
3. **Podaj nazwę**, np. `Skaner urządzeń medycznych`, wybierz uprawnienia (np. **Private** lub **Shared in App**) → **Save**.
4. **Dodaj panel (wykres/tabela):**
   - **Add Panel** → **New** (lub **Add Input** jeśli chcesz filtr).
   - **Content** → w polu **Search** wklej jedno z zapytań z sekcji [Komendy SPL](#-komendy-spl-do-przeglądania-danych-ściąga) poniżej.
   - **Visualization:** wybierz typ: **Table** (tabela), **Pie Chart**, **Column Chart**, **Single Value** itd.
   - **Title:** np. „Urządzenia wysokiego ryzyka”.
   - **Save**.
5. **Więcej paneli:** powtórz **Add Panel** dla innych zapytań (np. liczba po protokole, średni security score).
6. **Zapisz dashboard:** **Save** (prawy górny róg). Potem otwierasz go z **Dashboards** → wybrana nazwa.

**Przykład paneli na jeden dashboard:**
- Panel 1 (Single Value): `index=main event.type="device_scan" | stats count as "Liczba skanów"`
- Panel 2 (Table): `index=main event.type="device_scan" | table device.name, device.ip_address, device.security_score, device.protocol`
- Panel 3 (Pie): `index=main | stats count by device.protocol`
- Panel 4 (Table): `index=main (event.severity="High" OR event.severity="Critical") | table device.name, device.security_score, device.vulnerabilities`

### Więcej zapytań do paneli (skopiuj Search + wybierz typ wizualizacji)

| Typ panelu | Tytuł panelu | Search (wklej w panelu) |
|------------|--------------|-------------------------|
| **Single Value** | Liczba urządzeń (unikalnych) | `index=main event.type="device_scan" \| stats dc(device.name) as urzadzenia` |
| **Single Value** | Urządzenia wysokiego ryzyka | `index=main (event.severity="High" OR event.severity="Critical") \| stats count` |
| **Single Value** | Średni security score | `index=main event.type="device_scan" \| stats avg(device.security_score) as avg_score` |
| **Statistics Table** | Urządzenia z podatnościami | `index=main device.vulnerability_count>0 \| table device.name, device.ip_address, device.security_score, device.vulnerabilities \| sort - device.security_score` |
| **Statistics Table** | Ostatnie skany (nazwa, IP, czas) | `index=main event.type="device_scan" \| table _time, device.name, device.ip_address, device.protocol \| sort - _time \| head 50` |
| **Statistics Table** | Urządzenia po protokole (z score) | `index=main \| stats count as liczba, avg(device.security_score) as sredni_score by device.protocol \| sort - liczba` |
| **Pie Chart** | Rozkład ryzyka (Low/Medium/High/Critical) | `index=main \| stats count by event.severity` |
| **Column Chart** lub **Bar Chart** | Liczba urządzeń według protokołu | `index=main \| stats count by device.protocol` |
| **Column Chart** | Średni security score per urządzenie (top 10) | `index=main \| stats avg(device.security_score) as score by device.name \| sort - score \| head 10` |
| **Statistics Table** | Tylko WiFi – lista i score | `index=main device.protocol="WiFi" \| table device.name, device.ip_address, device.security_score \| dedup device.name \| sort - device.security_score` |
| **Statistics Table** | Tylko BLE – lista i score | `index=main device.protocol="BLE" \| table device.name, device.mac_address, device.security_score \| dedup device.name \| sort - device.security_score` |
| **Single Value** | Urządzenia ze score &lt; 50 | `index=main device.security_score<50 \| stats count` |
| **Events** | Surowe zdarzenia (do debugu) | `index=main event.type="device_scan" \| head 100` |

---

## 📋 Komendy SPL do przeglądania danych (ściąga)

Dane ze skanera trafiają do `index=main`. Pola: `device.*`, `event.*`, `scan.*`. Poniżej gotowe zapytania – wklej je w **Search** (pasek u góry) albo w panelu dashboardu.

### Podstawowe (przegląd)

| Opis | Komenda |
|------|--------|
| Wszystkie zdarzenia skanów | `index=main event.type="device_scan"` |
| Wszystkie urządzenia (lista) | `index=main device.name=*` |
| Tabela: nazwa, IP, score, protokół | `index=main | table device.name, device.ip_address, device.security_score, device.protocol` |
| Ostatnie 24 h (domyślnie czas) | `index=main event.type="device_scan" \| head 1000` |

### Statystyki i agregacje

| Opis | Komenda |
|------|--------|
| Liczba zdarzeń (skanów) | `index=main event.type="device_scan" \| stats count` |
| Liczba urządzeń po protokole | `index=main \| stats count by device.protocol` |
| Średni security score po urządzeniu | `index=main \| stats avg(device.security_score) as avg_score by device.name` |
| Liczba urządzeń po severity | `index=main \| stats count by event.severity` |

### Ryzyko i podatności

| Opis | Komenda |
|------|--------|
| Urządzenia wysokiego/krytycznego ryzyka | `index=main (event.severity="High" OR event.severity="Critical")` |
| Tabela: nazwa, score, podatności | `index=main \| table device.name, device.security_score, device.vulnerabilities` |
| Urządzenia z niskim score (&lt; 50) | `index=main device.security_score&lt;50` |
| Urządzenia z podatnościami | `index=main device.vulnerability_count&gt;0 \| table device.name, device.security_score, device.vulnerabilities` |

### Filtrowanie i wyszukiwanie

| Opis | Komenda |
|------|--------|
| Po nazwie urządzenia | `index=main device.name="*nazwa*"` |
| Po adresie IP | `index=main device.ip_address="192.168.1.10"` |
| Tylko WiFi | `index=main device.protocol="WiFi"` |
| Tylko BLE | `index=main device.protocol="BLE"` |

### Przydatne pipe’y (na końcu zapytania)

| Efekt | Dopisek do zapytania |
|-------|----------------------|
| Tabela wybranych pól | `\| table pole1, pole2, pole3` |
| Sortowanie | `\| sort - device.security_score` |
| Pierwsze N wierszy | `\| head 100` |
| Usuń duplikaty po nazwie | `\| dedup device.name` |
| Liczba wg pola | `\| stats count by device.protocol` |

**Przykład złożony:** urządzenia wysokiego ryzyka, tabela, posortowane po score:
```
index=main (event.severity="High" OR event.severity="Critical") | table device.name, device.ip_address, device.security_score, device.protocol, device.vulnerabilities | sort - device.security_score
```

---

## ⚙️ Konfiguracja (Opcjonalne)

### Automatyczny import z katalogu (wiele plików / cały folder)

To ta sama idea co **Metoda 3** powyżej: zamiast wgrywać pliki po jednym przez Upload, wskaż Splunkowi **katalog** – wtedy indeksuje wszystkie pasujące pliki i może brać też nowe:

1. **Settings** → **Data inputs** → **Files & Directories** → **New**
2. **File or Directory path:** np. `/home/twoja_nazwa/splunk_import` lub `.../medical-device-scanner-main/exports`
3. **File pattern:** `siem_export_*.jsonl`
4. **Source type:** `_json`
5. **Save**

Splunk zaimportuje istniejące pliki w folderze i (zależnie od konfiguracji) będzie mógł brać nowe.

---

## 💡 Wskazówki

1. **Limit 500MB/dzień** - wystarczy dla skanowania urządzeń
2. **Dashboard jest gotowy** - nie musisz nic konfigurować
3. **JSON Lines działa** - Splunk automatycznie parsuje JSON
4. **Bardzo szybki** - działa od razu po instalacji

---

## 💡 Dlaczego Splunk?

**Splunk Free jest idealny dla:**
- ✅ **Najprostsze** rozwiązanie SIEM
- ✅ Nie chcesz instalować OpenSearch/Elasticsearch
- ✅ Chcesz **gotowy dashboard** od razu
- ✅ 500MB/dzień Ci wystarczy (wystarczy dla skanowania urządzeń)

---

## 🚀 Szybki Start (3 kroki)

```bash
# 1. Zainstaluj Splunk (patrz wyżej)

# 2. Uruchom skaner
python3 src/scanner.py

# 3. Otwórz Splunk i zaimportuj plik siem_export_*.jsonl
# http://localhost:8000 → Settings → Add Data → Upload
```

**Gotowe!** 🎉

---

## 🔗 Linki

- **Pobierz Splunk:** https://www.splunk.com/en_us/download/splunk-enterprise.html
- **Dokumentacja:** https://docs.splunk.com/
- **Splunk Free:** https://www.splunk.com/en_us/products/splunk-enterprise/free.html

---

## ❓ Problemy?

### Błąd: "cannot create /opt/splunk/var/log/..." (Uprawnienia)

**Rozwiązanie:**
```bash
# Użyj automatycznego skryptu:
./napraw_splunk.sh

# Lub ręcznie:
sudo chown -R root:root /opt/splunk
sudo chmod -R 755 /opt/splunk
sudo mkdir -p /opt/splunk/var/log/{splunk,introspection,watchdog,client_events}
sudo mkdir -p /opt/splunk/etc/licenses/download-trial
```

### Splunk nie startuje:
```bash
# Sprawdź status (jako użytkownik splunk)
sudo -u splunk /opt/splunk/bin/splunk status

# Uruchom ponownie
sudo -u splunk /opt/splunk/bin/splunk start
```

### Ostrzeżenie: "Running Splunk Enterprise as root is deprecated"

**Rozwiązanie:** Uruchom jako użytkownik `splunk`:
```bash
# Zamiast: sudo /opt/splunk/bin/splunk start
# Użyj:
sudo -u splunk /opt/splunk/bin/splunk start --accept-license --answer-yes --no-prompt

# LUB jeśli musisz użyć root (niezalecane):
sudo /opt/splunk/bin/splunk start --accept-license --answer-yes --no-prompt --run-as-root
```

### Port 8000 zajęty:
```bash
# Zmień port w /opt/splunk/etc/system/local/web.conf
# server.socketPort = 8001
```

### Nie pamiętam hasła:
```bash
sudo -u splunk /opt/splunk/bin/splunk edit user admin -password NOWE_HASLO -auth admin:changeme
```
