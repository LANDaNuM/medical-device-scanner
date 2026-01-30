# 🔑 Jak Dodać Klucze API do Pliku .env

## 📍 Lokalizacja Pliku

Plik `.env` znajduje się w **głównym katalogu projektu**:
```
medical-device-scanner/
├── .env          ← TUTAJ!
├── .env.example  ← Przykładowy plik (możesz skopiować)
├── src/
└── ...
```

---

## 🚀 Szybki Start

### Metoda 1: Edytuj Istniejący Plik .env

1. **Otwórz plik `.env` w edytorze:**
   ```bash
   nano .env
   # lub
   gedit .env
   # lub użyj edytora w Cursor/VSCode
   ```

2. **Znajdź linię z kluczem API** (np. `VIRUSTOTAL_API_KEY=`)

3. **Wklej swój klucz po znaku `=`** (bez spacji!):
   ```bash
   VIRUSTOTAL_API_KEY=a937aaf2fe142dc6ac66eb8fa6f2e19227d5770409e4f56417f52f3b68bb593f
   ```

4. **Zapisz plik** (Ctrl+O, Enter, Ctrl+X w nano)

---

### Metoda 2: Skopiuj z .env.example

```bash
# Jeśli nie masz pliku .env, skopiuj przykładowy:
cp .env.example .env

# Potem edytuj .env i wklej klucze
nano .env
```

---

## 📝 Przykłady dla Każdego Klucza

### 1. VirusTotal API Key

**Format w pliku .env:**
```bash
VIRUSTOTAL_API_KEY=twoj_klucz_tutaj
```

**Przykład:**
```bash
VIRUSTOTAL_API_KEY=a937aaf2fe142dc6ac66eb8fa6f2e19227d5770409e4f56417f52f3b68bb593f
```

**Jak uzyskać:**
1. Idź na: https://www.virustotal.com/gui/join-us
2. Zarejestruj się (darmowe)
3. Zaloguj się
4. Przejdź do: https://www.virustotal.com/gui/user/[twoja-nazwa]/apikey
5. Skopiuj klucz

---

### 2. Shodan API Key

**Format:**
```bash
SHODAN_API_KEY=twoj_klucz_tutaj
```

**Przykład:**
```bash
SHODAN_API_KEY=v3XsbphQ7kzRrcTxZbl3lHAXC3rPEfEh
```

**Jak uzyskać:**
1. Idź na: https://account.shodan.io/register
2. Zarejestruj się
3. Po zalogowaniu: https://account.shodan.io/
4. Skopiuj klucz z sekcji "API Key"

---

### 3. NVD API Key

**Format:**
```bash
NVD_API_KEY=twoj_klucz_tutaj
```

**Przykład:**
```bash
NVD_API_KEY=098821df-ce90-4281-af50-857b1e73fe6f
```

**Jak uzyskać:**
1. Idź na: https://nvd.nist.gov/developers/request-an-api-key
2. Wypełnij formularz (darmowe)
3. Sprawdź email i kliknij link aktywacyjny
4. Skopiuj klucz

---

### 4. Vulners API Key

**Format:**
```bash
VULNERS_API_KEY=twoj_klucz_tutaj
```

**Przykład:**
```bash
VULNERS_API_KEY=RLN5GH2OH87PUIIXE7AOXFOPB4AIYF7U4X7ZO78Q8LQSJ3RB1QUNEPT0HQ68J272
```

**Jak uzyskać:**
1. Idź na: https://vulners.com/register
2. Zarejestruj się
3. Przejdź do ustawień konta
4. Skopiuj klucz API

---

### 5. AbuseIPDB API Key

**Format:**
```bash
ABUSEIPDB_API_KEY=twoj_klucz_tutaj
```

**Jak uzyskać:**
1. Idź na: https://www.abuseipdb.com/register
2. Zarejestruj się
3. Po zalogowaniu: Settings → API Key
4. Skopiuj klucz

---

## ⚠️ WAŻNE Zasady

### ✅ DOBRZE:
```bash
VIRUSTOTAL_API_KEY=abc123def456ghi789
SHODAN_API_KEY=xyz789abc123
NVD_API_KEY=12345678-1234-1234-1234-123456789012
```

### ❌ ŹLE:
```bash
# ❌ Z cudzysłowami
VIRUSTOTAL_API_KEY="abc123def456"

# ❌ Ze spacjami wokół =
VIRUSTOTAL_API_KEY = abc123def456

# ❌ Z komentarzem w tej samej linii (może nie działać)
VIRUSTOTAL_API_KEY=abc123def456  # mój klucz

# ❌ Z polskimi znakami w kluczu (jeśli są)
VIRUSTOTAL_API_KEY=abc123def456ąęć
```

---

## 🔍 Sprawdzenie Czy Klucze Działają

Uruchom skrypt weryfikacyjny:

```bash
python3 check_api_keys.py
```

**Wyświetli:**
- ✅ Które klucze są skonfigurowane
- ✅ Które działają (test połączenia)
- ⚠️ Które są nieprawidłowe

---

## 📋 Pełny Przykład Pliku .env

```bash
# VirusTotal API Key
VIRUSTOTAL_API_KEY=a937aaf2fe142dc6ac66eb8fa6f2e19227d5770409e4f56417f52f3b68bb593f

# Shodan API Key (opcjonalne)
SHODAN_API_KEY=v3XsbphQ7kzRrcTxZbl3lHAXC3rPEfEh

# NVD API Key (opcjonalne)
NVD_API_KEY=098821df-ce90-4281-af50-857b1e73fe6f

# Vulners API Key (opcjonalne)
VULNERS_API_KEY=RLN5GH2OH87PUIIXE7AOXFOPB4AIYF7U4X7ZO78Q8LQSJ3RB1QUNEPT0HQ68J272

# AbuseIPDB API Key (opcjonalne)
ABUSEIPDB_API_KEY=twoj_klucz_abuseipdb_tutaj
```

---

## 🛠️ Edycja w Terminalu (nano)

```bash
# Otwórz plik
nano .env

# Nawigacja:
# - Strzałki: poruszanie się
# - Ctrl+W: wyszukiwanie
# - Ctrl+O: zapisz (potem Enter)
# - Ctrl+X: wyjście

# Przykład edycji:
# 1. Znajdź linię: VIRUSTOTAL_API_KEY=
# 2. Przesuń kursor na koniec linii (po =)
# 3. Wklej klucz (Ctrl+Shift+V)
# 4. Zapisz (Ctrl+O, Enter)
# 5. Wyjdź (Ctrl+X)
```

---

## 🛠️ Edycja w Cursor/VSCode

1. **Otwórz plik `.env`** w edytorze
2. **Znajdź linię** z kluczem (np. `VIRUSTOTAL_API_KEY=`)
3. **Wklej klucz** po znaku `=`
4. **Zapisz** (Ctrl+S)

---

## ✅ Gotowe!

Po dodaniu kluczy, uruchom ponownie skaner:

```bash
python3 src/scanner.py
```

Skaner automatycznie użyje kluczy API do wzbogacenia danych.

---

## 🔒 Bezpieczeństwo

- ✅ Plik `.env` jest w `.gitignore` - **nie zostanie przesłany do GitHub**
- ✅ Nigdy nie udostępniaj kluczy publicznie
- ✅ Jeśli klucz wycieknie → wygeneruj nowy natychmiast

---

## ❓ Problem: Klucze Nie Działają?

1. **Sprawdź czy plik `.env` jest w głównym katalogu projektu**
2. **Sprawdź czy nie ma błędów składniowych** (spacje, cudzysłowy)
3. **Uruchom `python3 check_api_keys.py`** aby zdiagnozować
4. **Sprawdź czy klucze nie wygasły** (zaloguj się na stronie serwisu)

---

**Potrzebujesz pomocy z konkretnym kluczem? Sprawdź `KONFIGURACJA_API.md`**
