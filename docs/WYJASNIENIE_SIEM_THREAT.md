# 📚 Wyjaśnienie: SIEM i Threat Intelligence

## 🔍 Threat Intelligence - Co to jest?

**Threat Intelligence** = Sprawdzanie czy adresy IP urządzeń są znane jako **podejrzane/zagrożone**.

### Jak to działa?

Skaner automatycznie sprawdza adresy IP wykrytych urządzeń w bazach danych zagrożeń:
- **AbuseIPDB** - baza znanych złośliwych IP (spam, ataki, malware)
- **VirusTotal** - jeśli masz klucz API (sprawdzanie reputacji IP)
- **Shodan** - jeśli masz klucz API (informacje o urządzeniach w internecie)

### Przykład:

Jeśli skaner znajdzie urządzenie z IP `192.168.1.100`, sprawdzi:
- Czy to IP było używane do ataków?
- Czy jest na czarnej liście?
- Czy ma złą reputację?

**Wynik:** Plik `threat_intel_YYYYMMDD_HHMMSS.json` z informacjami o podejrzanych IP.

### Czy to potrzebne?

- ✅ **TAK** - jeśli chcesz wiedzieć czy urządzenia w sieci są bezpieczne
- ❌ **NIE** - jeśli skanujesz tylko lokalną sieć (192.168.x.x) - te IP są prywatne i nie będą w bazach

**Uwaga:** Threat Intelligence działa **automatycznie w tle** - nie spowalnia skanowania!

---

## 📤 SIEM - Co to jest?

**SIEM** = Security Information and Event Management = Systemy do monitorowania bezpieczeństwa.

### Popularne systemy SIEM:

1. **Splunk** - komercyjny, bardzo popularny
2. **ELK Stack** (Elasticsearch, Logstash, Kibana) - darmowy, open-source
3. **QRadar** - IBM
4. **ArcSight** - HP
5. **Splunk Free** - darmowy, limit 500MB/dzień

### Co robi eksport SIEM?

Skaner automatycznie tworzy plik `siem_export_YYYYMMDD_HHMMSS.jsonl` z danymi o urządzeniach w formacie, który systemy SIEM mogą zaimportować.

### Jak używać?

#### Opcja 1: Bez systemu SIEM (tylko do przechowania)
```bash
python3 src/scanner.py
# Tworzy plik siem_export_*.jsonl - możesz go przechować na później
```

#### Opcja 2: Z systemem SIEM (import do systemu)

**Dla ELK Stack:**
```bash
# 1. Uruchom skaner
python3 src/scanner.py

# 2. Zaimportuj plik do Elasticsearch
curl -X POST "localhost:9200/_bulk" -H 'Content-Type: application/json' --data-binary @siem_export_*.jsonl
```

**Dla Splunk:**
```bash
# 1. Uruchom skaner
python3 src/scanner.py

# 2. W Splunk: Settings → Data Inputs → Files & Directories
#    Dodaj katalog z plikami siem_export_*.jsonl
```

**Dla Splunk:**
```bash
# 1. Uruchom skaner
python3 src/scanner.py

# 2. Zaimportuj przez Splunk Web UI:
#    Settings → Add Data → Upload → Wybierz plik → Submit
#    Lub użyj: ./import_to_splunk.sh
```

### Czy to potrzebne?

- ✅ **TAK** - jeśli masz system SIEM w firmie/szpitalu
- ❌ **NIE** - jeśli skanujesz tylko dla siebie (możesz wyłączyć: `--no-siem`)

**Uwaga:** Eksport SIEM działa **automatycznie** - nie musisz nic robić! Plik jest gotowy do importu.

---

## 🔑 Klucze API - Skąd wziąć?

### 1. AbuseIPDB (Threat Intelligence) - **DARMOWE**

**Krok 1:** Zarejestruj się
- Wejdź na: https://www.abuseipdb.com/ (strona główna)
- Kliknij "Sign Up" w prawym górnym rogu (darmowe konto)
- **Alternatywnie:** https://www.abuseipdb.com/register (bezpośredni link do rejestracji)

**Krok 2:** Zdobądź klucz API
- Po zalogowaniu: Settings → API Key
- **Lub bezpośrednio:** https://www.abuseipdb.com/account/api (wymaga zalogowania)
- Skopiuj klucz

**Krok 3:** Dodaj do `.env`
```bash
# Otwórz plik .env w głównym katalogu projektu
nano .env

# Dodaj linię:
ABUSEIPDB_API_KEY=twoj_klucz_tutaj
```

**Limity darmowe:**
- 1000 requestów/dzień
- Wystarczy dla normalnego użytku

**Uwaga:** Jeśli strona `/pricing` nie działa (błąd 500), użyj strony głównej lub bezpośredniego linku do rejestracji.

### 2. VirusTotal (opcjonalne, już masz w .env.example)

**Krok 1:** Zarejestruj się
- Wejdź na: https://www.virustotal.com/gui/join-us
- Kliknij "Sign Up" (darmowe konto)

**Krok 2:** Zdobądź klucz API
- Po zalogowaniu: Settings → API Key
- Skopiuj klucz

**Krok 3:** Dodaj do `.env`
```bash
VIRUSTOTAL_API_KEY=twoj_klucz_tutaj
```

**Limity darmowe:**
- 4 requesty/minutę
- Wystarczy dla podstawowego użytku

### 3. Shodan (opcjonalne, już masz w .env.example)

**Krok 1:** Zarejestruj się
- Wejdź na: https://account.shodan.io/register
- Kliknij "Sign Up" (darmowe konto)

**Krok 2:** Zdobądź klucz API
- Po zalogowaniu: Account → API Key
- Skopiuj klucz

**Krok 3:** Dodaj do `.env`
```bash
SHODAN_API_KEY=twoj_klucz_tutaj
```

**Limity darmowe:**
- 1 request/sekundę
- Wystarczy dla podstawowego użytku

---

## 💡 Praktyczne Użycie

### Scenariusz 1: Skanowanie dla siebie (bez SIEM)

```bash
# Wyłącz SIEM (nie potrzebujesz)
python3 src/scanner.py --no-siem

# Threat Intelligence może być przydatne (sprawdza czy IP są podejrzane)
python3 src/scanner.py --no-siem
```

### Scenariusz 2: Skanowanie w firmie (z SIEM)

```bash
# Wszystko automatycznie
python3 src/scanner.py

# Pliki gotowe do importu:
# - siem_export_*.jsonl → zaimportuj do swojego SIEM
# - threat_intel_*.json → sprawdź podejrzane IP
```

### Scenariusz 3: Bez kluczy API

```bash
# Threat Intelligence nie zadziała (brak kluczy API)
# Ale reszta działa normalnie
python3 src/scanner.py --no-threat-intel
```

---

## ❓ Najczęstsze Pytania

### Q: Czy muszę mieć klucze API?
**A:** Nie! Threat Intelligence jest opcjonalne. Skaner działa bez kluczy API.

### Q: Czy muszę mieć system SIEM?
**A:** Nie! Eksport SIEM tworzy plik, który możesz:
- Przechować na później
- Zaimportować do SIEM w przyszłości
- Wyłączyć flagą `--no-siem`

### Q: Czy Threat Intelligence spowalnia skanowanie?
**A:** Nie! Działa **w tle** (asynchronicznie) - nie blokuje głównego skanowania.

### Q: Co jeśli nie mam kluczy API?
**A:** Nie ma problemu! Skaner działa normalnie, tylko Threat Intelligence nie sprawdzi IP w bazach (ale reszta funkcji działa).

### Q: Czy mogę wyłączyć wszystko?
**A:** Tak!
```bash
python3 src/scanner.py --no-siem --no-threat-intel
```

---

## 🎯 Podsumowanie

| Funkcja | Co robi | Czy potrzebne? | Klucz API? |
|---------|---------|----------------|------------|
| **Threat Intelligence** | Sprawdza IP w bazach zagrożeń | Opcjonalne | Tak (AbuseIPDB) |
| **Eksport SIEM** | Tworzy plik do importu do SIEM | Opcjonalne | Nie |

**Rekomendacja:**
- Jeśli skanujesz dla siebie → możesz wyłączyć obie funkcje (`--no-siem --no-threat-intel`)
- Jeśli skanujesz w firmie → zostaw włączone (przydatne)

**Wszystko działa automatycznie - nie musisz nic konfigurować!** 🚀
