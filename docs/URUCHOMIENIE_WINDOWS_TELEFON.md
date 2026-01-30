# 📱 Uruchomienie Skanera na Windows i Telefonie

## 🪟 Windows

### Wymagania
- Windows 10/11
- Python 3.9+ 
- Administrator privileges (dla niektórych funkcji)

### Instalacja Krok po Kroku

#### KROK 1: Zainstaluj Python
1. Pobierz Python z [python.org](https://www.python.org/downloads/)
2. Podczas instalacji **zaznacz**: "Add Python to PATH**
3. Zainstaluj

#### KROK 2: Zainstaluj Git (opcjonalne, jeśli klonujesz z repo)
1. Pobierz Git z [git-scm.com](https://git-scm.com/download/win)
2. Zainstaluj

#### KROK 3: Zainstaluj nmap (dla WiFi scanner)
1. Pobierz nmap z [nmap.org](https://nmap.org/download.html)
2. Zainstaluj (domyślne ustawienia OK)
3. Dodaj nmap do PATH (zazwyczaj: `C:\Program Files (x86)\Nmap`)

#### KROK 4: Sklonuj/Pobierz Projekt
```powershell
# Jeśli masz Git:
git clone <repo-url>
cd medical-device-scanner

# Lub po prostu pobierz i rozpakuj ZIP
```

#### KROK 5: Utwórz Virtual Environment
```powershell
# Otwórz PowerShell lub CMD w katalogu projektu
python -m venv venv

# Aktywuj venv
venv\Scripts\activate
```

#### KROK 6: Zainstaluj Zależności
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

#### KROK 7: Uruchom Skaner
```powershell
python src\scanner.py
```

### ⚠️ Problemy na Windows

#### Problem: "bleak nie działa"
**Rozwiązanie:**
```powershell
# Windows wymaga dodatkowych bibliotek dla Bluetooth
pip install bleak[winrt]
```

#### Problem: "nmap nie znaleziony"
**Rozwiązanie:**
1. Sprawdź czy nmap jest zainstalowany: `nmap --version`
2. Jeśli nie działa, dodaj do PATH:
   - Windows Settings → System → Advanced → Environment Variables
   - Dodaj: `C:\Program Files (x86)\Nmap` do PATH

#### Problem: "Permission denied" (WiFi)
**Rozwiązanie:**
- Uruchom PowerShell jako Administrator
- Lub użyj tylko podstawowego skanowania (bez sudo)

#### Problem: USB Scanner nie działa
**Rozwiązanie:**
```powershell
# Zainstaluj libusb drivers
# Pobierz z: https://libusb.info/
# Lub użyj Zadig: https://zadig.akeo.ie/
```

---

## 📱 Telefon (Android/iOS)

### ⚠️ Ważne Uwagi

**Python nie działa natywnie na telefonach!** Ale są alternatywy:

### Opcja 1: Termux (Android) ✅ **NAJŁATWIEJSZE**

Termux to terminal Linux na Androidzie - działa świetnie!

#### Instalacja Termux
1. Pobierz Termux z [F-Droid](https://f-droid.org/packages/com.termux/) (NIE z Google Play - stara wersja!)
2. Zainstaluj

#### Instalacja w Termux
```bash
# Aktualizuj pakiety
pkg update && pkg upgrade

# Zainstaluj Python i narzędzia
pkg install python git

# Sklonuj projekt (lub przenieś pliki)
git clone <repo-url>
cd medical-device-scanner

# Utwórz venv
python -m venv venv
source venv/bin/activate

# Zainstaluj zależności
pip install --upgrade pip
pip install -r requirements.txt
```

#### Uruchomienie
```bash
python src/scanner.py --ble  # Tylko BLE (najlepiej działa na telefonie)
```

#### ⚠️ Ograniczenia na Androidzie:
- ✅ **BLE działa** - telefon ma Bluetooth
- ❌ **WiFi scanner** - wymaga root (nie działa bez root)
- ❌ **USB scanner** - nie działa (telefon nie ma dostępu do USB host)
- ❌ **NFC scanner** - może działać, ale wymaga specjalnych bibliotek

### Opcja 2: Pydroid 3 (Android) - Prostsze, ale ograniczone

1. Pobierz **Pydroid 3** z Google Play
2. Otwórz Pydroid
3. **Menu → Pip** → Zainstaluj pakiety:
   ```
   bleak
   pandas
   numpy
   scikit-learn
   streamlit
   plotly
   ```
4. Przenieś pliki projektu do Pydroid
5. Uruchom: `python src/scanner.py --ble`

**Ograniczenia:**
- ❌ WiFi scanner nie działa
- ❌ USB scanner nie działa
- ✅ BLE może działać (zależy od telefonu)

### Opcja 3: iOS (iPhone/iPad) - Bardzo Ograniczone

iOS **NIE obsługuje** natywnego Pythona. Możliwe opcje:

#### A) Pythonista (Płatne, ~$10)
1. Pobierz Pythonista z App Store
2. Przenieś pliki projektu
3. Uruchom (ale wiele bibliotek nie działa)

#### B) SSH do komputera z Linux/Mac
- Uruchom skaner na komputerze
- Połącz się przez SSH z telefonu
- Użyj terminala SSH na telefonie

#### C) Web Interface (Najlepsze rozwiązanie!)
- Uruchom `api_server.py` na komputerze
- Otwórz w przeglądarce na telefonie
- Lub użyj Streamlit dashboard

### Opcja 4: Web Interface (Najlepsze dla telefonu!) ⭐

**Najlepsze rozwiązanie** - uruchom serwer na komputerze, użyj z telefonu:

#### Na Komputerze (Linux/Windows/Mac):
```bash
# Uruchom API Server
python src/api_server.py

# Lub Dashboard Streamlit
streamlit run src/dashboard.py
```

#### Na Telefonie:
1. Sprawdź IP komputera:
   ```bash
   # Linux/Mac:
   ip addr show | grep inet
   
   # Windows:
   ipconfig
   ```

2. Otwórz w przeglądarce telefonu:
   ```
   http://192.168.1.XXX:5000  # API Server
   # lub
   http://192.168.1.XXX:8501  # Streamlit Dashboard
   ```

**Zalety:**
- ✅ Działa na każdym telefonie (Android/iOS)
- ✅ Nie wymaga instalacji Pythona na telefonie
- ✅ Pełna funkcjonalność
- ✅ Ładny interfejs webowy

---

## 🌐 Uruchomienie przez Internet (Zdalne)

### Opcja 1: Render.com (Darmowe)

1. Utwórz konto na [render.com](https://render.com)
2. Połącz z GitHub repo
3. Render automatycznie uruchomi API Server
4. Dostęp z telefonu przez internet!

### Opcja 2: Ngrok (Tunel lokalny)

```bash
# Na komputerze:
# 1. Zainstaluj ngrok: https://ngrok.com/
# 2. Uruchom API Server:
python src/api_server.py

# 3. W innym terminalu:
ngrok http 5000

# 4. Skopiuj URL (np. https://abc123.ngrok.io)
# 5. Otwórz na telefonie!
```

---

## 📊 Porównanie Platform

| Platforma | BLE | WiFi | USB | NFC | Dashboard | Łatwość |
|-----------|-----|------|-----|-----|-----------|---------|
| **Linux** | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| **Windows** | ✅ | ✅ | ⚠️ | ❌ | ✅ | ⭐⭐⭐⭐ |
| **Mac** | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| **Android (Termux)** | ✅ | ❌* | ❌ | ⚠️ | ✅ | ⭐⭐⭐ |
| **iOS** | ❌ | ❌ | ❌ | ❌ | ✅** | ⭐⭐ |
| **Web (API)** | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |

\* Wymaga root  
\*\* Tylko przez przeglądarkę (serwer na komputerze)

---

## 🎯 Rekomendacje

### Dla Windows:
1. ✅ Zainstaluj Python, nmap, Git
2. ✅ Użyj PowerShell jako Administrator
3. ✅ Dla BLE: `pip install bleak[winrt]`

### Dla Telefonu (Android):
1. ✅ **Najlepsze:** Termux + BLE scanner
2. ✅ **Alternatywa:** Web interface (serwer na komputerze)

### Dla Telefonu (iOS):
1. ✅ **Tylko:** Web interface (serwer na komputerze)
2. ❌ Nie próbuj instalować Pythona na iOS (nie działa dobrze)

---

## 🚀 Szybki Start - Web Interface (Dla Telefonu)

### Na Komputerze:
```bash
# 1. Uruchom Streamlit Dashboard
streamlit run src/dashboard.py

# 2. Sprawdź IP:
# Linux/Mac:
hostname -I

# Windows:
ipconfig
# Szukaj "IPv4 Address"
```

### Na Telefonie:
1. Upewnij się, że telefon jest w tej samej sieci WiFi
2. Otwórz przeglądarkę
3. Wejdź na: `http://IP_KOMPUTERA:8501`
   - Przykład: `http://192.168.1.100:8501`

**Gotowe!** Masz pełny dashboard na telefonie! 📱

---

## 💡 Wskazówki

### Bezpieczeństwo:
- ⚠️ **Nie udostępniaj API Server publicznie** bez zabezpieczeń!
- ✅ Używaj tylko w sieci lokalnej
- ✅ Lub użyj HTTPS + autoryzacji dla publicznego dostępu

### Wydajność:
- 📱 Telefon ma mniej mocy - skanowanie może być wolniejsze
- 💻 Komputer jest szybszy - lepiej uruchomić tam

### Funkcjonalność:
- 🔵 **BLE** - działa najlepiej na telefonie (telefon ma Bluetooth)
- 📡 **WiFi** - wymaga root na Androidzie, lepiej na komputerze
- 🔌 **USB** - nie działa na telefonie
- 📱 **NFC** - może działać na telefonie (telefon ma NFC)

---

## 📚 Dodatkowe Zasoby

- [Termux Wiki](https://wiki.termux.com/)
- [Python na Windows](https://docs.python.org/3/using/windows.html)
- [Render.com Dokumentacja](https://render.com/docs)

---

**Gotowe!** Teraz możesz uruchomić skaner na Windows i używać z telefonu! 🎉
