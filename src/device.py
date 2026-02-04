"""
Moduł reprezentujący urządzenie medyczne.

Ten moduł definiuje klasę Device, która przechowuje informacje o urządzeniu medycznym.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum


class DeviceType(Enum):
    """Typy urządzeń medycznych"""
    GLUCOSE_METER = "glucose_meter"  # Glukometr
    INSULIN_PUMP = "insulin_pump"    # Pompa insulinowa
    BLOOD_PRESSURE = "blood_pressure"  # Ciśnieniomierz
    PULSE_OXIMETER = "pulse_oximeter"  # Pulsoksymetr
    FITNESS_TRACKER = "fitness_tracker"  # Opaska fitness
    SMARTWATCH = "smartwatch"  # Smartwatch z funkcjami medycznymi
    UNKNOWN = "unknown"  # Nieznany typ


class Protocol(Enum):
    """Protokoły komunikacji"""
    BLE = "BLE"  # Bluetooth Low Energy
    WIFI = "WiFi"
    USB = "USB"
    NFC = "NFC"


@dataclass
class Device:
    """
    Klasa reprezentująca urządzenie medyczne.
    
    Przechowuje wszystkie informacje o urządzeniu:
    - Podstawowe dane (nazwa, MAC, typ)
    - Informacje o bezpieczeństwie
    - Wyniki analizy
    """
    
    # Podstawowe informacje
    mac_address: str  # Adres MAC urządzenia (unikalny identyfikator)
    name: str  # Nazwa urządzenia
    device_type: DeviceType  # Typ urządzenia (glukometr, pompa, etc.)
    protocol: Protocol  # Protokół komunikacji (BLE, WiFi, etc.)
    
    # Informacje o bezpieczeństwie
    has_encryption: bool = False  # Czy używa szyfrowania
    encryption_type: Optional[str] = None  # Typ szyfrowania (np. "AES-128", "WPA2", "TLS 1.3", "HTTPS")
    requires_pairing: bool = False  # Czy wymaga parowania
    security_score: int = 0  # Wynik bezpieczeństwa (0-100)
    
    # Dodatkowe informacje
    rssi: Optional[int] = None  # Siła sygnału (dla Bluetooth)
    manufacturer: Optional[str] = None  # Producent
    model: Optional[str] = None  # Model
    firmware_version: Optional[str] = None  # Wersja firmware
    
    # Timestamps
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    
    # Lista znalezionych podatności
    vulnerabilities: List[str] = field(default_factory=list)
    
    # Dodatkowe metadane
    metadata: Dict = field(default_factory=dict)
    
    def update_last_seen(self):
        """Aktualizuje timestamp ostatniego widzenia"""
        self.last_seen = datetime.now()
    
    def calculate_security_score(self) -> int:
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
        
        Przykłady:
        - Urządzenie z szyfrowaniem i parowaniem, bez podatności: 100/100 ✅
        - Urządzenie bez szyfrowania, z parowaniem: 70/100 ⚠️
        - Urządzenie bez szyfrowania i parowania: 50/100 ❌
        - Urządzenie z wieloma podatnościami: <50/100 🔴
        
        Returns:
            Wynik bezpieczeństwa (0-100)
        """
        score = 100  # Startujemy od maksymalnego wyniku
        
        # Sprawdź szyfrowanie
        # Brak szyfrowania to poważna podatność - dane mogą być przechwycone
        if not self.has_encryption:
            score -= 30  # -30 punktów za brak szyfrowania
        
        # Sprawdź autoryzację (parowanie)
        # Brak wymagania parowania oznacza, że każdy może się połączyć
        if not self.requires_pairing:
            score -= 20  # -20 punktów za brak parowania
        
        # Sprawdź znane podatności
        # Każda dodatkowa podatność zmniejsza wynik bezpieczeństwa
        score -= len(self.vulnerabilities) * 25
        
        # Upewnij się, że wynik jest w zakresie 0-100
        # max(0, ...) - wynik nie może być ujemny
        # min(100, ...) - wynik nie może przekroczyć 100
        self.security_score = max(0, min(100, score))
        return self.security_score
    
    def add_vulnerability(self, vulnerability: str):
        """Dodaje podatność do listy"""
        if vulnerability not in self.vulnerabilities:
            self.vulnerabilities.append(vulnerability)
            # Przelicz wynik bezpieczeństwa
            self.calculate_security_score()
    
    def to_dict(self) -> dict:
        """Konwertuje urządzenie do słownika (dla JSON/API)"""
        import numpy as np
        
        # Konwertuj metadata na serializowalne typy
        metadata_serializable = {}
        if self.metadata:
            for key, value in self.metadata.items():
                if isinstance(value, (np.integer, np.floating)):
                    metadata_serializable[key] = value.item()
                elif isinstance(value, np.ndarray):
                    metadata_serializable[key] = value.tolist()
                elif isinstance(value, (np.bool_, bool)):
                    metadata_serializable[key] = bool(value)
                elif isinstance(value, dict):
                    # Rekurencyjnie konwertuj zagnieżdżone słowniki
                    metadata_serializable[key] = self._convert_dict_for_json(value)
                elif isinstance(value, (list, tuple)):
                    metadata_serializable[key] = [self._convert_value_for_json(item) for item in value]
                else:
                    metadata_serializable[key] = value
        else:
            metadata_serializable = {}
        
        # Pobierz IP z metadanych dla łatwiejszej identyfikacji
        device_ip = None
        if metadata_serializable:
            device_ip = metadata_serializable.get('ip_address') or metadata_serializable.get('ip')
        
        return {
            "mac_address": self.mac_address,
            "name": self.name,
            "display_name": self.get_display_name(),  # Czytelna nazwa
            "device_fingerprint": self.get_device_fingerprint(),  # Unikalny fingerprint
            "device_type": self.device_type.value,
            "protocol": self.protocol.value,
            "has_encryption": bool(self.has_encryption),
            "encryption_type": self.encryption_type,
            "requires_pairing": bool(self.requires_pairing),
            "security_score": int(self.security_score),
            "rssi": int(self.rssi) if self.rssi is not None else None,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "firmware_version": self.firmware_version,
            "ip_address": device_ip,  # Dodaj IP na głównym poziomie dla łatwego dostępu
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "vulnerabilities": self.vulnerabilities,
            "metadata": metadata_serializable
        }
    
    def _convert_value_for_json(self, value):
        """Konwertuje pojedynczą wartość na typ serializowalny do JSON"""
        import numpy as np
        if isinstance(value, (np.integer, np.floating)):
            return value.item()
        elif isinstance(value, np.ndarray):
            return value.tolist()
        elif isinstance(value, (np.bool_, bool)):
            return bool(value)
        elif isinstance(value, dict):
            return self._convert_dict_for_json(value)
        elif isinstance(value, (list, tuple)):
            return [self._convert_value_for_json(item) for item in value]
        else:
            return value
    
    def _convert_dict_for_json(self, d: dict) -> dict:
        """Konwertuje słownik na typy serializowalne do JSON"""
        result = {}
        for key, value in d.items():
            result[key] = self._convert_value_for_json(value)
        return result
    
    def get_device_fingerprint(self) -> str:
        """
        Generuje unikalny fingerprint urządzenia składający się z wielu cech.
        
        Fingerprint jest używany do identyfikacji urządzenia nawet jeśli:
        - MAC się zmieni (random MAC)
        - IP się zmieni
        - Nazwa się zmieni
        
        Składa się z:
        - Protokół
        - Typ urządzenia
        - Producent
        - Model
        - Ostatnie 6 znaków MAC (dla identyfikacji)
        - IP (jeśli dostępne)
        
        Returns:
            Unikalny fingerprint urządzenia
        """
        parts = [
            self.protocol.value,
            self.device_type.value,
        ]
        
        if self.manufacturer:
            parts.append(self.manufacturer)
        if self.model:
            parts.append(self.model)
        
        # Dodaj ostatnie 6 znaków MAC (dla identyfikacji)
        mac_short = self.mac_address.replace(":", "")[-6:].upper()
        parts.append(f"MAC:{mac_short}")
        
        # Dodaj IP jeśli dostępne (dla WiFi)
        if self.metadata:
            ip = self.metadata.get('ip_address') or self.metadata.get('ip')
            if ip:
                parts.append(f"IP:{ip}")
        
        return "|".join(parts)
    
    def get_display_name(self) -> str:
        """
        Zwraca czytelną nazwę urządzenia do wyświetlenia.
        
        Priorytet:
        1. Nazwa urządzenia (jeśli nie jest IP)
        2. Producent + Model
        3. Typ urządzenia + MAC/IP
        4. Protokół + MAC/IP
        
        Returns:
            Czytelna nazwa urządzenia
        """
        import re
        
        # Jeśli nazwa to IP, nie używaj jej jako głównej nazwy
        is_ip = bool(re.match(r'^(\d{1,3}\.){3}\d{1,3}$', self.name))
        
        if not is_ip and self.name and self.name not in ["Unknown", "Unknown Device"]:
            return self.name
        
        # Spróbuj producent + model
        if self.manufacturer and self.model:
            return f"{self.manufacturer} {self.model}"
        elif self.manufacturer:
            return f"{self.manufacturer} Device"
        
        # Spróbuj typ urządzenia
        if self.device_type != DeviceType.UNKNOWN:
            type_names = {
                DeviceType.GLUCOSE_METER: "Glukometr",
                DeviceType.INSULIN_PUMP: "Pompa insulinowa",
                DeviceType.BLOOD_PRESSURE: "Ciśnieniomierz",
                DeviceType.PULSE_OXIMETER: "Pulsoksymetr",
                DeviceType.FITNESS_TRACKER: "Opaska fitness",
                DeviceType.SMARTWATCH: "Smartwatch",
            }
            type_name = type_names.get(self.device_type, self.device_type.value)
            
            # Dodaj identyfikator
            if self.metadata:
                ip = self.metadata.get('ip_address') or self.metadata.get('ip')
                if ip:
                    return f"{type_name} ({ip})"
            
            mac_short = self.mac_address.replace(":", "")[-6:].upper()
            return f"{type_name} (MAC: {mac_short})"
        
        # Ostatnia opcja: protokół + identyfikator
        if self.metadata:
            ip = self.metadata.get('ip_address') or self.metadata.get('ip')
            if ip:
                return f"Urządzenie {self.protocol.value} ({ip})"
        
        mac_short = self.mac_address.replace(":", "")[-6:].upper()
        return f"Urządzenie {self.protocol.value} (MAC: {mac_short})"
    
    def __str__(self) -> str:
        """Reprezentacja tekstowa urządzenia"""
        return f"Device({self.name}, {self.device_type.value}, MAC: {self.mac_address}, Score: {self.security_score})"


# Przykładowe urządzenia medyczne (dla testów)
SAMPLE_MEDICAL_DEVICES = [
    {
        "mac_address": "AA:BB:CC:DD:EE:01",
        "name": "GlucoSmart Pro",
        "device_type": DeviceType.GLUCOSE_METER,
        "protocol": Protocol.BLE,
        "has_encryption": True,
        "requires_pairing": True,
        "manufacturer": "MedTech Inc",
        "model": "GS-Pro-2024",
        "firmware_version": "2.1.3"
    },
    {
        "mac_address": "AA:BB:CC:DD:EE:02",
        "name": "InsulinPump X1",
        "device_type": DeviceType.INSULIN_PUMP,
        "protocol": Protocol.BLE,
        "has_encryption": False,  # Podatność!
        "requires_pairing": False,  # Podatność!
        "manufacturer": "HealthDev Corp",
        "model": "IP-X1",
        "firmware_version": "1.0.0"
    },
    {
        "mac_address": "AA:BB:CC:DD:EE:03",
        "name": "BloodPressure Monitor",
        "device_type": DeviceType.BLOOD_PRESSURE,
        "protocol": Protocol.BLE,
        "has_encryption": True,
        "requires_pairing": True,
        "manufacturer": "VitalSigns Ltd",
        "model": "BP-3000",
        "firmware_version": "3.2.1"
    }
]
