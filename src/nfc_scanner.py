#!/usr/bin/env python3
"""
NFC scanner – detects NFC medical devices.

Uses nfcpy or other libraries to detect NFC devices and analyze their security properties.
"""

import sys
import os
from typing import List, Optional, Dict
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    import nfc
    NFC_AVAILABLE = True
except ImportError:
    NFC_AVAILABLE = False

try:
    from smartcard.System import readers
    from smartcard.util import toHexString
    PYSMCARD_AVAILABLE = True
except ImportError:
    PYSMCARD_AVAILABLE = False

from device import Device, DeviceType, Protocol

console = Console()


class NFCScanner:
    """NFC scanner using nfcpy or pyscard. Detects NFC devices (cards, tags) and analyzes security. Requires NFC reader."""
    
    def __init__(self):
        """Initialize NFC scanner."""
        if not NFC_AVAILABLE and not PYSMCARD_AVAILABLE:
            console.print("[yellow]⚠️  NFC libraries are not installed.[/yellow]")
            console.print("[yellow]   Install: pip install nfcpy pyscard[/yellow]")
            console.print("[yellow]   NFC reader required (e.g. ACR122U)[/yellow]\n")
        self.scanned_devices: List[Device] = []
    
    def scan_nfc_devices(self, duration: int = 5) -> List[Device]:
        """Scan for NFC devices in range. duration: scan time in seconds. Returns list of Device."""
        console.print("[cyan]🔍 Starting NFC scan...[/cyan]")
        console.print("[dim]Hold NFC device near the reader...[/dim]\n")
        
        devices: List[Device] = []
        
        if NFC_AVAILABLE:
            nfc_devices = self._scan_nfcpy(duration)
            devices.extend(nfc_devices)
        elif PYSMCARD_AVAILABLE:
            smartcard_devices = self._scan_smartcard()
            devices.extend(smartcard_devices)
        else:
            console.print("[yellow]⚠️  No NFC libraries available – cannot scan[/yellow]")
            console.print("[yellow]   NFC requires dedicated hardware (NFC reader)[/yellow]\n")
        self.scanned_devices = devices
        console.print(f"\n[green]✅ NFC scan finished. Found {len(devices)} device(s).[/green]\n")
        return devices
    
    def _scan_nfcpy(self, duration: int) -> List[Device]:
        """Scan NFC devices using nfcpy. Requires connected NFC reader (e.g. ACR122U, PN532). Returns list of Device."""
        devices: List[Device] = []
        try:
            clf = nfc.ContactlessFrontend('usb')
            if not clf:
                console.print("[yellow]⚠️  No NFC reader found[/yellow]")
                console.print("[yellow]   Check that the reader is connected[/yellow]\n")
                return devices
            console.print("[green]✓ NFC reader detected[/green]\n")
            import time
            start_time = time.time()
            while time.time() - start_time < duration:
                tag = clf.connect(rdwr={'on-connect': self._on_nfc_connect})
                if tag:
                    device = self._analyze_nfc_tag(tag)
                    if device:
                        devices.append(device)
                        console.print(f"  [green]✓[/green] Detected: {device.name}")
                        break
            clf.close()
        except Exception as e:
            console.print(f"[yellow]⚠️  NFC scan error: {e}[/yellow]")
            console.print("[yellow]   Check that the NFC reader is connected and working[/yellow]\n")
        
        return devices
    
    def _scan_smartcard(self) -> List[Device]:
        """Scan smart cards using pyscard (PC/SC). Requires system PCSC libs (e.g. libpcsclite-dev on Linux). Returns list of Device."""
        devices: List[Device] = []
        try:
            reader_list = readers()
            if not reader_list:
                console.print("[yellow]⚠️  No card readers found[/yellow]\n")
                return devices
            console.print(f"[green]✓ Found {len(reader_list)} reader(s)[/green]\n")
            for reader in reader_list:
                try:
                    connection = reader.createConnection()
                    connection.connect()
                    atr = connection.getATR()
                    device = Device(
                        mac_address=f"NFC-{toHexString(atr)[:17]}",
                        name=f"NFC-Card-{toHexString(atr)[:8]}",
                        device_type=DeviceType.UNKNOWN,
                        protocol=Protocol.NFC,
                        has_encryption=True,
                        encryption_type="Basic encryption (smart card)",
                        requires_pairing=True,
                        metadata={
                            "atr": toHexString(atr),
                            "reader": str(reader)
                        }
                    )
                    device.calculate_security_score()
                    devices.append(device)
                    console.print(f"  [green]✓[/green] Detected: {device.name}")
                except Exception:
                    continue
        except Exception as e:
            console.print(f"[yellow]⚠️  Card scan error: {e}[/yellow]\n")
        
        return devices
    
    def _on_nfc_connect(self, tag):
        """Callback when NFC tag is detected."""
        return True
    
    def _analyze_nfc_tag(self, tag) -> Optional[Device]:
        """Analyze NFC tag and create Device. Returns Device or None."""
        try:
            tag_type = str(tag.type)
            identifier = tag.identifier.hex()
            device_type = DeviceType.UNKNOWN
            has_encryption = True
            encryption_type = "Basic encryption (NFC tag)"
            requires_pairing = False
            
            device = Device(
                mac_address=f"NFC-{identifier[:17]}",
                name=f"NFC-Tag-{identifier[:8]}",
                device_type=device_type,
                protocol=Protocol.NFC,
                has_encryption=has_encryption,
                encryption_type=encryption_type,
                requires_pairing=requires_pairing,
                metadata={
                    "tag_type": tag_type,
                    "identifier": identifier
                }
            )
            
            device.calculate_security_score()
            return device
        
        except Exception:
            return None
    
    def get_all_devices(self) -> List[Device]:
        """Return all detected devices."""
        return self.scanned_devices


if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold cyan]🔍 Test: NFC Scanner[/bold cyan]\n"
        "[dim]Hold NFC device near the reader...[/dim]",
        style="cyan"
    ))
    console.print()
    scanner = NFCScanner()
    devices = scanner.scan_nfc_devices(duration=5)
    console.print(f"\n[bold green]✅ Found {len(devices)} device(s):[/bold green]\n")
    for device in devices:
        console.print(f"[cyan]{device.name}[/cyan] ({device.mac_address})")
        console.print(f"  Type: {device.device_type.value}")
        console.print(f"  Encryption: {'✅ Yes' if device.has_encryption else '❌ No'}")
        console.print(f"  Security Score: {device.security_score}/100")
        console.print()
