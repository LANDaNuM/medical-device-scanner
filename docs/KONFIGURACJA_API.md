# 🔑 Konfiguracja Kluczy API

Ten przewodnik pomoże Ci skonfigurować klucze API dla zewnętrznych serwisów używanych przez skaner.

## 📋 Wymagane Klucze API

### 1. VirusTotal API (Zalecane)

**Dlaczego:** Sprawdza reputację adresów IP i wykrywa potencjalne zagrożenia.

**Jak uzyskać:**
1. Przejdź na: https://www.virustotal.com/gui/join-us
2. Zarejestruj się (darmowe konto)
3. Po zalogowaniu, przejdź do: https://www.virustotal.com/gui/user/[twoja-nazwa]/apikey
4. Skopiuj swój klucz API

**Limity (darmowe konto):**
- 4 zapytania na minutę
- 500 zapytań dziennie

---

### 2. Shodan API (Opcjonalne)

**Dlaczego:** Wzbogaca informacje o urządzeniach znalezionych w internecie.

**Jak uzyskać:**
1. Przejdź na: https://account.shodan.io/register
2. Zarejestruj się (darmowe konto)
3. Po zalogowaniu, przejdź do: https://account.shodan.io/
4. Skopiuj swój klucz API z sekcji "API Key"

**Limity (darmowe konto):**
- 1 zapytanie na sekundę
- 100 wyników miesięcznie

---

### 3. NVD API Key (Opcjonalne)

**Dlaczego:** Zwiększa limity dla wyszukiwania podatności CVE (z 5 do 50 zapytań/30s).

**Jak uzyskać:**
1. Przejdź na: https://nvd.nist.gov/developers/request-an-api-key
2. Wypełnij formularz (darmowe)
3. Sprawdź email i kliknij link aktywacyjny
4. Skopiuj swój klucz API

**Limity:**
- Bez klucza: 5 zapytań/30s
- Z kluczem: 50 zapytań/30s

---

### 4. Vulners API Key (Opcjonalne)

**Dlaczego:** Alternatywne źródło informacji o podatnościach (wyższe limity).

**Jak uzyskać:**
1. Przejdź na: https://vulners.com/register
2. Zarejestruj się (darmowe konto)
3. Przejdź do ustawień konta
4. Skopiuj swój klucz API

---

## 🚀 Konfiguracja

### Krok 1: Utwórz plik .env

```bash
# Skopiuj przykładowy plik
cp .env.example .env
```

### Krok 2: Edytuj plik .env

Otwórz plik `.env` w edytorze tekstu i wklej swoje klucze:

```bash
# VirusTotal API Key
VIRUSTOTAL_API_KEY=twoj_klucz_virustotal_tutaj

# Shodan API Key (opcjonalne)
SHODAN_API_KEY=twoj_klucz_shodan_tutaj

# NVD API Key (opcjonalne)
NVD_API_KEY=twoj_klucz_nvd_tutaj

# Vulners API Key (opcjonalne)
VULNERS_API_KEY=twoj_klucz_vulners_tutaj
```

**WAŻNE:**
- Nie dodawaj cudzysłowów wokół kluczy
- Nie dodawaj spacji przed lub po znaku `=`
- Każdy klucz w osobnej linii

### Krok 3: Zweryfikuj klucze

Uruchom skrypt weryfikacyjny:

```bash
python3 check_api_keys.py
```

Skrypt sprawdzi:
- ✅ Czy klucze są poprawnie skonfigurowane
- ✅ Czy klucze działają (test połączenia)
- ✅ Czy klucze są ważne

---

## ⚠️ Rozwiązywanie Problemów

### Problem: "Nieprawidłowy klucz API"

**Rozwiązanie:**
1. Sprawdź czy klucz jest poprawnie skopiowany (bez spacji na początku/końcu)
2. Sprawdź czy klucz nie wygasł (zaloguj się na stronie serwisu)
3. Wygeneruj nowy klucz API jeśli stary nie działa

### Problem: "Brak uprawnień" (403 Forbidden)

**Rozwiązanie:**
1. Sprawdź czy konto jest aktywne
2. Sprawdź czy nie przekroczyłeś limitów (darmowe konta mają limity)
3. Poczekaj do resetu limitów (zwykle o północy UTC)

### Problem: "Rate limit exceeded" (429)

**Rozwiązanie:**
1. To normalne - skaner automatycznie czeka
2. Jeśli często się pojawia, rozważ:
   - Użycie wyższego planu (płatnego)
   - Zmniejszenie częstotliwości skanowania
   - Użycie cache (skaner automatycznie cache'uje wyniki)

### Problem: Klucze nie są ładowane

**Rozwiązanie:**
1. Sprawdź czy plik `.env` jest w katalogu głównym projektu
2. Sprawdź czy nie ma błędów składniowych w `.env` (każda linia: `KLUCZ=wartość`)
3. Uruchom `python3 check_api_keys.py` aby zdiagnozować problem

---

## 🔒 Bezpieczeństwo

**WAŻNE:**
- ✅ Plik `.env` jest już w `.gitignore` - nie zostanie przesłany do repozytorium
- ✅ Nigdy nie udostępniaj swoich kluczy API publicznie
- ✅ Jeśli klucz zostanie ujawniony, wygeneruj nowy natychmiast
- ✅ Regularnie sprawdzaj użycie kluczy na stronach serwisów

---

## 📝 Przykładowa Konfiguracja

Minimalna konfiguracja (tylko VirusTotal):

```bash
VIRUSTOTAL_API_KEY=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

Pełna konfiguracja (wszystkie serwisy):

```bash
VIRUSTOTAL_API_KEY=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
SHODAN_API_KEY=xyz789abc123def456ghi789jkl012mno345pqr678stu901vwx
NVD_API_KEY=12345678-1234-1234-1234-123456789012
VULNERS_API_KEY=abcdef1234567890abcdef1234567890abcdef12
```

---

## ✅ Gotowe!

Po skonfigurowaniu kluczy API, uruchom ponownie skaner:

```bash
python3 src/scanner.py
```

Skaner automatycznie użyje kluczy API do wzbogacenia danych o urządzeniach.
