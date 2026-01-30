#!/usr/bin/env python3
"""
Wrapper do modułu Rust dla szybkiego skanowania portów i przetwarzania danych.

Ten moduł integruje Rust z Pythonem używając PyO3.
Rust zapewnia:
- Bezpieczeństwo pamięci (brak dangling pointers, buffer overflows)
- Wydajność porównywalna z C/C++
- Przewidywalne zużycie pamięci, brak GC
- Doskonały do systemów wbudowanych i czasu rzeczywistego

UŻYCIE:
    # W Pythonie
    from rust_scanner_wrapper import FastPortScanner, DeviceProcessor
    
    scanner = FastPortScanner(timeout_ms=1000, max_concurrent=50)
    open_ports = scanner.scan_ports("192.168.1.1", [22, 80, 443, 3389])
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional

# Sprawdź czy moduł Rust jest dostępny
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
    # Moduł Rust nie jest dostępny - użyj fallback w Pythonie
    RUST_SCANNER_AVAILABLE = False


class FastPortScannerPython:
    """
    Fallback implementacja w Pythonie (gdy Rust nie jest dostępny).
    
    Ta implementacja jest wolniejsza niż Rust, ale zapewnia kompatybilność.
    """
    
    def __init__(self, timeout_ms: int = 1000, max_concurrent: int = 50):
        self.timeout_ms = timeout_ms
        self.max_concurrent = max_concurrent
    
    def scan_ports(self, ip: str, ports: List[int]) -> List[int]:
        """Skanuje porty TCP (implementacja Python - wolniejsza niż Rust)."""
        import socket
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        open_ports = []
        timeout = self.timeout_ms / 1000.0  # Konwertuj na sekundy
        
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
        """Skanuje wiele IP jednocześnie."""
        results = {}
        for ip in ips:
            results[ip] = self.scan_ports(ip, ports)
        return results


class DeviceProcessorPython:
    """
    Fallback implementacja w Pythonie (gdy Rust nie jest dostępny).
    """
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
    
    def process_devices(self, devices: List[Dict]) -> List[List[Dict]]:
        """Przetwarza urządzenia w batchach."""
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
        """Oblicza statystyki bezpieczeństwa."""
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


# Eksportuj odpowiednie klasy
if RUST_SCANNER_AVAILABLE:
    # Użyj Rust (szybsze)
    FastPortScanner = rust_scanner.FastPortScanner
    DeviceProcessor = rust_scanner.DeviceProcessor
    fast_scan_ports = rust_scanner.fast_scan_ports
else:
    # Użyj Python fallback (wolniejsze, ale działa)
    FastPortScanner = FastPortScannerPython
    DeviceProcessor = DeviceProcessorPython
    fast_scan_ports = None  # Nie dostępne w fallback


def is_rust_available() -> bool:
    """Sprawdza czy moduł Rust jest dostępny."""
    return RUST_SCANNER_AVAILABLE


# Przykład użycia
if __name__ == "__main__":
    if RUST_SCANNER_AVAILABLE:
        print("✅ Rust scanner dostępny - używam szybkiej wersji Rust!")
    else:
        print("⚠️  Rust scanner niedostępny - używam wolniejszej wersji Python")
        print("   Aby użyć Rust, zbuduj moduł:")
        print("   cd rust_scanner && maturin develop")
    
    # Test skanowania portów
    scanner = FastPortScanner(timeout_ms=1000, max_concurrent=50)
    print(f"\n🔍 Skanowanie portów na localhost...")
    open_ports = scanner.scan_ports("127.0.0.1", [22, 80, 443, 5432, 8080])
    print(f"✅ Otwarte porty: {open_ports}")
