#!/usr/bin/env python3
"""
SIEM (Security Information and Event Management) export.

Formats: CEF (Splunk, ArcSight, QRadar), JSON Lines (ELK), Syslog, CSV.
Usage: SIEMExporter(format='cef', output_file='siem_export.cef'); exporter.export_devices(devices)
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from enum import Enum

from device import Device


class SIEMFormat(Enum):
    """SIEM export formats."""
    CEF = "cef"
    JSON_LINES = "jsonl"
    SYSLOG = "syslog"
    CSV = "csv"


class SIEMExporter:
    """Export device data to SIEM in CEF, JSON Lines, Syslog, or CSV."""
    
    def __init__(self, format: str = "cef", output_file: Optional[str] = None, 
                 syslog_host: Optional[str] = None, syslog_port: int = 514):
        """format: 'cef'|'jsonl'|'syslog'|'csv'; output_file: path or None for stdout; syslog_host/port for syslog."""
        self.format = SIEMFormat(format.lower())
        self.output_file = output_file
        self.syslog_host = syslog_host
        self.syslog_port = syslog_port
        self.output_lines = []
    
    def export_devices(self, devices: List[Device], scan_timestamp: Optional[str] = None) -> str:
        """Export device list to selected SIEM format. Returns output path or 'stdout'."""
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
            raise ValueError(f"Unsupported format: {self.format}")
    
    def _export_cef(self, devices: List[Device], timestamp: str) -> str:
        """Export devices as CEF (Common Event Format). Returns file path or 'stdout'."""
        lines = []
        for device in devices:
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
        """Export devices as JSON Lines (for ELK Stack). Returns file path or 'stdout'."""
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
        """Export devices as Syslog. Returns file path or 'stdout'."""
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
        
        # If syslog host given, send over socket
        if self.syslog_host:
            self._send_syslog(lines)
        
        return self._write_output(lines)
    
    def _export_csv(self, devices: List[Device], timestamp: str) -> str:
        """Export devices as CSV. Returns file path or 'stdout'."""
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
        Write lines to file or stdout. Returns path or 'stdout'."""
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
        Send syslog lines over socket."""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            for line in lines:
                sock.sendto(line.encode('utf-8'), (self.syslog_host, self.syslog_port))
            
            sock.close()
        except Exception as e:
            print(f"⚠️  Syslog send error: {e}")
    
    def _calculate_severity(self, security_score: int) -> str:
        """Compute severity from security score (0-100). Returns 'Low'|'Medium'|'High'|'Critical'."""
        if security_score >= 80:
            return "Low"
        elif security_score >= 50:
            return "Medium"
        elif security_score >= 30:
            return "High"
        else:
            return "Critical"
    
    def _severity_to_syslog_num(self, severity: str) -> int:
        """Map severity to syslog priority number (0-7)."""
        mapping = {
            "Low": 6,      # Informational
            "Medium": 4,   # Warning
            "High": 3,     # Error
            "Critical": 2  # Critical
        }
        return mapping.get(severity, 6)
    
    def _escape_cef_value(self, value: str) -> str:
        """
        Escape value for CEF format."""
        return value.replace('\\', '\\\\').replace('|', '\\|').replace('\n', '\\n')


def export_to_siem(devices: List[Device], format: str = "cef", 
                   output_file: Optional[str] = None, **kwargs) -> str:
    """Helper: export devices to SIEM. Returns output path."""
    exporter = SIEMExporter(format=format, output_file=output_file, **kwargs)
    return exporter.export_devices(devices)


if __name__ == "__main__":
    from device import Device, DeviceType, Protocol
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
    test_device.add_vulnerability("HTTP without HTTPS")
    test_device.calculate_security_score()
    print("=== Test CEF ===")
    export_to_siem([test_device], format="cef", output_file="test_cef.cef")
    
    print("\n=== Test JSON Lines ===")
    export_to_siem([test_device], format="jsonl", output_file="test_jsonl.jsonl")
    
    print("\n=== Test CSV ===")
    export_to_siem([test_device], format="csv", output_file="test_csv.csv")
    
    print("\n✅ Test completed!")
