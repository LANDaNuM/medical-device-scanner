# 🔍 Ulepszenia Wykrywania Podatności

## ✅ Co Zostało Dodane

### 🆕 Nowe Testy Podatności

#### 1. **Testy Specyficzne dla BLE**
- ✅ **Słabe szyfrowanie BLE** - wykrywa AES-128 vs AES-256
- ✅ **Exposed Services** - wykrywa services dostępne bez autoryzacji:
  - Battery Service (0000180f)
  - Device Information Service (0000180a)
  - Location and Navigation Service (00001819)
  - Environmental Sensing Service (0000181a)
- ✅ **Random MAC Address** - informacja o losowym MAC (privacy vs identyfikacja)

#### 2. **Testy Specyficzne dla USB**
- ✅ **USB Unencrypted** - wykrywa brak szyfrowania USB
- ✅ **BadUSB Risk** - wykrywa urządzenia HID (klawiatury, myszy) podatne na BadUSB

#### 3. **Testy Specyficzne dla NFC**
- ✅ **NFC Unencrypted** - wykrywa brak szyfrowania (skimming risk)
- ✅ **NFC No Authentication** - wykrywa brak autoryzacji

#### 4. **Testy Firmware**
- ✅ **Outdated Firmware** - wykrywa przestarzałe wersje firmware (< 2.0)
- ✅ **Firmware Version Unknown** - informacja o braku danych o firmware

#### 5. **Testy Słabych Algorytmów Szyfrowania**
- ✅ **Weak Encryption Algorithms** - wykrywa DES, 3DES, RC4, MD5, SHA1, WEP, WPA
- ✅ **Outdated TLS Versions** - wykrywa TLS 1.0/1.1 (podatne na POODLE, BEAST)

#### 6. **Testy Domyślnych Haseł**
- ✅ **Default Password Risk** - wykrywa porty które często mają domyślne hasła:
  - SSH (22) - root/root, admin/admin
  - RDP (3389) - Administrator/password
  - HTTP Admin (80, 443, 8080) - admin/admin

#### 7. **Nowe Testy Portów**
- ✅ **VNC** - wykrywa brak szyfrowania VNC
- ✅ **FTP** - wykrywa brak szyfrowania i ryzyko domyślnych haseł
- ✅ **Telnet** - wykrywa przestarzały i niebezpieczny protokół
- ✅ **Mail (POP3/IMAP)** - wykrywa brak szyfrowania i słabe TLS
- ✅ **SNMP** - wykrywa słabe community strings
- ✅ **SMB** - wykrywa podatności WannaCry i brak szyfrowania

---

## 📊 Statystyki Wykrywania

### Przed ulepszeniami:
- **WiFi:** Porty, podstawowe CVE, DICOM/HL7
- **BLE:** Brak szyfrowania, brak parowania
- **USB:** Brak szyfrowania
- **NFC:** Brak szyfrowania

### Po ulepszeniach:
- **WiFi:** Porty, CVE, DICOM/HL7, **default passwords, VNC, FTP, Telnet, Mail, SNMP, SMB**
- **BLE:** Brak szyfrowania, brak parowania, **słabe algorytmy, exposed services, random MAC**
- **USB:** Brak szyfrowania, **BadUSB risk**
- **NFC:** Brak szyfrowania, **brak autoryzacji**
- **Wszystkie:** **Firmware tests, weak encryption keys, default passwords**

---

## 🎯 Co Jest Teraz Wykrywane

### 🔴 Krytyczne Podatności:
1. **Brak szyfrowania** (wszystkie protokoły)
2. **Telnet** - wszystkie dane w plaintext
3. **FTP** - hasła w plaintext
4. **VNC** - sesje mogą być przechwycone
5. **SMB WannaCry** - podatność na ransomware
6. **Słabe algorytmy** - DES, 3DES, RC4, MD5, SHA1, WEP, WPA
7. **Bazy danych otwarte** - MSSQL, MySQL, PostgreSQL, MongoDB

### 🟠 Wysokie Podatności:
1. **Brak autoryzacji** (wszystkie protokoły)
2. **Domyślne hasła** - SSH, RDP, HTTP Admin
3. **TLS 1.0/1.1** - przestarzałe wersje
4. **DICOM/HL7** - porty medyczne bez szyfrowania
5. **SNMP** - słabe community strings
6. **BadUSB** - urządzenia HID

### 🟡 Średnie Podatności:
1. **AES-128** (dla urządzeń medycznych - powinno być AES-256)
2. **Exposed BLE Services** - services dostępne bez autoryzacji
3. **Outdated Firmware** - stare wersje firmware
4. **HTTP bez HTTPS** - dla routerów mniej krytyczne

---

## 🔬 Jak Działa Wykrywanie

### 1. **Automatyczne Wykrywanie (zawsze włączone)**
- Podczas skanowania automatycznie wykrywa:
  - Brak szyfrowania
  - Brak parowania
  - Słabe algorytmy (jeśli wykryte)

### 2. **Testy z Flagą `--audit`**
- Pełny audyt bezpieczeństwa:
  - Testy portów (VNC, FTP, Telnet, Mail, SNMP, SMB)
  - Testy protokołów medycznych (DICOM, HL7)
  - Testy kombinacji portów
  - Testy firmware
  - Testy domyślnych haseł
  - Testy exposed services (BLE)

### 3. **CVE Lookup (jeśli API dostępne)**
- Automatyczne pobieranie aktualnych podatności z NIST NVD
- Sprawdzanie CVE dla konkretnych portów
- CVSS scores i szczegóły podatności

---

## 📈 Przykłady Wykrytych Podatności

### Przykład 1: Urządzenie BLE
```
🔴 Brak wykrytego szyfrowania - dane mogą być przechwycone
🔴 Brak wymagania parowania - każdy może się połączyć
🟡 BLE Weak Encryption (AES-128) - zalecane AES-256 dla urządzeń medycznych
🟡 BLE Exposed Service: Battery Service - dostępny bez autoryzacji
```

### Przykład 2: Urządzenie WiFi z portami
```
🔴 Telnet Unencrypted - wszystkie dane przesyłane jawnie
🔴 FTP Unencrypted - hasła przesyłane jawnie
🟠 FTP Default Passwords Risk - często używa domyślnych haseł
🔴 SMB WannaCry Vulnerability - podatny na ransomware
🟠 Default Password Risk (Port 22) - SSH może używać domyślnych haseł
```

### Przykład 3: Urządzenie USB
```
🔴 USB Unencrypted Communication - dane mogą być przechwycone
🟠 USB HID Device (Potential BadUSB) - może być użyte do ataków
```

---

## 🚀 Użycie

### Podstawowe skanowanie (automatyczne wykrywanie):
```bash
python3 src/scanner.py
```

### Pełny audyt bezpieczeństwa (wszystkie testy):
```bash
python3 src/scanner.py --audit
```

### Tylko WiFi z audytem:
```bash
python3 src/scanner.py --wifi --audit
```

---

## 💡 Wskazówki

1. **Użyj `--audit`** dla pełnego audytu - wykrywa więcej podatności
2. **CVE API** - dodaj `NVD_API_KEY` do `.env` dla aktualnych podatności
3. **Sprawdzaj raporty** - szczegółowe informacje w `report_*.json` i `report_*.pdf`

---

## ✅ Podsumowanie

**Dodano:**
- ✅ 7 nowych kategorii testów podatności
- ✅ Testy specyficzne dla BLE/USB/NFC
- ✅ Testy firmware i słabych algorytmów
- ✅ Testy domyślnych haseł
- ✅ Testy dla VNC, FTP, Telnet, Mail, SNMP, SMB

**Wykrywanie jest teraz znacznie bardziej kompleksowe!** 🔍
