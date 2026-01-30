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

### Metoda 1: Automatyczny Import (CEF Format)

Skaner automatycznie tworzy plik `siem_export_*.jsonl`. Splunk może importować JSON Lines bezpośrednio!

```bash
# 1. Uruchom skaner
python3 src/scanner.py

# 2. Zaimportuj do Splunk (przez web UI)
```

**W Splunk Web UI:**
1. Otwórz: http://localhost:8000
2. Kliknij: **Settings** → **Add Data**
3. Wybierz: **Upload** → **Select File**
4. Wybierz plik: `siem_export_*.jsonl`
5. Kliknij: **Next** → **Review** → **Submit**

### Metoda 2: Przez API (Automatycznie)

```bash
# Użyj skryptu do automatycznego importu
./import_to_splunk.sh
```

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

## ⚙️ Konfiguracja (Opcjonalne)

### Automatyczny Import z Katalogu

Jeśli chcesz, aby Splunk automatycznie importował pliki:

1. **Settings** → **Data inputs** → **Files & Directories**
2. Kliknij: **New**
3. **File or Directory path:** `/home/h9g120og/Downloads/medical-device-scanner-main/`
4. **File pattern:** `siem_export_*.jsonl`
5. **Source type:** `_json`
6. Kliknij: **Save**

Teraz Splunk automatycznie zaimportuje nowe pliki!

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
