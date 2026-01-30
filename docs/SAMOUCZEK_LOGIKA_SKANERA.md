# 📚 Samouczek - Logika Skanera Urządzeń Medycznych

## 🎯 Cel Dokumentu

Ten dokument wyjaśnia **wszystko** o projekcie:
- ✅ Podstawy Pythona (klasy, funkcje, importy)
- ✅ Architekturę projektu
- ✅ Za co odpowiada każda klasa i funkcja
- ✅ Wszystkie zależności między modułami
- ✅ Dlaczego kod jest napisany tak a nie inaczej
- ✅ Logikę działania całego systemu

**To nie jest plik do uruchomienia - to dokumentacja do czytania podczas pracy z kodem!**

---

# 📖 CZĘŚĆ 1: PODSTAWY PYTHONA

## 1.1. Importy i Moduły

### Co to jest import?

```python
from device import Device, DeviceType
```

**Wyjaśnienie:**
- `from device` - importuje z pliku `device.py`
- `import Device` - importuje klasę `Device`
- `import DeviceType` - importuje enum `DeviceType`

**Dlaczego tak?**
- **Modularność:** Każdy plik ma jedną odpowiedzialność
- **Czytelność:** Widać skąd pochodzi klasa
- **Unikanie konfliktów:** Jeśli dwie klasy mają tę samą nazwę, można użyć `from X import Y as Z`

### Try/Except dla Opcjonalnych Bibliotek

```python
try:
    from bleak import BleakScanner
    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False
    BleakScanner = None
```

**Wyjaśnienie:**
- `try/except` - próbuje zaimportować, jeśli się nie uda, obsługuje błąd
- `BLEAK_AVAILABLE` - flaga mówiąca czy biblioteka jest dostępna
- `BleakScanner = None` - ustawia na None, żeby kod nie crashował

**Dlaczego tak?**
- **Graceful degradation:** Jeśli biblioteka nie jest zainstalowana, program nadal działa (bez tej funkcjonalności)
- **Elastyczność:** Można uruchomić skaner bez wszystkich bibliotek (np. tylko BLE, bez WiFi)

---

## 1.2. Klasy i Obiekty

### Co to jest klasa?

```python
class Device:
    def __init__(self, mac_address: str, name: str):
        self.mac_address = mac_address
        self.name = name
```

**Wyjaśnienie:**
- `class Device:` - definicja klasy (szablon obiektu)
- `def __init__` - konstruktor (tworzy obiekt)
- `self.mac_address` - atrybut obiektu (dane przechowywane w obiekcie)

**Dlaczego klasy?**
- **Enkapsulacja:** Wszystkie dane urządzenia w jednym miejscu
- **Metody:** Funkcje działające na danych urządzenia (np. `calculate_security_score()`)
- **Reużywalność:** Można stworzyć wiele urządzeń z tego samego szablonu

### Dataclass - Uproszczona Klasa

```python
@dataclass
class Device:
    mac_address: str
    name: str
    security_score: int = 0
```

**Wyjaśnienie:**
- `@dataclass` - dekorator automatycznie tworzy `__init__`, `__repr__`, `__eq__`
- `mac_address: str` - atrybut z typem (type hint)
- `security_score: int = 0` - atrybut z wartością domyślną

**Dlaczego dataclass?**
- **Mniej kodu:** Nie trzeba pisać `__init__` ręcznie
- **Czytelność:** Widać wszystkie atrybuty na początku klasy
- **Type hints:** Python wie jakie typy są oczekiwane

---

## 1.3. Enum - Wyliczenia (SZCZEGÓŁOWE WYJAŚNIENIE)

### 📖 Podstawy

**Enum = Enumeration (Wyliczenie)** - to lista **stałych wartości**, które mogą być użyte w kodzie.

---

### 🔍 Jak działa import Enum?

```python
from enum import Enum
```

**Wyjaśnienie krok po kroku:**

1. **`from enum`** - mówi Pythonowi: "weź moduł o nazwie `enum`"
   - `enum` to **wbudowany moduł Pythona** (nie trzeba instalować!)
   - Jest w standardowej bibliotece Pythona

2. **`import Enum`** - mówi Pythonowi: "zaimportuj klasę `Enum` z tego modułu"
   - `Enum` to **klasa bazowa** do tworzenia wyliczeń

3. **Razem:** `from enum import Enum` = "zaimportuj klasę Enum z modułu enum"

---

### 📝 Przykład z Projektu

#### Definicja Enum:

```python
# W pliku device.py
from enum import Enum  # ← Import klasy Enum

class Protocol(Enum):  # ← Protocol dziedziczy po Enum
    """Protokoły komunikacji"""
    BLE = "BLE"        # ← Wartość 1
    WIFI = "WiFi"      # ← Wartość 2
    USB = "USB"        # ← Wartość 3
    NFC = "NFC"        # ← Wartość 4
```

**Co się dzieje:**
- `class Protocol(Enum):` - tworzy nowe wyliczenie o nazwie `Protocol`
- `BLE = "BLE"` - definiuje wartość `BLE` z wartością string `"BLE"`
- Teraz możesz użyć `Protocol.BLE` w kodzie!

---

### 🎯 Jak Używać Enum?

#### 1. Przypisanie wartości do zmiennej:

```python
# ✅ DOBRZE - używamy Enum
device.protocol = Protocol.BLE

# ❌ ŹLE - używamy stringa
device.protocol = "BLE"  # Działa, ale niebezpieczne!
```

#### 2. Porównywanie:

```python
# ✅ DOBRZE
if device.protocol == Protocol.BLE:
    print("To jest Bluetooth")

# ❌ ŹLE (ale działa)
if device.protocol == "BLE":
    print("To jest Bluetooth")
```

#### 3. Pobieranie wartości (string):

```python
# Enum → String
protocol_string = Protocol.BLE.value  # Zwraca: "BLE"
print(protocol_string)  # Wypisze: BLE

# String → Enum (jeśli potrzebujesz)
protocol_enum = Protocol("BLE")  # Zwraca: Protocol.BLE
```

---

### 🔄 Różnica: Enum vs String

#### ❌ BEZ Enum (używając stringów):

```python
device.protocol = "BLE"   # OK
device.protocol = "BLUE"  # ❌ BŁĄD! Ale Python tego nie wykryje!
device.protocol = "ble"   # ❌ BŁĄD! Małe litery!
device.protocol = "WiFi"  # OK
device.protocol = "wifi"  # ❌ BŁĄD! Małe litery!

# Problem: Można użyć DOWOLNEGO stringa, nawet błędnego!
# Python nie sprawdza czy wartość jest poprawna!
```

**Przykład błędu:**
```python
# Literówka w kodzie:
if device.protocol == "WIFI":  # ← Powinno być "WiFi"!
    print("WiFi")
# Warunek NIGDY nie jest spełniony, bo "WIFI" != "WiFi"
# Błąd jest trudny do znalezienia!
```

#### ✅ Z Enum (bezpieczne):

```python
device.protocol = Protocol.BLE   # ✅ OK
device.protocol = Protocol.BLUE  # ❌ BŁĄD! Python od razu pokaże błąd!
device.protocol = Protocol.ble    # ❌ BŁĄD! Małe litery nie istnieją!
device.protocol = Protocol.WIFI   # ✅ OK

# Python SPRAWDZA czy wartość istnieje w Enum!
# Jeśli nie istnieje → błąd od razu!
```

**Przykład bezpieczeństwa:**
```python
# Literówka w kodzie:
if device.protocol == Protocol.WIFI:  # ← Jeśli zrobisz literówkę, Python pokaże błąd!
    print("WiFi")
# IDE i Python od razu pokażą błąd jeśli Protocol.WIFI nie istnieje!
```

---

### 📊 Porównanie: String vs Enum

| Aspekt | String | Enum |
|--------|--------|------|
| **Bezpieczeństwo** | ❌ Można użyć dowolnego stringa | ✅ Tylko wartości z listy |
| **Błędy** | ❌ Błąd wykryty dopiero w runtime | ✅ Błąd wykryty od razu (IDE) |
| **Autouzupełnianie** | ❌ IDE nie podpowiada | ✅ IDE podpowiada dostępne wartości |
| **Czytelność** | ⚠️ `"BLE"` | ✅ `Protocol.BLE` (widać skąd pochodzi) |
| **Refaktoryzacja** | ❌ Trzeba zmieniać wszędzie | ✅ Zmiana w jednym miejscu |

---

### 💡 Przykłady z Projektu

#### Przykład 1: Definicja DeviceType

```python
from enum import Enum

class DeviceType(Enum):
    """Typy urządzeń medycznych"""
    GLUCOSE_METER = "glucose_meter"      # Glukometr
    INSULIN_PUMP = "insulin_pump"        # Pompa insulinowa
    BLOOD_PRESSURE = "blood_pressure"    # Ciśnieniomierz
    PULSE_OXIMETER = "pulse_oximeter"    # Pulsoksymetr
    UNKNOWN = "unknown"                  # Nieznany typ
```

#### Przykład 2: Użycie w kodzie

```python
# Tworzenie urządzenia
device = Device(
    mac_address="AA:BB:CC:DD:EE:FF",
    name="GlucoSmart",
    device_type=DeviceType.GLUCOSE_METER,  # ← Enum
    protocol=Protocol.BLE,                 # ← Enum
    has_encryption=True
)

# Sprawdzanie typu
if device.device_type == DeviceType.GLUCOSE_METER:
    print("To jest glukometr")

# Sprawdzanie protokołu
if device.protocol == Protocol.BLE:
    print("Komunikacja przez Bluetooth")
```

#### Przykład 3: Konwersja do JSON

```python
# Enum nie może być bezpośrednio w JSON
# Trzeba użyć .value aby dostać string

device_dict = {
    "name": device.name,
    "protocol": device.protocol.value,      # "BLE" (string)
    "device_type": device.device_type.value  # "glucose_meter" (string)
}

# JSON:
# {
#   "name": "GlucoSmart",
#   "protocol": "BLE",
#   "device_type": "glucose_meter"
# }
```

---

### 🧠 Co się dzieje pod spodem?

#### Kiedy piszesz:

```python
class Protocol(Enum):
    BLE = "BLE"
    WIFI = "WiFi"
```

#### Python tworzy:

```python
# Obiekty Enum:
Protocol.BLE   # To jest obiekt typu Protocol
Protocol.WIFI  # To jest obiekt typu Protocol

# Wartości (stringi):
Protocol.BLE.value   # "BLE" (string)
Protocol.WIFI.value  # "WiFi" (string)

# Porównywanie:
Protocol.BLE == Protocol.BLE   # True
Protocol.BLE == Protocol.WIFI  # False
Protocol.BLE == "BLE"          # False (różne typy!)
Protocol.BLE.value == "BLE"     # True (porównywanie wartości)
```

---

### 🎓 Ćwiczenia - Spróbuj Sam!

#### Ćwiczenie 1: Stwórz własny Enum

```python
from enum import Enum

class Kolor(Enum):
    CZERWONY = "czerwony"
    ZIELONY = "zielony"
    NIEBIESKI = "niebieski"

# Użyj:
moj_kolor = Kolor.CZERWONY
print(moj_kolor.value)  # Wypisze: "czerwony"
```

#### Ćwiczenie 2: Porównaj Enum

```python
kolor1 = Kolor.CZERWONY
kolor2 = Kolor.CZERWONY
kolor3 = Kolor.ZIELONY

print(kolor1 == kolor2)  # True (ten sam Enum)
print(kolor1 == kolor3)  # False (różne Enum)
print(kolor1 == "czerwony")  # False (różne typy!)
print(kolor1.value == "czerwony")  # True (porównywanie wartości)
```

---

### ✅ Podsumowanie

1. **`from enum import Enum`** - importuje klasę Enum z modułu enum
2. **`class Protocol(Enum):`** - tworzy wyliczenie (lista dozwolonych wartości)
3. **`Protocol.BLE`** - użycie wartości z wyliczenia
4. **`.value`** - pobiera wartość (string) z Enum
5. **Enum jest bezpieczniejszy** niż stringi (Python sprawdza poprawność)

#### Główne zalety Enum:

✅ **Bezpieczeństwo** - nie można użyć nieprawidłowej wartości  
✅ **Autouzupełnianie** - IDE podpowiada dostępne wartości  
✅ **Czytelność** - `Protocol.BLE` jest bardziej czytelne niż `"BLE"`  
✅ **Refaktoryzacja** - zmiana nazwy w jednym miejscu  

---

### 🚀 Teraz Rozumiesz Enum!

**Enum to po prostu bezpieczny sposób na używanie stałych wartości w kodzie!**

Zamiast:
```python
device.protocol = "BLE"  # ❌ Można zrobić błąd!
```

Używamy:
```python
device.protocol = Protocol.BLE  # ✅ Python sprawdza poprawność!
```

---

## 1.4. Funkcje i Metody

### Różnica między funkcją a metodą

```python
# Funkcja (niezależna)
def make_json_serializable(obj):
    return obj

# Metoda (należąca do klasy)
class Device:
    def calculate_security_score(self):
        return self.security_score
```

**Wyjaśnienie:**
- **Funkcja:** Działa niezależnie, nie potrzebuje obiektu
- **Metoda:** Działa na obiekcie, pierwszy parametr to `self` (odniesienie do obiektu)

**Dlaczego metody?**
- **Organizacja:** Metody związane z danymi są w klasie z danymi
- **Enkapsulacja:** Logika jest blisko danych

---

## 1.5. Type Hints (Typy)

```python
def scan_all(self) -> List[Device]:
    return []
```

**Wyjaśnienie:**
- `-> List[Device]` - funkcja zwraca listę obiektów `Device`
- `List[Device]` - import z `typing`: `from typing import List`

**Dlaczego type hints?**
- **Czytelność:** Widać co funkcja zwraca bez czytania kodu
- **IDE support:** Autouzupełnianie i sprawdzanie błędów
- **Dokumentacja:** Służy jako dokumentacja

---

## 1.6. Async/Await (Asynchroniczność)

```python
async def scan_ble_devices(self, duration: int = 10) -> List[Device]:
    devices = await BleakScanner.discover()
    return devices
```

**Wyjaśnienie:**
- `async def` - funkcja asynchroniczna (nie blokuje wykonania)
- `await` - czeka na zakończenie operacji asynchronicznej
- `asyncio.run()` - uruchamia funkcję async w kodzie synchronicznym

**Dlaczego async?**
- **Wydajność:** Można skanować wiele urządzeń jednocześnie
- **Nieblokujące:** Program nie czeka na jedno urządzenie, skanuje inne
- **BLE wymaga async:** Biblioteka `bleak` używa async

**Konwersja async → sync:**
```python
def _scan_ble_async(self, duration: int = 10) -> List[Device]:
    # Windows wymaga nowego event loop
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Uruchom funkcję async w kodzie synchronicznym
    return asyncio.run(self.scanners['ble'].scan_ble_devices(duration))
```

**Dlaczego wrapper?**
- Główny kod (`scanner.py`) jest synchroniczny
- BLE scanner jest asynchroniczny (wymaga `bleak`)
- Wrapper konwertuje async na sync

---

# 📁 CZĘŚĆ 2: ARCHITEKTURA PROJEKTU

## 2.1. Struktura Hierarchiczna

```
scanner.py (GŁÓWNY ORCHESTRATOR)
    ↓
    ├─→ real_scanner.py (BLE Scanner)
    ├─→ wifi_scanner.py (WiFi Scanner)
    ├─→ usb_scanner.py (USB Scanner)
    ├─→ nfc_scanner.py (NFC Scanner)
    ↓
device.py (MODEL DANYCH - używany przez wszystkie)
    ↓
    ├─→ encryption_analyzer.py (Analiza szyfrowania)
    ├─→ vulnerability_tester.py (Testy podatności)
    │   └─→ cve_lookup.py (Pobieranie CVE)
    ├─→ external_apis.py (VirusTotal, Shodan)
    ├─→ anomaly_detector.py (Machine Learning)
    ├─→ oui_lookup.py (Identyfikacja producenta)
    └─→ rust_scanner_wrapper.py
        └─→ lib.rs (Rust - szybkie skanowanie)
```

**Dlaczego taka struktura?**
- **Separation of Concerns:** Każdy moduł ma jedną odpowiedzialność
- **Reużywalność:** `Device` jest używany przez wszystkie moduły
- **Testowalność:** Każdy moduł można testować osobno
- **Czytelność:** Łatwo znaleźć kod odpowiedzialny za daną funkcjonalność

---

## 2.2. Przepływ Danych

### 1. Inicjalizacja (`__init__`)

```python
scanner = MedicalDeviceScanner(protocols=['ble', 'wifi'])
```

**Co się dzieje:**
1. Tworzy słownik `self.scanners = {}`
2. Dla każdego protokołu próbuje zaimportować odpowiedni skaner
3. Jeśli import się powiedzie → dodaje do `self.scanners`
4. Jeśli import się nie powiedzie → wyświetla warning, ale kontynuuje

**Dlaczego try/except przy importach?**
- Nie wszystkie biblioteki mogą być zainstalowane
- Program powinien działać nawet bez niektórych funkcjonalności
- Użytkownik może uruchomić tylko BLE (bez WiFi)

### 2. Skanowanie (`scan_all()`)

```python
devices = scanner.scan_all()
```

**Co się dzieje:**
1. Dla każdego protokołu w `self.scanners`:
   - Wywołuje odpowiednią metodę skanowania
   - Zbiera urządzenia do listy `all_devices`
2. Zapisuje wszystkie urządzenia w `self.devices`

**Dlaczego osobne metody dla każdego protokołu?**
- Każdy protokół ma inne API (BLE używa async, WiFi używa nmap)
- Łatwiej debugować (widać który protokół ma problem)
- Można skanować tylko wybrane protokoły

### 3. Analiza Bezpieczeństwa (`analyze_security()`)

```python
scanner.analyze_security(run_vulnerability_tests=True)
```

**Co się dzieje:**
1. Dla każdego urządzenia:
   - Oblicza `security_score` (`device.calculate_security_score()`)
   - Sprawdza zgodność z FDA (`_check_fda_compliance()`)
   - Wzbogaca danymi z API (`_enrich_device_with_external_apis()`)
   - Analizuje szyfrowanie (`_analyze_encryption()`)
   - (Opcjonalnie) Testuje podatności (`_run_vulnerability_tests()`)
2. Wykrywa anomalie ML (`_detect_anomalies()`)

**Dlaczego w pętli dla każdego urządzenia?**
- Każde urządzenie ma inne właściwości
- Analiza jest specyficzna dla urządzenia
- Można przerwać dla jednego urządzenia bez wpływu na inne

### 4. Wyświetlanie (`display_results()`)

```python
scanner.display_results()
```

**Co się dzieje:**
1. Grupuje urządzenia według ryzyka (high/medium/low)
2. Dla każdej grupy wyświetla karty urządzeń
3. Wyświetla analizę szyfrowania

**Dlaczego grupowanie?**
- **Czytelność:** Wysokie ryzyko na górze (najważniejsze)
- **Priorytetyzacja:** Łatwo zobaczyć które urządzenia wymagają uwagi

---

# 🔍 CZĘŚĆ 3: SZCZEGÓŁOWA ANALIZA PLIKÓW

## 3.1. `device.py` - Model Danych

### Klasa `Device`

```python
@dataclass
class Device:
    mac_address: str
    name: str
    device_type: DeviceType
    protocol: Protocol
    has_encryption: bool = False
    security_score: int = 0
    vulnerabilities: List[str] = field(default_factory=list)
```

**Co przechowuje:**
- **Podstawowe dane:** MAC, nazwa, typ, protokół
- **Bezpieczeństwo:** szyfrowanie, security score, podatności
- **Metadane:** producent, model, firmware, timestamps

**Dlaczego dataclass?**
- Automatycznie generuje `__init__`, `__repr__`, `__eq__`
- Mniej kodu do napisania
- Czytelna definicja struktury

### Metoda `calculate_security_score()`

```python
def calculate_security_score(self) -> int:
    score = 100  # Start od maksimum
    
    if not self.has_encryption:
        score -= 30  # -30 za brak szyfrowania
    
    if not self.requires_pairing:
        score -= 20  # -20 za brak parowania
    
    score -= len(self.vulnerabilities) * 25  # -25 za każdą podatność
    
    self.security_score = max(0, min(100, score))  # Ogranicz do 0-100
    return self.security_score
```

**Logika:**
- Start: 100 punktów (idealne bezpieczeństwo)
- Odejmowanie za każdą podatność
- Wynik w zakresie 0-100

**Dlaczego takie wartości (-30, -20, -25)?**
- **Brak szyfrowania (-30):** Najpoważniejsza podatność - dane mogą być przechwycone
- **Brak parowania (-20):** Średnia podatność - każdy może się połączyć
- **Podatności (-25):** Każda dodatkowa podatność zmniejsza bezpieczeństwo

**Dlaczego `max(0, min(100, score))`?**
- `max(0, ...)` - wynik nie może być ujemny
- `min(100, ...)` - wynik nie może przekroczyć 100
- Zapewnia poprawny zakres

### Metoda `to_dict()`

```python
def to_dict(self) -> dict:
    return {
        "mac_address": self.mac_address,
        "name": self.name,
        "security_score": int(self.security_score),
        ...
    }
```

**Dlaczego potrzebna?**
- JSON nie może serializować obiektów Python
- API i raporty potrzebują słowników
- Konwersja obiektu → słownik → JSON

**Dlaczego `int(self.security_score)`?**
- `security_score` może być `numpy.int64` (z ML)
- JSON wymaga natywnych typów Pythona
- `int()` konwertuje na natywny typ

---

## 3.2. `scanner.py` - Główny Orchestrator

### Klasa `MedicalDeviceScanner`

**Odpowiedzialność:**
- Zarządza wszystkimi skanerami
- Koordynuje skanowanie
- Analizuje bezpieczeństwo
- Wyświetla wyniki

### Metoda `__init__()`

```python
def __init__(self, protocols: List[str] = None):
    self.scanners = {}  # Słownik: 'ble' → RealBLEScanner()
    
    if protocols is None:
        protocols = ['ble', 'wifi', 'usb', 'nfc']
    
    if 'ble' in protocols:
        if BLE_SCANNER_AVAILABLE:
            self.scanners['ble'] = RealBLEScanner()
```

**Dlaczego słownik `self.scanners`?**
- **Dynamiczny dostęp:** `self.scanners['ble']` zamiast `self.ble_scanner`
- **Iteracja:** Można przejść przez wszystkie: `for protocol, scanner in self.scanners.items()`
- **Elastyczność:** Łatwo dodać nowy protokół

**Dlaczego sprawdzanie `BLE_SCANNER_AVAILABLE`?**
- Biblioteka `bleak` może nie być zainstalowana
- Program nie powinien crashować, tylko wyświetlić warning
- Użytkownik może uruchomić bez niektórych funkcjonalności

### Metoda `scan_all()`

```python
def scan_all(self) -> List[Device]:
    all_devices = []
    
    if 'ble' in self.scanners:
        ble_devices = self._scan_ble_async(duration=10)
        all_devices.extend(ble_devices)
    
    if 'wifi' in self.scanners:
        wifi_devices = self.scanners['wifi'].scan_wifi_devices()
        all_devices.extend(wifi_devices)
    
    self.devices = all_devices
    return all_devices
```

**Dlaczego osobne wywołania dla każdego protokołu?**
- Każdy protokół ma inne API
- BLE wymaga async wrappera
- WiFi, USB, NFC są synchroniczne
- Łatwiej debugować (widać który protokół ma problem)

**Dlaczego `extend()` zamiast `append()`?**
- `scan_wifi_devices()` zwraca `List[Device]`
- `extend()` dodaje wszystkie elementy z listy
- `append()` dodałby całą listę jako jeden element

### Metoda `analyze_security()`

```python
def analyze_security(self, run_vulnerability_tests: bool = False):
    for device in self.devices:
        device.calculate_security_score()
        self._check_fda_compliance(device)
        
        if self.external_apis:
            self._enrich_device_with_external_apis(device)
        
        if self.encryption_analyzer:
            self._analyze_encryption(device)
        
        if run_vulnerability_tests and self.vulnerability_tester:
            self._run_vulnerability_tests(device)
    
    if self.anomaly_detector and len(self.devices) >= 10:
        self._detect_anomalies()
```

**Dlaczego w pętli dla każdego urządzenia?**
- Każde urządzenie ma inne właściwości
- Analiza jest specyficzna dla urządzenia
- Można przerwać dla jednego urządzenia bez wpływu na inne

**Dlaczego sprawdzanie `if self.external_apis`?**
- API są opcjonalne (wymagają kluczy)
- Jeśli nie są dostępne, pomija wzbogacanie
- Program działa bez API (tylko z lokalnymi danymi)

**Dlaczego `len(self.devices) >= 10` dla ML?**
- ML wymaga minimum danych do treningu
- Z mniej niż 10 urządzeń model byłby niedokładny
- 10 to rozsądne minimum dla algorytmów ML

### Metoda `_detect_anomalies()`

```python
def _detect_anomalies(self):
    if not self.anomaly_detector.trained:
        train_result = self.anomaly_detector.train(self.devices)
    
    anomaly_results = self.anomaly_detector.detect_anomalies(self.devices)
    
    for result in anomaly_results:
        if result['is_anomaly']:
            device.add_vulnerability(f"ML Anomaly Detection: {result['reason']}")
```

**Dlaczego automatyczny trening?**
- Użytkownik nie musi ręcznie trenować modelu
- Model trenuje się przy pierwszym użyciu
- Zapisuje się automatycznie dla następnych użyć

**Dlaczego dodawanie podatności dla anomalii?**
- Anomalia = potencjalna podatność
- Integracja z resztą systemu (widać w raportach)
- Spójność z innymi podatnościami

---

## 3.3. `real_scanner.py` - Skaner BLE

### Klasa `RealBLEScanner`

**Odpowiedzialność:**
- Skanuje urządzenia BLE w zasięgu
- Analizuje właściwości bezpieczeństwa
- Wykrywa szyfrowanie i parowanie

### Metoda `scan_ble_devices()`

```python
async def scan_ble_devices(self, duration: int = 10) -> List[Device]:
    scanner = BleakScanner()
    devices = await scanner.discover(timeout=duration)
    
    for ble_device in devices:
        device = await self._analyze_device(ble_device.address)
        if device:
            all_devices.append(device)
    
    return all_devices
```

**Dlaczego async?**
- `bleak` używa asynchronicznego API
- Skanowanie wielu urządzeń jednocześnie
- Nie blokuje wykonania podczas czekania na odpowiedź

**Dlaczego `await`?**
- Czeka na zakończenie operacji asynchronicznej
- Bez `await` otrzymałbyś obiekt Promise, nie wynik

### Metoda `_analyze_device()`

```python
async def _analyze_device(self, address: str) -> Optional[Device]:
    try:
        async with BleakClient(address) as client:
            services = await client.get_services()
            
            # Sprawdź czy wymaga parowania
            requires_pairing = await self._check_pairing_required(client)
            
            # Sprawdź szyfrowanie
            has_encryption = await self._check_encryption(services)
    except Exception:
        # Błąd = prawdopodobnie wymaga parowania (bezpieczne!)
        requires_pairing = True
        has_encryption = False
    
    return Device(...)
```

**Dlaczego try/except?**
- Większość urządzeń wymaga parowania
- Błąd połączenia = urządzenie jest bezpieczne (wymaga autoryzacji)
- Nie wyświetlamy błędów jako problemów

**Dlaczego `Optional[Device]`?**
- Może zwrócić `None` jeśli urządzenie nie jest medyczne
- Filtruje niepotrzebne urządzenia (np. smartfony, słuchawki)

---

## 3.4. `wifi_scanner.py` - Skaner WiFi

### Klasa `WiFiScanner`

**Odpowiedzialność:**
- Skanuje urządzenia w sieci lokalnej
- Analizuje otwarte porty
- Wykrywa porty medyczne (DICOM, HL7)

### Metoda `scan_wifi_devices()`

```python
def scan_wifi_devices(self, network_range: Optional[str] = None) -> List[Device]:
    if network_range is None:
        network_range = self._detect_local_network()
    
    # Priorytet 1: tshark (najlepsze)
    devices = self._scan_with_tshark(network_range)
    if devices:
        return devices
    
    # Priorytet 2: scapy
    devices = self._scan_with_scapy(network_range)
    if devices:
        return devices
    
    # Priorytet 3: podstawowe (ping)
    devices = self._scan_basic(network_range)
    return devices
```

**Dlaczego 3 metody skanowania?**
- **tshark:** Najlepsze, ale wymaga zewnętrznego programu
- **scapy:** Dobre, ale wymaga uprawnień (raw sockets)
- **basic:** Działa zawsze, ale ograniczone (tylko ping)

**Dlaczego priorytety?**
- Używa najlepszej dostępnej metody
- Fallback jeśli lepsza metoda nie działa
- Program zawsze działa (nawet bez uprawnień)

### Metoda `_detect_local_network()`

```python
def _detect_local_network(self) -> Optional[str]:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))  # Połącz z zewnętrznym serwerem
    local_ip = s.getsockname()[0]  # Pobierz lokalny IP
    s.close()
    
    ip_parts = local_ip.split('.')
    network_base = '.'.join(ip_parts[:3])
    return f"{network_base}.0/24"  # np. "192.168.1.0/24"
```

**Dlaczego połączenie z zewnętrznym serwerem?**
- Nie można sprawdzić lokalnego IP bez połączenia
- Połączenie z `8.8.8.8` (Google DNS) ujawnia lokalny IP
- Nie wysyła danych, tylko sprawdza routing

**Dlaczego `/24`?**
- `/24` oznacza maskę podsieci 255.255.255.0
- Obejmuje 254 adresy IP (192.168.1.1 - 192.168.1.254)
- Standardowy rozmiar sieci domowej

---

## 3.5. `anomaly_detector.py` - Machine Learning

### Klasa `AnomalyDetector`

**Odpowiedzialność:**
- Wykrywa anomalie używając ML
- Trenuje modele na historycznych danych
- Predykcja przyszłych podatności
- Klasteryzacja urządzeń

### Metoda `extract_features()`

```python
def extract_features(self, devices: List[Device]) -> np.ndarray:
    features = []
    
    for device in devices:
        feature_vector = [
            device.security_score,           # 1. Security score
            len(device.vulnerabilities),     # 2. Liczba podatności
            1 if device.has_encryption else 0,  # 3. Szyfrowanie (0/1)
            1 if device.requires_pairing else 0,  # 4. Parowanie (0/1)
            # ... one-hot encoding dla protokołu
            # ... one-hot encoding dla typu urządzenia
        ]
        features.append(feature_vector)
    
    return np.array(features)
```

**Dlaczego ekstrakcja cech?**
- ML wymaga danych numerycznych
- Urządzenia mają różne typy danych (stringi, booleany, liczby)
- Konwersja na wektor numeryczny dla algorytmów ML

**Dlaczego one-hot encoding?**
- Protokół to kategoria (BLE, WiFi, USB, NFC)
- ML nie rozumie kategorii, tylko liczby
- One-hot: BLE = [1,0,0,0], WiFi = [0,1,0,0], etc.

### Metoda `train()`

```python
def train(self, devices: List[Device]) -> Dict:
    X = self.extract_features(devices)  # Cechy
    X_scaled = self.scaler.fit_transform(X)  # Normalizacja
    
    self.isolation_forest.fit(X_scaled)  # Trenuj model
    self.lof.fit(X_scaled)
    self.one_class_svm.fit(X_scaled)
    
    self.trained = True
    return {'trained': True, 'devices_count': len(devices)}
```

**Dlaczego normalizacja (`StandardScaler`)?**
- Różne cechy mają różne zakresy (security_score: 0-100, liczba podatności: 0-10)
- Algorytmy ML działają lepiej na znormalizowanych danych
- `StandardScaler` normalizuje do średniej=0, odchylenie=1

**Dlaczego 3 algorytmy?**
- **Isolation Forest:** Szybki, dobry dla wysokowymiarowych danych
- **LOF:** Wykrywa lokalne anomalie
- **One-Class SVM:** Wykrywa złożone wzorce
- **Ensemble:** Głosowanie większościowe (anomalia jeśli 2 z 3 wykryły)

### Metoda `detect_anomalies()`

```python
def detect_anomalies(self, devices: List[Device], use_ensemble: bool = True) -> List[Dict]:
    X = self.extract_features(devices)
    X_scaled = self.scaler.transform(X)  # Użyj tego samego skalera co przy treningu
    
    if_anomalies = self.isolation_forest.predict(X_scaled)
    lof_anomalies = self.lof.predict(X_scaled)
    svm_anomalies = self.one_class_svm.predict(X_scaled)
    
    # Ensemble: głosowanie większościowe
    for i, device in enumerate(devices):
        votes = sum([
            if_anomalies[i] == -1,  # -1 = anomalia
            lof_anomalies[i] == -1,
            svm_anomalies[i] == -1
        ])
        is_anomaly = votes >= 2  # Anomalia jeśli 2 z 3 wykryły
```

**Dlaczego ensemble?**
- Jeden algorytm może mieć fałszywe alarmy
- Głosowanie większościowe zmniejsza fałszywe alarmy
- Większa dokładność niż pojedynczy algorytm

**Dlaczego `transform()` zamiast `fit_transform()`?**
- `fit_transform()` - uczy się na danych (trening)
- `transform()` - używa już nauczonego skalera (predykcja)
- Musi używać tego samego skalera co przy treningu

---

## 3.6. `vulnerability_tester.py` - Testy Podatności

### Klasa `VulnerabilityTester`

**Odpowiedzialność:**
- Wykonuje testy podatności
- Symuluje ataki (bez faktycznego atakowania)
- Używa CVE do identyfikacji podatności

### Metoda `test_device()`

```python
def test_device(self, device: Device) -> List[VulnerabilityTest]:
    results = []
    open_ports = device.metadata.get('open_ports', [])
    
    for port in open_ports:
        # Sprawdź CVE dla portu
        cves = self.cve_lookup.get_cves_for_port(port)
        
        # Testuj specyficzne ataki
        if port == 3389:  # RDP
            rdp_tests = self._test_rdp(ip, port)
            results.extend(rdp_tests)
    
    return results
```

**Dlaczego testy są symulacją?**
- **Etyka:** Nie atakujemy rzeczywistych urządzeń medycznych
- **Bezpieczeństwo:** Nie chcemy uszkodzić urządzeń
- **Legalność:** Atakowanie urządzeń bez zgody jest nielegalne

**Dlaczego sprawdzanie CVE?**
- CVE to oficjalna baza podatności
- Aktualne informacje o znanych podatnościach
- CVSS scores pokazują poziom ryzyka

---

## 3.7. `encryption_analyzer.py` - Analiza Szyfrowania

### Klasa `EncryptionAnalyzer`

**Odpowiedzialność:**
- Analizuje typ szyfrowania
- Wykrywa słabe algorytmy
- Generuje rekomendacje

### Metoda `analyze()`

```python
def analyze(self, encryption_type: Optional[str], has_encryption: bool) -> EncryptionAnalysis:
    if not has_encryption:
        return EncryptionAnalysis(
            strength=EncryptionStrength.NONE,
            is_weak=True,
            issues=["Brak szyfrowania"],
            recommendations=["Włącz szyfrowanie"]
        )
    
    # Sprawdź czy algorytm jest słaby
    if encryption_type in self.WEAK_ALGORITHMS:
        strength = EncryptionStrength.WEAK
        is_weak = True
    elif encryption_type in self.STRONG_ALGORITHMS:
        strength = EncryptionStrength.STRONG
        is_weak = False
```

**Dlaczego lista słabych algorytmów?**
- Niektóre algorytmy są przestarzałe (DES, MD5, TLS 1.0)
- Znane podatności w starych algorytmach
- Łatwo sprawdzić czy urządzenie używa słabego algorytmu

**Dlaczego enum `EncryptionStrength`?**
- Ograniczone wartości (STRONG, MODERATE, WEAK, NONE)
- Nie można użyć nieprawidłowej wartości
- Czytelniejsze niż stringi

---

## 3.8. `cve_lookup.py` - Wyszukiwanie CVE

### Klasa `CVELookup`

**Odpowiedzialność:**
- Pobiera podatności CVE z NIST NVD API
- Cache dla szybkiego działania
- Fallback do lokalnej bazy

### Metoda `get_cves_for_port()`

```python
def get_cves_for_port(self, port: int) -> List[CVEInfo]:
    # Sprawdź cache
    cache_key = f"port_{port}"
    if cache_key in self.cache:
        if not self._is_cache_expired(cache_key):
            return self.cache[cache_key]['data']
    
    # Pobierz z API
    cves = self._fetch_cves_from_api(port)
    
    # Zapisz w cache
    self.cache[cache_key] = {
        'data': cves,
        'timestamp': time.time()
    }
    
    return cves
```

**Dlaczego cache?**
- **Rate limiting:** API ma limity (5-50 zapytań/30s)
- **Szybkość:** Cache jest natychmiastowy, API wymaga czasu
- **Offline:** Działa nawet gdy API nie jest dostępne

**Dlaczego sprawdzanie wygaśnięcia cache?**
- CVE są aktualizowane regularnie
- Stary cache może mieć nieaktualne dane
- 24h to rozsądny czas ważności

---

## 3.9. `rust_scanner_wrapper.py` - Integracja Rust

### Klasa `FastPortScannerPython` (Fallback)

```python
class FastPortScannerPython:
    def scan_ports(self, ip: str, ports: List[int]) -> List[int]:
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            futures = {executor.submit(check_port, port): port for port in ports}
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    open_ports.append(result)
```

**Dlaczego fallback?**
- Rust może nie być skompilowany
- Program powinien działać bez Rust (tylko wolniej)
- Python fallback zapewnia kompatybilność

**Dlaczego `ThreadPoolExecutor`?**
- Równoległe skanowanie portów
- `max_workers` ogranicza liczbę jednoczesnych połączeń
- `as_completed` zbiera wyniki gdy są gotowe

---

## 3.10. `rust_scanner/src/lib.rs` - Kod Rust

### Struktura `FastPortScanner`

```rust
#[pyclass]
pub struct FastPortScanner {
    timeout_ms: u64,
    max_concurrent: usize,
}
```

**Wyjaśnienie Rust:**
- `#[pyclass]` - oznacza klasę dostępną z Pythona (PyO3)
- `pub struct` - publiczna struktura (klasa w Rust)
- `u64` - 64-bitowa liczba bez znaku
- `usize` - rozmiar wskaźnika (zależny od architektury)

**Dlaczego Rust?**
- **Wydajność:** 3-5x szybsze niż Python
- **Bezpieczeństwo pamięci:** Brak buffer overflows
- **Równoległość:** Tokio zapewnia wydajne async I/O

### Metoda `scan_ports()`

```rust
fn scan_ports(&self, ip: &str, ports: Vec<u16>) -> PyResult<Vec<u16>> {
    let semaphore = Arc::new(tokio::sync::Semaphore::new(self.max_concurrent));
    let rt = tokio::runtime::Runtime::new()?;
    
    rt.block_on(async {
        for port in ports {
            let semaphore = semaphore.clone();
            let task = tokio::spawn(async move {
                let _permit = semaphore.acquire().await.unwrap();
                // Skanuj port
            });
        }
    })
}
```

**Wyjaśnienie:**
- `Arc` - Atomic Reference Counter (współdzielony wskaźnik)
- `Semaphore` - ogranicza liczbę jednoczesnych operacji
- `tokio::spawn` - uruchamia zadanie asynchroniczne
- `block_on` - czeka na zakończenie async operacji

**Dlaczego semafor?**
- Bez semafora: 1000 portów = 1000 jednoczesnych połączeń (przeciążenie)
- Z semaforem: maksymalnie 50 jednoczesnych (kontrolowane)
- Zapobiega przeciążeniu sieci

---

# 🔗 CZĘŚĆ 4: ZALEŻNOŚCI I INTEGRACJE

## 4.1. Zależności Między Modułami

### Hierarchia Importów

```
scanner.py
    ↓ importuje
    ├─→ device.py (Device, DeviceType, Protocol)
    ├─→ real_scanner.py (RealBLEScanner)
    ├─→ wifi_scanner.py (WiFiScanner)
    ├─→ usb_scanner.py (USBScanner)
    ├─→ nfc_scanner.py (NFCScanner)
    ├─→ vulnerability_tester.py (VulnerabilityTester)
    ├─→ encryption_analyzer.py (EncryptionAnalyzer)
    ├─→ external_apis.py (ExternalAPIs)
    └─→ anomaly_detector.py (AnomalyDetector)
```

**Dlaczego taka hierarchia?**
- `scanner.py` jest na górze (orchestrator)
- Wszystkie moduły używają `device.py` (wspólny model)
- Każdy moduł jest niezależny (można użyć osobno)

### Circular Dependencies (Brak!)

**Dlaczego nie ma circular dependencies?**
- `scanner.py` importuje wszystkie moduły
- Moduły nie importują `scanner.py`
- `device.py` nie importuje nic (tylko standardowe biblioteki)

**Co by się stało z circular dependency?**
```python
# scanner.py
from real_scanner import RealBLEScanner

# real_scanner.py
from scanner import MedicalDeviceScanner  # ❌ CIRCULAR!
```
- Python nie może zaimportować (nieskończona pętla)
- Program się nie uruchomi

---

## 4.2. Przekazywanie Danych

### Flow: Skanowanie → Analiza → Wyświetlanie

```
1. scanner.scan_all()
   ↓
2. real_scanner.scan_ble_devices() → List[Device]
   ↓
3. scanner.devices = all_devices
   ↓
4. scanner.analyze_security()
   ↓
5. device.calculate_security_score()
   encryption_analyzer.analyze(device)
   vulnerability_tester.test_device(device)
   ↓
6. scanner.display_results()
```

**Dlaczego taki przepływ?**
- **Separacja:** Skanowanie → Analiza → Wyświetlanie
- **Modularność:** Każdy krok jest osobną metodą
- **Testowalność:** Można testować każdy krok osobno

---

## 4.3. Współdzielone Dane

### `self.devices` - Centralne Przechowywanie

```python
class MedicalDeviceScanner:
    def __init__(self):
        self.devices: List[Device] = []  # Pusta lista na start
    
    def scan_all(self):
        self.devices = all_devices  # Zapisuje wyniki
    
    def analyze_security(self):
        for device in self.devices:  # Używa zapisanych urządzeń
            ...
```

**Dlaczego `self.devices`?**
- Wszystkie metody mają dostęp do urządzeń
- Nie trzeba przekazywać jako parametr
- Stan jest przechowywany w obiekcie

**Dlaczego lista, nie słownik?**
- Kolejność ma znaczenie (wysokie ryzyko na górze)
- Łatwo iterować: `for device in self.devices`
- Słownik byłby lepszy dla szybkiego wyszukiwania po MAC

---

# 🎯 CZĘŚĆ 5: DLACZEGO KOD JEST NAPISANY TAK A NIE INACZEJ

## 5.1. Dlaczego Try/Except Przy Importach?

```python
try:
    from bleak import BleakScanner
    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False
```

**Alternatywa (zła):**
```python
from bleak import BleakScanner  # ❌ Crashuje jeśli nie zainstalowane
```

**Dlaczego try/except jest lepsze?**
- Program działa nawet bez niektórych bibliotek
- Użytkownik może uruchomić tylko BLE (bez WiFi)
- Graceful degradation zamiast crashowania

---

## 5.2. Dlaczego Async dla BLE?

```python
async def scan_ble_devices(self, duration: int = 10):
    devices = await BleakScanner.discover()
```

**Alternatywa (synchroniczna):**
```python
def scan_ble_devices(self, duration: int = 10):
    devices = BleakScanner.discover()  # ❌ Blokuje wykonanie
```

**Dlaczego async jest lepsze?**
- **Równoległość:** Można skanować wiele urządzeń jednocześnie
- **Wydajność:** Nie czeka na jedno urządzenie, skanuje inne
- **Wymaganie biblioteki:** `bleak` używa async API

---

## 5.3. Dlaczego Wrapper Async → Sync?

```python
def _scan_ble_async(self, duration: int = 10) -> List[Device]:
    return asyncio.run(self.scanners['ble'].scan_ble_devices(duration))
```

**Dlaczego wrapper?**
- Główny kod (`scanner.py`) jest synchroniczny
- BLE scanner jest asynchroniczny
- Wrapper konwertuje async na sync dla spójności

**Dlaczego nie cały kod async?**
- Większość kodu jest synchroniczna (WiFi, USB, NFC)
- Async dodaje złożoność (nie zawsze potrzebna)
- Wrapper jest prostszym rozwiązaniem

---

## 5.4. Dlaczego Słownik `self.scanners`?

```python
self.scanners = {
    'ble': RealBLEScanner(),
    'wifi': WiFiScanner(),
    ...
}
```

**Alternatywa (zła):**
```python
self.ble_scanner = RealBLEScanner()
self.wifi_scanner = WiFiScanner()
# ... trzeba sprawdzać każdy osobno
```

**Dlaczego słownik jest lepszy?**
- **Dynamiczny dostęp:** `self.scanners['ble']`
- **Iteracja:** `for protocol, scanner in self.scanners.items()`
- **Elastyczność:** Łatwo dodać nowy protokół

---

## 5.5. Dlaczego Metoda `to_dict()`?

```python
def to_dict(self) -> dict:
    return {
        "mac_address": self.mac_address,
        "security_score": int(self.security_score),
        ...
    }
```

**Dlaczego potrzebna?**
- JSON nie może serializować obiektów Python
- API i raporty potrzebują słowników
- Konwersja obiektu → słownik → JSON

**Dlaczego nie użyć `dataclasses.asdict()`?**
- `asdict()` nie konwertuje NumPy types
- Trzeba ręcznie konwertować `numpy.int64` → `int`
- Większa kontrola nad formatem

---

## 5.6. Dlaczego Funkcja `make_json_serializable()`?

```python
def make_json_serializable(obj: Any) -> Any:
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    ...
```

**Dlaczego potrzebna?**
- NumPy types nie są JSON serializowalne
- ML zwraca NumPy types (`numpy.int64`, `numpy.bool_`)
- Konwersja do natywnych typów Pythona

**Dlaczego rekurencyjna?**
- Metadata może zawierać zagnieżdżone słowniki
- Trzeba konwertować na wszystkich poziomach
- `isinstance()` sprawdza typ i konwertuje

---

## 5.7. Dlaczego Cache w CVE Lookup?

```python
def get_cves_for_port(self, port: int) -> List[CVEInfo]:
    if cache_key in self.cache:
        return self.cache[cache_key]['data']  # Szybkie!
    
    cves = self._fetch_cves_from_api(port)  # Wolne (API call)
    self.cache[cache_key] = {'data': cves, 'timestamp': time.time()}
```

**Dlaczego cache?**
- **Rate limiting:** API ma limity (5-50 zapytań/30s)
- **Szybkość:** Cache jest natychmiastowy
- **Offline:** Działa bez połączenia z internetem

**Dlaczego sprawdzanie wygaśnięcia?**
- CVE są aktualizowane regularnie
- Stary cache = nieaktualne dane
- 24h to rozsądny czas ważności

---

## 5.8. Dlaczego Fallback w Rust Wrapper?

```python
if RUST_SCANNER_AVAILABLE:
    FastPortScanner = rust_scanner.FastPortScanner
else:
    FastPortScanner = FastPortScannerPython  # Fallback
```

**Dlaczego fallback?**
- Rust może nie być skompilowany
- Program powinien działać bez Rust (tylko wolniej)
- Python fallback zapewnia kompatybilność

**Dlaczego nie wymagać Rust?**
- Nie wszyscy użytkownicy mają Rust zainstalowany
- Kompilacja Rust wymaga czasu
- Python fallback działa od razu

---

# 🔄 CZĘŚĆ 6: PRZEPŁYW WYKONANIA

## 6.1. Pełny Przepływ: Uruchomienie → Wyniki

### KROK 1: Uruchomienie (`main()`)

```python
def main():
    scanner = MedicalDeviceScanner(protocols=['ble', 'wifi'])
    devices = scanner.scan_all()
    scanner.analyze_security(run_vulnerability_tests=True)
    scanner.display_results()
```

**Co się dzieje:**
1. Tworzy obiekt `MedicalDeviceScanner`
2. W `__init__`: inicjalizuje skanery, analizatory, ML
3. Wywołuje `scan_all()` - skanuje urządzenia
4. Wywołuje `analyze_security()` - analizuje bezpieczeństwo
5. Wywołuje `display_results()` - wyświetla wyniki

---

### KROK 2: Skanowanie BLE

```
scanner.scan_all()
    ↓
scanner._scan_ble_async()
    ↓
asyncio.run(real_scanner.scan_ble_devices())
    ↓
BleakScanner.discover()  # Biblioteka bleak
    ↓
Dla każdego urządzenia BLE:
    real_scanner._analyze_device()
        ↓
    BleakClient.connect()  # Próba połączenia
        ↓
    Sprawdź GATT services
        ↓
    Sprawdź szyfrowanie i parowanie
        ↓
    Utwórz obiekt Device
    ↓
Zwróć List[Device]
```

**Dlaczego taki przepływ?**
- **Warstwy abstrakcji:** Każda warstwa ma swoją odpowiedzialność
- **Obsługa błędów:** Błędy są łapane na każdym poziomie
- **Modularność:** Każdy krok można zmienić niezależnie

---

### KROK 3: Analiza Bezpieczeństwa

```
scanner.analyze_security()
    ↓
Dla każdego urządzenia:
    device.calculate_security_score()
        ↓
    Sprawdź has_encryption → -30 jeśli False
    Sprawdź requires_pairing → -20 jeśli False
    Sprawdź vulnerabilities → -25 za każdą
        ↓
    Wynik: 0-100
    ↓
    scanner._check_fda_compliance(device)
        ↓
    Sprawdź czy urządzenie medyczne
        ↓
    Sprawdź szyfrowanie i autoryzację
        ↓
    Dodaj podatności jeśli niezgodne
    ↓
    scanner._analyze_encryption(device)
        ↓
    encryption_analyzer.analyze()
        ↓
    Sprawdź czy algorytm jest słaby
        ↓
    Dodaj podatności jeśli słabe
    ↓
    scanner._run_vulnerability_tests(device)
        ↓
    vulnerability_tester.test_device()
        ↓
    Dla każdego otwartego portu:
        cve_lookup.get_cves_for_port()
        vulnerability_tester._test_specific_port()
        ↓
    Dodaj podatności do device
    ↓
scanner._detect_anomalies()
    ↓
anomaly_detector.detect_anomalies()
    ↓
Trenuj model jeśli nie wytrenowany
    ↓
Wykryj anomalie używając ML
    ↓
Dodaj podatności dla anomalii
```

**Dlaczego taki przepływ?**
- **Kolejność ma znaczenie:** Security score → FDA → Encryption → Vulnerabilities → ML
- **Każdy krok dodaje informacje:** Urządzenie jest wzbogacane danymi
- **ML na końcu:** Używa wszystkich zebranych danych

---

# 🧠 CZĘŚĆ 7: DECYZJE PROJEKTOWE

## 7.1. Dlaczego Osobne Pliki dla Każdego Protokołu?

**Struktura:**
- `real_scanner.py` - BLE
- `wifi_scanner.py` - WiFi
- `usb_scanner.py` - USB
- `nfc_scanner.py` - NFC

**Alternatywa (zła):**
```python
# Wszystko w scanner.py - ❌ 5000+ linii kodu!
```

**Dlaczego osobne pliki?**
- **Czytelność:** Każdy plik ma ~300-1000 linii (czytelne)
- **Maintainability:** Łatwo znaleźć i zmienić kod dla protokołu
- **Testowalność:** Można testować każdy protokół osobno
- **Reużywalność:** Można użyć tylko BLE scanner w innym projekcie

---

## 7.2. Dlaczego Klasa `Device` zamiast Słownika?

**Obecne rozwiązanie:**
```python
device = Device(mac_address="...", name="...")
device.calculate_security_score()
```

**Alternatywa (słownik):**
```python
device = {"mac_address": "...", "name": "..."}
calculate_security_score(device)  # Funkcja zamiast metody
```

**Dlaczego klasa jest lepsza?**
- **Enkapsulacja:** Dane + metody w jednym miejscu
- **Type safety:** Type hints pokazują strukturę
- **Metody:** `device.calculate_security_score()` jest czytelniejsze
- **Walidacja:** Można dodać walidację w `__init__`

---

## 7.3. Dlaczego Enum zamiast Stringów?

**Obecne rozwiązanie:**
```python
device.protocol = Protocol.BLE
```

**Alternatywa:**
```python
device.protocol = "BLE"  # ❌ Można użyć "BLUE" (błąd!)
```

**Dlaczego Enum jest lepszy?**
- **Bezpieczeństwo typów:** Nie można użyć nieprawidłowej wartości
- **Autouzupełnianie:** IDE podpowiada dostępne wartości
- **Refaktoryzacja:** Zmiana nazwy w jednym miejscu (Enum)
- **Czytelność:** `Protocol.BLE` jest bardziej czytelne

---

## 7.4. Dlaczego Optional Types?

```python
rssi: Optional[int] = None
manufacturer: Optional[str] = None
```

**Dlaczego Optional?**
- Nie wszystkie urządzenia mają RSSI (tylko BLE)
- Nie wszystkie mają producenta (nieznane MAC)
- `None` oznacza brak danych (explicit)

**Alternatywa (zła):**
```python
rssi: int = 0  # ❌ 0 może oznaczać brak danych LUB rzeczywiste 0
```

**Dlaczego None jest lepsze?**
- **Explicit:** Widać że dane nie są dostępne
- **Type safety:** `Optional[int]` mówi że może być `None`
- **Obsługa:** `if device.rssi is not None:` jest czytelne

---

## 7.5. Dlaczego Metadata jako Słownik?

```python
device.metadata: Dict = field(default_factory=dict)
device.metadata['encryption_analysis'] = {...}
device.metadata['ip_address'] = "192.168.1.1"
```

**Dlaczego metadata?**
- **Elastyczność:** Różne protokoły mają różne dane
- **Rozszerzalność:** Łatwo dodać nowe dane bez zmiany klasy
- **Opcjonalność:** Nie wszystkie urządzenia mają wszystkie dane

**Alternatywa (zła):**
```python
# Wszystkie możliwe pola w klasie - ❌ 50+ pól!
device.ip_address: Optional[str] = None
device.encryption_analysis: Optional[Dict] = None
device.open_ports: Optional[List[int]] = None
# ... 47 więcej pól
```

**Dlaczego metadata jest lepsze?**
- **Czytelność:** Klasa ma tylko podstawowe pola
- **Elastyczność:** Można dodać dowolne dane
- **Organizacja:** Podobne dane są grupowane (np. `metadata['wifi_info']`)

---

# 🎓 CZĘŚĆ 8: PODSTAWY PYTHONA - SZCZEGÓŁY

## 8.1. List Comprehensions

```python
high_risk = [d for d in self.devices if d.security_score < 50]
```

**Wyjaśnienie:**
- `[d for d in self.devices]` - dla każdego urządzenia w liście
- `if d.security_score < 50` - tylko jeśli warunek jest spełniony
- Zwraca listę urządzeń z wysokim ryzykiem

**Równoważny kod:**
```python
high_risk = []
for d in self.devices:
    if d.security_score < 50:
        high_risk.append(d)
```

**Dlaczego list comprehension?**
- **Krótsze:** 1 linia zamiast 4
- **Czytelniejsze:** Widać od razu co robi
- **Szybsze:** Python optymalizuje list comprehensions

---

## 8.2. Dictionary Comprehensions

```python
severity_counts = {severity: count for severity, count in data.items()}
```

**Wyjaśnienie:**
- Tworzy słownik z pętli
- `severity: count` - klucz: wartość
- `for severity, count in data.items()` - iteracja

**Dlaczego używać?**
- Krótsze niż pętla `for`
- Czytelniejsze
- Pythonic (idiomatyczny Python)

---

## 8.3. F-Strings (Formatted Strings)

```python
console.print(f"[green]✅ Znaleziono {len(devices)} urządzeń[/green]")
```

**Wyjaśnienie:**
- `f"..."` - formatted string
- `{len(devices)}` - wstawia wartość wyrażenia
- `{device.name}` - wstawia atrybut obiektu

**Dlaczego f-strings?**
- **Czytelność:** Widać gdzie jest wartość
- **Wydajność:** Szybsze niż `.format()` lub `%`
- **Wyrażenia:** Można użyć wyrażeń: `f"{score * 100:.1f}%"`

---

## 8.4. Context Managers (`with`)

```python
with open(filepath, 'w') as f:
    json.dump(data, f)
# Plik jest automatycznie zamknięty
```

**Wyjaśnienie:**
- `with` - context manager
- Automatycznie zamyka plik po wyjściu z bloku
- Nawet jeśli wystąpi błąd

**Dlaczego `with`?**
- **Bezpieczeństwo:** Plik jest zawsze zamknięty
- **Czytelność:** Widać zakres użycia pliku
- **Best practice:** Zalecany sposób w Pythonie

---

## 8.5. Type Hints

```python
def scan_all(self) -> List[Device]:
    return []
```

**Wyjaśnienie:**
- `-> List[Device]` - funkcja zwraca listę obiektów `Device`
- `List[Device]` - import: `from typing import List`

**Dlaczego type hints?**
- **Dokumentacja:** Widać co funkcja zwraca
- **IDE support:** Autouzupełnianie i sprawdzanie błędów
- **Czytelność:** Kod jest bardziej czytelny

---

## 8.6. Default Arguments

```python
def scan_ble_devices(self, duration: int = 10) -> List[Device]:
    ...
```

**Wyjaśnienie:**
- `duration: int = 10` - parametr z wartością domyślną
- Jeśli nie podano, używa 10

**Dlaczego default arguments?**
- **Elastyczność:** Można wywołać bez parametru
- **Convenience:** Sensowne domyślne wartości
- **Backward compatibility:** Można dodać nowy parametr bez łamania kodu

---

## 8.7. Kwargs i Args

```python
def function(*args, **kwargs):
    # args - lista argumentów pozycyjnych
    # kwargs - słownik argumentów nazwanych
```

**W projekcie nie używane bezpośrednio, ale warto wiedzieć:**
- `*args` - dowolna liczba argumentów
- `**kwargs` - dowolna liczba argumentów nazwanych

---

# 🔧 CZĘŚĆ 9: WZORCE PROJEKTOWE

## 9.1. Factory Pattern (Niejawny)

```python
if 'ble' in protocols:
    if BLE_SCANNER_AVAILABLE:
        self.scanners['ble'] = RealBLEScanner()  # Tworzy obiekt
```

**Wyjaśnienie:**
- Tworzenie obiektów w zależności od warunków
- Każdy protokół ma swoją klasę skanera

**Dlaczego taki wzorzec?**
- **Polimorfizm:** Wszystkie skanery mają tę samą metodę `scan_*_devices()`
- **Elastyczność:** Łatwo dodać nowy protokół
- **Enkapsulacja:** Logika tworzenia jest w jednym miejscu

---

## 9.2. Strategy Pattern

```python
# Różne strategie skanowania WiFi
devices = self._scan_with_tshark(network_range)  # Strategia 1
if not devices:
    devices = self._scan_with_scapy(network_range)  # Strategia 2
if not devices:
    devices = self._scan_basic(network_range)  # Strategia 3 (fallback)
```

**Wyjaśnienie:**
- Różne algorytmy do tego samego zadania
- Wybór najlepszej dostępnej strategii

**Dlaczego Strategy Pattern?**
- **Elastyczność:** Można użyć różnych metod
- **Fallback:** Zawsze działa (nawet bez uprawnień)
- **Testowalność:** Każdą strategię można testować osobno

---

## 9.3. Observer Pattern (Częściowy)

```python
# W anomaly_detector.py
self.siem_callbacks: List[Callable] = []

def add_siem_callback(self, callback: Callable):
    self.siem_callbacks.append(callback)

def _send_to_siem(self, anomaly_result: Dict):
    for callback in self.siem_callbacks:
        callback(anomaly_result)  # Wywołaj wszystkie callbacki
```

**Wyjaśnienie:**
- Callbacki są powiadamiane o zdarzeniach (anomalie)
- Można dodać wiele obserwatorów

**Dlaczego Observer Pattern?**
- **Rozszerzalność:** Można dodać nowe systemy SIEM bez zmiany kodu
- **Loose coupling:** AnomalyDetector nie wie o szczegółach SIEM
- **Flexibility:** Każdy callback może robić coś innego

---

# 🎯 CZĘŚĆ 10: PYTANIA I ODPOWIEDZI

## Q: Dlaczego nie używasz bazy danych?

**A:** Projekt używa plików JSON zamiast bazy danych, bo:
- **Prostota:** Nie wymaga instalacji bazy danych
- **Portability:** Pliki JSON działają wszędzie
- **Czytelność:** Można otworzyć w edytorze tekstu
- **Dla większych projektów:** Można dodać SQLite/PostgreSQL (sqlalchemy jest w requirements.txt)

---

## Q: Dlaczego niektóre funkcje są async a inne nie?

**A:**
- **BLE:** Wymaga async (biblioteka `bleak`)
- **WiFi/USB/NFC:** Synchroniczne (używają standardowych bibliotek)
- **Wrapper:** Konwertuje async → sync dla spójności

**Dlaczego nie cały kod async?**
- Większość kodu nie potrzebuje async
- Async dodaje złożoność
- Wrapper jest prostszym rozwiązaniem

---

## Q: Dlaczego używasz `Path` zamiast stringów dla ścieżek?

```python
filepath = Path(__file__).parent.parent / "data" / "scans"
```

**A:**
- **Cross-platform:** Działa na Windows, Linux, Mac (`/` vs `\`)
- **Czytelność:** `/` jest bardziej czytelne niż `os.path.join()`
- **Type safety:** `Path` ma metody (`exists()`, `mkdir()`)

**Alternatywa (zła):**
```python
filepath = os.path.join(os.path.dirname(__file__), "..", "data", "scans")  # ❌ Mniej czytelne
```

---

## Q: Dlaczego używasz `rich` zamiast `print()`?

```python
console.print("[green]✅ Sukces[/green]")
```

**A:**
- **Kolory:** Łatwo dodać kolory i formatowanie
- **Tabele:** `Table()` tworzy ładne tabele
- **Panele:** `Panel()` tworzy ramki wokół tekstu
- **Progress bars:** `Progress()` pokazuje postęp

**Alternatywa:**
```python
print("✅ Sukces")  # ❌ Bez kolorów, mniej czytelne
```

---

## Q: Dlaczego niektóre metody są prywatne (`_method`)?

```python
def _analyze_encryption(self, device: Device):
    ...
```

**A:**
- **Konwencja:** `_method` oznacza metodę wewnętrzną
- **Enkapsulacja:** Nie powinna być wywoływana z zewnątrz
- **API:** Publiczne API to tylko `scan_all()`, `analyze_security()`, etc.

**Dlaczego nie użyć `__method` (name mangling)?**
- `_method` - konwencja (soft private)
- `__method` - name mangling (hard private, rzadko używane)

---

# 📊 CZĘŚĆ 11: PRZYKŁADY KODU Z WYJAŚNIENIAMI

## Przykład 1: Skanowanie BLE z Obsługą Błędów

```python
async def scan_ble_devices(self, duration: int = 10) -> List[Device]:
    scanner = BleakScanner()
    devices = await scanner.discover(timeout=duration)
    
    for ble_device in devices:
        try:
            device = await self._analyze_device(ble_device.address)
            if device:
                all_devices.append(device)
        except Exception as e:
            # Błąd = urządzenie wymaga parowania (bezpieczne!)
            # Nie wyświetlaj błędów - to jest normalne
            continue
    
    return all_devices
```

**Wyjaśnienie linia po linii:**
1. `async def` - funkcja asynchroniczna
2. `BleakScanner()` - tworzy skaner BLE
3. `await scanner.discover()` - czeka na skanowanie (async)
4. `for ble_device in devices:` - iteruje przez wykryte urządzenia
5. `try/except` - łapie błędy (większość urządzeń wymaga parowania)
6. `continue` - pomija urządzenie z błędem, kontynuuje z następnym
7. `return all_devices` - zwraca listę urządzeń

**Dlaczego try/except w pętli?**
- Jedno urządzenie z błędem nie powinno zatrzymać całego skanowania
- Większość urządzeń wymaga parowania (błąd = bezpieczne!)
- `continue` pomija urządzenie i kontynuuje

---

## Przykład 2: Obliczanie Security Score

```python
def calculate_security_score(self) -> int:
    score = 100  # Start od maksimum
    
    if not self.has_encryption:
        score -= 30  # -30 za brak szyfrowania
    
    if not self.requires_pairing:
        score -= 20  # -20 za brak parowania
    
    score -= len(self.vulnerabilities) * 25  # -25 za każdą podatność
    
    self.security_score = max(0, min(100, score))  # Ogranicz do 0-100
    return self.security_score
```

**Wyjaśnienie:**
1. Start: 100 punktów (idealne bezpieczeństwo)
2. Sprawdź szyfrowanie: jeśli brak → -30
3. Sprawdź parowanie: jeśli brak → -20
4. Sprawdź podatności: -25 za każdą
5. Ogranicz wynik do 0-100

**Dlaczego takie wartości?**
- **Brak szyfrowania (-30):** Najpoważniejsza podatność
- **Brak parowania (-20):** Średnia podatność
- **Podatności (-25):** Każda dodatkowa podatność

**Dlaczego `max(0, min(100, score))`?**
- `max(0, ...)` - wynik nie może być ujemny
- `min(100, ...)` - wynik nie może przekroczyć 100
- Zapewnia poprawny zakres

---

## Przykład 3: ML - Ekstrakcja Cech

```python
def extract_features(self, devices: List[Device]) -> np.ndarray:
    features = []
    
    for device in devices:
        feature_vector = [
            device.security_score,                    # 1. Security score (0-100)
            len(device.vulnerabilities),              # 2. Liczba podatności
            1 if device.has_encryption else 0,       # 3. Szyfrowanie (0/1)
            1 if device.requires_pairing else 0,     # 4. Parowanie (0/1)
        ]
        
        # One-hot encoding dla protokołu
        protocol_encoded = [0, 0, 0, 0]  # [BLE, WiFi, USB, NFC]
        if device.protocol == Protocol.BLE:
            protocol_encoded[0] = 1
        elif device.protocol == Protocol.WIFI:
            protocol_encoded[1] = 1
        # ...
        feature_vector.extend(protocol_encoded)
        
        features.append(feature_vector)
    
    return np.array(features)
```

**Wyjaśnienie:**
1. Dla każdego urządzenia tworzy wektor cech
2. Dodaje podstawowe cechy (score, podatności, szyfrowanie)
3. One-hot encoding dla kategorii (protokół, typ urządzenia)
4. Zwraca macierz NumPy (wymagana przez ML)

**Dlaczego one-hot encoding?**
- ML nie rozumie kategorii (BLE, WiFi, etc.)
- Konwersja na liczby: BLE = [1,0,0,0], WiFi = [0,1,0,0]
- Każda kategoria = osobna kolumna (0 lub 1)

**Dlaczego NumPy array?**
- Algorytmy ML wymagają NumPy arrays
- Szybsze niż listy Pythona
- Wsparcie dla operacji wektorowych

---

# 🎓 CZĘŚĆ 12: PODSUMOWANIE - CO SIĘ DZIEJE OD STARTU DO KOŃCA

## Pełny Przepływ Wykonania

```
1. Użytkownik uruchamia: python src/scanner.py --ble --wifi
   ↓
2. main() parsuje argumenty: protocols=['ble', 'wifi']
   ↓
3. scanner = MedicalDeviceScanner(protocols=['ble', 'wifi'])
   ↓
4. __init__():
   - Tworzy self.scanners = {}
   - Próbuje zaimportować RealBLEScanner → dodaje do self.scanners['ble']
   - Próbuje zaimportować WiFiScanner → dodaje do self.scanners['wifi']
   - Inicjalizuje anomaly_detector, vulnerability_tester, etc.
   ↓
5. devices = scanner.scan_all()
   ↓
6. scan_all():
   - Jeśli 'ble' in self.scanners:
     → _scan_ble_async() → real_scanner.scan_ble_devices()
     → Zwraca List[Device]
   - Jeśli 'wifi' in self.scanners:
     → wifi_scanner.scan_wifi_devices()
     → Zwraca List[Device]
   - Zapisuje w self.devices
   ↓
7. scanner.analyze_security(run_vulnerability_tests=False)
   ↓
8. analyze_security():
   - Dla każdego device w self.devices:
     → device.calculate_security_score()
     → _check_fda_compliance(device)
     → _enrich_device_with_external_apis(device)
     → _analyze_encryption(device)
   - Jeśli len(self.devices) >= 10:
     → _detect_anomalies()
   ↓
9. scanner.display_results()
   ↓
10. display_results():
    - Grupuje urządzenia według ryzyka
    - Wyświetla karty urządzeń
    - Wyświetla analizę szyfrowania
```

---

## Kluczowe Decyzje Projektowe - Podsumowanie

| Decyzja | Dlaczego |
|---------|----------|
| **Osobne pliki dla protokołów** | Czytelność, maintainability, testowalność |
| **Klasa Device zamiast słownika** | Enkapsulacja, type safety, metody |
| **Enum zamiast stringów** | Bezpieczeństwo typów, autouzupełnianie |
| **Try/except przy importach** | Graceful degradation, elastyczność |
| **Async dla BLE** | Wymaganie biblioteki, wydajność |
| **Wrapper async → sync** | Spójność z resztą kodu |
| **Słownik self.scanners** | Dynamiczny dostęp, iteracja |
| **Metadata jako słownik** | Elastyczność, rozszerzalność |
| **Cache w CVE lookup** | Rate limiting, szybkość, offline |
| **Fallback w Rust wrapper** | Kompatybilność, nie wymaga Rust |
| **List comprehension** | Krótsze, czytelniejsze, szybsze |
| **F-strings** | Czytelność, wydajność |
| **Context managers (with)** | Bezpieczeństwo, best practice |
| **Type hints** | Dokumentacja, IDE support |

---

# 🎯 KONIEC SAMOUCZKA

**Masz teraz pełne zrozumienie:**
- ✅ Podstaw Pythona używanych w projekcie
- ✅ Architektury i struktury projektu
- ✅ Za co odpowiada każda klasa i funkcja
- ✅ Wszystkich zależności między modułami
- ✅ Dlaczego kod jest napisany tak a nie inaczej
- ✅ Logiki działania całego systemu

**Używaj tego dokumentu jako referencji podczas pracy z kodem!** 📚
