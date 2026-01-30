# 🧰 Ubuntu na laptopie (Ethernet + Bluetooth) — krok po kroku

Ten plik prowadzi Cię od świeżego **Ubuntu (rekomendowane: 24.04 LTS)** do działającego:
- skanera `src/scanner.py` (BLE/WiFi/USB/NFC)
- API `src/api_server.py` (do używania z telefonu w tej samej sieci)

Zakładam:
- laptop jest podłączony **kablem Ethernet** do routera (Internet + LAN),
- laptop **ma Bluetooth** (albo użyjesz dongla USB Bluetooth),
- projekt jest w katalogu: `~/medical-device-scanner` (możesz mieć inną ścieżkę).

---

## 0) Po instalacji Ubuntu — aktualizacja systemu

```bash
sudo apt update && sudo apt -y upgrade
sudo reboot
```

---

## 1) Pakiety systemowe (ważne dla BLE/WiFi/USB/NFC)

```bash
sudo apt install -y \
  git curl ca-certificates \
  python3 python3-venv python3-pip \
  build-essential pkg-config \
  bluetooth bluez bluez-tools rfkill \
  nmap \
  libusb-1.0-0 libusb-1.0-0-dev \
  pcscd libpcsclite-dev
```

Uwagi:
- `bluetooth/bluez` → BLE działa stabilniej.
- `nmap` → wymagane dla części skanowania sieci (WiFi/LAN).
- `libusb` → czasem potrzebne dla `pyusb`.
- `pcscd`/`libpcsclite-dev` → przydatne, jeśli będziesz używać NFC + PC/SC (opcjonalne).

---

## 2) Bluetooth (BLE) — szybki test, czy wszystko działa

### 2.1 Sprawdź czy Bluetooth nie jest zablokowany

```bash
rfkill list
```

Jeśli widzisz `Soft blocked: yes`, odblokuj:

```bash
sudo rfkill unblock bluetooth
```

### 2.2 Włącz usługę Bluetooth

```bash
sudo systemctl enable --now bluetooth
systemctl status bluetooth --no-pager
```

### 2.3 Sprawdź adapter i zasilanie w `bluetoothctl`

```bash
bluetoothctl show
```

Jeśli `Powered: no`, włącz:

```bash
bluetoothctl power on
```

---

## 3) Pobierz projekt i zrób instalację Pythona (venv)

Jeśli masz już projekt w tym repo — przejdź do katalogu projektu.

### 3.1 Wejdź do katalogu projektu

```bash
cd ~/medical-device-scanner
```

### 3.2 Automatyczny setup (zalecane)

```bash
chmod +x setup.sh
./setup.sh
source venv/bin/activate
```

### 3.3 Ręczny setup (gdybyś wolał)

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4) Uruchamianie skanera (najważniejsze komendy)

Zawsze najpierw aktywuj venv:

```bash
cd ~/medical-device-scanner
source venv/bin/activate
```

### 4.1 Skan wszystkich protokołów

```bash
python3 src/scanner.py
```

### 4.2 Tylko BLE (najlepsze na start)

```bash
python3 src/scanner.py --ble
```

Ważne:
- **Nie uruchamiaj BLE przez `sudo`**, bo często “gubi” biblioteki z venv.

### 4.3 Tylko WiFi/LAN

```bash
python3 src/scanner.py --wifi
```

Jeśli potrzebujesz skanowania, które wymaga uprawnień (np. ARP), użyj:

```bash
sudo -E python3 src/scanner.py --wifi
```

(`-E` zachowuje środowisko venv)

### 4.4 Tylko USB

```bash
python3 src/scanner.py --usb
```

Jeśli nie widzi portów szeregowych, dodaj użytkownika do grupy i zaloguj się ponownie:

```bash
sudo usermod -aG dialout $USER
```

### 4.5 Tylko NFC (jeśli masz czytnik)

```bash
python3 src/scanner.py --nfc
```

### 4.6 Pełny audyt (testy podatności)

```bash
python3 src/scanner.py --audit
python3 src/scanner.py --wifi --audit
```

---

## 5) Gdzie zapisują się wyniki (lokalnie)

Projekt zapisuje dane w:

```text
data/
├── scans/          # scan_*.json
└── reports/        # report_*.json / report_*.csv / report_*.pdf
```

To jest ważne też dla API — API czyta “najnowsze pliki” właśnie z `data/scans` i `data/reports`.

---

## 6) Uruchom API (żeby używać z telefonu w tej samej sieci)

### 6.1 Start API

```bash
cd ~/medical-device-scanner
source venv/bin/activate
python3 src/api_server.py
```

Serwer nasłuchuje na `0.0.0.0:5000`, więc telefon w tej samej sieci może wejść po IP laptopa.

### 6.2 Sprawdź IP laptopa w LAN

Najprościej:

```bash
hostname -I
```

Wejdź na telefonie w przeglądarkę:
- `http://TWOJE_IP:5000/` (strona “czytelna”)
- `http://TWOJE_IP:5000/devices`
- `http://TWOJE_IP:5000/report`

Jeśli firewall blokuje:

```bash
sudo ufw allow 5000/tcp
```

---

## 7) (Opcjonalnie) Dashboard w przeglądarce (na laptopie/telefonie)

```bash
cd ~/medical-device-scanner
source venv/bin/activate
streamlit run src/dashboard.py --server.address 0.0.0.0 --server.port 8501
```

Telefon:
- `http://TWOJE_IP:8501`

---

## 8) Najczęstsze problemy (szybkie rozwiązania)

### BLE: “nie widzi urządzeń”
- sprawdź `rfkill list` i `bluetoothctl show`
- zrestartuj usługę:

```bash
sudo systemctl restart bluetooth
```

### WiFi: “permission denied” / słabe wyniki
- uruchom tylko WiFi jako root (z venv):

```bash
source venv/bin/activate
sudo -E python3 src/scanner.py --wifi
```

### USB: brak portów / brak uprawnień
- dodaj do `dialout` i zaloguj się ponownie:

```bash
sudo usermod -aG dialout $USER
```

### `pip install -r requirements.txt` trwa długo / błędy (np. ciężkie ML)
- na start możesz korzystać z BLE/WiFi/USB bez “ciężkich” elementów ML,
- jeśli instalacja się wysypie na dużych paczkach (np. TensorFlow), daj znać — podam “minimalny zestaw zależności” pod same skany.

---

## 9) Minimalny “test końcowy” (10 minut)

1) `source venv/bin/activate`  
2) `python3 src/scanner.py --ble`  
3) `python3 src/scanner.py --wifi`  
4) `python3 src/api_server.py` i wejdź na `http://TWOJE_IP:5000/` z telefonu  

