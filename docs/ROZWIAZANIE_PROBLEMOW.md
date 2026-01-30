# 🔧 Rozwiązywanie Problemów

## Problem 1: scapy jest zainstalowane, ale skaner używa podstawowego skanowania

### Przyczyna
scapy jest zainstalowane w `venv`, ale skaner jest uruchamiany **bez aktywacji venv**.

### Rozwiązanie

**Opcja 1: Aktywuj venv przed uruchomieniem (ZALECANE)**
```bash
cd /home/h9g120og/Downloads/medical-device-scanner-main
source venv/bin/activate
python3 src/scanner.py --wifi
```

**Opcja 2: Użyj Python z venv bezpośrednio**
```bash
cd /home/h9g120og/Downloads/medical-device-scanner-main
./venv/bin/python3 src/scanner.py --wifi
```

**Opcja 3: Zainstaluj scapy globalnie (niezalecane)**
```bash
sudo pip3 install scapy
```

### Sprawdzenie
```bash
# Sprawdź czy venv jest aktywowany
echo $VIRTUAL_ENV

# Jeśli pusty, aktywuj:
source venv/bin/activate

# Sprawdź czy scapy jest dostępne
python3 -c "from scapy.all import ARP; print('✅ scapy działa')"
```

---

## Problem 2: ABUSEIPDB_API_KEY jest w .env, ale skaner go nie widzi

### Przyczyna
Komunikat był wyświetlany zawsze, nawet gdy klucz był dostępny. **Naprawione** - teraz komunikat pojawia się tylko gdy klucz rzeczywiście nie jest dostępny.

### Sprawdzenie

**Sprawdź czy klucz jest w .env:**
```bash
grep ABUSEIPDB_API_KEY .env
```

**Sprawdź czy klucz jest ładowany:**
```bash
cd /home/h9g120og/Downloads/medical-device-scanner-main
python3 -c "
from dotenv import load_dotenv
from pathlib import Path
import os
project_dir = Path('.')
env_file = project_dir / '.env'
load_dotenv(env_file)
key = os.getenv('ABUSEIPDB_API_KEY')
print('ABUSEIPDB_API_KEY:', '✅ OK' if key else '❌ BRAK')
if key:
    print('Długość klucza:', len(key))
"
```

### Rozwiązanie

Jeśli klucz jest w `.env` ale nie jest widziany:

1. **Sprawdź czy plik .env jest w głównym katalogu projektu:**
   ```bash
   ls -la .env
   ```

2. **Sprawdź czy nie ma błędów składniowych w .env:**
   ```bash
   # Każda linia powinna być: KLUCZ=wartość (bez spacji wokół =)
   cat .env | grep ABUSEIPDB
   ```

3. **Upewnij się że używasz python-dotenv:**
   ```bash
   pip install python-dotenv
   ```

4. **Uruchom ponownie skaner:**
   ```bash
   python3 src/scanner.py --wifi
   ```

---

## Problem 3: Skanowanie jest wolne

### Przyczyna
Używane jest podstawowe skanowanie (ping + socket) zamiast scapy.

### Rozwiązanie

1. **Aktywuj venv:**
   ```bash
   source venv/bin/activate
   ```

2. **Sprawdź czy scapy działa:**
   ```bash
   python3 -c "from scapy.all import ARP; print('✅ OK')"
   ```

3. **Uruchom skaner:**
   ```bash
   python3 src/scanner.py --wifi
   ```

**Teraz powinieneś zobaczyć:**
- ✅ Szybsze skanowanie
- ✅ Więcej wykrytych urządzeń
- ✅ Brak komunikatu o "podstawowym skanowaniu"

---

## Sprawdzanie Statusu

Uruchom ten skrypt aby sprawdzić wszystkie komponenty:

```bash
cd /home/h9g120og/Downloads/medical-device-scanner-main
source venv/bin/activate

python3 << 'EOF'
print("🔍 Sprawdzam status komponentów...\n")

# Sprawdź venv
import os
venv = os.getenv('VIRTUAL_ENV')
if venv:
    print(f"✅ VENV: Aktywowany ({venv})")
else:
    print("❌ VENV: Nieaktywowany (uruchom: source venv/bin/activate)")

# Sprawdź scapy
try:
    from scapy.all import ARP
    print("✅ scapy: DOSTĘPNY")
except:
    print("❌ scapy: NIEDOSTĘPNY (zainstaluj: pip install scapy)")

# Sprawdź ABUSEIPDB_API_KEY
from dotenv import load_dotenv
from pathlib import Path
project_dir = Path('.')
env_file = project_dir / '.env'
load_dotenv(env_file)
key = os.getenv('ABUSEIPDB_API_KEY')
if key:
    print(f"✅ ABUSEIPDB_API_KEY: OK (długość: {len(key)})")
else:
    print("❌ ABUSEIPDB_API_KEY: BRAK (dodaj do .env)")

# Sprawdź Rust scanner
try:
    from rust_scanner_wrapper import is_rust_available
    if is_rust_available():
        print("✅ Rust scanner: DOSTĘPNY (3-4x szybsze!)")
    else:
        print("⚠️  Rust scanner: NIEDOSTĘPNY")
except:
    print("⚠️  Rust scanner: NIEDOSTĘPNY")

print("\n💡 Aby użyć szybszego skanowania:")
print("   1. source venv/bin/activate")
print("   2. python3 src/scanner.py --wifi")
EOF
```

---

## Najczęstsze Błędy

### Błąd: "ModuleNotFoundError: No module named 'scapy'"

**Przyczyna:** scapy nie jest zainstalowane lub venv nie jest aktywowany.

**Rozwiązanie:**
```bash
source venv/bin/activate
pip install scapy
```

---

### Błąd: "Używam podstawowego skanowania"

**Przyczyna:** scapy nie jest dostępne (venv nieaktywowany lub scapy nie zainstalowane).

**Rozwiązanie:**
```bash
source venv/bin/activate
python3 src/scanner.py --wifi
```

---

### Błąd: "Dodaj ABUSEIPDB_API_KEY do .env"

**Przyczyna:** Klucz nie jest w .env lub nie jest poprawnie ładowany.

**Rozwiązanie:**
1. Sprawdź czy klucz jest w `.env`:
   ```bash
   grep ABUSEIPDB_API_KEY .env
   ```

2. Sprawdź składnię (bez spacji wokół `=`):
   ```bash
   ABUSEIPDB_API_KEY=twoj_klucz_tutaj
   ```

3. Uruchom ponownie skaner

---

## ✅ Podsumowanie

**Aby wszystko działało poprawnie:**

1. **Aktywuj venv:**
   ```bash
   source venv/bin/activate
   ```

2. **Sprawdź komponenty:**
   ```bash
   pip list | grep -E "scapy|python-dotenv"
   ```

3. **Uruchom skaner:**
   ```bash
   python3 src/scanner.py --wifi
   ```

**Teraz powinieneś zobaczyć:**
- ✅ Szybsze skanowanie (scapy)
- ✅ Threat Intelligence działa (ABUSEIPDB_API_KEY)
- ✅ Brak komunikatów o brakujących komponentach
