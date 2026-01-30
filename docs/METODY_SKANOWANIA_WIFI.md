# 🔍 Metody Skanowania WiFi

## 📋 Dostępne Metody Skanowania

Skaner WiFi używa **3 metod skanowania** w kolejności priorytetu:

### 1. 🥇 **tshark (Wireshark CLI)** - Najlepsze
- **Co to:** Bardzo rozbudowane narzędzie do analizy sieci
- **Zalety:**
  - Najdokładniejsze wykrywanie urządzeń
  - Wykrywa aktywne hosty (ARP, DHCP, DNS)
  - Skanuje porty (TCP SYN scan)
  - Pobiera MAC adresy bezpośrednio
  - Wykrywa usługi i protokoły
- **Wymagania:** Wymaga zainstalowania `tshark` (część Wireshark)
- **Status:** Używane jeśli dostępne

---

### 2. 🥈 **scapy (Python Library)** - Zalecane
- **Co to:** Python library do manipulacji pakietów sieciowych
- **Zalety:**
  - Nie wymaga zewnętrznych programów (tylko Python)
  - Szybkie skanowanie (ARP scan lub ping scan)
  - Wykrywa aktywne hosty i MAC adresy
  - Może używać **Rust scanner** (3-4x szybsze skanowanie portów!)
- **Wymagania:** Wymaga zainstalowania `scapy`
- **Status:** Używane jeśli dostępne (gdy tshark nie działa)

---

### 3. 🥉 **Podstawowe skanowanie (ping + socket)** - Fallback
- **Co to:** Proste skanowanie używając `ping` i `socket`
- **Zalety:**
  - **Działa zawsze** (nie wymaga dodatkowych bibliotek)
  - Nie wymaga uprawnień root
  - Może używać **Rust scanner** (jeśli dostępny)
- **Wady:**
  - Wolniejsze niż scapy/tshark
  - Mniej dokładne (może przegapić niektóre urządzenia)
  - Skanuje tylko pierwsze 50 adresów IP (dla szybkości)
- **Status:** Używane gdy tshark i scapy nie są dostępne

---

## ⚡ Rust Scanner - Dodatkowe Przyspieszenie

Niezależnie od metody skanowania (scapy lub podstawowe), skaner może używać **Rust scanner** do skanowania portów:

- **Szybkość:** 3-4x szybsze niż Python socket
- **Równoległość:** Skanuje wiele portów jednocześnie
- **Status:** Automatycznie używany jeśli dostępny

**Sprawdź czy Rust scanner jest dostępny:**
```bash
python3 -c "from rust_scanner_wrapper import is_rust_available; print('✅ Rust dostępny' if is_rust_available() else '❌ Rust niedostępny')"
```

---

## 🔍 Dlaczego Używane Jest Podstawowe Skanowanie?

Jeśli widzisz komunikat:
```
⚠️  Używam podstawowego skanowania (ping + socket)
   Uwaga: Podstawowe skanowanie może być wolniejsze i mniej dokładne
```

To oznacza, że:
1. ❌ **tshark nie jest dostępny** (nie zainstalowany lub nie zwrócił wyników)
2. ❌ **scapy nie jest dostępny** (nie zainstalowany lub wystąpił błąd)

---

## 🚀 Jak Użyć Szybszej Metody (scapy)

### Krok 1: Zainstaluj scapy

```bash
# W katalogu projektu (z venv aktywowanym)
pip install scapy
```

### Krok 2: Sprawdź czy działa

```bash
python3 -c "from scapy.all import ARP; print('✅ scapy działa')"
```

### Krok 3: Uruchom skaner ponownie

```bash
python3 src/scanner.py --wifi
```

**Teraz powinieneś zobaczyć:**
- ✅ Szybsze skanowanie
- ✅ Więcej wykrytych urządzeń
- ✅ Brak komunikatu o "podstawowym skanowaniu"

---

## 🔧 Instalacja tshark (Opcjonalne - Najlepsze)

Jeśli chcesz użyć najlepszej metody (tshark):

### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tshark
```

### Sprawdź czy działa:
```bash
tshark --version
```

**Uwaga:** tshark może wymagać uprawnień root do przechwytywania pakietów, ale skaner ma fallback.

---

## 📊 Porównanie Metod

| Metoda | Szybkość | Dokładność | Wymagania | Rust Scanner |
|--------|----------|------------|-----------|--------------|
| **tshark** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Wymaga instalacji | ✅ Tak |
| **scapy** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | `pip install scapy` | ✅ Tak |
| **Podstawowe** | ⭐⭐⭐ | ⭐⭐⭐ | Brak (działa zawsze) | ✅ Tak |

---

## 🛠️ Rozwiązywanie Problemów

### Problem: "Używam podstawowego skanowania"

**Rozwiązanie 1: Zainstaluj scapy (ZALECANE)**
```bash
pip install scapy
```

**Rozwiązanie 2: Sprawdź czy scapy jest zainstalowane**
```bash
pip list | grep scapy
```

**Rozwiązanie 3: Sprawdź czy nie ma błędów importu**
```bash
python3 -c "from scapy.all import ARP; print('OK')"
```

---

### Problem: Skanowanie jest wolne

**Rozwiązanie 1: Zainstaluj scapy**
- scapy jest szybsze niż podstawowe skanowanie

**Rozwiązanie 2: Sprawdź czy Rust scanner jest dostępny**
```bash
python3 -c "from rust_scanner_wrapper import is_rust_available; print('Rust:', is_rust_available())"
```

**Rozwiązanie 3: Zbuduj Rust scanner (jeśli dostępny kod Rust)**
```bash
cd rust_scanner
maturin develop
```

---

## ✅ Sprawdzenie Statusu

Uruchom ten skrypt aby sprawdzić dostępne metody:

```bash
python3 << 'EOF'
print("🔍 Sprawdzam dostępne metody skanowania...\n")

# Sprawdź tshark
import subprocess
try:
    result = subprocess.run(['tshark', '--version'], capture_output=True, timeout=2)
    if result.returncode == 0:
        print("✅ tshark: DOSTĘPNY")
    else:
        print("❌ tshark: NIEDOSTĘPNY")
except:
    print("❌ tshark: NIEDOSTĘPNY (nie zainstalowany)")

# Sprawdź scapy
try:
    from scapy.all import ARP
    print("✅ scapy: DOSTĘPNY")
except:
    print("❌ scapy: NIEDOSTĘPNY (zainstaluj: pip install scapy)")

# Sprawdź Rust scanner
try:
    from rust_scanner_wrapper import is_rust_available
    if is_rust_available():
        print("✅ Rust scanner: DOSTĘPNY (3-4x szybsze skanowanie portów!)")
    else:
        print("⚠️  Rust scanner: NIEDOSTĘPNY (używany będzie Python socket)")
except:
    print("⚠️  Rust scanner: NIEDOSTĘPNY")

print("\n💡 Aby użyć szybszej metody, zainstaluj: pip install scapy")
EOF
```

---

## 📝 Podsumowanie

- **Podstawowe skanowanie** = fallback gdy tshark/scapy nie są dostępne
- **scapy** = szybsze i dokładniejsze (zalecane)
- **tshark** = najlepsze, ale wymaga instalacji
- **Rust scanner** = dodatkowe przyspieszenie (3-4x) dla skanowania portów

**Zalecenie:** Zainstaluj `scapy` aby użyć szybszej metody:
```bash
pip install scapy
```
