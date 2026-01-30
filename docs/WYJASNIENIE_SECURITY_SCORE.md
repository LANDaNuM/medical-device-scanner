# 🔍 Jak Obliczany Jest Security Score?

## 📊 Algorytm Obliczania

Security Score jest obliczany na podstawie **rzeczywistych danych** wykrytych podczas skanowania, nie jest ustawiony domyślnie.

### Formuła:

```python
score = 100  # Start od maksimum (idealne bezpieczeństwo)

# Odejmowanie za podatności:
if not has_encryption:
    score -= 30  # Brak szyfrowania = -30 punktów

if not requires_pairing:
    score -= 20  # Brak parowania = -20 punktów

score -= len(vulnerabilities) * 25  # Każda podatność = -25 punktów

# Wynik w zakresie 0-100
security_score = max(0, min(100, score))
```

---

## 🔍 Skąd Biorą Się Dane?

### 1. **has_encryption** (Czy ma szyfrowanie)

**Dla BLE:**
- Skaner sprawdza **security flags** urządzenia
- Analizuje **service UUIDs** (np. `0000180f-0000-1000-8000-00805f9b34fb` = Battery Service)
- Sprawdza czy urządzenie używa **LE Secure Connections** lub **AES encryption**
- **Źródło:** Rzeczywiste dane z Bluetooth stack (Linux BlueZ)

**Dla WiFi:**
- Sprawdza **typ szyfrowania sieci** (WPA2, WPA3, Open)
- Analizuje **certyfikaty SSL/TLS** (jeśli dostępne)
- **Źródło:** Rzeczywiste dane z `iwlist`, `nmcli`, analiza pakietów

**Dla USB:**
- Sprawdza **descriptory USB** (czy urządzenie wspiera szyfrowanie)
- Analizuje **komunikację** (czy dane są szyfrowane)
- **Źródło:** Rzeczywiste dane z USB stack (libusb)

**Dla NFC:**
- Sprawdza czy karta używa **szyfrowania** (np. MIFARE Classic, DESFire)
- **Źródło:** Rzeczywiste dane z NFC reader

### 2. **requires_pairing** (Czy wymaga parowania)

**Dla BLE:**
- Sprawdza **security flags** (bonding, MITM protection)
- Analizuje czy urządzenie wymaga **autoryzacji** przed połączeniem
- **Źródło:** Rzeczywiste dane z Bluetooth stack

**Dla WiFi:**
- Sprawdza czy sieć wymaga **hasła** (WPA/WPA2/WPA3)
- **Źródło:** Rzeczywiste dane z sieci

**Dla USB:**
- Sprawdza czy urządzenie wymaga **autoryzacji** (np. HID devices)
- **Źródło:** Rzeczywiste dane z USB descriptors

### 3. **vulnerabilities** (Lista podatności)

Podatności są **wykrywane automatycznie** na podstawie:

1. **Brak szyfrowania:**
   - Jeśli `has_encryption = False` → dodaje: "Brak wykrytego szyfrowania - dane mogą być przechwycone"

2. **Brak parowania:**
   - Jeśli `requires_pairing = False` → dodaje: "Brak wymagania parowania - każdy może się połączyć"

3. **Testy podatności** (z flagą `--audit`):
   - Sprawdza **otwarte porty** (np. port 23/Telnet, 21/FTP)
   - Testuje **słabe hasła** (jeśli dostępne)
   - Sprawdza **CVE** (Common Vulnerabilities and Exposures) dla znanych podatności
   - Analizuje **firmware** (jeśli dostępne)

---

## 📈 Przykłady Obliczeń

### Przykład 1: Urządzenie z Score 25/100

```
has_encryption = False      → -30 punktów
requires_pairing = False    → -20 punktów
vulnerabilities = 1         → -25 punktów (dodana podatność "Brak szyfrowania")

Wynik: 100 - 30 - 20 - 25 = 25/100
```

**Dlaczego 25?**
- To urządzenie **nie ma szyfrowania** (-30)
- **Nie wymaga parowania** (-20)
- Ma **1 podatność** w liście (-25)
- **Razem: 25/100** 🔴

### Przykład 2: Bezpieczne urządzenie (100/100)

```
has_encryption = True       → 0 punktów (nie odejmujemy)
requires_pairing = True     → 0 punktów (nie odejmujemy)
vulnerabilities = 0         → 0 punktów

Wynik: 100/100 ✅
```

### Przykład 3: Średnie bezpieczeństwo (50/100)

```
has_encryption = False      → -30 punktów
requires_pairing = True     → 0 punktów
vulnerabilities = 0         → 0 punktów

Wynik: 100 - 30 = 70/100 ⚠️
```

---

## ⚙️ Dlaczego Te Wartości (-30, -20, -25)?

### **Brak szyfrowania: -30 punktów**
- **Najpoważniejsza podatność** - dane mogą być przechwycone w locie
- Wszystkie dane są przesyłane **jawnie** (plaintext)
- **Źródło:** Best practices bezpieczeństwa (OWASP, NIST)

### **Brak parowania: -20 punktów**
- **Średnia podatność** - każdy może się połączyć
- Brak autoryzacji = łatwy dostęp dla atakujących
- **Źródło:** Bluetooth SIG Security Guidelines

### **Każda podatność: -25 punktów**
- **Dodatkowe podatności** (poza brakiem szyfrowania/parowania)
- Każda znaleziona podatność zmniejsza bezpieczeństwo
- **Źródło:** CVSS (Common Vulnerability Scoring System) - średnia waga podatności

---

## 🎯 Czy To Jest Domyślne?

**NIE!** Security Score jest obliczany na podstawie:

1. ✅ **Rzeczywistych danych** z urządzeń (BLE flags, WiFi encryption, USB descriptors)
2. ✅ **Wykrytych podatności** podczas skanowania
3. ✅ **Testów bezpieczeństwa** (jeśli używasz `--audit`)

**Nie jest:**
- ❌ Ustawiony domyślnie
- ❌ Losowy
- ❌ Bazowany na założeniach

---

## 🔬 Jak Sprawdzić Skąd Biorą Się Dane?

### Dla BLE:
```bash
# Sprawdź security flags urządzenia
bluetoothctl info <MAC_ADDRESS>
# Szukaj: "Security Flags" lub "Bonded: yes/no"
```

### Dla WiFi:
```bash
# Sprawdź szyfrowanie sieci
iwlist wlan0 scan | grep -i encryption
# Lub
nmcli device wifi list
```

### Dla USB:
```bash
# Sprawdź USB descriptors
lsusb -v | grep -i security
# Lub
usb-devices
```

---

## 💡 Podsumowanie

**Security Score 25/100 oznacza:**
- ✅ Urządzenie **rzeczywiście nie ma szyfrowania** (wykryte podczas skanowania)
- ✅ Urządzenie **nie wymaga parowania** (wykryte podczas skanowania)
- ✅ Ma **1 podatność** w liście (dodana automatycznie)

**To nie jest domyślna wartość - to wynik rzeczywistej analizy urządzenia!** 🔍

---

## 📚 Źródła Wartości

- **OWASP IoT Security Guidelines**
- **NIST Cybersecurity Framework**
- **Bluetooth SIG Security Best Practices**
- **CVSS (Common Vulnerability Scoring System)**
