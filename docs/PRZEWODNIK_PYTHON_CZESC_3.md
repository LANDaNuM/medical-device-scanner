# 🐍 Kompletny Przewodnik po Kodzie Python - Część 3: ANALIZA I BEZPIECZEŃSTWO

## 📚 Spis Treści Części 3

1. [Wprowadzenie](#wprowadzenie)
2. [Plik 7: `vulnerability_tester.py` - Testy Podatności](#plik-7-vulnerability_testerpy---testy-podatności)
3. [Plik 8: `anomaly_detector.py` - Wykrywanie Anomalii (ML)](#plik-8-anomaly_detectorpy---wykrywanie-anomalii-ml)
4. [Plik 9: `encryption_analyzer.py` - Analiza Szyfrowania](#plik-9-encryption_analyzerpy---analiza-szyfrowania)

---

## Wprowadzenie

Moduły analizy i bezpieczeństwa **testują** i **oceniają** wykryte urządzenia:
- **Vulnerability Tester** - testuje podatności (porty, protokoły, konfiguracje)
- **Anomaly Detector** - używa Machine Learning do wykrywania nietypowych urządzeń
- **Encryption Analyzer** - analizuje algorytmy szyfrowania

---

## Plik 7: `vulnerability_tester.py` - Testy Podatności

### 📍 Lokalizacja: `src/vulnerability_tester.py`

### 🎯 Cel
Testuje urządzenia pod kątem **znanych podatności** i słabych konfiguracji.

### 📝 Kod z Wyjaśnieniami

#### Enum: AttackType

```python
class AttackType(Enum):
    """Typy ataków do symulacji"""
    PORT_SCAN = "Skanowanie portów"
    BRUTE_FORCE = "Atak brute-force"
    SQL_INJECTION = "SQL Injection"
```

**Wyjaśnienie:**
- **Enum** - lista stałych wartości
- Reprezentuje różne typy ataków
- **Dlaczego Enum?** Zamiast stringów ("port_scan", "brute_force") używamy stałych (mniej błędów)

#### Enum: Severity

```python
class Severity(Enum):
    """Poziomy ważności podatności"""
    CRITICAL = "Krytyczna"
    HIGH = "Wysoka"
    MEDIUM = "Średnia"
    LOW = "Niska"
    INFO = "Informacyjna"
```

**Wyjaśnienie:**
- Poziomy ważności podatności
- **CRITICAL** - natychmiastowe zagrożenie (np. brak szyfrowania)
- **HIGH** - poważne zagrożenie (np. słabe hasła)
- **MEDIUM** - umiarkowane (np. przestarzałe oprogramowanie)

#### Dataclass: VulnerabilityTest

```python
@dataclass
class VulnerabilityTest:
    """Wynik testu podatności"""
    name: str
    description: str
    severity: Severity
    attack_type: AttackType
    port: Optional[int] = None
    is_vulnerable: bool = False
    details: str = ""
    recommendation: str = ""
```

**Wyjaśnienie:**
- **Dataclass** - automatycznie tworzy `__init__`, `__repr__`, `__eq__`
- Przechowuje wynik jednego testu podatności
- `is_vulnerable: bool` - czy urządzenie jest rzeczywiście podatne

#### Klasa VulnerabilityTester - Konstruktor

```python
    def __init__(self, use_cve_api: bool = True):
        self.use_cve_api = use_cve_api and CVE_AVAILABLE
        if self.use_cve_api:
            self.cve_lookup = get_cve_lookup()
```

**Wyjaśnienie:**
- `use_cve_api` - czy używać zewnętrznego API CVE (NIST NVD)
- **CVE** - Common Vulnerabilities and Exposures (baza znanych podatności)
- `get_cve_lookup()` - pobiera obiekt do wyszukiwania CVE

```python
        self.known_exploits = {
            104: {
                "name": "DICOM Unauthorized Access",
                "cve": ["CVE-2019-11687", "CVE-2020-13160"],
                "description": "DICOM często nie wymaga autoryzacji",
                "severity": Severity.HIGH
            },
            # ... więcej portów
        }
```

**Wyjaśnienie:**
- **Słownik** z znanymi podatnościami dla portów
- **Klucz:** numer portu (104 = DICOM)
- **Wartość:** słownik z informacjami o podatności
- **Fallback** - używany gdy CVE API nie jest dostępne

#### Metoda: test_device() - Główna Metoda Testowania

```python
    def test_device(self, device: Device) -> List[VulnerabilityTest]:
        results = []
        
        # Testuj porty jeśli urządzenie ma IP (WiFi)
        if device.protocol.value == "WIFI" and "ip_address" in device.metadata:
```

**Wyjaśnienie:**
- Sprawdza czy urządzenie to WiFi (ma IP)
- `device.protocol.value` - pobiera wartość Enum (string "WIFI")
- `"ip_address" in device.metadata` - sprawdza czy **klucz istnieje** w słowniku

```python
            ip = device.metadata["ip_address"]
            open_ports = device.metadata.get("open_ports", [])
```

**Wyjaśnienie:**
- `device.metadata["ip_address"]` - pobiera IP (rzuca błąd jeśli nie ma)
- `device.metadata.get("open_ports", [])` - **bezpieczne** pobranie (zwraca `[]` jeśli nie ma)
- **Różnica:**
  ```python
  metadata["key"]  # Rzuca KeyError jeśli nie ma
  metadata.get("key", default)  # Zwraca default jeśli nie ma
  ```

```python
            # Testuj każdy otwarty port
            for port in open_ports:
                port_tests = self._test_port(ip, port, device)
                results.extend(port_tests)
```

**Wyjaśnienie:**
- `for port in open_ports:` - iteruje przez wszystkie otwarte porty
- `self._test_port(...)` - testuje jeden port
- `results.extend(port_tests)` - **dodaje wszystkie** testy do listy

```python
            # Testuj znane podatności protokołów medycznych
            if any(p in open_ports for p in [104, 11112]):  # DICOM
                dicom_tests = self._test_dicom_protocol(ip, device)
                results.extend(dicom_tests)
```

**Wyjaśnienie:**
- `any(p in open_ports for p in [104, 11112])` - sprawdza czy **którykolwiek** port z listy jest otwarty
- **List comprehension w any:**
  ```python
  # Równoważne z:
  has_dicom = False
  for p in [104, 11112]:
      if p in open_ports:
          has_dicom = True
          break
  if has_dicom:
      # ...
  ```

#### Metoda: _test_port() - Test Pojedynczego Portu

```python
    def _test_port(self, ip: str, port: int, device: Device) -> List[VulnerabilityTest]:
        results = []
        
        # Sprawdź czy port jest otwarty
        is_open = self._check_port_open(ip, port)
        if not is_open:
            return results  # Port zamknięty - nie ma podatności
```

**Wyjaśnienie:**
- Sprawdza czy port jest **rzeczywiście otwarty**
- Jeśli zamknięty → zwraca pustą listę (nie ma podatności)

```python
        # Porty medyczne - sprawdź czy to rzeczywiście urządzenie medyczne
        medical_ports = [104, 11112, 5000]
        if port in medical_ports:
            is_medical = self._is_medical_device(device)
            if not is_medical:
                return results  # Nie jest medyczne - nie dodawaj podatności medycznych
```

**Wyjaśnienie:**
- **Kontekst** - port 104 (DICOM) jest podatny tylko dla urządzeń medycznych
- Jeśli to nie urządzenie medyczne → nie dodawaj podatności medycznych
- **Dlaczego?** Komputer może mieć port 104 otwarty (jako serwer), ale to nie jest podatność medyczna

```python
        # Pobierz aktualne CVE dla tego portu
        if self.use_cve_api and self.cve_lookup:
            try:
                cves = self.cve_lookup.get_cves_for_port(port)
                for cve in cves[:5]:  # Max 5 najważniejszych CVE
```

**Wyjaśnienie:**
- `self.cve_lookup.get_cves_for_port(port)` - pobiera CVE z API
- `cves[:5]` - **slice** - tylko pierwsze 5 CVE (najważniejsze)
- **Dlaczego 5?** Może być setki CVE dla jednego portu - bierzemy tylko najważniejsze

```python
                    severity_map = {
                        "CRITICAL": Severity.CRITICAL,
                        "HIGH": Severity.HIGH,
                        "MEDIUM": Severity.MEDIUM,
                        "LOW": Severity.LOW
                    }
                    severity = severity_map.get(cve.severity, Severity.MEDIUM)
```

**Wyjaśnienie:**
- **Mapowanie** - konwertuje string na Enum
- `severity_map.get(cve.severity, Severity.MEDIUM)` - jeśli nie ma w mapie, użyj MEDIUM (domyślne)

```python
                    test = VulnerabilityTest(
                        name=f"{cve.cve_id}",
                        description=cve.description,
                        severity=severity,
                        attack_type=AttackType.UNAUTHORIZED_ACCESS,
                        port=port,
                        is_vulnerable=True,
                        details=f"CVSS Score: {cve.cvss_score or 'N/A'}",
                        recommendation=f"Zaktualizuj oprogramowanie aby naprawić {cve.cve_id}"
                    )
                    results.append(test)
```

**Wyjaśnienie:**
- Tworzy obiekt `VulnerabilityTest` z danymi CVE
- `f"{cve.cve_id}"` - **f-string** - formatuje string (wstawia wartość)
- `cve.cvss_score or 'N/A'` - jeśli `cvss_score` jest None, użyj 'N/A'
- `results.append(test)` - dodaje test do listy wyników

#### Testy Specyficzne dla Portów

```python
        if port == 3389:  # RDP
            if not is_router:
                rdp_tests = self._test_rdp(ip, port)
                results.extend(rdp_tests)
```

**Wyjaśnienie:**
- Port 3389 = RDP (Remote Desktop Protocol)
- `if not is_router:` - routery rzadko mają RDP, więc nie testuj
- **Warunki** - różne porty mają różne testy

```python
        elif port in [1433, 3306, 5432, 27017]:  # Bazy danych
            if not is_router:
                db_tests = self._test_database(ip, port)
                results.extend(db_tests)
```

**Wyjaśnienie:**
- `elif` - **else if** (jeśli poprzedni warunek był False)
- `port in [1433, ...]` - sprawdza czy port **jest w** liście
- Porty baz danych: 1433 (MSSQL), 3306 (MySQL), 5432 (PostgreSQL), 27017 (MongoDB)

#### Metoda: _test_rdp() - Test RDP

```python
    def _test_rdp(self, ip: str, port: int) -> List[VulnerabilityTest]:
        results = []
        
        test = VulnerabilityTest(
            name="RDP BlueKeep Vulnerability",
            description="Sprawdzanie podatności na exploita BlueKeep (CVE-2019-0708)",
            severity=Severity.CRITICAL,
            attack_type=AttackType.BUFFER_OVERFLOW,
            port=port,
            is_vulnerable=True,  # Zakładamy że może być podatny jeśli port otwarty
            details="Port RDP jest otwarty. BlueKeep pozwala na zdalne wykonanie kodu bez autoryzacji.",
            recommendation="Zaktualizuj system, wyłącz RDP jeśli nie jest potrzebny, użyj VPN"
        )
        results.append(test)
        return results
```

**Wyjaśnienie:**
- **Symulacja** - nie wykonuje rzeczywistego ataku, tylko sprawdza znane podatności
- BlueKeep (CVE-2019-0708) - krytyczna podatność RDP
- `is_vulnerable=True` - zakładamy że może być podatny (jeśli port otwarty)

#### Metoda: _test_encryption() - Test Szyfrowania

```python
    def _test_encryption(self, device: Device) -> List[VulnerabilityTest]:
        results = []
        
        if not device.has_encryption:
            test = VulnerabilityTest(
                name="No Encryption",
                description="Urządzenie nie używa szyfrowania",
                severity=Severity.CRITICAL,
                attack_type=AttackType.DATA_EXFILTRATION,
                is_vulnerable=True,
                details="Dane medyczne mogą być przechwycone podczas transmisji",
                recommendation="Włącz szyfrowanie (TLS/SSL, AES-256)"
            )
            results.append(test)
        
        return results
```

**Wyjaśnienie:**
- Sprawdza czy urządzenie **ma szyfrowanie**
- Jeśli nie → dodaje krytyczną podatność
- **DATA_EXFILTRATION** - typ ataku (wyciek danych)

#### Metoda: _test_ble_specific() - Testy Specyficzne dla BLE

```python
    def _test_ble_specific(self, device: Device) -> List[VulnerabilityTest]:
        results = []
        
        # Testuj słabe szyfrowanie BLE
        if device.has_encryption:
            if device.encryption_type and "AES-128" in device.encryption_type:
                if device.device_type != DeviceType.UNKNOWN:
                    test = VulnerabilityTest(
                        name="BLE Weak Encryption (AES-128)",
                        description="Urządzenie medyczne używa AES-128 zamiast AES-256",
                        severity=Severity.MEDIUM,
                        # ...
                    )
                    results.append(test)
```

**Wyjaśnienie:**
- Testuje **specyficzne** podatności dla BLE
- AES-128 vs AES-256 - dla urządzeń medycznych zalecane AES-256
- `device.device_type != DeviceType.UNKNOWN` - tylko dla znanych typów urządzeń

```python
        # Testuj exposed services
        service_uuids = device.metadata.get("service_uuids", [])
        dangerous_services = {
            "0000180f": "Battery Service - może ujawnić informacje o stanie urządzenia",
            # ...
        }
        
        for uuid, description in dangerous_services.items():
            if any(uuid.lower() in str(s).lower() for s in service_uuids):
                if not device.requires_pairing:
                    test = VulnerabilityTest(...)
                    results.append(test)
```

**Wyjaśnienie:**
- Sprawdza czy urządzenie ma **niebezpieczne services** dostępne bez autoryzacji
- `any(uuid.lower() in str(s).lower() for s in service_uuids)` - sprawdza czy którykolwiek UUID pasuje
- `if not device.requires_pairing:` - tylko jeśli nie wymaga parowania (to jest podatność!)

### 🔗 Kiedy jest używany?
- Gdy uruchamiasz `scanner.py --audit`
- Automatycznie testuje podatności dla wszystkich urządzeń

---

## Plik 8: `anomaly_detector.py` - Wykrywanie Anomalii (ML)

### 📍 Lokalizacja: `src/anomaly_detector.py`

### 🎯 Cel
Używa **Machine Learning** do wykrywania nietypowych urządzeń.

### 📝 Kod z Wyjaśnieniami

#### Importy ML

```python
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.neighbors import LocalOutlierFactor
    from sklearn.svm import OneClassSVM
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
```

**Wyjaśnienie:**
- `sklearn` - biblioteka Machine Learning (scikit-learn)
- **Isolation Forest** - algorytm wykrywania anomalii (szybki)
- **Local Outlier Factor (LOF)** - wykrywa lokalne anomalie
- **One-Class SVM** - wykrywa odstające urządzenia
- **StandardScaler** - normalizuje dane (wszystkie cechy w tym samym zakresie)

#### Klasa AnomalyDetector - Konstruktor

```python
    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
```

**Wyjaśnienie:**
- `contamination=0.1` - oczekuje 10% anomalii w danych
- `random_state=42` - **seed** dla losowości (dla powtarzalności wyników)
- `n_estimators=100` - 100 drzew w lesie (więcej = dokładniej, ale wolniej)

#### Metoda: extract_features() - Ekstrakcja Cech

```python
    def extract_features(self, devices: List[Device]) -> np.ndarray:
        features = []
        
        for device in devices:
            feature_vector = []
            
            # 1. Security score
            feature_vector.append(device.security_score)
```

**Wyjaśnienie:**
- **Ekstrakcja cech** - konwertuje obiekty Device na liczby
- ML wymaga **liczb**, nie obiektów!
- `feature_vector` - lista cech dla jednego urządzenia

```python
            # 3. Czy ma szyfrowanie (0/1)
            feature_vector.append(1 if device.has_encryption else 0)
```

**Wyjaśnienie:**
- **One-hot encoding** dla wartości boolean
- `1 if device.has_encryption else 0` - **ternary operator** (skrócony if/else)
- **Równoważne z:**
  ```python
  if device.has_encryption:
      feature_vector.append(1)
  else:
      feature_vector.append(0)
  ```

```python
            # 5. Typ protokołu (one-hot encoded)
            protocol_map = {
                Protocol.BLE: 0,
                Protocol.WIFI: 1,
                Protocol.USB: 2,
                Protocol.NFC: 3
            }
            protocol_encoded = [0, 0, 0, 0]
            protocol_idx = protocol_map.get(device.protocol, 0)
            protocol_encoded[protocol_idx] = 1
            feature_vector.extend(protocol_encoded)
```

**Wyjaśnienie:**
- **One-hot encoding** dla kategorii (protokoły)
- Zamiast jednej liczby (0, 1, 2, 3), używamy **4 liczb** (0/1 dla każdej kategorii)
- **Przykład:**
  - BLE → `[1, 0, 0, 0]`
  - WiFi → `[0, 1, 0, 0]`
  - USB → `[0, 0, 1, 0]`
  - NFC → `[0, 0, 0, 1]`
- **Dlaczego?** ML lepiej radzi sobie z one-hot encoding niż z liczbami porządkowymi

```python
            features.append(feature_vector)
        
        return np.array(features)
```

**Wyjaśnienie:**
- `features.append(feature_vector)` - dodaje wektor cech do listy
- `np.array(features)` - konwertuje listę na **tablicę numpy**
- **Dlaczego numpy?** Szybsze obliczenia, wymagane przez sklearn

#### Metoda: train() - Trening Modeli

```python
    def train(self, devices: List[Device]) -> Dict:
        if len(devices) < 10:
            return {'trained': False, 'reason': 'Za mało danych'}
```

**Wyjaśnienie:**
- Sprawdza czy jest **wystarczająco danych** do treningu
- Minimum 10 urządzeń (ML potrzebuje danych!)

```python
        # Ekstrahuj cechy
        X = self.extract_features(devices)
        
        # Normalizuj cechy
        X_scaled = self.scaler.fit_transform(X)
```

**Wyjaśnienie:**
- `X` - macierz cech (n_urządzeń × n_cech)
- `scaler.fit_transform(X)` - **uczy się** zakresu danych i **normalizuje**
- **Normalizacja** - wszystkie cechy w zakresie 0-1 (lub -1 do 1)
- **Dlaczego?** Security score (0-100) i liczba portów (0-65535) są w różnych zakresach
- Po normalizacji: obie w zakresie 0-1 → ML działa lepiej

```python
        # Trenuj modele
        self.isolation_forest.fit(X_scaled)
        self.lof.fit(X_scaled)
        self.one_class_svm.fit(X_scaled)
```

**Wyjaśnienie:**
- `.fit(X_scaled)` - **trenuje** model na danych
- Model **uczy się** co jest "normalne", a co "anomalia"
- **3 modele** - używamy ensemble (głosowanie większościowe)

#### Metoda: detect_anomalies() - Wykrywanie Anomalii

```python
    def detect_anomalies(self, devices: List[Device], use_ensemble: bool = True) -> List[Dict]:
        if not devices:
            return []
```

**Wyjaśnienie:**
- Sprawdza czy lista nie jest pusta
- `if not devices:` - jeśli lista jest pusta (falsy)

```python
        # Jeśli model nie jest wytrenowany, użyj domyślnych wartości
        if not self.trained:
            results = []
            for device in devices:
                is_anomaly = device.security_score < 30 or len(device.vulnerabilities) > 5
                results.append({
                    'device': device,
                    'is_anomaly': is_anomaly,
                    'anomaly_score': 1.0 - (device.security_score / 100),
                    'method': 'heuristic',
                    'reason': 'Low security score or many vulnerabilities' if is_anomaly else 'Normal'
                })
            return results
```

**Wyjaśnienie:**
- **Fallback** - jeśli model nie jest wytrenowany, użyj **heurystyki**
- `device.security_score < 30` - bardzo niski wynik = anomalia
- `len(device.vulnerabilities) > 5` - wiele podatności = anomalia
- `1.0 - (device.security_score / 100)` - konwertuje score (0-100) na anomaly_score (1.0-0.0)
  - Score 0 → anomaly_score 1.0 (bardzo anomalia)
  - Score 100 → anomaly_score 0.0 (normalne)

```python
        # Ekstrahuj cechy
        X = self.extract_features(devices)
        X_scaled = self.scaler.transform(X)
```

**Wyjaśnienie:**
- `self.scaler.transform(X)` - **tylko normalizuje** (nie uczy się - już wytrenowany)
- **Różnica:**
  - `fit_transform()` - uczy się i normalizuje (trening)
  - `transform()` - tylko normalizuje (predykcja)

```python
        # Wykryj anomalie używając różnych metod
        if_anomalies = self.isolation_forest.predict(X_scaled)
        if_scores = -self.isolation_forest.score_samples(X_scaled)
```

**Wyjaśnienie:**
- `.predict(X_scaled)` - **przewiduje** czy to anomalia (-1 = anomalia, 1 = normalne)
- `.score_samples(X_scaled)` - zwraca **wynik anomalii** (niższy = bardziej anomalia)
- `-score_samples` - negujemy (bo Isolation Forest zwraca ujemne dla anomalii)

```python
        # Ensemble: głosowanie większościowe
        results = []
        for i, device in enumerate(devices):
            # Zlicz głosy (ile modeli uważa za anomalia)
            votes = sum([
                if_anomalies[i] == -1,  # Isolation Forest
                lof_anomalies[i] == -1,  # LOF
                svm_anomalies[i] == -1   # SVM
            ])
            
            is_anomaly = votes >= 2  # Jeśli 2+ modele uważają za anomalia
```

**Wyjaśnienie:**
- **Ensemble** - łączy wyniki wielu modeli
- `sum([True, False, True])` - zlicza True (2 w tym przypadku)
- `votes >= 2` - jeśli **2 lub więcej** modeli uważa za anomalia → to anomalia
- **Dlaczego?** Większość modeli musi się zgodzić (mniej fałszywych alarmów)

### 🔗 Kiedy jest używany?
- Automatycznie przez `scanner.py` (zawsze włączony)
- Używa ML do wykrywania nietypowych urządzeń

---

## Plik 9: `encryption_analyzer.py` - Analiza Szyfrowania

### 📍 Lokalizacja: `src/encryption_analyzer.py`

### 🎯 Cel
Analizuje **algorytmy szyfrowania** i wykrywa słabe standardy.

### 📝 Kod z Wyjaśnieniami

#### Enum: EncryptionStrength

```python
class EncryptionStrength(Enum):
    STRONG = "strong"  # Silne szyfrowanie
    MODERATE = "moderate"  # Umiarkowane
    WEAK = "weak"  # Słabe
    NONE = "none"  # Brak
    UNKNOWN = "unknown"  # Nieznane
```

**Wyjaśnienie:**
- Poziomy siły szyfrowania
- **STRONG** - AES-256, TLS 1.3, WPA3
- **WEAK** - DES, RC4, TLS 1.0, WEP

#### Klasa EncryptionAnalyzer - Listy Algorytmów

```python
    WEAK_ALGORITHMS = [
        "DES", "3DES", "RC4", "MD5", "SHA1", "RSA-1024",
        "TLS 1.0", "TLS 1.1", "SSL 2.0", "SSL 3.0",
        "WEP", "WPA", "WPA2-TKIP"
    ]
```

**Wyjaśnienie:**
- Lista **słabych** algorytmów (przestarzałe, łatwe do złamania)
- **DES** - można złamać w kilka godzin
- **TLS 1.0/1.1** - podatne na ataki (POODLE, BEAST)
- **WEP** - można złamać w kilka minut

```python
    STRONG_ALGORITHMS = [
        "AES-256", "ChaCha20-Poly1305", "TLS 1.3", "WPA3",
        "RSA-4096", "ECDSA", "Ed25519"
    ]
```

**Wyjaśnienie:**
- Lista **silnych** algorytmów (nowoczesne, bezpieczne)
- **AES-256** - standardowy, bardzo bezpieczny
- **TLS 1.3** - najnowsza wersja TLS
- **WPA3** - najnowszy standard WiFi

#### Metoda: analyze() - Analiza Szyfrowania

```python
    def analyze(self, encryption_type: Optional[str], has_encryption: bool) -> EncryptionAnalysis:
        if not has_encryption or not encryption_type:
            return EncryptionAnalysis(
                encryption_type="No encryption",
                strength=EncryptionStrength.NONE,
                is_weak=True,
                issues=["Brak szyfrowania - wszystkie dane przesyłane jawnie"],
                recommendations=["Włącz szyfrowanie dla wszystkich połączeń"],
                score=0
            )
```

**Wyjaśnienie:**
- Jeśli brak szyfrowania → zwraca analizę z **score=0** (najgorsze)
- `issues` - lista problemów
- `recommendations` - lista rekomendacji naprawy

```python
        encryption_type_lower = encryption_type.lower()
        issues = []
        recommendations = []
```

**Wyjaśnienie:**
- `.lower()` - konwertuje na małe litery (porównywanie bez rozróżniania wielkości)
- Tworzy puste listy dla problemów i rekomendacji

```python
        # Sprawdź siłę szyfrowania
        for key, value in self.ENCRYPTION_STRENGTH_MAP.items():
            if key.lower() in encryption_type_lower:
                strength = value
                break
```

**Wyjaśnienie:**
- Iteruje przez mapę siły szyfrowania
- `if key.lower() in encryption_type_lower:` - sprawdza czy klucz **jest w** stringu
- **Przykład:**
  - `encryption_type = "AES-256"`
  - `"aes-256" in "aes-256"` → True
  - `strength = EncryptionStrength.STRONG`
- `break` - **przerywa** pętlę (znaleziono, nie szukaj dalej)

```python
        # Sprawdź słabe algorytmy
        for weak_alg in self.WEAK_ALGORITHMS:
            if weak_alg.lower() in encryption_type_lower:
                is_weak = True
                issues.append(f"Używa słabego algorytmu: {weak_alg}")
                recommendations.extend(self._get_recommendations_for_weak_algorithm(weak_alg))
```

**Wyjaśnienie:**
- Sprawdza czy szyfrowanie **zawiera** słaby algorytm
- `recommendations.extend(...)` - **dodaje wszystkie** rekomendacje (nie tylko jedną)

```python
        # Oblicz wynik (0-100)
        score = self._calculate_encryption_score(strength, is_weak, len(issues))
```

**Wyjaśnienie:**
- Oblicza wynik szyfrowania na podstawie siły, słabości i liczby problemów

#### Metoda: _calculate_encryption_score()

```python
    def _calculate_encryption_score(self, strength: EncryptionStrength, is_weak: bool, issues_count: int) -> int:
        base_scores = {
            EncryptionStrength.STRONG: 90,
            EncryptionStrength.MODERATE: 60,
            EncryptionStrength.WEAK: 30,
            EncryptionStrength.NONE: 0,
            EncryptionStrength.UNKNOWN: 50
        }
        
        score = base_scores.get(strength, 50)
        score -= issues_count * 10
        if is_weak:
            score -= 20
        
        return max(0, min(100, score))
```

**Wyjaśnienie:**
- **Bazowy wynik** na podstawie siły (STRONG=90, WEAK=30, NONE=0)
- `score -= issues_count * 10` - odejmij 10 punktów za każdy problem
- `if is_weak: score -= 20` - jeśli słabe, odejmij dodatkowe 20
- `max(0, min(100, score))` - ogranicza do zakresu 0-100

### 🔗 Kiedy jest używany?
- Automatycznie przez `scanner.py` podczas analizy bezpieczeństwa
- Analizuje szyfrowanie każdego urządzenia

---

## 📝 Podsumowanie Części 3

### Co nauczyłeś się:
1. ✅ Jak działają testy podatności
2. ✅ Jak używa Machine Learning do wykrywania anomalii
3. ✅ Jak analizuje szyfrowanie
4. ✅ Koncepty: Enum, dataclass, one-hot encoding, normalizacja danych
5. ✅ Ensemble methods (łączenie wielu modeli ML)

### Kluczowe Koncepty:

**One-Hot Encoding:**
```python
# Zamiast: BLE=0, WiFi=1, USB=2
# Używamy: BLE=[1,0,0,0], WiFi=[0,1,0,0], USB=[0,0,1,0]
```

**Normalizacja:**
```python
# Przed: security_score=50, ports=10 (różne zakresy)
# Po: security_score=0.5, ports=0.1 (ten sam zakres 0-1)
```

**Ensemble:**
```python
# Łączy wyniki wielu modeli
# Jeśli 2+ modele zgadzają się → decyzja
```

---

**Kontynuacja w: PRZEWODNIK_PYTHON_CZESC_4.md** (Integracje: API, Dashboard, SIEM)
