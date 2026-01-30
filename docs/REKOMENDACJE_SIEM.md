# 🛡️ Rekomendacje Systemów SIEM

## 🏆 Top 3 Rekomendacje (Darmowe/Open-Source)

### 1. **Splunk Free** ⭐⭐⭐⭐⭐ (NAJŁATWIEJSZY - ZALECANE!)

**Dlaczego Splunk?**
- ✅ **NAJPROSTSZY w instalacji** - jeden plik .deb/.rpm
- ✅ **Nie wymaga OpenSearch/Elasticsearch**
- ✅ **Gotowy dashboard** - działa od razu, bez konfiguracji
- ✅ **Bardzo dobry interfejs** - profesjonalny, łatwy w użyciu
- ✅ **Darmowy limit:** 500MB/dzień (wystarczy dla skanowania)

**Instalacja (Ubuntu/Debian):**

**Krok 1: Pobierz Splunk Free**
1. Otwórz: https://www.splunk.com/en_us/download/splunk-enterprise.html
2. Kliknij "Free Download" i utwórz darmowe konto
3. Wybierz: **Platform: Linux**, **Architecture: 64-bit**, **Package: Debian Package (.deb)**
4. Pobierz plik `.deb`

**Krok 2: Zainstaluj**
```bash
# Zainstaluj pobrany plik
cd ~/Downloads  # lub gdzie pobrałeś plik
sudo dpkg -i splunk*.deb
sudo apt-get install -f  # Napraw zależności jeśli potrzeba
```

**Krok 3: Uruchom Splunk**
```bash
# Najpierw napraw uprawnienia (jeśli potrzeba):
# ./napraw_splunk.sh

# Pierwsze uruchomienie (jako użytkownik splunk - ZALECANE)
sudo -u splunk /opt/splunk/bin/splunk start --accept-license --answer-yes --no-prompt

# Ustaw hasło admina
sudo -u splunk /opt/splunk/bin/splunk edit user admin -password TWOJE_HASLO -auth admin:changeme

# Uruchom przy starcie systemu
sudo -u splunk /opt/splunk/bin/splunk enable boot-start -user splunk

# Otwórz w przeglądarce
# http://localhost:8000
# Login: admin / Hasło: (to które ustawiłeś)
```

**Import danych ze skanera:**
```bash
# Skaner automatycznie tworzy plik siem_export_*.jsonl
# Zaimportuj przez Splunk Web UI:
# Settings → Add Data → Upload → Wybierz plik → Submit

# Lub użyj skryptu:
./import_to_splunk.sh
```

**Dokumentacja:** Zobacz `SPLUNK_INSTRUKCJA.md` (szczegółowa instrukcja)

---

### 2. **ELK Stack** (Elasticsearch + Logstash + Kibana) ⭐⭐⭐⭐

**Dlaczego ELK?**
- ✅ **Bardzo popularny** - używany przez wiele firm
- ✅ **Darmowy** (open-source wersja)
- ✅ **Bardzo elastyczny** - możesz wszystko dostosować
- ✅ **Duża społeczność** - dużo tutoriali i pomocy

**Wady:**
- ⚠️ Wymaga więcej konfiguracji
- ⚠️ Większe wymagania sprzętowe

**Instalacja (Docker - najłatwiejsze):**
```bash
# 1. Zainstaluj Docker
sudo apt install docker.io docker-compose

# 2. Pobierz docker-compose dla ELK
git clone https://github.com/deviantony/docker-elk.git
cd docker-elk

# 3. Uruchom
docker-compose up -d

# 4. Otwórz w przeglądarce
# http://localhost:5601
# Login: elastic / changeme
```

**Import danych ze skanera:**
```bash
# 1. Uruchom skaner
python3 src/scanner.py

# 2. Zaimportuj do Elasticsearch
curl -X POST "localhost:9200/_bulk" \
  -H 'Content-Type: application/json' \
  --data-binary @siem_export_*.jsonl
```

**Dokumentacja:** https://www.elastic.co/guide/

---

### 3. **Security Onion** ⭐⭐⭐

**Dlaczego Security Onion?**
- ✅ **Kompleksowy** - zawiera wiele narzędzi (Suricata, Zeek, etc.)
- ✅ **Gotowy do użycia** - wszystko w jednym
- ✅ **Darmowy**

**Wady:**
- ⚠️ Wymaga dedykowanego serwera (nie działa jako aplikacja)
- ⚠️ Bardziej zaawansowany

**Instalacja:**
- Pobierz ISO: https://securityonion.net/
- Zainstaluj na dedykowanym serwerze
- Wymaga minimum 16GB RAM

**Dokumentacja:** https://docs.securityonion.net/

---

## 🎯 Moja Rekomendacja: **Splunk Free**

### Dlaczego Splunk Free?

1. **NAJŁATWIEJSZY setup** - jeden plik .deb/.rpm, działa od razu
2. **Gotowy dashboard** - nie musisz nic konfigurować
3. **Nie wymaga OpenSearch** - działa samodzielnie
4. **Profesjonalny interfejs** - bardzo łatwy w użyciu
5. **Darmowy limit 500MB/dzień** - wystarczy dla skanowania urządzeń

---

## 🚀 Szybki Start z Splunk (ZALECANE!)

### Krok 1: Instalacja (5 minut)

```bash
# 1. Pobierz Splunk z oficjalnej strony:
#    https://www.splunk.com/en_us/download/splunk-enterprise.html
#    (Wybierz: Linux, 64-bit, Debian Package)

# 2. Zainstaluj pobrany plik:
cd ~/Downloads  # lub gdzie pobrałeś plik
sudo dpkg -i splunk*.deb
sudo apt-get install -f

# Uruchom
sudo /opt/splunk/bin/splunk start --accept-license --answer-yes --no-prompt
sudo /opt/splunk/bin/splunk edit user admin -password TWOJE_HASLO -auth admin:changeme
sudo /opt/splunk/bin/splunk enable boot-start
```

### Krok 2: Otwórz Dashboard

```
http://localhost:8000
Login: admin
Hasło: (to które ustawiłeś)
```

### Krok 3: Uruchom Skaner

```bash
python3 src/scanner.py
```

### Krok 4: Zaimportuj Dane

**Przez Web UI:**
1. Otwórz: http://localhost:8000
2. Settings → Add Data → Upload
3. Wybierz: `siem_export_*.jsonl`
4. Next → Review → Submit

**Lub automatycznie:**
```bash
./import_to_splunk.sh
```

### Krok 5: Zobacz Wyniki

W polu wyszukiwania Splunk wpisz:
```
index=main device.name=*
```

**Gotowe!** 🎉

---


## 💡 Wskazówki

1. **Zacznij od Splunk Free** - najłatwiejszy w instalacji i użyciu
2. **Jeśli potrzebujesz więcej** - przejdź na ELK Stack
3. **Dla zaawansowanych** - Security Onion

**Splunk Free ma limit 500MB/dzień, ale to wystarczy dla skanowania urządzeń!** 🎉

---

## 🔗 Linki

- **Splunk Free:** https://www.splunk.com/en_us/download/splunk-enterprise.html
- **Splunk Instrukcja:** Zobacz `SPLUNK_INSTRUKCJA.md`
- **ELK Stack:** https://www.elastic.co/
- **Security Onion:** https://securityonion.net/
- **AbuseIPDB (Threat Intelligence):** https://www.abuseipdb.com/register (rejestracja)
