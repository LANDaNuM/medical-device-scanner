# 🐍 Kompletny Przewodnik po Kodzie Python - Część 2: SKANERY

## 📚 Spis Treści Części 2

1. [Wprowadzenie do Skanerów](#wprowadzenie-do-skanerów)
2. [Plik 3: `real_scanner.py` - Skaner BLE](#plik-3-real_scannerpy---skaner-ble)
3. [Plik 4: `wifi_scanner.py` - Skaner WiFi](#plik-4-wifi_scannerpy---skaner-wifi)
4. [Plik 5: `usb_scanner.py` - Skaner USB](#plik-5-usb_scannerpy---skaner-usb)
5. [Plik 6: `nfc_scanner.py` - Skaner NFC](#plik-6-nfc_scannerpy---skaner-nfc)

---

## Wprowadzenie do Skanerów

Skanery to moduły które **wykrywają urządzenia** w różnych protokołach komunikacji:
- **BLE** (Bluetooth Low Energy) - urządzenia bezprzewodowe
- **WiFi** - urządzenia w sieci lokalnej
- **USB** - urządzenia podłączone przez kabel USB
- **NFC** - karty i tagi NFC

**Wszystkie skanery:**
1. Wykrywają urządzenia
2. Analizują ich właściwości bezpieczeństwa
3. Tworzą obiekty `Device` (z `device.py`)
4. Zwracają listę urządzeń

---

## Plik 3: `real_scanner.py` - Skaner BLE

### 📍 Lokalizacja: `src/real_scanner.py`

### 🎯 Cel
Wykrywa rzeczywiste urządzenia **Bluetooth Low Energy (BLE)** i analizuje ich bezpieczeństwo.

### 📝 Kod z Wyjaśnieniami

#### Importy i Konfiguracja

```python
#!/usr/bin/env python3
```

**Wyjaśnienie:**
- **Shebang** - mówi systemowi operacyjnemu jak uruchomić plik
- `#!/usr/bin/env python3` - użyj `python3` z PATH
- **Dlaczego?** Pozwala uruchomić plik bezpośrednio: `./real_scanner.py`

```python
import asyncio
```

**Wyjaśnienie:**
- `asyncio` - moduł do **programowania asynchronicznego**
- **Asynchroniczne** = wiele operacji jednocześnie (nie czeka na jedną, wykonuje inne)
- **Przykład:** Podczas skanowania BLE, możemy skanować wiele urządzeń jednocześnie

```python
import platform
```

**Wyjaśnienie:**
- `platform` - moduł do wykrywania systemu operacyjnego (Windows, Linux, Mac)
- Używamy do różnych implementacji dla różnych systemów

```python
from typing import List, Optional, Dict, Set
```

**Wyjaśnienie:**
- **Type hints** - adnotacje typów
- `List` - lista elementów
- `Optional[str]` - string lub None
- `Dict` - słownik (klucz: wartość)
- `Set` - zbiór (unikalne elementy, bez duplikatów)

#### Import Biblioteki BLE

```python
try:
    from bleak import BleakScanner, BleakClient
    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False
    print("⚠️  Biblioteka 'bleak' nie jest zainstalowana.")
```

**Wyjaśnienie:**
- `try/except` - **obsługa błędów**
- `try:` - spróbuj wykonać kod
- `except ImportError:` - jeśli wystąpi błąd importu, wykonaj to
- **Dlaczego?** Biblioteka `bleak` może nie być zainstalowana - nie chcemy żeby program się zakończył błędem
- `BLEAK_AVAILABLE` - flaga mówiąca czy biblioteka jest dostępna

#### UUID Serwisów Medycznych

```python
MEDICAL_SERVICE_UUIDS = {
    "00001808-0000-1000-8000-00805f9b34fb": "Glucose Service",  # Glukometr
    "0000180f-0000-1000-8000-00805f9b34fb": "Battery Service",
    # ...
}
```

**Wyjaśnienie:**
- **UUID** - Universal Unique Identifier (unikalny identyfikator)
- **Service UUID** - identyfikator serwisu Bluetooth
- `"00001808-..."` - standardowy UUID dla Glucose Service (zdefiniowany przez Bluetooth SIG)
- **Słownik** - mapuje UUID na nazwę serwisu
- **Dlaczego?** Jeśli urządzenie ma UUID `0x1808`, wiemy że to glukometr!

#### Klasa RealBLEScanner - Konstruktor

```python
class RealBLEScanner:
    def __init__(self):
        """Inicjalizacja skanera BLE."""
        if not BLEAK_AVAILABLE:
            raise ImportError("Biblioteka 'bleak' nie jest zainstalowana.")
```

**Wyjaśnienie:**
- `__init__` - **konstruktor** (wykonuje się gdy tworzysz obiekt)
- `raise ImportError(...)` - **rzuca wyjątek** (błąd)
- **Dlaczego?** Jeśli biblioteka nie jest zainstalowana, lepiej przerwać od razu niż działać z błędami

```python
        self.scanned_devices_dict: Dict[str, BLEDevice] = {}
```

**Wyjaśnienie:**
- `self.scanned_devices_dict` - **atrybut instancji** (zmienna należąca do obiektu)
- `Dict[str, BLEDevice]` - słownik: klucz = string (MAC), wartość = BLEDevice
- `{}` - pusty słownik
- **Przechowuje:** adres MAC → obiekt BLEDevice (z biblioteki bleak)

```python
        self.device_names: Dict[str, str] = {}
```

**Wyjaśnienie:**
- Przechowuje: adres MAC → nazwa urządzenia
- **Dlaczego osobno?** Nazwa może być dostępna tylko podczas callback, więc zapisujemy ją od razu

```python
        self.scanned_devices: List[Device] = []
```

**Wyjaśnienie:**
- Lista wszystkich wykrytych urządzeń jako obiekty `Device`
- **To jest główna lista** którą zwracamy

#### Metoda: scan_ble_devices() - Główna Metoda Skanowania

```python
    async def scan_ble_devices(self, duration: int = 10) -> List[Device]:
```

**Wyjaśnienie:**
- `async def` - **funkcja asynchroniczna**
- `duration: int = 10` - parametr z domyślną wartością (10 sekund)
- `-> List[Device]` - zwraca listę obiektów Device
- **Asynchroniczna** = może być przerwana i wznowiona (nie blokuje innych operacji)

```python
        devices: List[Device] = []
        discovered_devices: Set[str] = set()
```

**Wyjaśnienie:**
- `devices` - lista urządzeń do zwrócenia
- `discovered_devices` - **zbiór** (Set) unikalnych adresów MAC
- **Dlaczego Set?** Zbiór automatycznie usuwa duplikaty
- **Przykład:**
  ```python
  discovered_devices.add("AA:BB:CC")
  discovered_devices.add("AA:BB:CC")  # Duplikat - nie zostanie dodany
  # discovered_devices = {"AA:BB:CC"}  # Tylko jeden element
  ```

#### Callback Function - Wykrywanie Urządzeń

```python
        def detection_callback(device: BLEDevice, advertisement_data: AdvertisementData):
```

**Wyjaśnienie:**
- **Callback** - funkcja wywoływana automatycznie przez BleakScanner
- **Nie wywołujemy jej ręcznie!** BleakScanner wywołuje ją za każdym razem gdy wykryje urządzenie
- `device` - informacje o urządzeniu (nazwa, MAC)
- `advertisement_data` - dane które urządzenie wysyła w kółko (broadcast)

```python
            if device.address not in discovered_devices:
                discovered_devices.add(device.address)
```

**Wyjaśnienie:**
- `if device.address not in discovered_devices:` - sprawdza czy adres MAC **nie jest** już w zbiorze
- `not in` - operator sprawdzający czy element **nie jest** w kolekcji
- `discovered_devices.add(...)` - **dodaje** adres MAC do zbioru
- **Dlaczego?** To samo urządzenie może być wykryte wiele razy - chcemy tylko raz

```python
                self.advertisement_data[device.address] = advertisement_data
```

**Wyjaśnienie:**
- Zapisuje advertising data do słownika
- **Klucz:** adres MAC
- **Wartość:** advertising data
- **Dlaczego?** Będziemy potrzebować tych danych później do analizy

```python
                device_name = None
                
                # Priorytet 1: device.name
                if device.name:
                    device_name = str(device.name).strip()
                # Priorytet 2: advertisement_data.local_name
                elif advertisement_data.local_name:
                    device_name = str(advertisement_data.local_name).strip()
```

**Wyjaśnienie:**
- **Priorytet** - kolejność sprawdzania (najpierw najlepsze źródło)
- `device.name` - nazwa z obiektu BLEDevice (najbardziej niezawodna)
- `advertisement_data.local_name` - nazwa z advertising data (zapasowa)
- `.strip()` - usuwa białe znaki z początku i końca (spacje, entery)
- **Dlaczego wiele źródeł?** Nie wszystkie urządzenia podają nazwę w tym samym miejscu

```python
                if device_name and device_name.strip():
                    normalized_address = device.address.upper()
                    self.device_names[normalized_address] = device_name.strip()
```

**Wyjaśnienie:**
- `device_name and device_name.strip()` - sprawdza czy nazwa **istnieje** i **nie jest pusta**
- `and` - oba warunki muszą być True
- `.upper()` - konwertuje na wielkie litery (normalizacja)
- **Dlaczego normalizacja?** "aa:bb:cc" i "AA:BB:CC" to ten sam adres, ale różne stringi

#### Rozpoczęcie Skanowania

```python
        async with BleakScanner(detection_callback=detection_callback):
            await asyncio.sleep(duration)
```

**Wyjaśnienie:**
- `async with` - **context manager** dla asynchronicznych operacji
- `BleakScanner(...)` - tworzy skaner BLE
- `detection_callback=...` - przekazuje funkcję callback
- `await asyncio.sleep(duration)` - **czeka** przez określony czas
- **Co się dzieje?**
  1. BleakScanner zaczyna skanować
  2. Gdy wykryje urządzenie → wywołuje `detection_callback`
  3. Czekamy `duration` sekund
  4. Po tym czasie skanowanie się kończy

#### Analiza Urządzeń

```python
            with Progress(...) as progress:
                for address in discovered_devices:
                    device = await self._analyze_device(address)
                    if device:
                        devices.append(device)
```

**Wyjaśnienie:**
- `with Progress(...)` - **progress bar** (pasek postępu) z biblioteki rich
- `for address in discovered_devices:` - **pętla for** - iteruje przez wszystkie wykryte adresy MAC
- `await self._analyze_device(address)` - **analizuje** urządzenie (asynchronicznie)
- `await` - czeka na zakończenie funkcji asynchronicznej
- `if device:` - sprawdza czy analiza zwróciła urządzenie (nie None)
- `devices.append(device)` - **dodaje** urządzenie do listy

#### Metoda: _analyze_device() - Analiza Bezpieczeństwa

```python
    async def _analyze_device(self, address: str) -> Optional[Device]:
```

**Wyjaśnienie:**
- `async def` - funkcja asynchroniczna
- `address: str` - adres MAC urządzenia
- `-> Optional[Device]` - zwraca Device lub None (jeśli nie można przeanalizować)

```python
        ad_data = self.advertisement_data.get(address)
        if not ad_data:
            return None
```

**Wyjaśnienie:**
- `.get(address)` - **bezpieczne** pobranie z słownika (nie rzuca błędu jeśli nie ma)
- Jeśli nie ma advertising data, nie możemy analizować → zwróć None

```python
        name = None
        
        # PRIORYTET 1: Zapisana nazwa z detection_callback
        normalized_address = address.upper()
        if normalized_address in self.device_names:
            saved_name = self.device_names[normalized_address]
            if saved_name and saved_name.strip():
                name = saved_name.strip()
```

**Wyjaśnienie:**
- Sprawdza zapisaną nazwę (z callback)
- **Dlaczego priorytet?** Nazwa może być dostępna tylko podczas callback!

```python
        # Sprawdź właściwości bezpieczeństwa
        has_encryption = False
        requires_pairing = False
```

**Wyjaśnienie:**
- Startujemy od `False` (zakładamy brak szyfrowania/parowania)
- Jeśli znajdziemy dowody → zmienimy na `True`

```python
        try:
            async with BleakClient(address, timeout=3.0) as client:
```

**Wyjaśnienie:**
- `BleakClient` - próbuje **połączyć się** z urządzeniem
- `timeout=3.0` - maksymalny czas czekania (3 sekundy)
- `async with` - automatycznie zamyka połączenie po zakończeniu
- **UWAGA:** Większość urządzeń NIE pozwoli na połączenie bez parowania - to jest **NORMALNE** i oznacza bezpieczeństwo!

```python
                requires_pairing = False  # Możemy się połączyć bez parowania
```

**Wyjaśnienie:**
- Jeśli udało się połączyć → urządzenie **nie wymaga** parowania
- **To jest ZŁE** dla bezpieczeństwa (każdy może się połączyć)

```python
                try:
                    if hasattr(client, 'get_services') and callable(getattr(client, 'get_services')):
                        services = await client.get_services()
```

**Wyjaśnienie:**
- `hasattr(client, 'get_services')` - sprawdza czy obiekt **ma** atrybut/metodę
- `callable(...)` - sprawdza czy to jest **funkcja** (można wywołać)
- **Dlaczego?** Różne wersje bleak mają różne API - sprawdzamy obie

```python
                for service in services:
                    service_uuid = str(service.uuid).lower()
                    
                    for char in service.characteristics:
                        char_props = char.properties
```

**Wyjaśnienie:**
- `for service in services:` - iteruje przez **serwisy** (grupy funkcji)
- `for char in service.characteristics:` - iteruje przez **charakterystyki** (konkretne funkcje)
- `char.properties` - lista właściwości (np. ["read", "write", "encrypt"])

```python
                        if "encrypt" in char_props or "encrypt-authenticate" in char_props:
                            has_encryption = True
                            security_flags.append(f"Encryption required for {service_uuid[:8]}")
```

**Wyjaśnienie:**
- `"encrypt" in char_props` - sprawdza czy lista **zawiera** string "encrypt"
- `or` - operator logiczny (lub) - jeśli którykolwiek warunek jest True
- `has_encryption = True` - ✅ Wykryto wymaganie szyfrowania!
- `security_flags.append(...)` - **dodaje** informację do listy

```python
        except Exception as e:
            error_msg = str(e).lower()
            
            if ("not paired" in error_msg or "pairing" in error_msg):
                requires_pairing = True  # ✅ Urządzenie wymaga parowania - BEZPIECZNE!
                has_encryption = True
```

**Wyjaśnienie:**
- `except Exception as e:` - **łapie** wszystkie błędy
- **WAŻNE:** Błędy połączenia są **NORMALNE** dla Bluetooth!
- Jeśli błąd zawiera "not paired" → urządzenie **wymaga** parowania (to jest DOBRE!)
- `requires_pairing = True` - oznacza że urządzenie jest **bezpieczne**

#### Wykrywanie Typu Urządzenia

```python
    def _detect_device_type(self, service_uuids: List[str], name: Optional[str], manufacturer: Optional[str] = None) -> DeviceType:
```

**Wyjaśnienie:**
- Wykrywa typ urządzenia na podstawie UUID serwisów, nazwy i producenta
- **Metoda 1:** UUID serwisów (najbardziej niezawodne)
- **Metoda 2:** Analiza nazwy (heurystyka)
- **Metoda 3:** Analiza producenta

```python
        # Metoda 1: Sprawdź UUID serwisów medycznych
        for uuid in service_uuids:
            uuid_lower = str(uuid).lower()
            
            if "1808" in uuid_lower:
                return DeviceType.GLUCOSE_METER
```

**Wyjaśnienie:**
- `for uuid in service_uuids:` - iteruje przez wszystkie UUID
- `"1808" in uuid_lower` - sprawdza czy UUID **zawiera** "1808"
- UUID `0x1808` = Glucose Service (standardowy, zdefiniowany przez Bluetooth SIG)
- `return DeviceType.GLUCOSE_METER` - **zwraca** typ i kończy funkcję

```python
        # Metoda 2: Sprawdź nazwę urządzenia
        name_lower = (name or "").lower()
        
        if any(word in name_lower for word in ["glucose", "gluco", "sugar"]):
            return DeviceType.GLUCOSE_METER
```

**Wyjaśnienie:**
- `(name or "")` - jeśli `name` jest None, użyj pustego stringa
- `.lower()` - konwertuje na małe litery (porównywanie bez rozróżniania wielkości)
- `any(...)` - zwraca True jeśli **którykolwiek** element jest True
- `word in name_lower` - sprawdza czy słowo **jest w** nazwie
- **List comprehension w any:** `[word in name_lower for word in ["glucose", ...]]` tworzy listę True/False
- **Przykład:**
  ```python
  name = "GlucoSmart Pro"
  name_lower = "glucosmart pro"
  ["glucose" in name_lower, "gluco" in name_lower] = [False, True]
  any([False, True]) = True  # ✅ Znaleziono!
  ```

#### Tworzenie Obiektu Device

```python
        device = Device(
            mac_address=address,
            name=name,
            device_type=device_type,
            protocol=Protocol.BLE,
            has_encryption=has_encryption,
            encryption_type=encryption_type,
            requires_pairing=requires_pairing,
            rssi=rssi,
            manufacturer=manufacturer_from_mac,
            metadata={...}
        )
```

**Wyjaśnienie:**
- Tworzy obiekt `Device` z wszystkimi danymi
- `protocol=Protocol.BLE` - używa Enum (z `device.py`)
- `metadata={...}` - dodatkowe dane (UUID serwisów, flagi bezpieczeństwa)

```python
        # Dodaj podatności jeśli urządzenie jest niebezpieczne
        if not has_encryption:
            device.add_vulnerability("Brak wykrytego szyfrowania - dane mogą być przechwycone")
```

**Wyjaśnienie:**
- Jeśli urządzenie **nie ma** szyfrowania → dodaj podatność
- `device.add_vulnerability(...)` - metoda z klasy Device (dodaje do listy)

```python
        device.calculate_security_score()
        return device
```

**Wyjaśnienie:**
- Oblicza wynik bezpieczeństwa (0-100)
- Zwraca gotowy obiekt Device

### 🔗 Kiedy jest używany?
- Gdy uruchamiasz `scanner.py --ble`
- Automatycznie przez `scanner.py` (jeśli BLE jest włączony)

### 💡 Przykład użycia:

```python
# Utwórz skaner
scanner = RealBLEScanner()

# Skanuj przez 10 sekund (asynchronicznie)
devices = await scanner.scan_ble_devices(duration=10)

# Lub synchronicznie (dla skryptów)
devices = scan_devices(duration=10)
```

---

## Plik 4: `wifi_scanner.py` - Skaner WiFi

### 📍 Lokalizacja: `src/wifi_scanner.py`

### 🎯 Cel
Wykrywa urządzenia w **sieci lokalnej WiFi** i analizuje otwarte porty.

### 📝 Kod z Wyjaśnieniami

#### Importy

```python
import socket
```

**Wyjaśnienie:**
- `socket` - moduł do komunikacji sieciowej
- Używamy do: ping, skanowania portów, połączeń TCP

```python
import subprocess
```

**Wyjaśnienie:**
- `subprocess` - uruchamianie zewnętrznych programów
- Używamy do: `ping`, `nmblookup`, `tshark`

```python
try:
    from scapy.all import ARP, Ether, IP, TCP, srp, sr1, conf
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
```

**Wyjaśnienie:**
- `scapy` - biblioteka do manipulacji pakietów sieciowych
- `ARP` - protokół ARP (wykrywanie hostów)
- `Ether` - warstwa Ethernet
- `srp` - send/receive packets (wysyłanie i odbieranie pakietów)

#### Klasa WiFiScanner - Konstruktor

```python
    def __init__(self, max_ips_to_scan: int = 50, ping_timeout: float = 0.5, port_timeout: float = 0.2):
```

**Wyjaśnienie:**
- `max_ips_to_scan=50` - maksymalna liczba IP do skanowania (zamiast wszystkich 254)
- **Dlaczego?** Skanowanie wszystkich 254 adresów jest wolne - skanujemy tylko pierwsze 50
- `ping_timeout=0.5` - timeout dla ping (0.5 sekundy)
- `port_timeout=0.2` - timeout dla skanowania portów (0.2 sekundy)

```python
        if RUST_SCANNER_AVAILABLE and FastPortScanner:
            self.rust_scanner = FastPortScanner(
                timeout_ms=int(port_timeout * 1000),
                max_concurrent=50
            )
```

**Wyjaśnienie:**
- `FastPortScanner` - szybki skaner portów napisany w **Rust**
- `timeout_ms=int(port_timeout * 1000)` - konwertuje sekundy na milisekundy
- `max_concurrent=50` - maksymalnie 50 równoległych skanowań
- **Dlaczego Rust?** Rust jest **znacznie szybszy** niż Python dla operacji sieciowych

#### Metoda: scan_wifi_devices()

```python
    def scan_wifi_devices(self, network_range: Optional[str] = None) -> List[Device]:
```

**Wyjaśnienie:**
- Główna metoda skanowania WiFi
- `network_range` - zakres sieci (np. "192.168.1.0/24")
- Jeśli `None`, automatycznie wykrywa sieć lokalną

```python
        if network_range is None:
            network_range = self._detect_local_network()
```

**Wyjaśnienie:**
- Automatycznie wykrywa sieć lokalną
- **Jak?** Łączy się z zewnętrznym serwerem (8.8.8.8) i sprawdza lokalny IP

#### Metoda: _detect_local_network()

```python
    def _detect_local_network(self) -> Optional[str]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
```

**Wyjaśnienie:**
- `socket.socket(...)` - tworzy gniazdo sieciowe
- `socket.AF_INET` - IPv4
- `socket.SOCK_DGRAM` - UDP (nie TCP)
- `s.connect(("8.8.8.8", 80))` - **próbuje** połączyć się (nie faktycznie łączy)
- **Dlaczego?** System operacyjny automatycznie wybiera lokalny interfejs sieciowy
- `s.getsockname()[0]` - pobiera **lokalny IP** (np. "192.168.1.100")
- `s.close()` - zamyka gniazdo

```python
            ip_parts = local_ip.split('.')
            network_base = '.'.join(ip_parts[:3])
            return f"{network_base}.0/24"
```

**Wyjaśnienie:**
- `local_ip.split('.')` - dzieli IP na części: `["192", "168", "1", "100"]`
- `ip_parts[:3]` - **slice** (wycina pierwsze 3 elementy): `["192", "168", "1"]`
- `'.'.join(...)` - łączy elementy kropką: `"192.168.1"`
- `f"{network_base}.0/24"` - tworzy zakres sieci: `"192.168.1.0/24"`
- **`/24`** oznacza maskę podsieci (255.255.255.0 = 254 możliwe adresy)

#### Metoda: _scan_with_scapy() - Skanowanie z Scapy

```python
    def _scan_with_scapy(self, network_range: str) -> List[Device]:
        try:
            conf.verb = 0  # Wyłącz verbose mode
```

**Wyjaśnienie:**
- `conf.verb = 0` - wyłącza szczegółowe komunikaty scapy (mniej outputu)

```python
            # Krok 1: ARP scan (wymaga root)
            arp_request = ARP(pdst=network_range)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request
```

**Wyjaśnienie:**
- `ARP(pdst=network_range)` - tworzy pakiet ARP dla całej sieci
- `Ether(dst="ff:ff:ff:ff:ff:ff")` - broadcast (wysyła do wszystkich)
- `broadcast / arp_request` - **łączy** pakiety (warstwa Ethernet + ARP)
- **ARP** - protokół do wykrywania MAC adresów po IP

```python
            answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]
```

**Wyjaśnienie:**
- `srp` - send/receive packets (wysyła i odbiera pakiety)
- `timeout=2` - czeka maksymalnie 2 sekundy na odpowiedzi
- `[0]` - pobiera **pierwszy element** (odpowiedzi, nie błędów)
- **Zwraca:** listę par `(wysłany_pakiet, odebrana_odpowiedź)`

```python
            for element in answered_list:
                host_info = {
                    'ip': element[1].psrc,  # IP address
                    'mac': element[1].hwsrc  # MAC address
                }
                active_hosts.append(host_info)
```

**Wyjaśnienie:**
- `element[1]` - odpowiedź (drugi element pary)
- `.psrc` - Protocol Source (IP źródła)
- `.hwsrc` - Hardware Source (MAC źródła)
- **Tworzy słownik** z IP i MAC każdego aktywnego hosta

#### Ping Scan (Bez Uprawnień Root)

```python
        except PermissionError:
            # Brak uprawnień - użyj ping scan
            priority_ips = [1, 254]  # Routery
            common_ips = list(range(2, min(21, self.max_ips_to_scan + 1)))
```

**Wyjaśnienie:**
- `except PermissionError:` - jeśli brak uprawnień root
- `priority_ips = [1, 254]` - priorytetowe IP (routery często mają .1 lub .254)
- `list(range(2, 21))` - tworzy listę `[2, 3, 4, ..., 20]`
- `min(21, self.max_ips_to_scan + 1)` - używa mniejszej wartości (ogranicza do max_ips_to_scan)

```python
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            def ping_host(ip: str) -> tuple:
                try:
                    result = subprocess.run(
                        ['ping', '-c', '1', '-W', str(int(self.ping_timeout * 1000)), ip],
                        timeout=self.ping_timeout + 0.5,
                        capture_output=True
                    )
                    return (ip, result.returncode == 0)
                except:
                    return (ip, False)
```

**Wyjaśnienie:**
- `concurrent.futures` - moduł do **równoległego** wykonywania
- `ThreadPoolExecutor` - wykonuje funkcje w **osobnych wątkach** (równolegle)
- `def ping_host(ip: str):` - funkcja pingująca jeden IP
- `subprocess.run(['ping', ...])` - uruchamia program `ping`
- `-c 1` - tylko 1 pakiet ping
- `-W` - timeout w milisekundach
- `result.returncode == 0` - ping zwraca 0 jeśli sukces
- **Zwraca:** `(ip, True/False)` - czy host odpowiada

```python
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = {executor.submit(ping_host, f"{network_base}.{ip}"): ip 
                          for ip in ips_to_scan}
```

**Wyjaśnienie:**
- `ThreadPoolExecutor(max_workers=20)` - maksymalnie 20 wątków jednocześnie
- `executor.submit(ping_host, ip)` - **dodaje zadanie** do wykonania (asynchronicznie)
- `{executor.submit(...): ip for ip in ips_to_scan}` - **dict comprehension**
- **Tworzy słownik:** `{future: ip}` - przyszły wynik → IP

```python
                for future in as_completed(futures):
                    ip, is_alive = future.result()
                    if is_alive:
                        active_hosts.append({'ip': ip, 'mac': None})
```

**Wyjaśnienie:**
- `as_completed(futures)` - iteruje przez zakończone zadania (gdy są gotowe)
- `future.result()` - **pobiera wynik** zadania (czeka jeśli jeszcze nie gotowe)
- `if is_alive:` - jeśli host odpowiada na ping
- **Dlaczego równolegle?** Pingowanie 50 hostów sekwencyjnie = 25 sekund, równolegle = ~2 sekundy!

#### Skanowanie Portów

```python
            # Skanuj porty dla każdego aktywnego hosta
            if self.rust_scanner:
                open_ports = self.rust_scanner.scan_ports(ip, common_ports)
```

**Wyjaśnienie:**
- Używa **Rust scanner** jeśli dostępny (znacznie szybszy!)
- `common_ports` - lista popularnych portów (80, 443, 22, 3389, ...)

```python
            else:
                # Fallback: Python socket scan
                for port in common_ports:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(self.port_timeout)
                    result = sock.connect_ex((ip, port))
                    sock.close()
                    if result == 0:
                        open_ports.append(port)
```

**Wyjaśnienie:**
- **Fallback** - jeśli Rust scanner nie jest dostępny
- `socket.SOCK_STREAM` - TCP (nie UDP)
- `sock.connect_ex((ip, port))` - próbuje połączyć się (nie rzuca błędu)
- `result == 0` - sukces (port otwarty)
- **Dlaczego Rust?** Skanowanie portów w Python jest **wolne** - Rust jest 10-100x szybszy

#### Analiza Urządzenia WiFi

```python
    def _analyze_wifi_device(self, ip: str, mac: Optional[str], open_ports: List[int]) -> Optional[Device]:
```

**Wyjaśnienie:**
- Analizuje urządzenie WiFi na podstawie IP, MAC i otwartych portów
- Tworzy obiekt `Device`

```python
        # Wykryj typ urządzenia
        device_type = self._detect_device_type(open_ports, hostname, mac)
```

**Wyjaśnienie:**
- Wykrywa typ na podstawie portów
- **Przykład:** Port 104 (DICOM) = urządzenie medyczne

```python
        # Sprawdź szyfrowanie
        has_encryption = False
        if 443 in open_ports or 8443 in open_ports:
            has_encryption = True  # Ma HTTPS
        elif 80 in open_ports or 8080 in open_ports:
            has_encryption = False  # Tylko HTTP (niezaszyfrowane)
```

**Wyjaśnienie:**
- Port 443/8443 = HTTPS (szyfrowane) ✅
- Port 80/8080 = HTTP (niezaszyfrowane) ❌

```python
        # Dodaj podatności dla portów
        if 23 in open_ports:  # Telnet
            device.add_vulnerability("Telnet bez szyfrowania - wszystkie dane przesyłane jawnie")
```

**Wyjaśnienie:**
- Port 23 = Telnet (bardzo niebezpieczny - wszystko w plaintext)
- Automatycznie dodaje podatność

### 🔗 Kiedy jest używany?
- Gdy uruchamiasz `scanner.py --wifi`
- Automatycznie przez `scanner.py` (jeśli WiFi jest włączony)

---

## Plik 5: `usb_scanner.py` - Skaner USB

### 📍 Lokalizacja: `src/usb_scanner.py`

### 🎯 Cel
Wykrywa urządzenia **USB** podłączone do komputera.

### 📝 Kod z Wyjaśnieniami

#### Metoda: scan_usb_devices()

```python
    def scan_usb_devices(self) -> List[Device]:
        devices: List[Device] = []
        
        if PYUSB_AVAILABLE:
            usb_devices = self._scan_pyusb()
            devices.extend(usb_devices)
```

**Wyjaśnienie:**
- `devices.extend(usb_devices)` - **rozszerza** listę (dodaje wszystkie elementy)
- **Różnica:**
  ```python
  devices.append(usb_devices)  # Dodaje listę jako jeden element: [[dev1, dev2]]
  devices.extend(usb_devices)  # Dodaje elementy: [dev1, dev2]
  ```

#### Metoda: _scan_serial() - Porty Szeregowe

```python
    def _scan_serial(self) -> List[Device]:
        ports = serial.tools.list_ports.comports()
```

**Wyjaśnienie:**
- `comports()` - zwraca listę wszystkich dostępnych portów szeregowych
- **Przykład:** `/dev/ttyUSB0`, `COM3`, `/dev/ttyACM0`

```python
        for port in ports:
            is_medical = self._is_medical_device(port)
            is_microcontroller = self._is_microcontroller(port)
```

**Wyjaśnienie:**
- Sprawdza czy port może być urządzeniem medycznym lub mikrokontrolerem

#### Metoda: _auto_detect_and_monitor() - Automatyczne Wykrywanie

```python
    def _auto_detect_and_monitor(self, port_name: str, timeout: float = 3.0) -> tuple:
        for baudrate in self.common_baudrates:
            try:
                ser = serial.Serial(
                    port=port_name,
                    baudrate=baudrate,
                    timeout=0.5
                )
```

**Wyjaśnienie:**
- Próbuje różne prędkości (9600, 19200, 115200, ...)
- `serial.Serial(...)` - otwiera port szeregowy
- **Baudrate** - prędkość transmisji (bitów na sekundę)

```python
                while time.time() - start_time < timeout:
                    if ser.in_waiting > 0:
                        line = ser.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            temp_messages.append(line)
```

**Wyjaśnienie:**
- `ser.in_waiting` - ile bajtów czeka w buforze
- `ser.readline()` - czyta linię (do znaku nowej linii)
- `.decode('utf-8', errors='ignore')` - konwertuje bajty na string (ignoruje błędy)
- `.strip()` - usuwa białe znaki

```python
                # Jeśli nie ma komunikatów, spróbuj wysłać komendy testowe
                if not temp_messages:
                    test_commands = ["AT\r\n", "HELLO\r\n", "?\r\n"]
                    for cmd in test_commands:
                        ser.write(cmd.encode('utf-8'))
                        ser.flush()
```

**Wyjaśnienie:**
- Jeśli mikrokontroler nie wysyła danych, **wysyłamy** komendy testowe
- `ser.write(...)` - wysyła dane
- `.encode('utf-8')` - konwertuje string na bajty
- `ser.flush()` - **wymusza** wysłanie (nie czeka na bufor)

### 🔗 Kiedy jest używany?
- Gdy uruchamiasz `scanner.py --usb`
- Automatycznie wykrywa mikrokontrolery i porty szeregowe

---

## Plik 6: `nfc_scanner.py` - Skaner NFC

### 📍 Lokalizacja: `src/nfc_scanner.py`

### 🎯 Cel
Wykrywa urządzenia **NFC** (karty, tagi).

### 📝 Kod z Wyjaśnieniami

#### Metoda: scan_nfc_devices()

```python
    def scan_nfc_devices(self, duration: int = 5) -> List[Device]:
        if NFC_AVAILABLE:
            nfc_devices = self._scan_nfcpy(duration)
            devices.extend(nfc_devices)
```

**Wyjaśnienie:**
- Skanuje przez określony czas (domyślnie 5 sekund)
- Czeka na zbliżenie karty/tagu do czytnika

#### Metoda: _scan_nfcpy()

```python
        clf = nfc.ContactlessFrontend('usb')
```

**Wyjaśnienie:**
- `ContactlessFrontend` - interfejs do czytnika NFC
- `'usb'` - czytnik podłączony przez USB

```python
            while time.time() - start_time < duration:
                tag = clf.connect(rdwr={'on-connect': self._on_nfc_connect})
                if tag:
                    device = self._analyze_nfc_tag(tag)
                    break
```

**Wyjaśnienie:**
- `clf.connect(...)` - próbuje odczytać tag/kartę
- `rdwr={'on-connect': ...}` - callback gdy wykryto tag
- Jeśli wykryto tag → analizuj i zakończ skanowanie

### 🔗 Kiedy jest używany?
- Gdy uruchamiasz `scanner.py --nfc`
- Wymaga czytnika NFC (np. ACR122U)

---

## 📝 Podsumowanie Części 2

### Co nauczyłeś się:
1. ✅ Jak działają skanery (BLE, WiFi, USB, NFC)
2. ✅ Koncepty: async/await, callbacks, threading
3. ✅ Jak wykrywają urządzenia
4. ✅ Jak analizują bezpieczeństwo
5. ✅ Jak tworzą obiekty Device

### Kluczowe Koncepty:

**Async/Await:**
```python
async def funkcja():
    await inna_funkcja()  # Czeka na zakończenie
```

**Callbacks:**
```python
def callback(data):
    # Wywoływana automatycznie
    print(data)

scanner.start(callback=callback)  # Przekazujemy funkcję
```

**Threading:**
```python
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(funkcja, arg) for arg in args]
    # Wykonuje równolegle!
```

---

**Kontynuacja w: PRZEWODNIK_PYTHON_CZESC_3.md** (Analiza i Bezpieczeństwo)
