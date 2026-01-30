# 💻 Ćwiczenia Programistyczne - Medical Device Scanner

## 📚 Wprowadzenie

Ten plik zawiera ćwiczenia programistyczne, które pomogą Ci zrozumieć kod skanera urządzeń medycznych. Każde ćwiczenie:
- ✅ Jest **samodzielne** - możesz uruchomić je osobno
- ✅ Ma **podpowiedzi** - pomogą Ci napisać kod
- ✅ Ma **testy** - sprawdzą czy Twój kod działa
- ✅ Jest **progresywne** - od prostych do bardziej złożonych

**Jak używać:**
1. Przeczytaj zadanie
2. Spójrz na podpowiedzi (jeśli potrzebujesz)
3. Napisz kod
4. Uruchom testy
5. Porównaj z przykładowym rozwiązaniem

---

## 🎯 Ćwiczenie 1: Klasa Device - Podstawy

### 📝 Zadanie

Stwórz klasę `Device`, która przechowuje podstawowe informacje o urządzeniu medycznym.

**Wymagania:**
- `mac_address` (str) - adres MAC urządzenia
- `name` (str) - nazwa urządzenia
- `security_score` (int) - wynik bezpieczeństwa (0-100)
- `has_encryption` (bool) - czy używa szyfrowania

### 💡 Podpowiedzi

```python
# Użyj dataclass dla prostoty
from dataclasses import dataclass

@dataclass
class Device:
    # Dodaj pola tutaj
    pass
```

### ✅ Test

```python
# test_exercise_1.py
def test_device():
    device = Device(
        mac_address="AA:BB:CC:DD:EE:FF",
        name="Glukometr XYZ",
        security_score=75,
        has_encryption=True
    )
    
    assert device.mac_address == "AA:BB:CC:DD:EE:FF"
    assert device.name == "Glukometr XYZ"
    assert device.security_score == 75
    assert device.has_encryption == True
    print("✅ Test 1: PASSED!")

if __name__ == "__main__":
    test_device()
```

### 🔧 Przykładowe Rozwiązanie

<details>
<summary>Kliknij aby zobaczyć rozwiązanie</summary>

```python
from dataclasses import dataclass

@dataclass
class Device:
    mac_address: str
    name: str
    security_score: int
    has_encryption: bool
```

</details>

---

## 🎯 Ćwiczenie 2: Obliczanie Security Score

### 📝 Zadanie

Dodaj metodę `calculate_security_score()` do klasy `Device`, która oblicza wynik bezpieczeństwa na podstawie:
- Startujemy od 100 punktów
- Brak szyfrowania: -30 punktów
- Każda podatność: -25 punktów
- Wynik musi być w zakresie 0-100

**Dodatkowe pola:**
- `vulnerabilities` (List[str]) - lista podatności

### 💡 Podpowiedzi

```python
def calculate_security_score(self) -> int:
    score = 100  # Start od 100
    
    # Sprawdź szyfrowanie
    if not self.has_encryption:
        score -= 30
    
    # Odejmij za podatności
    score -= len(self.vulnerabilities) * 25
    
    # Upewnij się że wynik jest w zakresie 0-100
    return max(0, min(100, score))
```

### ✅ Test

```python
# test_exercise_2.py
def test_calculate_security_score():
    # Test 1: Urządzenie z szyfrowaniem, bez podatności
    device1 = Device(
        mac_address="AA:BB:CC:DD:EE:FF",
        name="Bezpieczne urządzenie",
        security_score=0,  # Będzie przeliczony
        has_encryption=True,
        vulnerabilities=[]
    )
    assert device1.calculate_security_score() == 100
    
    # Test 2: Urządzenie bez szyfrowania
    device2 = Device(
        mac_address="11:22:33:44:55:66",
        name="Niebezpieczne urządzenie",
        security_score=0,
        has_encryption=False,
        vulnerabilities=[]
    )
    assert device2.calculate_security_score() == 70
    
    # Test 3: Urządzenie z podatnościami
    device3 = Device(
        mac_address="FF:EE:DD:CC:BB:AA",
        name="Urządzenie z podatnościami",
        security_score=0,
        has_encryption=True,
        vulnerabilities=["CVE-2023-1234", "CVE-2023-5678"]
    )
    assert device3.calculate_security_score() == 50
    
    print("✅ Test 2: PASSED!")

if __name__ == "__main__":
    test_calculate_security_score()
```

### 🔧 Przykładowe Rozwiązanie

<details>
<summary>Kliknij aby zobaczyć rozwiązanie</summary>

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class Device:
    mac_address: str
    name: str
    security_score: int
    has_encryption: bool
    vulnerabilities: List[str] = field(default_factory=list)
    
    def calculate_security_score(self) -> int:
        score = 100
        
        if not self.has_encryption:
            score -= 30
        
        score -= len(self.vulnerabilities) * 25
        
        return max(0, min(100, score))
```

</details>

---

## 🎯 Ćwiczenie 3: Enum dla Typów Urządzeń

### 📝 Zadanie

Stwórz enum `DeviceType` z typami urządzeń medycznych:
- `GLUCOSE_METER` - glukometr
- `INSULIN_PUMP` - pompa insulinowa
- `BLOOD_PRESSURE` - ciśnieniomierz
- `UNKNOWN` - nieznany typ

Dodaj pole `device_type` do klasy `Device`.

### 💡 Podpowiedzi

```python
from enum import Enum

class DeviceType(Enum):
    GLUCOSE_METER = "glucose_meter"
    INSULIN_PUMP = "insulin_pump"
    # Dodaj pozostałe typy
```

### ✅ Test

```python
# test_exercise_3.py
def test_device_type():
    device = Device(
        mac_address="AA:BB:CC:DD:EE:FF",
        name="Glukometr",
        security_score=100,
        has_encryption=True,
        device_type=DeviceType.GLUCOSE_METER
    )
    
    assert device.device_type == DeviceType.GLUCOSE_METER
    assert device.device_type.value == "glucose_meter"
    print("✅ Test 3: PASSED!")

if __name__ == "__main__":
    test_device_type()
```

### 🔧 Przykładowe Rozwiązanie

<details>
<summary>Kliknij aby zobaczyć rozwiązanie</summary>

```python
from enum import Enum

class DeviceType(Enum):
    GLUCOSE_METER = "glucose_meter"
    INSULIN_PUMP = "insulin_pump"
    BLOOD_PRESSURE = "blood_pressure"
    UNKNOWN = "unknown"

@dataclass
class Device:
    mac_address: str
    name: str
    security_score: int
    has_encryption: bool
    device_type: DeviceType
    vulnerabilities: List[str] = field(default_factory=list)
```

</details>

---

## 🎯 Ćwiczenie 4: Metoda do Dodawania Podatności

### 📝 Zadanie

Dodaj metodę `add_vulnerability()` do klasy `Device`, która:
- Dodaje podatność do listy
- Automatycznie przelicza `security_score`
- Nie dodaje duplikatów

### 💡 Podpowiedzi

```python
def add_vulnerability(self, vulnerability: str):
    # Sprawdź czy już istnieje
    if vulnerability not in self.vulnerabilities:
        self.vulnerabilities.append(vulnerability)
        # Przepisz security_score używając calculate_security_score()
        self.security_score = self.calculate_security_score()
```

### ✅ Test

```python
# test_exercise_4.py
def test_add_vulnerability():
    device = Device(
        mac_address="AA:BB:CC:DD:EE:FF",
        name="Test Device",
        security_score=100,
        has_encryption=True,
        device_type=DeviceType.UNKNOWN,
        vulnerabilities=[]
    )
    
    # Dodaj pierwszą podatność
    device.add_vulnerability("CVE-2023-1234")
    assert len(device.vulnerabilities) == 1
    assert device.security_score == 75  # 100 - 25
    
    # Spróbuj dodać duplikat
    device.add_vulnerability("CVE-2023-1234")
    assert len(device.vulnerabilities) == 1  # Nie powinno się dodać
    
    # Dodaj drugą podatność
    device.add_vulnerability("CVE-2023-5678")
    assert len(device.vulnerabilities) == 2
    assert device.security_score == 50  # 100 - 25 - 25
    
    print("✅ Test 4: PASSED!")

if __name__ == "__main__":
    test_add_vulnerability()
```

### 🔧 Przykładowe Rozwiązanie

<details>
<summary>Kliknij aby zobaczyć rozwiązanie</summary>

```python
def add_vulnerability(self, vulnerability: str):
    if vulnerability not in self.vulnerabilities:
        self.vulnerabilities.append(vulnerability)
        self.security_score = self.calculate_security_score()
```

</details>

---

## 🎯 Ćwiczenie 5: Analizator Szyfrowania - Podstawy

### 📝 Zadanie

Stwórz klasę `EncryptionAnalyzer` z metodą `analyze()`, która:
- Przyjmuje `encryption_type` (str) i `has_encryption` (bool)
- Zwraca słownik z wynikami:
  - `is_weak` (bool) - czy szyfrowanie jest słabe
  - `score` (int) - wynik 0-100
  - `issues` (List[str]) - lista problemów

**Reguły:**
- Brak szyfrowania: `is_weak=True`, `score=0`
- TLS 1.0 lub 1.1: `is_weak=True`, `score=30`
- TLS 1.2: `is_weak=False`, `score=70`
- TLS 1.3: `is_weak=False`, `score=100`

### 💡 Podpowiedzi

```python
class EncryptionAnalyzer:
    def analyze(self, encryption_type: str, has_encryption: bool) -> dict:
        if not has_encryption or not encryption_type:
            return {
                "is_weak": True,
                "score": 0,
                "issues": ["Brak szyfrowania"]
            }
        
        encryption_lower = encryption_type.lower()
        issues = []
        score = 0
        
        # Sprawdź wersję TLS
        if "tls 1.3" in encryption_lower:
            score = 100
        elif "tls 1.2" in encryption_lower:
            score = 70
        elif "tls 1.1" in encryption_lower or "tls 1.0" in encryption_lower:
            score = 30
            issues.append("Przestarzała wersja TLS")
        
        return {
            "is_weak": score < 50,
            "score": score,
            "issues": issues
        }
```

### ✅ Test

```python
# test_exercise_5.py
def test_encryption_analyzer():
    analyzer = EncryptionAnalyzer()
    
    # Test 1: Brak szyfrowania
    result1 = analyzer.analyze("", False)
    assert result1["is_weak"] == True
    assert result1["score"] == 0
    assert "Brak szyfrowania" in result1["issues"]
    
    # Test 2: TLS 1.3
    result2 = analyzer.analyze("TLS 1.3", True)
    assert result2["is_weak"] == False
    assert result2["score"] == 100
    
    # Test 3: TLS 1.0
    result3 = analyzer.analyze("TLS 1.0", True)
    assert result3["is_weak"] == True
    assert result3["score"] == 30
    assert "Przestarzała wersja TLS" in result3["issues"]
    
    print("✅ Test 5: PASSED!")

if __name__ == "__main__":
    test_encryption_analyzer()
```

### 🔧 Przykładowe Rozwiązanie

<details>
<summary>Kliknij aby zobaczyć rozwiązanie</summary>

```python
from typing import List, Optional

class EncryptionAnalyzer:
    def analyze(self, encryption_type: Optional[str], has_encryption: bool) -> dict:
        if not has_encryption or not encryption_type:
            return {
                "is_weak": True,
                "score": 0,
                "issues": ["Brak szyfrowania"]
            }
        
        encryption_lower = encryption_type.lower()
        issues = []
        score = 0
        
        if "tls 1.3" in encryption_lower:
            score = 100
        elif "tls 1.2" in encryption_lower:
            score = 70
        elif "tls 1.1" in encryption_lower or "tls 1.0" in encryption_lower:
            score = 30
            issues.append("Przestarzała wersja TLS")
        
        return {
            "is_weak": score < 50,
            "score": score,
            "issues": issues
        }
```

</details>

---

## 🎯 Ćwiczenie 6: Prosty Skaner - Symulacja

### 📝 Zadanie

Stwórz klasę `SimpleScanner`, która symuluje skanowanie urządzeń:
- Metoda `scan()` zwraca listę urządzeń (symulowanych)
- Każde urządzenie ma losowy security_score (50-100)
- Każde urządzenie ma losowy `has_encryption` (True/False)

**Wymagania:**
- Zwróć 3-5 urządzeń
- Użyj `random` do losowania

### 💡 Podpowiedzi

```python
import random

class SimpleScanner:
    def scan(self) -> List[Device]:
        devices = []
        names = ["Glukometr A", "Pompa B", "Monitor C", "Urządzenie D"]
        
        for i, name in enumerate(names):
            device = Device(
                mac_address=f"AA:BB:CC:DD:EE:{i:02X}",
                name=name,
                security_score=random.randint(50, 100),
                has_encryption=random.choice([True, False]),
                device_type=DeviceType.UNKNOWN,
                vulnerabilities=[]
            )
            devices.append(device)
        
        return devices
```

### ✅ Test

```python
# test_exercise_6.py
def test_simple_scanner():
    scanner = SimpleScanner()
    devices = scanner.scan()
    
    assert len(devices) >= 3
    assert len(devices) <= 5
    
    for device in devices:
        assert isinstance(device, Device)
        assert 50 <= device.security_score <= 100
        assert isinstance(device.has_encryption, bool)
    
    print("✅ Test 6: PASSED!")

if __name__ == "__main__":
    test_simple_scanner()
```

### 🔧 Przykładowe Rozwiązanie

<details>
<summary>Kliknij aby zobaczyć rozwiązanie</summary>

```python
import random
from typing import List

class SimpleScanner:
    def scan(self) -> List[Device]:
        devices = []
        names = ["Glukometr A", "Pompa B", "Monitor C", "Urządzenie D", "Sensor E"]
        
        for i, name in enumerate(names):
            device = Device(
                mac_address=f"AA:BB:CC:DD:EE:{i:02X}",
                name=name,
                security_score=random.randint(50, 100),
                has_encryption=random.choice([True, False]),
                device_type=DeviceType.UNKNOWN,
                vulnerabilities=[]
            )
            devices.append(device)
        
        return devices
```

</details>

---

## 🎯 Ćwiczenie 7: Filtrowanie Urządzeń

### 📝 Zadanie

Stwórz funkcję `filter_devices()`, która filtruje listę urządzeń według:
- `min_score` (int) - minimalny security_score
- `has_encryption` (bool) - czy ma szyfrowanie
- `device_type` (DeviceType) - typ urządzenia

### 💡 Podpowiedzi

```python
def filter_devices(
    devices: List[Device],
    min_score: int = 0,
    has_encryption: Optional[bool] = None,
    device_type: Optional[DeviceType] = None
) -> List[Device]:
    filtered = []
    
    for device in devices:
        # Sprawdź min_score
        if device.security_score < min_score:
            continue
        
        # Sprawdź has_encryption
        if has_encryption is not None and device.has_encryption != has_encryption:
            continue
        
        # Sprawdź device_type
        if device_type is not None and device.device_type != device_type:
            continue
        
        filtered.append(device)
    
    return filtered
```

### ✅ Test

```python
# test_exercise_7.py
def test_filter_devices():
    devices = [
        Device("AA:BB:CC:DD:EE:01", "Device 1", 80, True, DeviceType.GLUCOSE_METER, []),
        Device("AA:BB:CC:DD:EE:02", "Device 2", 60, False, DeviceType.INSULIN_PUMP, []),
        Device("AA:BB:CC:DD:EE:03", "Device 3", 90, True, DeviceType.GLUCOSE_METER, []),
    ]
    
    # Test 1: Filtruj po min_score
    filtered1 = filter_devices(devices, min_score=70)
    assert len(filtered1) == 2
    
    # Test 2: Filtruj po has_encryption
    filtered2 = filter_devices(devices, has_encryption=True)
    assert len(filtered2) == 2
    
    # Test 3: Filtruj po device_type
    filtered3 = filter_devices(devices, device_type=DeviceType.GLUCOSE_METER)
    assert len(filtered3) == 2
    
    print("✅ Test 7: PASSED!")

if __name__ == "__main__":
    test_filter_devices()
```

### 🔧 Przykładowe Rozwiązanie

<details>
<summary>Kliknij aby zobaczyć rozwiązanie</summary>

```python
from typing import List, Optional

def filter_devices(
    devices: List[Device],
    min_score: int = 0,
    has_encryption: Optional[bool] = None,
    device_type: Optional[DeviceType] = None
) -> List[Device]:
    filtered = []
    
    for device in devices:
        if device.security_score < min_score:
            continue
        
        if has_encryption is not None and device.has_encryption != has_encryption:
            continue
        
        if device_type is not None and device.device_type != device_type:
            continue
        
        filtered.append(device)
    
    return filtered
```

</details>

---

## 🎯 Ćwiczenie 8: Statystyki Urządzeń

### 📝 Zadanie

Stwórz funkcję `calculate_statistics()`, która oblicza statystyki z listy urządzeń:
- `total_devices` - całkowita liczba urządzeń
- `avg_security_score` - średni security_score
- `devices_with_encryption` - liczba urządzeń z szyfrowaniem
- `high_risk_devices` - liczba urządzeń z score < 50

### 💡 Podpowiedzi

```python
def calculate_statistics(devices: List[Device]) -> dict:
    if not devices:
        return {
            "total_devices": 0,
            "avg_security_score": 0,
            "devices_with_encryption": 0,
            "high_risk_devices": 0
        }
    
    total = len(devices)
    avg_score = sum(d.security_score for d in devices) / total
    with_encryption = sum(1 for d in devices if d.has_encryption)
    high_risk = sum(1 for d in devices if d.security_score < 50)
    
    return {
        "total_devices": total,
        "avg_security_score": round(avg_score, 2),
        "devices_with_encryption": with_encryption,
        "high_risk_devices": high_risk
    }
```

### ✅ Test

```python
# test_exercise_8.py
def test_calculate_statistics():
    devices = [
        Device("AA:BB:CC:DD:EE:01", "Device 1", 80, True, DeviceType.UNKNOWN, []),
        Device("AA:BB:CC:DD:EE:02", "Device 2", 40, False, DeviceType.UNKNOWN, []),
        Device("AA:BB:CC:DD:EE:03", "Device 3", 90, True, DeviceType.UNKNOWN, []),
    ]
    
    stats = calculate_statistics(devices)
    
    assert stats["total_devices"] == 3
    assert stats["avg_security_score"] == 70.0
    assert stats["devices_with_encryption"] == 2
    assert stats["high_risk_devices"] == 1
    
    print("✅ Test 8: PASSED!")

if __name__ == "__main__":
    test_calculate_statistics()
```

### 🔧 Przykładowe Rozwiązanie

<details>
<summary>Kliknij aby zobaczyć rozwiązanie</summary>

```python
def calculate_statistics(devices: List[Device]) -> dict:
    if not devices:
        return {
            "total_devices": 0,
            "avg_security_score": 0,
            "devices_with_encryption": 0,
            "high_risk_devices": 0
        }
    
    total = len(devices)
    avg_score = sum(d.security_score for d in devices) / total
    with_encryption = sum(1 for d in devices if d.has_encryption)
    high_risk = sum(1 for d in devices if d.security_score < 50)
    
    return {
        "total_devices": total,
        "avg_security_score": round(avg_score, 2),
        "devices_with_encryption": with_encryption,
        "high_risk_devices": high_risk
    }
```

</details>

---

## 🎯 Ćwiczenie 9: Prosty Scanner Manager

### 📝 Zadanie

Stwórz klasę `ScannerManager`, która:
- Przechowuje listę skanerów
- Ma metodę `add_scanner(name, scanner)` - dodaje skaner
- Ma metodę `scan_all()` - uruchamia wszystkie skanery i zwraca wszystkie urządzenia
- Ma metodę `get_statistics()` - zwraca statystyki wszystkich urządzeń

### 💡 Podpowiedzi

```python
class ScannerManager:
    def __init__(self):
        self.scanners = {}  # Słownik: name -> scanner
    
    def add_scanner(self, name: str, scanner):
        self.scanners[name] = scanner
    
    def scan_all(self) -> List[Device]:
        all_devices = []
        for name, scanner in self.scanners.items():
            devices = scanner.scan()
            all_devices.extend(devices)
        return all_devices
    
    def get_statistics(self) -> dict:
        devices = self.scan_all()
        return calculate_statistics(devices)
```

### ✅ Test

```python
# test_exercise_9.py
def test_scanner_manager():
    manager = ScannerManager()
    
    # Dodaj skanery
    scanner1 = SimpleScanner()
    scanner2 = SimpleScanner()
    manager.add_scanner("scanner1", scanner1)
    manager.add_scanner("scanner2", scanner2)
    
    # Skanuj wszystkie
    devices = manager.scan_all()
    assert len(devices) >= 6  # Co najmniej 3 z każdego skanera
    
    # Pobierz statystyki
    stats = manager.get_statistics()
    assert stats["total_devices"] >= 6
    
    print("✅ Test 9: PASSED!")

if __name__ == "__main__":
    test_scanner_manager()
```

### 🔧 Przykładowe Rozwiązanie

<details>
<summary>Kliknij aby zobaczyć rozwiązanie</summary>

```python
from typing import Dict

class ScannerManager:
    def __init__(self):
        self.scanners: Dict[str, SimpleScanner] = {}
    
    def add_scanner(self, name: str, scanner: SimpleScanner):
        self.scanners[name] = scanner
    
    def scan_all(self) -> List[Device]:
        all_devices = []
        for scanner in self.scanners.values():
            devices = scanner.scan()
            all_devices.extend(devices)
        return all_devices
    
    def get_statistics(self) -> dict:
        devices = self.scan_all()
        return calculate_statistics(devices)
```

</details>

---

## 🎯 Ćwiczenie 10: Eksport do JSON

### 📝 Zadanie

Dodaj metodę `to_dict()` do klasy `Device`, która konwertuje urządzenie na słownik (do JSON).

Dodaj funkcję `export_to_json()`, która eksportuje listę urządzeń do pliku JSON.

### 💡 Podpowiedzi

```python
# W klasie Device
def to_dict(self) -> dict:
    return {
        "mac_address": self.mac_address,
        "name": self.name,
        "security_score": self.security_score,
        "has_encryption": self.has_encryption,
        "device_type": self.device_type.value,
        "vulnerabilities": self.vulnerabilities
    }

# Funkcja eksportu
import json

def export_to_json(devices: List[Device], filename: str):
    data = [device.to_dict() for device in devices]
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

### ✅ Test

```python
# test_exercise_10.py
import os
import json

def test_export_to_json():
    devices = [
        Device("AA:BB:CC:DD:EE:01", "Device 1", 80, True, DeviceType.GLUCOSE_METER, []),
        Device("AA:BB:CC:DD:EE:02", "Device 2", 60, False, DeviceType.INSULIN_PUMP, ["CVE-123"]),
    ]
    
    filename = "test_devices.json"
    export_to_json(devices, filename)
    
    # Sprawdź czy plik istnieje
    assert os.path.exists(filename)
    
    # Sprawdź zawartość
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert len(data) == 2
    assert data[0]["name"] == "Device 1"
    assert data[1]["vulnerabilities"] == ["CVE-123"]
    
    # Usuń plik testowy
    os.remove(filename)
    
    print("✅ Test 10: PASSED!")

if __name__ == "__main__":
    test_export_to_json()
```

### 🔧 Przykładowe Rozwiązanie

<details>
<summary>Kliknij aby zobaczyć rozwiązanie</summary>

```python
import json
from typing import List

# W klasie Device
def to_dict(self) -> dict:
    return {
        "mac_address": self.mac_address,
        "name": self.name,
        "security_score": self.security_score,
        "has_encryption": self.has_encryption,
        "device_type": self.device_type.value,
        "vulnerabilities": self.vulnerabilities
    }

# Funkcja eksportu
def export_to_json(devices: List[Device], filename: str):
    data = [device.to_dict() for device in devices]
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
```

</details>

---

## 🎯 Ćwiczenie 11: Kompletny Program - Mini Scanner

### 📝 Zadanie

Stwórz kompletny program, który:
1. Tworzy `ScannerManager`
2. Dodaje kilka skanerów
3. Skanuje wszystkie urządzenia
4. Filtruje urządzenia wysokiego ryzyka (score < 50)
5. Wyświetla statystyki
6. Eksportuje wyniki do JSON

### 💡 Podpowiedzi

```python
def main():
    # 1. Utwórz manager
    manager = ScannerManager()
    
    # 2. Dodaj skanery
    scanner1 = SimpleScanner()
    scanner2 = SimpleScanner()
    manager.add_scanner("scanner1", scanner1)
    manager.add_scanner("scanner2", scanner2)
    
    # 3. Skanuj
    all_devices = manager.scan_all()
    print(f"Znaleziono {len(all_devices)} urządzeń")
    
    # 4. Filtruj wysokie ryzyko
    high_risk = filter_devices(all_devices, min_score=0)
    high_risk = [d for d in high_risk if d.security_score < 50]
    print(f"Urządzenia wysokiego ryzyka: {len(high_risk)}")
    
    # 5. Statystyki
    stats = manager.get_statistics()
    print(f"Statystyki: {stats}")
    
    # 6. Eksport
    export_to_json(all_devices, "devices.json")
    print("Eksportowano do devices.json")

if __name__ == "__main__":
    main()
```

### ✅ Test

```python
# test_exercise_11.py
def test_complete_program():
    # Uruchom program
    main()
    
    # Sprawdź czy plik został utworzony
    assert os.path.exists("devices.json")
    
    # Sprawdź zawartość
    with open("devices.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert len(data) > 0
    print("✅ Test 11: PASSED!")

if __name__ == "__main__":
    test_complete_program()
```

### 🔧 Przykładowe Rozwiązanie

<details>
<summary>Kliknij aby zobaczyć rozwiązanie</summary>

```python
def main():
    print("🔍 Medical Device Scanner - Mini Version")
    print("=" * 50)
    
    # 1. Utwórz manager
    manager = ScannerManager()
    
    # 2. Dodaj skanery
    scanner1 = SimpleScanner()
    scanner2 = SimpleScanner()
    manager.add_scanner("scanner1", scanner1)
    manager.add_scanner("scanner2", scanner2)
    
    # 3. Skanuj
    print("\n📡 Skanowanie urządzeń...")
    all_devices = manager.scan_all()
    print(f"✅ Znaleziono {len(all_devices)} urządzeń")
    
    # 4. Filtruj wysokie ryzyko
    high_risk = [d for d in all_devices if d.security_score < 50]
    print(f"⚠️  Urządzenia wysokiego ryzyka: {len(high_risk)}")
    
    # 5. Statystyki
    stats = manager.get_statistics()
    print(f"\n📊 Statystyki:")
    print(f"   - Całkowita liczba: {stats['total_devices']}")
    print(f"   - Średni security score: {stats['avg_security_score']}")
    print(f"   - Z szyfrowaniem: {stats['devices_with_encryption']}")
    print(f"   - Wysokie ryzyko: {stats['high_risk_devices']}")
    
    # 6. Eksport
    export_to_json(all_devices, "devices.json")
    print(f"\n💾 Eksportowano {len(all_devices)} urządzeń do devices.json")

if __name__ == "__main__":
    main()
```

</details>

---

## 🎯 Ćwiczenie 12: Obsługa Błędów

### 📝 Zadanie

Dodaj obsługę błędów do klasy `ScannerManager`:
- Jeśli skaner zwróci pustą listę, wyświetl ostrzeżenie
- Jeśli skaner rzuci wyjątek, złap go i kontynuuj z innymi skanerami
- Zwróć informację o błędach w statystykach

### 💡 Podpowiedzi

```python
def scan_all(self) -> List[Device]:
    all_devices = []
    errors = []
    
    for name, scanner in self.scanners.items():
        try:
            devices = scanner.scan()
            if not devices:
                print(f"⚠️  {name}: Brak urządzeń")
            all_devices.extend(devices)
        except Exception as e:
            errors.append(f"{name}: {str(e)}")
            print(f"❌ Błąd w {name}: {e}")
    
    return all_devices
```

### ✅ Test

```python
# test_exercise_12.py
class BrokenScanner:
    def scan(self):
        raise Exception("Scanner broken!")

def test_error_handling():
    manager = ScannerManager()
    manager.add_scanner("good", SimpleScanner())
    manager.add_scanner("broken", BrokenScanner())
    
    devices = manager.scan_all()
    assert len(devices) > 0  # Powinno działać mimo błędu
    
    print("✅ Test 12: PASSED!")

if __name__ == "__main__":
    test_error_handling()
```

### 🔧 Przykładowe Rozwiązanie

<details>
<summary>Kliknij aby zobaczyć rozwiązanie</summary>

```python
class ScannerManager:
    def __init__(self):
        self.scanners: Dict[str, SimpleScanner] = {}
        self.errors: List[str] = []
    
    def scan_all(self) -> List[Device]:
        all_devices = []
        self.errors = []
        
        for name, scanner in self.scanners.items():
            try:
                devices = scanner.scan()
                if not devices:
                    print(f"⚠️  {name}: Brak urządzeń")
                all_devices.extend(devices)
            except Exception as e:
                error_msg = f"{name}: {str(e)}"
                self.errors.append(error_msg)
                print(f"❌ Błąd w {name}: {e}")
        
        return all_devices
```

</details>

---

## 🎯 Ćwiczenie 13: Sortowanie Urządzeń

### 📝 Zadanie

Stwórz funkcję `sort_devices()`, która sortuje urządzenia według:
- `security_score` (domyślnie - od najwyższego)
- `name` (alfabetycznie)
- `mac_address`

### 💡 Podpowiedzi

```python
def sort_devices(
    devices: List[Device],
    by: str = "security_score",
    reverse: bool = True
) -> List[Device]:
    if by == "security_score":
        return sorted(devices, key=lambda d: d.security_score, reverse=reverse)
    elif by == "name":
        return sorted(devices, key=lambda d: d.name, reverse=reverse)
    elif by == "mac_address":
        return sorted(devices, key=lambda d: d.mac_address, reverse=reverse)
    return devices
```

### ✅ Test

```python
# test_exercise_13.py
def test_sort_devices():
    devices = [
        Device("CC:CC:CC:CC:CC:CC", "Device C", 60, True, DeviceType.UNKNOWN, []),
        Device("AA:AA:AA:AA:AA:AA", "Device A", 80, True, DeviceType.UNKNOWN, []),
        Device("BB:BB:BB:BB:BB:BB", "Device B", 70, True, DeviceType.UNKNOWN, []),
    ]
    
    # Sortuj po security_score
    sorted_by_score = sort_devices(devices, by="security_score")
    assert sorted_by_score[0].security_score == 80
    assert sorted_by_score[-1].security_score == 60
    
    # Sortuj po name
    sorted_by_name = sort_devices(devices, by="name")
    assert sorted_by_name[0].name == "Device A"
    
    print("✅ Test 13: PASSED!")

if __name__ == "__main__":
    test_sort_devices()
```

### 🔧 Przykładowe Rozwiązanie

<details>
<summary>Kliknij aby zobaczyć rozwiązanie</summary>

```python
def sort_devices(
    devices: List[Device],
    by: str = "security_score",
    reverse: bool = True
) -> List[Device]:
    if by == "security_score":
        return sorted(devices, key=lambda d: d.security_score, reverse=reverse)
    elif by == "name":
        return sorted(devices, key=lambda d: d.name, reverse=reverse)
    elif by == "mac_address":
        return sorted(devices, key=lambda d: d.mac_address, reverse=reverse)
    return devices
```

</details>

---

## 🎯 Ćwiczenie 14: Grupowanie Urządzeń

### 📝 Zadanie

Stwórz funkcję `group_devices()`, która grupuje urządzenia według:
- `device_type` - grupa według typu urządzenia
- `has_encryption` - grupa według szyfrowania
- `risk_level` - grupa według poziomu ryzyka (high: <50, medium: 50-75, low: >75)

Zwróć słownik z kluczami jako nazwy grup i wartościami jako listy urządzeń.

### 💡 Podpowiedzi

```python
def group_devices(devices: List[Device], by: str = "device_type") -> dict:
    groups = {}
    
    for device in devices:
        if by == "device_type":
            key = device.device_type.value
        elif by == "has_encryption":
            key = "encrypted" if device.has_encryption else "unencrypted"
        elif by == "risk_level":
            if device.security_score < 50:
                key = "high"
            elif device.security_score < 75:
                key = "medium"
            else:
                key = "low"
        else:
            continue
        
        if key not in groups:
            groups[key] = []
        groups[key].append(device)
    
    return groups
```

### ✅ Test

```python
# test_exercise_14.py
def test_group_devices():
    devices = [
        Device("AA:AA:AA:AA:AA:AA", "Device 1", 40, True, DeviceType.GLUCOSE_METER, []),
        Device("BB:BB:BB:BB:BB:BB", "Device 2", 60, False, DeviceType.INSULIN_PUMP, []),
        Device("CC:CC:CC:CC:CC:CC", "Device 3", 90, True, DeviceType.GLUCOSE_METER, []),
    ]
    
    # Grupuj po device_type
    grouped = group_devices(devices, by="device_type")
    assert "glucose_meter" in grouped
    assert len(grouped["glucose_meter"]) == 2
    
    # Grupuj po risk_level
    grouped_risk = group_devices(devices, by="risk_level")
    assert "high" in grouped_risk
    assert "low" in grouped_risk
    
    print("✅ Test 14: PASSED!")

if __name__ == "__main__":
    test_group_devices()
```

### 🔧 Przykładowe Rozwiązanie

<details>
<summary>Kliknij aby zobaczyć rozwiązanie</summary>

```python
from typing import Dict

def group_devices(devices: List[Device], by: str = "device_type") -> Dict[str, List[Device]]:
    groups = {}
    
    for device in devices:
        if by == "device_type":
            key = device.device_type.value
        elif by == "has_encryption":
            key = "encrypted" if device.has_encryption else "unencrypted"
        elif by == "risk_level":
            if device.security_score < 50:
                key = "high"
            elif device.security_score < 75:
                key = "medium"
            else:
                key = "low"
        else:
            continue
        
        if key not in groups:
            groups[key] = []
        groups[key].append(device)
    
    return groups
```

</details>

---

## 🎯 Ćwiczenie 15: Wyszukiwanie Urządzeń

### 📝 Zadanie

Stwórz funkcję `search_devices()`, która wyszukuje urządzenia według:
- `query` (str) - wyszukuje w nazwie lub MAC address
- Zwraca listę pasujących urządzeń

### 💡 Podpowiedzi

```python
def search_devices(devices: List[Device], query: str) -> List[Device]:
    query_lower = query.lower()
    results = []
    
    for device in devices:
        if query_lower in device.name.lower() or query_lower in device.mac_address.lower():
            results.append(device)
    
    return results
```

### ✅ Test

```python
# test_exercise_15.py
def test_search_devices():
    devices = [
        Device("AA:BB:CC:DD:EE:FF", "Glukometr XYZ", 80, True, DeviceType.GLUCOSE_METER, []),
        Device("11:22:33:44:55:66", "Pompa ABC", 70, False, DeviceType.INSULIN_PUMP, []),
        Device("FF:EE:DD:CC:BB:AA", "Monitor DEF", 90, True, DeviceType.UNKNOWN, []),
    ]
    
    # Wyszukaj po nazwie
    results1 = search_devices(devices, "Glukometr")
    assert len(results1) == 1
    assert results1[0].name == "Glukometr XYZ"
    
    # Wyszukaj po MAC
    results2 = search_devices(devices, "AA:BB")
    assert len(results2) == 1
    
    print("✅ Test 15: PASSED!")

if __name__ == "__main__":
    test_search_devices()
```

### 🔧 Przykładowe Rozwiązanie

<details>
<summary>Kliknij aby zobaczyć rozwiązanie</summary>

```python
def search_devices(devices: List[Device], query: str) -> List[Device]:
    query_lower = query.lower()
    results = []
    
    for device in devices:
        if query_lower in device.name.lower() or query_lower in device.mac_address.lower():
            results.append(device)
    
    return results
```

</details>

---

## 📚 Podsumowanie

Gratulacje! Ukończyłeś wszystkie ćwiczenia! 🎉

### Co się nauczyłeś:

1. ✅ **Klasy i dataclass** - jak tworzyć modele danych
2. ✅ **Enum** - jak używać typów wyliczeniowych
3. ✅ **Metody** - jak dodawać funkcjonalność do klas
4. ✅ **Listy i filtrowanie** - jak pracować z kolekcjami
5. ✅ **Statystyki** - jak obliczać dane z list
6. ✅ **Manager pattern** - jak zarządzać wieloma obiektami
7. ✅ **Eksport danych** - jak zapisywać dane do JSON
8. ✅ **Kompletny program** - jak łączyć wszystko razem

### Następne kroki:

- Spróbuj dodać więcej funkcji do `Device`
- Dodaj więcej typów skanerów
- Stwórz interfejs użytkownika (CLI)
- Dodaj więcej formatów eksportu (CSV, PDF)

---

**Powodzenia w dalszej nauce! 🚀**
