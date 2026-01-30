# 🐍 Kompletny Przewodnik po Kodzie Python - Część 1

## 📚 Spis Treści

1. [Wprowadzenie](#wprowadzenie)
2. [Mapa Zależności](#mapa-zależności)
3. [Podstawowe Koncepty Python](#podstawowe-koncepty-python)
4. [Plik 1: `__init__.py`](#plik-1-__init__py)
5. [Plik 2: `device.py`](#plik-2-devicepy)

---

## Wprowadzenie

Ten przewodnik wyjaśnia **każdą linię kodu** we wszystkich plikach `.py` w projekcie Medical Device Security Scanner. 

### Dla kogo jest ten przewodnik?
- ✅ Osoby, które widzą kod Python **pierwszy raz**
- ✅ Osoby uczące się programowania
- ✅ Osoby chcące zrozumieć jak działa projekt

### Co znajdziesz w tym przewodniku?
- 📖 Wyjaśnienie każdej linii kodu
- 🔗 Zależności między plikami
- 💡 Wyjaśnienia konceptów Python (pętle, funkcje, klasy)
- 🎯 Przykłady użycia każdego modułu
- 🔍 Diagramy przepływu danych

---

## Mapa Zależności

### Hierarchia Importów

```
scanner.py (GŁÓWNY MODUŁ)
    │
    ├── device.py (podstawowa klasa Device)
    │
    ├── real_scanner.py (BLE scanning)
    │   └── device.py
    │
    ├── wifi_scanner.py (WiFi scanning)
    │   ├── device.py
    │   └── rust_scanner_wrapper.py (szybkie skanowanie portów)
    │
    ├── usb_scanner.py (USB scanning)
    │   └── device.py
    │
    ├── nfc_scanner.py (NFC scanning)
    │   └── device.py
    │
    ├── vulnerability_tester.py (testy podatności)
    │   ├── device.py
    │   └── cve_lookup.py (baza CVE)
    │
    ├── anomaly_detector.py (ML - wykrywanie anomalii)
    │   └── device.py
    │
    ├── encryption_analyzer.py (analiza szyfrowania)
    │   └── device.py
    │
    ├── external_apis.py (API zewnętrzne)
    │   └── device.py
    │
    ├── api_server.py (REST API)
    │   └── device.py
    │
    ├── dashboard.py (Streamlit dashboard)
    │   ├── device.py
    │   ├── scanner.py
    │   └── anomaly_detector.py
    │
    ├── siem_exporter.py (eksport do SIEM)
    │   └── device.py
    │
    ├── threat_intelligence.py (threat intelligence)
    │   └── device.py
    │
    ├── history_db.py (baza danych historii)
    │   └── device.py
    │
    ├── scheduler.py (zaplanowane skanowania)
    │
    └── monitor.py (monitoring w czasie rzeczywistym)
        └── history_db.py
```

### Kluczowe Zależności

1. **device.py** - używany przez **WSZYSTKIE** moduły (podstawowa klasa)
2. **scanner.py** - główny moduł, importuje wszystkie skanery
3. **anomaly_detector.py** - używany przez scanner.py i dashboard.py
4. **vulnerability_tester.py** - używany przez scanner.py
5. **api_server.py** i **dashboard.py** - używają device.py i scanner.py

---

## Podstawowe Koncepty Python

### 1. Importy

```python
# Import całego modułu
import json  # Używasz: json.loads()

# Import konkretnej klasy/funkcji
from device import Device  # Używasz: Device()

# Import z aliasem
import numpy as np  # Używasz: np.array()
```

### 2. Klasy i Obiekty

```python
# Definicja klasy
class Device:
    def __init__(self, name):  # Konstruktor (tworzy obiekt)
        self.name = name  # self = ten obiekt
    
    def get_name(self):  # Metoda (funkcja w klasie)
        return self.name

# Użycie
device = Device("Glukometr")  # Tworzy obiekt
print(device.get_name())  # Wywołuje metodę
```

### 3. Pętle

```python
# Pętla for - wykonuje kod dla każdego elementu
for device in devices:  # devices = lista urządzeń
    print(device.name)  # Wykonuje się dla każdego urządzenia

# Pętla while - wykonuje dopóki warunek jest True
while True:  # Wykonuje się w nieskończoność
    scan()  # Skanuj urządzenia
    time.sleep(5)  # Czekaj 5 sekund
```

### 4. Funkcje

```python
# Definicja funkcji
def calculate_score(device):  # device = parametr
    score = 100  # Zmienna lokalna
    if not device.has_encryption:
        score -= 30  # Odejmij 30 punktów
    return score  # Zwróć wynik

# Wywołanie funkcji
result = calculate_score(my_device)  # Przekaż urządzenie
```

### 5. Warunki (if/else)

```python
if device.has_encryption:  # Jeśli urządzenie ma szyfrowanie
    print("Bezpieczne")  # Wykonaj to
else:  # W przeciwnym razie
    print("Niebezpieczne")  # Wykonaj to
```

---

## Plik 1: `__init__.py`

### 📍 Lokalizacja: `src/__init__.py`

### 🎯 Cel
Ten plik oznacza katalog `src/` jako **pakiet Python**. Bez tego pliku Python nie wie, że `src/` to pakiet i nie można importować modułów.

### 📝 Kod z Wyjaśnieniami

```python
"""
Medical Device Security Scanner

Główny pakiet aplikacji do skanowania i analizy bezpieczeństwa urządzeń medycznych IoT.

Ten pakiet zawiera:
- device.py: Klasa Device reprezentująca urządzenie medyczne
- scanner.py: Główny moduł skanera łączący wszystkie komponenty
- real_scanner.py: Prawdziwy skaner BLE używający biblioteki bleak
- wifi_scanner.py: Skaner WiFi używający nmap
- usb_scanner.py: Skaner USB używający pyusb i pyserial
- nfc_scanner.py: Skaner NFC używający nfcpy i pyscard
"""
```

**Wyjaśnienie:**
- `"""..."""` - to jest **docstring** (dokumentacja modułu)
- Python używa tego do automatycznej dokumentacji
- Opisuje co zawiera pakiet

```python
__version__ = "0.1.0"
```

**Wyjaśnienie:**
- `__version__` - specjalna zmienna w Pythonie
- Przechowuje wersję pakietu
- Można sprawdzić: `import src; print(src.__version__)`

```python
__author__ = "Medical Device Security Scanner Team"
```

**Wyjaśnienie:**
- `__author__` - specjalna zmienna z informacją o autorze
- Używana w dokumentacji

### 🔗 Kiedy jest używany?
- Automatycznie gdy importujesz moduł: `from src import device`
- Python szuka `__init__.py` w katalogu aby wiedzieć, że to pakiet

### 💡 Przykład użycia:
```python
# W innym pliku:
import src  # Python automatycznie wykonuje __init__.py
print(src.__version__)  # Wyświetli: "0.1.0"
```

---

## Plik 2: `device.py`

### 📍 Lokalizacja: `src/device.py`

### 🎯 Cel
Definiuje **klasę Device** - podstawową strukturę danych reprezentującą urządzenie medyczne. **WSZYSTKIE** inne moduły używają tej klasy.

### 📝 Kod z Wyjaśnieniami

#### Importy

```python
from dataclasses import dataclass, field
```

**Wyjaśnienie:**
- `dataclass` - dekorator Python, który automatycznie tworzy metody dla klasy
- `field` - funkcja do definiowania domyślnych wartości w dataclass
- **Dlaczego?** Zamiast pisać `__init__`, `__repr__`, `__eq__` ręcznie, dataclass robi to automatycznie

```python
from datetime import datetime
```

**Wyjaśnienie:**
- `datetime` - klasa do pracy z datami i czasem
- Używamy do przechowywania kiedy urządzenie zostało wykryte

```python
from typing import Optional, List, Dict
```

**Wyjaśnienie:**
- `typing` - moduł do **adnotacji typów** (type hints)
- `Optional[str]` - oznacza "string lub None"
- `List[str]` - oznacza "lista stringów"
- `Dict` - oznacza "słownik"
- **Dlaczego?** Pomaga IDE i innym programistom zrozumieć jakie typy danych są oczekiwane

```python
from enum import Enum
```

**Wyjaśnienie:**
- `Enum` - klasa do tworzenia **wyliczeń** (enumerations)
- Lista stałych wartości (np. dni tygodnia: PONIEDZIAŁEK, WTOREK...)

#### Enum: DeviceType

```python
class DeviceType(Enum):
    """Typy urządzeń medycznych"""
    GLUCOSE_METER = "glucose_meter"  # Glukometr
```

**Wyjaśnienie:**
- `class DeviceType(Enum)` - tworzy klasę wyliczeniową
- `GLUCOSE_METER` - nazwa stałej (używamy w kodzie)
- `"glucose_meter"` - wartość (przechowywana w danych)
- **Przykład użycia:**
  ```python
  device_type = DeviceType.GLUCOSE_METER  # Użycie
  print(device_type.value)  # Wyświetli: "glucose_meter"
  ```

```python
    INSULIN_PUMP = "insulin_pump"    # Pompa insulinowa
    BLOOD_PRESSURE = "blood_pressure"  # Ciśnieniomierz
    PULSE_OXIMETER = "pulse_oximeter"  # Pulsoksymetr
    FITNESS_TRACKER = "fitness_tracker"  # Opaska fitness
    SMARTWATCH = "smartwatch"  # Smartwatch z funkcjami medycznymi
    UNKNOWN = "unknown"  # Nieznany typ
```

**Wyjaśnienie:**
- Każda linia definiuje jeden typ urządzenia
- `UNKNOWN` - używany gdy nie wiemy jaki to typ urządzenia

#### Enum: Protocol

```python
class Protocol(Enum):
    """Protokoły komunikacji"""
    BLE = "BLE"  # Bluetooth Low Energy
    WIFI = "WiFi"
    USB = "USB"
    NFC = "NFC"
```

**Wyjaśnienie:**
- Definiuje protokoły komunikacji
- `BLE` - Bluetooth Low Energy (niskie zużycie energii)
- `WIFI` - sieć bezprzewodowa
- `USB` - port USB
- `NFC` - Near Field Communication (komunikacja bliskiego zasięgu)

#### Klasa Device - Dekorator

```python
@dataclass
class Device:
```

**Wyjaśnienie:**
- `@dataclass` - **dekorator** (modifier dla klasy)
- Automatycznie dodaje:
  - `__init__()` - konstruktor
  - `__repr__()` - reprezentacja tekstowa
  - `__eq__()` - porównywanie obiektów
- **Bez dataclass musiałbyś napisać:**
  ```python
  class Device:
      def __init__(self, mac_address, name, ...):
          self.mac_address = mac_address
          self.name = name
          # ... 20 linii więcej
  ```

#### Klasa Device - Dokumentacja

```python
    """
    Klasa reprezentująca urządzenie medyczne.
    
    Przechowuje wszystkie informacje o urządzeniu:
    - Podstawowe dane (nazwa, MAC, typ)
    - Informacje o bezpieczeństwie
    - Wyniki analizy
    """
```

**Wyjaśnienie:**
- **Docstring** klasy - opisuje co robi klasa
- Używany przez IDE i dokumentację automatyczną

#### Klasa Device - Podstawowe Informacje

```python
    # Podstawowe informacje
    mac_address: str  # Adres MAC urządzenia (unikalny identyfikator)
```

**Wyjaśnienie:**
- `mac_address: str` - **adnotacja typu**: zmienna typu string
- `# ...` - komentarz wyjaśniający
- **MAC Address** - unikalny identyfikator urządzenia sieciowego (np. "AA:BB:CC:DD:EE:FF")
- **Przykład:** `"00:1B:44:11:3A:B7"`

```python
    name: str  # Nazwa urządzenia
```

**Wyjaśnienie:**
- Nazwa urządzenia (np. "GlucoSmart Pro", "iPhone")

```python
    device_type: DeviceType  # Typ urządzenia (glukometr, pompa, etc.)
```

**Wyjaśnienie:**
- Typ urządzenia używając Enum `DeviceType`
- **Przykład:** `DeviceType.GLUCOSE_METER`

```python
    protocol: Protocol  # Protokół komunikacji (BLE, WiFi, etc.)
```

**Wyjaśnienie:**
- Protokół używając Enum `Protocol`
- **Przykład:** `Protocol.BLE`

#### Klasa Device - Informacje o Bezpieczeństwie

```python
    # Informacje o bezpieczeństwie
    has_encryption: bool = False  # Czy używa szyfrowania
```

**Wyjaśnienie:**
- `has_encryption: bool` - zmienna typu boolean (True/False)
- `= False` - **domyślna wartość** (jeśli nie podasz, będzie False)
- `False` - urządzenie NIE używa szyfrowania (domyślnie)

```python
    encryption_type: Optional[str] = None  # Typ szyfrowania
```

**Wyjaśnienie:**
- `Optional[str]` - może być string LUB None
- `= None` - domyślnie None (brak wartości)
- **Przykłady:** `"AES-128"`, `"WPA2"`, `"TLS 1.3"`, `None`

```python
    requires_pairing: bool = False  # Czy wymaga parowania
```

**Wyjaśnienie:**
- Czy urządzenie wymaga parowania (autoryzacji) przed połączeniem
- `False` - każdy może się połączyć (domyślnie)

```python
    security_score: int = 0  # Wynik bezpieczeństwa (0-100)
```

**Wyjaśnienie:**
- Wynik bezpieczeństwa od 0 (niebezpieczne) do 100 (bezpieczne)
- Obliczany przez metodę `calculate_security_score()`

#### Klasa Device - Dodatkowe Informacje

```python
    # Dodatkowe informacje
    rssi: Optional[int] = None  # Siła sygnału (dla Bluetooth)
```

**Wyjaśnienie:**
- `rssi` - Received Signal Strength Indicator
- Siła sygnału Bluetooth (np. -50 dBm = silny sygnał, -90 dBm = słaby)
- `Optional[int]` - może być liczbą całkowitą LUB None

```python
    manufacturer: Optional[str] = None  # Producent
    model: Optional[str] = None  # Model
    firmware_version: Optional[str] = None  # Wersja firmware
```

**Wyjaśnienie:**
- Opcjonalne informacje o urządzeniu
- `None` - nie znamy tej informacji

#### Klasa Device - Timestamps

```python
    # Timestamps
    first_seen: datetime = field(default_factory=datetime.now)
```

**Wyjaśnienie:**
- `first_seen` - kiedy urządzenie zostało wykryte **pierwszy raz**
- `field(default_factory=datetime.now)` - używa funkcji `datetime.now` do utworzenia domyślnej wartości
- **Dlaczego `default_factory`?** Bo `datetime.now()` wykonuje się **w momencie tworzenia obiektu**, nie w momencie definicji klasy

```python
    last_seen: datetime = field(default_factory=datetime.now)
```

**Wyjaśnienie:**
- `last_seen` - kiedy urządzenie zostało wykryte **ostatni raz**
- Aktualizowane przez metodę `update_last_seen()`

#### Klasa Device - Lista Podatności

```python
    # Lista znalezionych podatności
    vulnerabilities: List[str] = field(default_factory=list)
```

**Wyjaśnienie:**
- `vulnerabilities` - lista stringów z podatnościami
- `field(default_factory=list)` - domyślnie pusta lista `[]`
- **Dlaczego `default_factory`?** Bo `list` tworzy nową listę dla każdego obiektu
- **Przykład:** `["Brak szyfrowania", "Brak parowania"]`

#### Klasa Device - Metadane

```python
    # Dodatkowe metadane
    metadata: Dict = field(default_factory=dict)
```

**Wyjaśnienie:**
- `metadata` - słownik z dodatkowymi danymi
- `field(default_factory=dict)` - domyślnie pusty słownik `{}`
- **Przykład:** `{"ip_address": "192.168.1.100", "open_ports": [80, 443]}`

#### Metoda: update_last_seen()

```python
    def update_last_seen(self):
        """Aktualizuje timestamp ostatniego widzenia"""
        self.last_seen = datetime.now()
```

**Wyjaśnienie:**
- `def update_last_seen(self):` - definicja metody
- `self` - odniesienie do obiektu (urządzenia)
- `datetime.now()` - zwraca aktualną datę i czas
- **Użycie:**
  ```python
  device = Device(...)
  device.update_last_seen()  # Aktualizuje last_seen na teraz
  ```

#### Metoda: calculate_security_score()

```python
    def calculate_security_score(self) -> int:
```

**Wyjaśnienie:**
- `-> int` - **adnotacja zwracanego typu**: funkcja zwraca integer
- Metoda oblicza wynik bezpieczeństwa (0-100)

```python
        """
        Oblicza wynik bezpieczeństwa urządzenia (0-100).
        
        Security Score to szybki sposób na ocenę bezpieczeństwa urządzenia.
        Im wyższy wynik, tym bezpieczniejsze urządzenie.
        
        Algorytm:
        - Startujemy od 100 punktów (idealne bezpieczeństwo)
        - Odejmujemy punkty za każdą podatność
        - Brak szyfrowania: -30 punktów (poważna podatność)
        - Brak wymagania parowania: -20 punktów (średnia podatność)
        - Każda znana podatność: -25 punktów (dodatkowe podatności)
        """
```

**Wyjaśnienie:**
- **Docstring metody** - opisuje co robi i jak działa
- Zawiera algorytm obliczania

```python
        score = 100  # Startujemy od maksymalnego wyniku
```

**Wyjaśnienie:**
- Tworzy zmienną lokalną `score` z wartością 100
- To jest **punkt startowy** (idealne bezpieczeństwo)

```python
        # Sprawdź szyfrowanie
        # Brak szyfrowania to poważna podatność - dane mogą być przechwycone
        if not self.has_encryption:
            score -= 30  # -30 punktów za brak szyfrowania
```

**Wyjaśnienie:**
- `if not self.has_encryption:` - **warunek**: jeśli urządzenie NIE ma szyfrowania
- `not` - negacja (odwraca True na False i vice versa)
- `score -= 30` - skrót od `score = score - 30` (odejmij 30 od score)
- **Przykład:**
  - `score = 100`
  - `self.has_encryption = False` (brak szyfrowania)
  - `score -= 30` → `score = 70`

```python
        # Sprawdź autoryzację (parowanie)
        # Brak wymagania parowania oznacza, że każdy może się połączyć
        if not self.requires_pairing:
            score -= 20  # -20 punktów za brak parowania
```

**Wyjaśnienie:**
- Podobnie jak wyżej, ale sprawdza parowanie
- `-20` punktów za brak wymagania parowania

```python
        # Sprawdź znane podatności
        # Każda dodatkowa podatność zmniejsza wynik bezpieczeństwa
        score -= len(self.vulnerabilities) * 25
```

**Wyjaśnienie:**
- `len(self.vulnerabilities)` - zwraca **długość listy** (ile elementów)
- `* 25` - mnoży przez 25 (każda podatność = -25 punktów)
- **Przykład:**
  - `self.vulnerabilities = ["Podatność 1", "Podatność 2"]` (2 podatności)
  - `len(self.vulnerabilities) = 2`
  - `2 * 25 = 50`
  - `score -= 50` → odejmij 50 punktów

```python
        # Upewnij się, że wynik jest w zakresie 0-100
        # max(0, ...) - wynik nie może być ujemny
        # min(100, ...) - wynik nie może przekroczyć 100
        self.security_score = max(0, min(100, score))
```

**Wyjaśnienie:**
- `min(100, score)` - zwraca **mniejszą** wartość (score lub 100)
  - Jeśli `score = 150`, zwróci `100`
  - Jeśli `score = 50`, zwróci `50`
- `max(0, ...)` - zwraca **większą** wartość (0 lub wynik min)
  - Jeśli wynik min = -10, zwróci `0`
  - Jeśli wynik min = 50, zwróci `50`
- **Przykład:**
  - `score = 120` → `min(100, 120) = 100` → `max(0, 100) = 100` ✅
  - `score = -10` → `min(100, -10) = -10` → `max(0, -10) = 0` ✅
  - `score = 50` → `min(100, 50) = 50` → `max(0, 50) = 50` ✅

```python
        return self.security_score
```

**Wyjaśnienie:**
- `return` - zwraca wartość z funkcji
- Zwraca obliczony `security_score`

#### Metoda: add_vulnerability()

```python
    def add_vulnerability(self, vulnerability: str):
        """Dodaje podatność do listy"""
        if vulnerability not in self.vulnerabilities:
            self.vulnerabilities.append(vulnerability)
            # Przelicz wynik bezpieczeństwa
            self.calculate_security_score()
```

**Wyjaśnienie:**
- `vulnerability: str` - parametr typu string
- `if vulnerability not in self.vulnerabilities:` - sprawdza czy podatność **NIE jest** już w liście
- `not in` - operator sprawdzający czy element **nie jest** w kolekcji
- `self.vulnerabilities.append(vulnerability)` - **dodaje** podatność do listy
- `self.calculate_security_score()` - **wywołuje** metodę obliczania score (ponieważ dodałaś nową podatność)
- **Przykład:**
  ```python
  device = Device(...)
  device.add_vulnerability("Brak szyfrowania")
  # device.vulnerabilities = ["Brak szyfrowania"]
  # device.security_score zostanie przeliczony automatycznie
  ```

#### Metoda: to_dict()

```python
    def to_dict(self) -> dict:
        """Konwertuje urządzenie do słownika (dla JSON/API)"""
        import numpy as np
```

**Wyjaśnienie:**
- `-> dict` - zwraca słownik
- `import numpy as np` - import **wewnątrz funkcji** (lokalny import)
- **Dlaczego?** Bo numpy jest używany tylko w tej funkcji, nie w całym pliku

```python
        # Konwertuj metadata na serializowalne typy
        metadata_serializable = {}
```

**Wyjaśnienie:**
- Tworzy pusty słownik dla metadanych
- **Serializowalne** = można zapisać do JSON (nie wszystkie typy Python można zapisać do JSON)

```python
        if self.metadata:
```

**Wyjaśnienie:**
- Sprawdza czy `metadata` **nie jest puste**
- W Pythonie puste kolekcje (`[]`, `{}`, `None`) są **falsy** (traktowane jako False)

```python
            for key, value in self.metadata.items():
```

**Wyjaśnienie:**
- `for key, value in ...` - **pętla for** iterująca przez słownik
- `.items()` - zwraca pary (klucz, wartość)
- **Przykład:**
  ```python
  metadata = {"ip": "192.168.1.1", "port": 80}
  for key, value in metadata.items():
      # Iteracja 1: key="ip", value="192.168.1.1"
      # Iteracja 2: key="port", value=80
  ```

```python
                if isinstance(value, (np.integer, np.floating)):
                    metadata_serializable[key] = value.item()
```

**Wyjaśnienie:**
- `isinstance(value, (np.integer, np.floating))` - sprawdza czy `value` jest typem numpy integer LUB floating
- `isinstance()` - funkcja sprawdzająca typ obiektu
- `value.item()` - konwertuje numpy typ na zwykły Python typ
- **Dlaczego?** JSON nie rozumie typów numpy, tylko zwykłe typy Python

```python
                elif isinstance(value, np.ndarray):
                    metadata_serializable[key] = value.tolist()
```

**Wyjaśnienie:**
- `elif` - **else if** (jeśli poprzedni warunek był False, sprawdź ten)
- `np.ndarray` - tablica numpy
- `.tolist()` - konwertuje tablicę numpy na listę Python

```python
                elif isinstance(value, (np.bool_, bool)):
                    metadata_serializable[key] = bool(value)
```

**Wyjaśnienie:**
- Konwertuje boolean numpy na zwykły boolean Python

```python
                elif isinstance(value, dict):
                    # Rekurencyjnie konwertuj zagnieżdżone słowniki
                    metadata_serializable[key] = self._convert_dict_for_json(value)
```

**Wyjaśnienie:**
- **Rekurencyjnie** - funkcja wywołuje samą siebie
- Jeśli wartość to słownik, konwertuj go używając pomocniczej metody

```python
                elif isinstance(value, (list, tuple)):
                    metadata_serializable[key] = [self._convert_value_for_json(item) for item in value]
```

**Wyjaśnienie:**
- **List comprehension** - skrócony sposób tworzenia listy
- `[wyrażenie for item in kolekcja]` - tworzy listę
- **Równoważne z:**
  ```python
  result = []
  for item in value:
      result.append(self._convert_value_for_json(item))
  ```

```python
                else:
                    metadata_serializable[key] = value
```

**Wyjaśnienie:**
- Jeśli wartość nie pasuje do żadnego warunku, użyj jej bez zmian

```python
        else:
            metadata_serializable = {}
```

**Wyjaśnienie:**
- Jeśli `metadata` było puste, użyj pustego słownika

```python
        return {
            "mac_address": self.mac_address,
            "name": self.name,
            # ... więcej pól
        }
```

**Wyjaśnienie:**
- Zwraca słownik z wszystkimi danymi urządzenia
- Używany do zapisu do JSON lub wysłania przez API

### 🔗 Kiedy jest używany?
- **Zawsze!** Każdy moduł tworzy obiekty `Device`
- Skanery tworzą `Device` dla każdego wykrytego urządzenia
- API i Dashboard wyświetlają obiekty `Device`

### 💡 Przykład użycia:

```python
# Utwórz urządzenie
device = Device(
    mac_address="AA:BB:CC:DD:EE:FF",
    name="GlucoSmart Pro",
    device_type=DeviceType.GLUCOSE_METER,
    protocol=Protocol.BLE,
    has_encryption=True,
    requires_pairing=True
)

# Dodaj podatność
device.add_vulnerability("Słabe hasło")

# Oblicz score
score = device.calculate_security_score()
print(f"Security Score: {score}/100")

# Konwertuj do słownika (dla JSON)
device_dict = device.to_dict()
```

---

## 📝 Podsumowanie Części 1

### Co nauczyłeś się:
1. ✅ Jak działa `__init__.py` (oznacza pakiet)
2. ✅ Jak działa `device.py` (podstawowa klasa)
3. ✅ Koncepty Python: klasy, metody, pętle, warunki
4. ✅ Enum (wyliczenia)
5. ✅ Dataclass (automatyczne metody)
6. ✅ Type hints (adnotacje typów)

### Następne kroki:
W **Części 2** nauczysz się:
- Jak działają skanery (real_scanner.py, wifi_scanner.py)
- Jak skanują urządzenia
- Jak tworzą obiekty Device

---

**Kontynuacja w: PRZEWODNIK_PYTHON_CZESC_2.md**
