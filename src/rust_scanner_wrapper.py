#!/usr/bin/env python3
"""
Rust module wrapper for fast port scanning and data processing (PyO3). Use when built; Python fallback otherwise.
Usage: from rust_scanner_wrapper import FastPortScanner, DeviceProcessor; scanner.scan_ports(host, ports)
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional

RUST_SCANNER_AVAILABLE = False
FastPortScanner = None
DeviceProcessor = None
fast_scan_ports = None

try:
    import rust_scanner
    RUST_SCANNER_AVAILABLE = True
    FastPortScanner = rust_scanner.FastPortScanner
    DeviceProcessor = rust_scanner.DeviceProcessor
    fast_scan_ports = rust_scanner.fast_scan_ports
except ImportError:
    RUST_SCANNER_AVAILABLE = False


class FastPortScannerPython:
    """Python fallback when Rust module is not available (slower but compatible)."""
    
    def __init__(self, timeout_ms: int = 1000, max_concurrent: int = 50):
        self.timeout_ms = timeout_ms
        self.max_concurrent = max_concurrent
    
    def scan_ports(self, ip: str, ports: List[int]) -> List[int]:
        """Scan TCP ports (Python implementation)."""
        import socket
        from concurrent.futures import ThreadPoolExecutor, as_completed
        open_ports = []
        timeout = self.timeout_ms / 1000.0
        
        def check_port(port: int) -> Optional[int]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))
                sock.close()
                return port if result == 0 else None
            except Exception:
                return None
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            futures = {executor.submit(check_port, port): port for port in ports}
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    open_ports.append(result)
        
        return sorted(open_ports)
    
    def scan_multiple_ips(self, ips: List[str], ports: List[int]) -> Dict[str, List[int]]:
        """Scan multiple IPs."""
        results = {}
        for ip in ips:
            results[ip] = self.scan_ports(ip, ports)
        return results


class DeviceProcessorPython:
    """Python fallback when Rust is not available."""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
    
    def process_devices(self, devices: List[Dict]) -> List[List[Dict]]:
        """Process devices in batches."""
        from datetime import datetime
        
        results = []
        for i in range(0, len(devices), self.batch_size):
            batch = devices[i:i + self.batch_size]
            processed_batch = []
            for device in batch:
                processed = device.copy()
                processed['processed_at'] = int(datetime.now().timestamp())
                processed_batch.append(processed)
            results.append(processed_batch)
        
        return results
    
    def calculate_security_stats(self, devices: List[Dict]) -> Dict:
        """Compute security statistics."""
        if not devices:
            return {
                'total_devices': 0,
                'avg_security_score': 0.0,
                'with_encryption': 0,
                'with_pairing': 0,
                'total_vulnerabilities': 0,
                'avg_vulnerabilities_per_device': 0.0
            }
        
        total_score = 0.0
        with_encryption = 0
        with_pairing = 0
        vulnerability_count = 0
        
        for device in devices:
            total_score += device.get('security_score', 0)
            if device.get('has_encryption', False):
                with_encryption += 1
            if device.get('requires_pairing', False):
                with_pairing += 1
            vulnerability_count += len(device.get('vulnerabilities', []))
        
        device_count = len(devices)
        return {
            'total_devices': device_count,
            'avg_security_score': total_score / device_count if device_count > 0 else 0.0,
            'with_encryption': with_encryption,
            'with_pairing': with_pairing,
            'total_vulnerabilities': vulnerability_count,
            'avg_vulnerabilities_per_device': vulnerability_count / device_count if device_count > 0 else 0.0
        }


if RUST_SCANNER_AVAILABLE:
    FastPortScanner = rust_scanner.FastPortScanner
    DeviceProcessor = rust_scanner.DeviceProcessor
    fast_scan_ports = rust_scanner.fast_scan_ports
else:
    FastPortScanner = FastPortScannerPython
    DeviceProcessor = DeviceProcessorPython
    fast_scan_ports = None


def is_rust_available() -> bool:
    """Return whether the Rust module is available."""
    return RUST_SCANNER_AVAILABLE


if __name__ == "__main__":
    if RUST_SCANNER_AVAILABLE:
        print("✅ Rust scanner available – using Rust version!")
    else:
        print("⚠️  Rust scanner not available – using Python fallback")
        print("   To use Rust, build the module: cd rust_scanner && maturin develop")
    scanner = FastPortScanner(timeout_ms=1000, max_concurrent=50)
    print("\n🔍 Scanning ports on localhost...")
    open_ports = scanner.scan_ports("127.0.0.1", [22, 80, 443, 5432, 8080])
    print(f"✅ Open ports: {open_ports}")
