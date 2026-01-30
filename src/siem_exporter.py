#!/usr/bin/env python3
"""
Moduł eksportu danych do systemów SIEM (Security Information and Event Management).

Obsługuje formaty:
- CEF (Common Event Format) - Splunk, ArcSight, QRadar
- JSON Lines - ELK Stack (Elasticsearch, Logstash, Kibana)
- Syslog - QRadar, inne SIEM
- CSV - uniwersalny format

UŻYCIE:
    exporter = SIEMExporter(format='cef', output_file='siem_export.cef')
    exporter.export_devices(devices)
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from enum import Enum

from device import Device


class SIEMFormat(Enum):
    """Formaty eksportu SIEM."""
    CEF = "cef"
    JSON_LINES = "jsonl"
    SYSLOG = "syslog"
    CSV = "csv"


class SIEMExporter:
    """
    Eksporter danych do systemów SIEM.
    
    Eksportuje dane o urządzeniach w różnych formatach:
    - CEF (Common Event Format) - standardowy format dla SIEM
    - JSON Lines - dla ELK Stack
    - Syslog - dla QRadar i innych
    - CSV - uniwersalny format
    """
    
    def __init__(self, format: str = "cef", output_file: Optional[str] = None, 
                 syslog_host: Optional[str] = None, syslog_port: int = 514):
        """
        Inicjalizacja eksportera SIEM.
        
        Args:
            format: Format eksportu ('cef', 'jsonl', 'syslog', 'csv')
            output_file: Ścieżka do pliku wyjściowego (None = stdout)
            syslog_host: Host syslog (tylko dla formatu syslog)
            syslog_port: Port syslog (tylko dla formatu syslog)
        """
        self.format = SIEMFormat(format.lower())
        self.output_file = output_file
        self.syslog_host = syslog_host
        self.syslog_port = syslog_port
        self.output_lines = []
    
    def export_devices(self, devices: List[Device], scan_timestamp: Optional[str] = None) -> str:
        """
        Eksportuje listę urządzeń do wybranego formatu SIEM.
        
        Args:
            devices: Lista urządzeń Device do eksportu
            scan_timestamp: Timestamp skanowania (opcjonalne)
        
        Returns:
            Ścieżka do wygenerowanego pliku lub stdout
        """
        if not scan_timestamp:
            scan_timestamp = datetime.now().isoformat()
        
        if self.format == SIEMFormat.CEF:
            return self._export_cef(devices, scan_timestamp)
        elif self.format == SIEMFormat.JSON_LINES:
            return self._export_json_lines(devices, scan_timestamp)
        elif self.format == SIEMFormat.SYSLOG:
            return self._export_syslog(devices, scan_timestamp)
        elif self.format == SIEMFormat.CSV:
            return self._export_csv(devices, scan_timestamp)
        else:
            raise ValueError(f"Nieobsługiwany format: {self.format}")
    
    def _export_cef(self, devices: List[Device], timestamp: str) -> str:
        """
        Eksportuje urządzenia w formacie CEF (Common Event Format).
        
        Format CEF:
        CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|Extension
        
        Args:
            devices: Lista urządzeń
            timestamp: Timestamp skanowania
        
        Returns:
            Ścieżka do pliku lub stdout
        """
        lines = []
        
        for device in devices:
            # Określ severity na podstawie security score
            severity = self._calculate_severity(device.security_score)
            
            # Extension fields (key=value pairs)
            extension = {
                'src': device.metadata.get('ip_address', 'N/A'),
                'mac': device.mac_address,
                'deviceType': device.device_type.value,
                'protocol': device.protocol.value,
                'securityScore': device.security_score,
                'hasEncryption': 'true' if device.has_encryption else 'false',
                'vulnerabilityCount': len(device.vulnerabilities),
                'vulnerabilities': ';'.join(device.vulnerabilities[:5]) if device.vulnerabilities else 'none'
            }
            
            # Format extension
            ext_str = ' '.join([f"{k}={self._escape_cef_value(str(v))}" for k, v in extension.items()])
            
            # CEF header
            cef_line = (
                f"CEF:0|Medical Device Scanner|Security Scanner|1.0|"
                f"device_scan|{self._escape_cef_value(device.name)}|{severity}|{ext_str}"
            )
            
            lines.append(cef_line)
        
        return self._write_output(lines)
    
    def _export_json_lines(self, devices: List[Device], timestamp: str) -> str:
        """
        Eksportuje urządzenia w formacie JSON Lines (dla ELK Stack).
        
        Args:
            devices: Lista urządzeń
            timestamp: Timestamp skanowania
        
        Returns:
            Ścieżka do pliku lub stdout
        """
        lines = []
        
        for device in devices:
            event = {
                '@timestamp': timestamp,
                'event': {
                    'kind': 'event',
                    'category': 'network',
                    'type': 'device_scan',
                    'severity': self._calculate_severity(device.security_score)
                },
                'device': {
                    'name': device.name,
                    'mac_address': device.mac_address,
                    'ip_address': device.metadata.get('ip_address'),
                    'type': device.device_type.value,
                    'protocol': device.protocol.value,
                    'manufacturer': device.manufacturer,
                    'security_score': device.security_score,
                    'has_encryption': device.has_encryption,
                    'encryption_type': device.encryption_type,
                    'requires_pairing': device.requires_pairing,
                    'vulnerabilities': device.vulnerabilities,
                    'vulnerability_count': len(device.vulnerabilities),
                    'open_ports': device.metadata.get('open_ports', [])
                },
                'scan': {
                    'timestamp': timestamp,
                    'scanner': 'Medical Device Security Scanner'
                }
            }
            
            lines.append(json.dumps(event, ensure_ascii=False))
        
        return self._write_output(lines)
    
    def _export_syslog(self, devices: List[Device], timestamp: str) -> str:
        """
        Eksportuje urządzenia w formacie Syslog.
        
        Format: <PRI>timestamp hostname tag: message
        
        Args:
            devices: Lista urządzeń
            timestamp: Timestamp skanowania
        
        Returns:
            Ścieżka do pliku lub stdout
        """
        lines = []
        hostname = "medical-scanner"
        
        for device in devices:
            # Priority: facility (16 = local0) + severity
            severity_num = self._severity_to_syslog_num(self._calculate_severity(device.security_score))
            priority = 16 * 8 + severity_num  # local0 facility
            
            # Message
            message = (
                f"device_scan device={device.name} "
                f"mac={device.mac_address} "
                f"ip={device.metadata.get('ip_address', 'N/A')} "
                f"type={device.device_type.value} "
                f"protocol={device.protocol.value} "
                f"score={device.security_score} "
                f"vulns={len(device.vulnerabilities)}"
            )
            
            # Syslog format
            syslog_line = f"<{priority}>{timestamp} {hostname} medical-scanner: {message}"
            lines.append(syslog_line)
        
        # Jeśli podano syslog host, wyślij przez socket
        if self.syslog_host:
            self._send_syslog(lines)
        
        return self._write_output(lines)
    
    def _export_csv(self, devices: List[Device], timestamp: str) -> str:
        """
        Eksportuje urządzenia w formacie CSV.
        
        Args:
            devices: Lista urządzeń
            timestamp: Timestamp skanowania
        
        Returns:
            Ścieżka do pliku lub stdout
        """
        if not self.output_file:
            self.output_file = f"siem_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Timestamp', 'Name', 'MAC Address', 'IP Address', 'Type', 'Protocol',
                'Manufacturer', 'Security Score', 'Has Encryption', 'Encryption Type',
                'Requires Pairing', 'Vulnerability Count', 'Vulnerabilities', 'Open Ports'
            ])
            
            # Data
            for device in devices:
                writer.writerow([
                    timestamp,
                    device.name,
                    device.mac_address,
                    device.metadata.get('ip_address', 'N/A'),
                    device.device_type.value,
                    device.protocol.value,
                    device.manufacturer or 'N/A',
                    device.security_score,
                    'Yes' if device.has_encryption else 'No',
                    device.encryption_type or 'N/A',
                    'Yes' if device.requires_pairing else 'No',
                    len(device.vulnerabilities),
                    '; '.join(device.vulnerabilities[:10]),
                    ', '.join(map(str, device.metadata.get('open_ports', [])))
                ])
        
        return self.output_file
    
    def _write_output(self, lines: List[str]) -> str:
        """
        Zapisuje linie do pliku lub stdout.
        
        Args:
            lines: Lista linii do zapisania
        
        Returns:
            Ścieżka do pliku lub 'stdout'
        """
        if self.output_file:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            return self.output_file
        else:
            # stdout
            print('\n'.join(lines))
            return 'stdout'
    
    def _send_syslog(self, lines: List[str]):
        """
        Wysyła linie syslog przez socket.
        
        Args:
            lines: Lista linii syslog
        """
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            for line in lines:
                sock.sendto(line.encode('utf-8'), (self.syslog_host, self.syslog_port))
            
            sock.close()
        except Exception as e:
            print(f"⚠️  Błąd wysyłania syslog: {e}")
    
    def _calculate_severity(self, security_score: int) -> str:
        """
        Oblicza severity na podstawie security score.
        
        Args:
            security_score: Security score (0-100)
        
        Returns:
            Severity ('Low', 'Medium', 'High', 'Critical')
        """
        if security_score >= 80:
            return "Low"
        elif security_score >= 50:
            return "Medium"
        elif security_score >= 30:
            return "High"
        else:
            return "Critical"
    
    def _severity_to_syslog_num(self, severity: str) -> int:
        """
        Konwertuje severity na numer syslog.
        
        Args:
            severity: Severity string
        
        Returns:
            Numer severity syslog (0-7)
        """
        mapping = {
            "Low": 6,      # Informational
            "Medium": 4,   # Warning
            "High": 3,     # Error
            "Critical": 2  # Critical
        }
        return mapping.get(severity, 6)
    
    def _escape_cef_value(self, value: str) -> str:
        """
        Escapuje wartość dla formatu CEF.
        
        Args:
            value: Wartość do escapowania
        
        Returns:
            Escapowana wartość
        """
        # CEF wymaga escapowania: \ = \\, | = \|, \n = \\n
        return value.replace('\\', '\\\\').replace('|', '\\|').replace('\n', '\\n')


def export_to_siem(devices: List[Device], format: str = "cef", 
                   output_file: Optional[str] = None, **kwargs) -> str:
    """
    Funkcja pomocnicza do eksportu do SIEM.
    
    Args:
        devices: Lista urządzeń
        format: Format eksportu ('cef', 'jsonl', 'syslog', 'csv')
        output_file: Ścieżka do pliku wyjściowego
        **kwargs: Dodatkowe parametry (syslog_host, syslog_port)
    
    Returns:
        Ścieżka do wygenerowanego pliku
    """
    exporter = SIEMExporter(format=format, output_file=output_file, **kwargs)
    return exporter.export_devices(devices)


if __name__ == "__main__":
    # Test eksportera
    from device import Device, DeviceType, Protocol
    
    # Przykładowe urządzenie
    test_device = Device(
        mac_address="00:11:22:33:44:55",
        name="Test Medical Device",
        device_type=DeviceType.UNKNOWN,
        protocol=Protocol.WIFI,
        has_encryption=True,
        encryption_type="WPA2",
        requires_pairing=True,
        metadata={
            "ip_address": "192.168.1.100",
            "open_ports": [80, 443, 22]
        }
    )
    test_device.add_vulnerability("HTTP bez HTTPS")
    test_device.calculate_security_score()
    
    # Test różnych formatów
    print("=== Test CEF ===")
    export_to_siem([test_device], format="cef", output_file="test_cef.cef")
    
    print("\n=== Test JSON Lines ===")
    export_to_siem([test_device], format="jsonl", output_file="test_jsonl.jsonl")
    
    print("\n=== Test CSV ===")
    export_to_siem([test_device], format="csv", output_file="test_csv.csv")
    
    print("\n✅ Test zakończony!")
