#!/usr/bin/env python3
"""
Real BLE scanner – discovers actual Bluetooth Low Energy devices.

Uses the 'bleak' library to scan BLE devices and infer security properties
from advertising and GATT data.

Encryption detection:
1. Parse advertising data (flags, services)
2. Check GATT services/characteristics (security requirements)
3. Attempt connection without pairing (failure implies pairing required)
4. Use service UUIDs (medical devices use well-known UUIDs)

Medical vs consumer:
- Medical devices use standard UUIDs (e.g. 0x1808 Glucose Service)
- Consumer devices may use custom UUIDs
- Both use BLE but differ in services/characteristics

Connection errors are expected:
- Most BLE devices do not allow unpaired connections (secure by default)
- "Device not found", "Not paired", "Timeout" are normal
- Scanner still uses advertising data when connection fails
"""

import asyncio
import platform
import sys
import os
from typing import List, Optional, Dict, Set
from datetime import datetime

# Ensure src/ is on path for direct run: python3 src/real_scanner.py
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

try:
    from bleak import BleakScanner, BleakClient  # type: ignore
    from bleak.backends.device import BLEDevice  # type: ignore
    from bleak.backends.scanner import AdvertisementData  # type: ignore
    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False
    print("⚠️  'bleak' is not installed. Run: pip install bleak")

from device import Device, DeviceType, Protocol

console = Console()

# Medical service UUIDs (Bluetooth SIG)
MEDICAL_SERVICE_UUIDS = {
    "00001808-0000-1000-8000-00805f9b34fb": "Glucose Service",
    "0000180f-0000-1000-8000-00805f9b34fb": "Battery Service",
    "0000180a-0000-1000-8000-00805f9b34fb": "Device Information Service",
    "0000180d-0000-1000-8000-00805f9b34fb": "Heart Rate Service",
    "00001810-0000-1000-8000-00805f9b34fb": "Blood Pressure Service",
    "0000181a-0000-1000-8000-00805f9b34fb": "Environmental Sensing",
}

# Medical characteristic UUIDs
MEDICAL_CHARACTERISTIC_UUIDS = {
    "00002a18-0000-1000-8000-00805f9b34fb": "Blood Pressure Measurement",
    "00002a52-0000-1000-8000-00805f9b34fb": "Glucose Measurement",
    "00002a37-0000-1000-8000-00805f9b34fb": "Heart Rate Measurement",
}


class RealBLEScanner:
    """
    BLE scanner using the 'bleak' library.
    Discovers BLE devices and analyses their security properties from real data.
    """

    def __init__(self):
        """Initialize BLE scanner."""
        if not BLEAK_AVAILABLE:
            raise ImportError(
                "Biblioteka 'bleak' nie jest zainstalowana.\n"
                "Install: pip install bleak"
            )
        self.scanned_devices_dict: Dict[str, BLEDevice] = {}
        self.device_names: Dict[str, str] = {}  # Names captured in detection_callback
        self.scanned_devices: List[Device] = []
        self.advertisement_data: Dict[str, AdvertisementData] = {}
        
        # OUI lookup for manufacturer from MAC (first 3 bytes)
        try:
            from mac_vendor_lookup import MacLookup  # type: ignore
            self.mac_lookup = MacLookup()
            # Optional: update vendor DB (first run may be slow)
            # self.mac_lookup.update_vendors()  # Uncomment to update the database
            self.mac_lookup_available = True
        except ImportError:
            self.mac_lookup = None
            self.mac_lookup_available = False
            console.print("[dim]ℹ️  mac-vendor-lookup not available – manufacturer identification by MAC will be limited[/dim]")
            console.print("[dim]   Install: pip install mac-vendor-lookup[/dim]")
    
    def _scan_with_bluetoothctl_removed(self, duration: int = 10) -> List[Device]:
        """
        Alternative scan method using bluetoothctl – more reliable for device names.
        
        bluetoothctl is the official BlueZ tool and always shows device names.
        More reliable than bleak for name detection because it uses the system stack directly.
        
        Args:
            duration: Scan duration in seconds
            
        Returns:
            List of detected Device objects, or empty list if bluetoothctl is not available
        """
        devices: List[Device] = []
        device_info: Dict[str, Dict] = {}  # MAC -> {name, rssi}
        
        try:
            import subprocess
            import time
            import re
            
            console.print(f"[cyan]🔍 Using bluetoothctl for BLE scan ({duration}s)...[/cyan]")
            console.print("[dim]bluetoothctl is more reliable for detecting device names...[/dim]\n")
            
            # Start scan (bluetoothctl scan on)
            process = subprocess.Popen(
                ['bluetoothctl', 'scan', 'on'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Collect results for the given duration
            start_time = time.time()
            last_mac = None
            
            while time.time() - start_time < duration:
                try:
                    line = process.stdout.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    
                    line = line.strip()
                    
                    # Format: "[NEW] Device A6:D7:3C:DD:05:13 L3560 Series"
                    # lub: "Device A6:D7:3C:DD:05:13 L3560 Series"
                    match = re.search(r'Device\s+([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})\s*(.*)', line)
                    if match:
                        mac = match.group(1).upper()
                        name = match.group(2).strip() if match.group(2) else None
                        
                        if mac and mac.count(':') == 5:
                            if mac not in device_info:
                                device_info[mac] = {'name': name, 'rssi': None}
                            elif name and not device_info[mac]['name']:
                                device_info[mac]['name'] = name
                            last_mac = mac
                    
                    # RSSI: "RSSI: -91"
                    rssi_match = re.search(r'RSSI:\s*(-?\d+)', line)
                    if rssi_match and last_mac:
                        try:
                            rssi = int(rssi_match.group(1))
                            if last_mac in device_info:
                                device_info[last_mac]['rssi'] = rssi
                        except ValueError:
                            pass
                
                except Exception:
                    continue
            
            # Zatrzymaj skanowanie
            try:
                subprocess.run(['bluetoothctl', 'scan', 'off'], timeout=2, capture_output=True)
            except Exception:
                pass
            
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
            
            # Show found devices
            for mac, info in device_info.items():
                name = info['name'] or "Unknown Device"
                rssi = info.get('rssi')
                console.print(f"  [green]✓[/green] Detected: [cyan]{name}[/cyan] ({mac})")
                if rssi:
                    console.print(f"    RSSI: {rssi} dBm")
            
            # Save to self.device_names for later analysis
            for mac, info in device_info.items():
                if info['name']:
                    self.device_names[mac] = info['name']
            
            # Analyze each device with bleak (for security details)
            if device_info:
                console.print(f"\n[green]✅ Scan complete. Found {len(device_info)} devices.[/green]\n")
                console.print("[cyan]🔒 Analyzing device security properties...[/cyan]\n")
                
                for mac, info in device_info.items():
                    try:
                        device = asyncio.run(self._analyze_device(mac))
                        if device:
                            if info['name']:
                                device.name = info['name']
                            devices.append(device)
                    except Exception:
                        name = info['name'] or "Unknown Device"
                        manufacturer = self._get_manufacturer_from_mac(mac)
                        
                        device = Device(
                            mac_address=mac,
                            name=name,
                            device_type=DeviceType.UNKNOWN,
                            protocol=Protocol.BLE,
                            has_encryption=False,
                            requires_pairing=False,
                            manufacturer=manufacturer,
                            rssi=info.get('rssi'),
                            metadata={'scanned_with': 'bluetoothctl'}
                        )
                        device.calculate_security_score()
                        devices.append(device)
            
        except FileNotFoundError:
            return []
        except Exception as e:
            return []
        
        return devices
    
    async def scan_ble_devices(self, duration: int = 10) -> List[Device]:
        """
        Scan for BLE devices in range.
        
        Args:
            duration: Scan duration in seconds
            
        Returns:
            List of detected Device objects
        """
        console.print(f"[cyan]🔍 Starting BLE scan ({duration}s)...[/cyan]")
        console.print("[dim]Scanning for Bluetooth devices in range...[/dim]")
        console.print("[dim]💡 Physical device: laptop Bluetooth adapter[/dim]")
        console.print("[dim]💡 Only devices in range are detected (RSSI > -90 dBm)[/dim]")
        if duration < 15:
            console.print("[dim]💡 Longer scan (--ble-duration 20–30) helps detect devices that advertise less often.[/dim]")
        console.print()
        
        devices: List[Device] = []
        # Set of unique MAC addresses to avoid duplicates
        # (same device may be seen multiple times during scan)
        discovered_devices: Set[str] = set()
        
        def detection_callback(device: BLEDevice, advertisement_data: AdvertisementData):
            """
            Callback invoked by BleakScanner when a device is detected.
            
            We do not call this manually; BleakScanner calls it for each new BLE device.
            
            Args:
                device: Device info (name, MAC address)
                advertisement_data: Advertising data broadcast by the device
            """
            if device.address not in discovered_devices:
                discovered_devices.add(device.address)
                self.advertisement_data[device.address] = advertisement_data
                self.scanned_devices_dict[device.address] = device
                
                # Save device name now – it may not be available later
                # device.name can be None; advertisement_data.local_name may have the name
                device_name = None
                
                # Priorytet 1: device.name (najbardziej niezawodna)
                if device.name:
                    device_name = str(device.name).strip()
                # Priorytet 2: advertisement_data.local_name
                elif advertisement_data.local_name:
                    device_name = str(advertisement_data.local_name).strip()
                else:
                    device_name = None
                
                # Always save name if available (may only be available during callback)
                if device_name and device_name.strip():
                    normalized_address = device.address.upper()
                    self.device_names[normalized_address] = device_name.strip()
                
                display_name = device_name
                if not display_name:
                    try:
                        from oui_lookup import get_oui_lookup
                        oui_lookup = get_oui_lookup()
                        manufacturer = oui_lookup.lookup(device.address)
                        if manufacturer:
                            display_name = manufacturer
                    except Exception:
                        pass
                
                display_name = display_name or "Unknown Device"
                console.print(f"  [green]✓[/green] Detected: [cyan]{display_name}[/cyan] ({device.address})")
                if advertisement_data.rssi:
                    console.print(f"    RSSI: {advertisement_data.rssi} dBm")
        
        async with BleakScanner(detection_callback=detection_callback):
            await asyncio.sleep(duration)
        
        console.print(f"\n[green]✅ Scan complete. Found {len(discovered_devices)} devices.[/green]\n")
        
        if discovered_devices:
            console.print("[cyan]🔒 Analyzing device security properties...[/cyan]")
            console.print("[dim]ℹ️  Connection errors are normal – most devices require pairing (that is secure!)[/dim]\n")
            
            # Filter by RSSI (only devices in range). RSSI > -95 dBm = reasonable range
            # No RSSI = accept (some stacks do not provide RSSI in callback)
            filtered_addresses = []
            for address in discovered_devices:
                ad_data = self.advertisement_data.get(address)
                if ad_data and ad_data.rssi is not None:
                    if ad_data.rssi > -95:
                        filtered_addresses.append(address)
                else:
                    filtered_addresses.append(address)
            
            if len(discovered_devices) > len(filtered_addresses):
                console.print(f"[dim]   Skipped {len(discovered_devices) - len(filtered_addresses)} devices out of range (RSSI ≤ -95 dBm)[/dim]\n")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                for address in filtered_addresses:
                    device_display_name = self.device_names.get(address) or "Unknown Device"
                    task = progress.add_task(f"Analyzing {device_display_name}...", total=None)
                    
                    try:
                        device = await self._analyze_device(address)
                        if device:
                            devices.append(device)
                            progress.update(task, description=f"✓ {device.name}")
                    except Exception as e:
                        if "TimeoutError" not in str(type(e).__name__) and "not found" not in str(e).lower():
                            console.print(f"[red]  ✗ Analysis error {address}: {e}[/red]")
                        progress.update(task, description=f"✗ {device_display_name}")
        
        self.scanned_devices = devices
        return devices
    
    async def _analyze_device(self, address: str) -> Optional[Device]:
        """
        Analyze a BLE device and detect its security properties.
        
        1. Get advertising data
        2. Attempt to connect
        3. Check GATT services and characteristics
        4. Detect encryption and pairing requirements
        5. Determine device type (medical vs consumer)
        
        Args:
            address: Device MAC address
            
        Returns:
            Device object with security analysis
        """
        ad_data = self.advertisement_data.get(address)
        if not ad_data:
            return None
        
        ble_device = self.scanned_devices_dict.get(address)
        name = None
        
        normalized_address = address.upper()
        if normalized_address in self.device_names:
            saved_name = self.device_names[normalized_address]
            if saved_name and saved_name.strip():
                name = saved_name.strip()
        
        if not name and ble_device:
            if hasattr(ble_device, 'name') and ble_device.name:
                name = ble_device.name
        
        if not name and ad_data.local_name:
            name = ad_data.local_name
        
        rssi = ad_data.rssi or -100
        
        service_uuids = ad_data.service_uuids or []
        manufacturer_data = ad_data.manufacturer_data or {}
        
        manufacturer_from_mac = self._get_manufacturer_from_mac(address)
        if not name and manufacturer_from_mac:
            name = manufacturer_from_mac
        
        device_type = self._detect_device_type(service_uuids, name, manufacturer_from_mac)
        
        if not name or name == "Unknown Device":
            mac_short = address.replace(":", "")[-6:].upper()
            
            if device_type != DeviceType.UNKNOWN:
                type_names = {
                    DeviceType.GLUCOSE_METER: "Glucose meter",
                    DeviceType.INSULIN_PUMP: "Insulin pump",
                    DeviceType.BLOOD_PRESSURE: "Blood pressure monitor",
                    DeviceType.PULSE_OXIMETER: "Pulse oximeter",
                    DeviceType.FITNESS_TRACKER: "Fitness tracker",
                    DeviceType.SMARTWATCH: "Smartwatch",
                }
                type_name = type_names.get(device_type, device_type.value)
                name = f"{type_name} ({mac_short})"
            elif manufacturer_from_mac:
                manufacturer_short = manufacturer_from_mac[:20] if len(manufacturer_from_mac) > 20 else manufacturer_from_mac
                name = f"{manufacturer_short} ({mac_short})"
            else:
                name = f"Device ({mac_short})"
        
        has_encryption = False
        requires_pairing = False
        security_flags = []
        
        try:
            async with BleakClient(address, timeout=3.0) as client:
                requires_pairing = False
                
                try:
                    if hasattr(client, 'get_services') and callable(getattr(client, 'get_services')):
                        services = await client.get_services()
                    else:
                        if hasattr(client, 'services'):
                            services = client.services
                        else:
                            services = await client.get_services() if hasattr(client, 'get_services') else []
                except (AttributeError, TypeError) as api_error:
                    try:
                        services = client.services
                    except AttributeError:
                        services = []
                
                for service in services:
                    service_uuid = str(service.uuid).lower()
                    
                    for char in service.characteristics:
                        char_props = char.properties
                        
                        if "encrypt" in char_props or "encrypt-authenticate" in char_props:
                            has_encryption = True
                            security_flags.append(f"Encryption required for {service_uuid[:8]}")
                        
                        if "authenticate" in char_props or "authorize" in char_props:
                            requires_pairing = True
                            security_flags.append(f"Authentication required for {service_uuid[:8]}")
                
                if not has_encryption and not requires_pairing:
                    flags = ad_data.service_data or {}
                    if flags and device_type != DeviceType.UNKNOWN:
                        has_encryption = True
                        requires_pairing = True
                
        except Exception as e:
            error_msg = str(e).lower()
            error_type = type(e).__name__
            
            if ("not paired" in error_msg or "pairing" in error_msg or 
                "authentication" in error_msg or "not authorized" in error_msg or
                "insufficient authentication" in error_msg):
                requires_pairing = True
                has_encryption = True
                
            elif "not found" in error_msg or "was not found" in error_msg or "device" in error_msg and "not found" in error_msg:
                pass
                
            elif "timeout" in error_msg or "timed out" in error_msg:
                if device_type != DeviceType.UNKNOWN:
                    has_encryption = True
                    requires_pairing = True
                
            elif "get_services" in error_msg or "attribute" in error_msg:
                console.print(f"[dim]    ⚠️  {address}: bleak API issue (possible version mismatch)[/dim]")
                
            elif "connection" in error_msg or "failed" in error_msg:
                if device_type != DeviceType.UNKNOWN:
                    has_encryption = True
                    requires_pairing = True
                
            else:
                if "get_services" not in error_msg and "not found" not in error_msg:
                    console.print(f"[dim]    ⚠️  {address}: {error_type}[/dim]")
        
        if device_type != DeviceType.UNKNOWN and not has_encryption:
            pass  # Keep has_encryption=False to flag as vulnerability
        
        encryption_type = None
        if has_encryption:
            if requires_pairing:
                encryption_type = "LE Secure Connections (AES-256)"
            elif "encrypt-authenticate" in str(security_flags).lower():
                encryption_type = "AES-256"
            else:
                encryption_type = "AES-128"
        else:
            encryption_type = "No encryption"
        
        # Create Device object
        device = Device(
            mac_address=address,
            name=name,
            device_type=device_type,
            protocol=Protocol.BLE,
            has_encryption=has_encryption,
            encryption_type=encryption_type,
            requires_pairing=requires_pairing,
            rssi=rssi,
            manufacturer=manufacturer_from_mac or (self._extract_manufacturer(manufacturer_data) if not self._is_random_mac(address) else None),
            metadata={
                "service_uuids": [str(uuid) for uuid in service_uuids],
                "security_flags": security_flags,
                "manufacturer_data": {str(k): v.hex() for k, v in manufacturer_data.items()},
            }
        )
        
        if not has_encryption:
            device.add_vulnerability("No encryption detected – data may be intercepted")
        if not requires_pairing:
            device.add_vulnerability("No pairing required – anyone can connect")
        
        # Oblicz security score
        device.calculate_security_score()
        
        return device
    
    def _detect_device_type(self, service_uuids: List[str], name: Optional[str], manufacturer: Optional[str] = None) -> DeviceType:
        """
        Detect device type from service UUIDs and name.
        
        Method 1: Service UUIDs (most reliable) – Bluetooth SIG standard UUIDs.
        Method 2: Name heuristics (keywords like glucose, insulin).
        Method 3: Manufacturer (from MAC OUI) – known medical device makers.
        
        Args:
            service_uuids: List of service UUIDs from advertising data
            name: Device name (may be None)
            manufacturer: Manufacturer name (from MAC OUI)
            
        Returns:
            DeviceType or UNKNOWN
        """
        name_lower = (name or "").lower()
        manufacturer_lower = (manufacturer or "").lower()
        
        for uuid in service_uuids:
            uuid_lower = str(uuid).lower()
            
            if "1808" in uuid_lower or uuid_lower == "00001808-0000-1000-8000-00805f9b34fb":
                return DeviceType.GLUCOSE_METER
            if "1810" in uuid_lower or uuid_lower == "00001810-0000-1000-8000-00805f9b34fb":
                return DeviceType.BLOOD_PRESSURE
            if "180d" in uuid_lower or uuid_lower == "0000180d-0000-1000-8000-00805f9b34fb":
                return DeviceType.PULSE_OXIMETER
        
        if any(word in name_lower for word in ["glucose", "gluco", "sugar", "diabetes"]):
            return DeviceType.GLUCOSE_METER
        if any(word in name_lower for word in ["insulin", "pump"]):
            return DeviceType.INSULIN_PUMP
        if any(word in name_lower for word in ["blood", "pressure", "bp", "sphygmo"]):
            return DeviceType.BLOOD_PRESSURE
        if any(word in name_lower for word in ["pulse", "oximeter", "spo2", "heart"]):
            return DeviceType.PULSE_OXIMETER
        if any(word in name_lower for word in ["fitness", "tracker", "band"]):
            return DeviceType.FITNESS_TRACKER
        if any(word in name_lower for word in ["watch", "smartwatch"]):
            return DeviceType.SMARTWATCH
        
        if manufacturer_lower:
            glucose_manufacturers = [
                "roche", "accu-chek", "freestyle", "abbott", "onetouch", "life scan",
                "bayer", "contour", "ascensia", "sanofi", "medtronic"
            ]
            if any(manuf in manufacturer_lower for manuf in glucose_manufacturers):
                return DeviceType.GLUCOSE_METER
            
            insulin_manufacturers = [
                "medtronic", "tandem", "insulet", "omnipod", "cellnovo"
            ]
            if any(manuf in manufacturer_lower for manuf in insulin_manufacturers):
                return DeviceType.INSULIN_PUMP
            
            bp_manufacturers = [
                "omron", "withings", "a&d", "microlife", "beurer", "panasonic"
            ]
            if any(manuf in manufacturer_lower for manuf in bp_manufacturers):
                return DeviceType.BLOOD_PRESSURE
            
            pulse_manufacturers = [
                "masimo", "nonin", "philips", "ge healthcare", "medtronic"
            ]
            if any(manuf in manufacturer_lower for manuf in pulse_manufacturers):
                return DeviceType.PULSE_OXIMETER
            
            fitness_manufacturers = [
                "apple", "samsung", "fitbit", "garmin", "polar", "suunto", "xiaomi"
            ]
            if any(manuf in manufacturer_lower for manuf in fitness_manufacturers):
                if any(word in name_lower for word in ["watch", "smartwatch"]):
                    return DeviceType.SMARTWATCH
                return DeviceType.FITNESS_TRACKER
        
        return DeviceType.UNKNOWN
    
    def _get_manufacturer_from_mac(self, mac_address: str) -> Optional[str]:
        """
        Get manufacturer name from MAC address (OUI).
        Uses IEEE OUI, mac-vendor-lookup, then macvendors.com API.
        OUI = first 3 bytes of MAC identifying the vendor.
        
        Args:
            mac_address: MAC address (e.g. AA:BB:CC:DD:EE:FF)
        
        Returns:
            Manufacturer name or None
        """
        is_random = False
        try:
            mac_normalized = mac_address.replace("-", ":").replace(" ", ":").replace(".", ":").upper()
            first_byte = int(mac_normalized.split(":")[0], 16)
            is_random = (first_byte & 0x02) != 0
        except Exception:
            pass
        
        try:
            from oui_lookup import get_oui_lookup
            oui_lookup = get_oui_lookup()
            manufacturer = oui_lookup.lookup(mac_address)
            if manufacturer and not mac_address.startswith("00:00:"):
                return manufacturer
        except Exception:
            pass
        
        # mac-vendor-lookup (local DB)
        if self.mac_lookup_available and self.mac_lookup:
            try:
                mac_normalized = mac_address.replace("-", ":").replace(" ", ":").upper()
                
                if not is_random:
                    vendor = self.mac_lookup.lookup(mac_normalized)
                    if vendor and vendor != "Unknown":
                        return vendor
            except Exception:
                pass
        
        if not is_random:
            try:
                import requests  # type: ignore
                import time
                
                mac_normalized = mac_address.replace("-", ":").replace(" ", ":").replace(".", ":").upper()
                url = f"https://api.macvendors.com/{mac_normalized}"
                response = requests.get(url, timeout=3)
                
                # Rate limiting
                time.sleep(1.1)
                
                if response.status_code == 200:
                    vendor = response.text.strip()
                    if vendor and vendor != "404" and "not found" not in vendor.lower():
                        return vendor
            except Exception:
                pass
        
        return None
    
    def _is_random_mac(self, mac_address: str) -> bool:
        """
        Check if MAC address is random (privacy-preserving).
        Random MACs do not represent the real manufacturer.
        
        Args:
            mac_address: Device MAC address
        
        Returns:
            True if random, False otherwise
        """
        try:
            mac_normalized = mac_address.replace("-", ":").replace(" ", ":").replace(".", ":").upper()
            first_byte = int(mac_normalized.split(":")[0], 16)
            # Bit 1 (0x02) w pierwszym bajcie oznacza losowy adres MAC
            is_random = (first_byte & 0x02) != 0
            return is_random
        except Exception:
            return False
    
    def _extract_manufacturer(self, manufacturer_data: Dict) -> Optional[str]:
        """
        Extract manufacturer name from BLE manufacturer data (Company ID).
        Fallback; main identification is via MAC OUI.
        """
        if not manufacturer_data:
            return None
        
        for company_id_str, data in manufacturer_data.items():
            try:
                company_id = int(company_id_str)
                company_ids = {
                    0: "Ericsson Technology Licensing",
                    6: "Microsoft Corporation",
                    15: "3Com",
                    76: "Apple, Inc.",
                    89: "Nordic Semiconductor ASA",
                    117: "Google Inc.",
                    152: "Samsung Electronics Co. Ltd.",
                }
                if company_id in company_ids:
                    return company_ids[company_id]
            except (ValueError, TypeError):
                continue
        return None
    
    def get_all_devices(self) -> List[Device]:
        """Return all detected devices."""
        return self.scanned_devices


async def scan_devices_async(duration: int = 10) -> List[Device]:
    """
    Async helper to scan BLE devices.
    Args:
        duration: Scan duration in seconds
    Returns:
        List of detected devices
    """
    scanner = RealBLEScanner()
    return await scanner.scan_ble_devices(duration=duration)


def scan_devices(duration: int = 10) -> List[Device]:
    """
    Synchronous wrapper to scan BLE devices.
    Args:
        duration: Scan duration in seconds
    Returns:
        List of detected devices
    """
    if not BLEAK_AVAILABLE:
        raise ImportError(
            "Biblioteka 'bleak' nie jest zainstalowana.\n"
            "Install: pip install bleak"
        )
    
    # Uruchom asynchroniczne skanowanie
    if platform.system() == "Windows":
        # Windows wymaga innego event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(scan_devices_async(duration))
        finally:
            loop.close()
    else:
        # Linux/Mac
        return asyncio.run(scan_devices_async(duration))


if __name__ == "__main__":
    # Test prawdziwego skanera
    console.print(Panel.fit(
        "[bold cyan]🔍 Test: Prawdziwy skaner BLE[/bold cyan]\n"
        "[dim]Scanning for Bluetooth devices in range...[/dim]",
        style="cyan"
    ))
    console.print()
    
    try:
        devices = scan_devices(duration=10)
        
        console.print(f"\n[bold green]✅ Found {len(devices)} devices:[/bold green]\n")
        
        for device in devices:
            console.print(f"[cyan]{device.name}[/cyan] ({device.mac_address})")
            console.print(f"  Typ: {device.device_type.value}")
            console.print(f"  Szyfrowanie: {'✅ Tak' if device.has_encryption else '❌ Nie'}")
            console.print(f"  Parowanie: {'✅ Wymagane' if device.requires_pairing else '❌ Nie wymagane'}")
            console.print(f"  Security Score: {device.security_score}/100")
            if device.vulnerabilities:
                console.print(f"  Vulnerabilities: {', '.join(device.vulnerabilities)}")
            console.print()
            
    except ImportError as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        console.print("[yellow]Install: pip install bleak[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
