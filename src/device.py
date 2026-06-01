"""Medical device representation. Defines Device class and related enums."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
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
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_last_seen(self) -> None:
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
    
    def add_vulnerability(self, vulnerability: str) -> None:
        """Add vulnerability to list."""
        if vulnerability not in self.vulnerabilities:
            self.vulnerabilities.append(vulnerability)
            # Recalculate security score
            self.calculate_security_score()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert device to dict (for JSON/API)."""
        import numpy as np
        
        # Convert metadata to JSON-serializable types
        metadata_serializable: Dict[str, Any] = {}
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
        device_ip: Optional[str] = None
        if metadata_serializable:
            device_ip = metadata_serializable.get('ip_address') or metadata_serializable.get('ip')
        
        display_name = self.get_display_name()
        identification_quality = self._get_identification_quality(display_name, metadata_serializable)

        # Keep report concise: remove noisy empty/null fields from top-level output
        payload: Dict[str, Any] = {
            "label": display_name,
            "mac_address": self.mac_address,
            "name": self.name,
            "display_name": display_name,
            "identification_quality": identification_quality,
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
        return {
            k: v for k, v in payload.items()
            if v is not None and v != "" and not (isinstance(v, (list, dict)) and len(v) == 0)
        }

    def _get_identification_quality(self, display_name: str, metadata: Dict[str, Any]) -> str:
        """
        Estimate how confidently the device is identified:
        - high: explicit non-generic name or manufacturer+model
        - medium: useful hints (BLE local name/service names, manufacturer)
        - low: mostly generic fallback naming
        """
        import re

        name = (self.name or "").strip()
        generic_name = name in ("", "Unknown", "Unknown Device")
        generic_fallback = bool(re.match(r"^(Device|.+device)\s+\((MAC:\s*)?[0-9A-Fa-f]{6}\)$", display_name))
        manufacturer_with_suffix = bool(
            self.manufacturer and re.match(rf"^{re.escape(self.manufacturer)}\s+\([0-9A-Fa-f]{{6}}\)$", display_name)
        )
        ip_fallback = bool(re.match(r"^[A-Za-z0-9 _\-,.]+?\s*\(\d{1,3}(?:\.\d{1,3}){3}\)$", display_name))

        # Manufacturer-only fallback ("<Vendor> Device") is useful but not high-confidence.
        if display_name.endswith(" Device"):
            return "medium"
        if manufacturer_with_suffix:
            return "medium"
        if ip_fallback and not self.manufacturer and self.device_type == DeviceType.UNKNOWN:
            return "low"

        if self.manufacturer and self.model:
            return "high"
        if not generic_name and not generic_fallback and not display_name.startswith("Service ("):
            return "high"

        local_name = metadata.get("local_name")
        service_names = metadata.get("service_names") or []
        has_named_service = any(isinstance(s, str) and "Service (" not in s for s in service_names)

        if (local_name and str(local_name).strip()) or self.manufacturer or has_named_service:
            return "medium"

        return "low"
    
    def _convert_value_for_json(self, value: Any) -> Any:
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
    
    def _convert_dict_for_json(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Convert dict to JSON-serializable types."""
        result: Dict[str, Any] = {}
        for key, value in d.items():
            result[key] = self._convert_value_for_json(value)
        return result
    
    def get_device_fingerprint(self) -> str:
        """Generate unique device fingerprint (protocol, type, manufacturer, model, MAC suffix, IP)."""
        parts: List[str] = [
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
        Priority: device name (if not generic) → BLE: metadata local_name / service_names →
        manufacturer + model → device type + MAC → protocol + MAC.
        """
        import re
        
        # If name is IP, do not use as primary name
        is_ip = bool(re.match(r'^(\d{1,3}\.){3}\d{1,3}$', self.name))
        if is_ip:
            pass
        elif self.name and self.name not in ("Unknown", "Unknown Device"):
            # BLE: avoid generic inferred names like "Device (AB12CD)" or "Pulse oximeter (AB12CD)"
            mac_short_suffix = re.search(r'\s*\(([0-9A-Fa-f]{6})\)\s*$', self.name)
            if mac_short_suffix and (
                self.name.startswith("Device (") or
                self.name.startswith("Glucose meter (") or
                self.name.startswith("Pulse oximeter (") or
                self.name.startswith("Blood pressure monitor (") or
                self.name.startswith("Fitness tracker (") or
                self.name.startswith("Smartwatch (") or
                self.name.startswith("Insulin pump (")
            ):
                # Prefer advertised/local name or first service name from BLE metadata
                if self.protocol == Protocol.BLE and self.metadata:
                    local = self.metadata.get("local_name") or self.metadata.get("gatt_device_name")
                    if local and str(local).strip():
                        return str(local).strip()
                    services = self.metadata.get("service_names") or []
                    if services and isinstance(services, list) and len(services) > 0:
                        first_svc = services[0]
                        if isinstance(first_svc, str) and first_svc and "Service (" not in first_svc:
                            return f"{first_svc} ({mac_short_suffix.group(1)})"
                        if isinstance(first_svc, str):
                            return f"{first_svc} ({mac_short_suffix.group(1)})"
            else:
                return self.name
        
        # Try manufacturer + model
        if self.manufacturer and self.model:
            return f"{self.manufacturer} {self.model}"
        elif self.manufacturer:
            # Keep devices distinguishable in SIEM/Splunk even when many map to same vendor.
            if self.mac_address and self.mac_address != "--":
                mac_short = self.mac_address.replace(":", "")[-6:].upper()
                return f"{self.manufacturer} ({mac_short})"
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
