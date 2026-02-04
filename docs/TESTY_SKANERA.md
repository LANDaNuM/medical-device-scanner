# 🧪 Przewodnik Testowania Skanera

Ten przewodnik pokazuje jak przetestować skaner w **bezpieczny sposób** i mieć **fizyczny dowód** że działa.

## 🎯 Cel

Chcesz mieć pewność, że skaner działa przed użyciem go w prawdziwym środowisku. Ten przewodnik pokazuje jak to zrobić **bez narażania bezpieczeństwa**.

---

## ✅ Opcja 1: Test WiFi (NAJŁATWIEJSZY - ZALECANY)

### Krok 1: Uruchom Serwer Testowy

W **pierwszym terminalu**:
```bash
python scripts/test_scanner.py --wifi
```

To uruchomi prosty serwer HTTP na porcie 8080, który symuluje podatne urządzenie medyczne.

**Powinieneś zobaczyć:**
```
🧪 Test WiFi - Symulacja Podatnego Urządzenia Medycznego
Serwer testowy uruchomiony na: 192.168.1.XXX:8080
✅ Serwer testowy uruchomiony!
```

### Krok 2: Uruchom Skaner

W **drugim terminalu** (nowe okno terminala):
```bash
python src/scanner.py --wifi
```

### Krok 3: Sprawdź Wyniki

Skaner powinien wykryć:
- ✅ Urządzenie na adresie IP serwera testowego
- ✅ Port 8080 (HTTP) - otwarty
- ✅ Podatność: "HTTP bez HTTPS - dane przesyłane niezaszyfrowane"
- ✅ Security Score: < 80 (średnie/ wysokie ryzyko)

**To jest fizyczny dowód że skaner działa!** 🎉

### Zatrzymanie Serwera

W pierwszym terminalu naciśnij `Ctrl+C` aby zatrzymać serwer testowy.

---

## ✅ Opcja 2: Test BLE (z Telefonem)

### Krok 1: Przygotuj Telefon

1. Włącz Bluetooth na telefonie
2. Upewnij się że telefon jest w zasięgu (< 10 metrów)
3. Sprawdź czy telefon nie jest w trybie "Niewidoczny"

### Krok 2: Uruchom Skaner

```bash
python src/scanner.py --ble
```

### Krok 3: Sprawdź Wyniki

Skaner powinien wykryć:
- ✅ Twój telefon (nazwa urządzenia)
- ✅ Adres MAC telefonu
- ✅ RSSI (siła sygnału)
- ✅ Typ urządzenia (np. Smartphone)

**To jest fizyczny dowód że skaner BLE działa!** 🎉

### Rozwiązywanie Problemów

Jeśli telefon nie jest widoczny:
- Sprawdź czy Bluetooth jest włączony na telefonie
- Sprawdź czy telefon nie jest w trybie "Niewidoczny"
- Spróbuj zbliżyć telefon do laptopa
- Sprawdź czy Bluetooth działa na laptopie: `bluetoothctl list`

---

## ✅ Opcja 3: Test USB (z Pendrive)

### Krok 1: Podłącz Urządzenie USB

Podłącz dowolne urządzenie USB:
- Pendrive USB
- Zewnętrzna klawiatura/mysz
- Telefon przez USB (tryb MTP)
- Zewnętrzny dysk USB

### Krok 2: Uruchom Skaner

```bash
python src/scanner.py --usb
```

### Krok 3: Sprawdź Wyniki

Skaner powinien wykryć:
- ✅ Podłączone urządzenie USB
- ✅ Vendor ID i Product ID
- ✅ Nazwę urządzenia
- ✅ Typ urządzenia

**To jest fizyczny dowód że skaner USB działa!** 🎉

### Rozwiązywanie Problemów

Jeśli urządzenie nie jest widoczne:
- Sprawdź czy urządzenie jest podłączone
- Sprawdź czy urządzenie jest zasilone
- Spróbuj innego portu USB
- Sprawdź czy urządzenie jest widoczne w systemie: `lsusb` (Linux)

---

## 🎯 Pełny Test (Wszystkie Protokoły)

Jeśli chcesz przetestować wszystkie protokoły jednocześnie:

### Terminal 1: Serwer Testowy WiFi
```bash
python scripts/test_scanner.py --wifi
```

### Terminal 2: Skaner
```bash
python src/scanner.py --wifi --ble --usb
```

To przetestuje:
- ✅ WiFi (serwer testowy)
- ✅ BLE (telefon)
- ✅ USB (pendrive)

---

## 📊 Co Oczekiwać w Wynikach

### WiFi Test
```
✓ Wykryto: Device-XXX (192.168.1.XXX)
  Porty: 8080 (HTTP)
  Podatności:
    • HTTP bez HTTPS - dane przesyłane niezaszyfrowane
  Security Score: 65/100
```

### BLE Test
```
✓ Wykryto: iPhone (AA:BB:CC:DD:EE:FF)
  RSSI: -45 dBm
  Typ: Smartphone
  Security Score: 85/100
```

### USB Test
```
✓ Wykryto: SanDisk USB Drive (1234:5678)
  Vendor: SanDisk
  Security Score: 70/100
```

---

## ⚠️ Bezpieczeństwo

### ✅ BEZPIECZNE Testy (Zalecane)
- ✅ Serwer testowy w sieci lokalnej (tylko w Twojej sieci)
- ✅ Test z telefonem (tylko lokalne Bluetooth)
- ✅ Test z pendrive (tylko lokalne USB)

### ❌ NIEBEZPIECZNE (Nie rób tego!)
- ❌ Słabe hasło WiFi (może narazić Twoją sieć)
- ❌ Testowanie na prawdziwych urządzeniach medycznych (bez zgody)
- ❌ Testowanie w sieciach publicznych

---

## 🎓 Dodatkowe Opcje

### Test z Audytem Bezpieczeństwa

```bash
# Terminal 1: Serwer testowy
python scripts/test_scanner.py --wifi

# Terminal 2: Skaner z audytem
python src/scanner.py --wifi --audit
```

To wykona pełny audyt bezpieczeństwa z testami podatności.

### Test z Monitorowaniem

```bash
# Terminal 1: Serwer testowy
python scripts/test_scanner.py --wifi --duration 600

# Terminal 2: Monitorowanie
python src/scanner.py --wifi --monitor --interval 60
```

To będzie monitorować urządzenia co 60 sekund.

---

## 📝 Podsumowanie

| Test | Trudność | Czas | Fizyczny Dowód |
|------|----------|------|----------------|
| WiFi (serwer testowy) | 🟢 Łatwe | 2 min | ✅ Tak |
| BLE (telefon) | 🟢 Łatwe | 1 min | ✅ Tak |
| USB (pendrive) | 🟢 Łatwe | 1 min | ✅ Tak |

**Zalecenie:** Zacznij od testu WiFi - jest najłatwiejszy i daje natychmiastowy fizyczny dowód że skaner działa!

---

## 🆘 Pomoc

Jeśli masz problemy:
1. Sprawdź czy wszystkie biblioteki są zainstalowane: `pip install -r requirements.txt`
2. Sprawdź czy masz uprawnienia (Linux): `sudo usermod -aG plugdev $USER`
3. Zobacz instrukcje: `python scripts/test_scanner.py --guide`
