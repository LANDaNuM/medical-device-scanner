"""Medical device representation. Defines Device class and related enums."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum


class DeviceType(Enum):
    """Medical device types."""
    GLUCOSE_METER = "glucose_meter"
    INSULIN_PUMP = "insulin_pump"
    BLOOD_PRESSURE = "blood_pressure"
    PULSE_OXIMETER = "pulse_oximeter"
    FITNESS_TRACKER = "fitness_tracker"
    SMARTWATCH = "smartwatch"
    UNKNOWN = "unknown"


class Protocol(Enum):
    """Communication protocols."""
    BLE = "BLE"  # Bluetooth Low Energy
    WIFI = "WiFi"
    USB = "USB"
    NFC = "NFC"


@dataclass
class Device:
    """Medical device. Holds name, MAC, type, security info, analysis results."""
    
    mac_address: str
    name: str
    device_type: DeviceType
    protocol: Protocol
    
    has_encryption: bool = False
    encryption_type: Optional[str] = None
    requires_pairing: bool = False
    security_score: int = 0
    
    rssi: Optional[int] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    
    # Timestamps
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    
    vulnerabilities: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def update_last_seen(self):
        """Update last seen timestamp."""
        self.last_seen = datetime.now()
    
    def calculate_security_score(self) -> int:
        """Compute security score 0-100. Starts at 100, subtracts for no encryption (-30), no pairing (-20), each vulnerability (-25)."""
        score = 100
        
        # Check encryption
        if not self.has_encryption:
            score -= 30
        if not self.requires_pairing:
            score -= 20
        score -= len(self.vulnerabilities) * 25
        
        # Clamp to 0-100
        self.security_score = max(0, min(100, score))
        return self.security_score
    
    def add_vulnerability(self, vulnerability: str):
        """Add vulnerability to list."""
        if vulnerability not in self.vulnerabilities:
            self.vulnerabilities.append(vulnerability)
            # Recalculate security score
            self.calculate_security_score()
    
    def to_dict(self) -> dict:
        """Convert device to dict (for JSON/API)."""
        import numpy as np
        
        # Convert metadata to JSON-serializable types
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
                    # Recursively convert nested dicts
                    metadata_serializable[key] = self._convert_dict_for_json(value)
                elif isinstance(value, (list, tuple)):
                    metadata_serializable[key] = [self._convert_value_for_json(item) for item in value]
                else:
                    metadata_serializable[key] = value
        else:
            metadata_serializable = {}
        
        # Get IP from metadata for easier identification
        device_ip = None
        if metadata_serializable:
            device_ip = metadata_serializable.get('ip_address') or metadata_serializable.get('ip')
        
        return {
            "mac_address": self.mac_address,
            "name": self.name,
            "display_name": self.get_display_name(),  # Human-readable name
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
            "ip_address": device_ip,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "vulnerabilities": self.vulnerabilities,
            "metadata": metadata_serializable
        }
    
    def _convert_value_for_json(self, value):
        """Convert single value to JSON-serializable type."""
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
        """Convert dict to JSON-serializable types."""
        result = {}
        for key, value in d.items():
            result[key] = self._convert_value_for_json(value)
        return result
    
    def get_device_fingerprint(self) -> str:
        """Generate unique device fingerprint (protocol, type, manufacturer, model, MAC suffix, IP)."""
        parts = [
            self.protocol.value,
            self.device_type.value,
        ]
        
        if self.manufacturer:
            parts.append(self.manufacturer)
        if self.model:
            parts.append(self.model)
        
        # Add last 6 chars of MAC
        mac_short = self.mac_address.replace(":", "")[-6:].upper()
        parts.append(f"MAC:{mac_short}")
        
        # Add IP if available (WiFi)
        if self.metadata:
            ip = self.metadata.get('ip_address') or self.metadata.get('ip')
            if ip:
                parts.append(f"IP:{ip}")
        
        return "|".join(parts)
    
    def get_display_name(self) -> str:
        """
        Return a human-readable display name for the device.
        Priority: device name (if not IP) → manufacturer + model → device type + MAC/IP → protocol + MAC/IP.
        """
        import re
        
        # If name is IP, do not use as primary name
        is_ip = bool(re.match(r'^(\d{1,3}\.){3}\d{1,3}$', self.name))
        
        if not is_ip and self.name and self.name not in ["Unknown", "Unknown Device"]:
            return self.name
        
        # Try manufacturer + model
        if self.manufacturer and self.model:
            return f"{self.manufacturer} {self.model}"
        elif self.manufacturer:
            return f"{self.manufacturer} Device"
        
        # Try device type
        if self.device_type != DeviceType.UNKNOWN:
            type_names = {
                DeviceType.GLUCOSE_METER: "Glucose meter",
                DeviceType.INSULIN_PUMP: "Insulin pump",
                DeviceType.BLOOD_PRESSURE: "Blood pressure monitor",
                DeviceType.PULSE_OXIMETER: "Pulse oximeter",
                DeviceType.FITNESS_TRACKER: "Fitness tracker",
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
        
        # Last resort: protocol + identifier
        if self.metadata:
            ip = self.metadata.get('ip_address') or self.metadata.get('ip')
            if ip:
                return f"{self.protocol.value} device ({ip})"
        
        mac_short = self.mac_address.replace(":", "")[-6:].upper()
        return f"{self.protocol.value} device (MAC: {mac_short})"
    
    def __str__(self) -> str:
        """String representation of device."""
        return f"Device({self.name}, {self.device_type.value}, MAC: {self.mac_address}, Score: {self.security_score})"


# Sample medical devices (for tests)
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
        "has_encryption": False,
        "requires_pairing": False,
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
