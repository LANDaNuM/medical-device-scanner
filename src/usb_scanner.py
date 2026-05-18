#!/usr/bin/env python3
"""Real USB scanner – detects medical devices connected via USB. Uses pyusb and related tools."""

import sys
import os
import platform
from typing import List, Optional, Dict
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

# Add src/ to path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    import usb.core
    import usb.util
    PYUSB_AVAILABLE = True
except ImportError:
    PYUSB_AVAILABLE = False

# Or use pyserial for serial devices
try:
    import serial
    import serial.tools.list_ports
    PYSERIAL_AVAILABLE = True
except ImportError:
    PYSERIAL_AVAILABLE = False
    serial = None

from device import Device, DeviceType, Protocol

console = Console()

# Medical device vendor IDs
MEDICAL_VENDOR_IDS = {
    0x0A5C: "Broadcom (often in medical devices)",
    0x04E6: "Xerox (some medical devices)",
    0x046D: "Logitech (some medical devices)",
}

# USB class codes for medical devices
MEDICAL_USB_CLASSES = {
    0x01: "Audio",
    0x03: "HID (Human Interface Device)",
    0x08: "Mass Storage",
    0xFF: "Vendor Specific",
}


class USBScanner:
    """USB scanner using pyusb and pyserial. Detects and analyzes USB devices."""
    
    def __init__(self):
        """Init USB scanner."""
        if not PYUSB_AVAILABLE and not PYSERIAL_AVAILABLE:
            console.print("[yellow]⚠️  USB libraries not installed.[/yellow]")
            console.print("[yellow]   Install: pip install pyusb pyserial[/yellow]")
            console.print("[yellow]   On Linux you may need: sudo apt-get install libusb-1.0-0-dev[/yellow]\n")
        self.scanned_devices: List[Device] = []
        self.common_baudrates = [9600, 19200, 38400, 57600, 115200, 230400, 460800]
        self.internal_device_ids = {
            (0x046D, 0xC077): "Logitech Keyboard (internal)",
            (0x046D, 0xC07D): "Logitech Keyboard (internal)",
            # Touchpads
            (0x06CB, None): "Synaptics Touchpad",  # Synaptics – all products
            (0x04F3, None): "Elan Touchpad",  # Elan – all products
            # Built-in cameras
            (0x0C45, None): "Microdia Camera (internal)",  # Many built-in cameras
            (0x174F, None): "Syntek Camera (internal)",
            (0x5986, None): "Acer Camera (internal)",
            (0x0BDA, None): "Realtek Camera (internal)",  # Realtek – many cameras
            # USB controllers (hubs) – always internal
            (0x1D6B, 0x0001): "Linux USB Hub Controller",
            (0x1D6B, 0x0002): "Linux USB Hub Controller",
            (0x1D6B, 0x0003): "Linux USB Hub Controller",
            # Internal audio controllers
            (0x8086, None): "Intel Audio Controller",
            (0x10EC, None): "Realtek Audio Controller",
            # Internal Bluetooth
            (0x0A5C, None): "Broadcom Bluetooth (internal)",
            (0x8087, None): "Intel Bluetooth Controller",
            # Internal WiFi
            (0x168C, None): "Qualcomm WiFi (internal)",
            (0x10EC, None): "Realtek WiFi (internal)",
        }
        
        # USB class codes for internal devices (usually part of laptop)
        self.internal_usb_classes = {
            0x09: "USB Hub",
            0x0E: "Video",
            0x01: "Audio",
        }
        self.always_internal_vendors = {
            0x1D6B,  # Linux Foundation
            0x8086,  # Intel
            0x8087,  # Intel USB
        }
    
    def scan_usb_devices(self) -> List[Device]:
        """Scan USB devices. USB controllers see all devices (external + internal); we filter to external only. Returns list of Device."""
        console.print("[cyan]🔍 Starting USB scan...[/cyan]")
        console.print("[dim]Scanning USB devices connected to this computer...[/dim]")
        console.print("[dim]💡 Physical device: laptop USB controllers (on motherboard)[/dim]")
        console.print("[dim]💡 Due to laptop topology we see ALL USB devices: external (ports) and internal (camera, BT, hubs)[/dim]")
        console.print("[dim]💡 Internal devices are filtered out so only external ones are shown[/dim]\n")
        
        devices: List[Device] = []
        if PYUSB_AVAILABLE:
            usb_devices = self._scan_pyusb()
            devices.extend(usb_devices)
        if PYSERIAL_AVAILABLE:
            serial_devices = self._scan_serial()
            devices.extend(serial_devices)
        if not PYUSB_AVAILABLE and not PYSERIAL_AVAILABLE:
            console.print("[yellow]⚠️  No USB libraries available – cannot scan[/yellow]\n")
        self.scanned_devices = devices
        console.print(f"\n[green]✅ USB scan complete. Found {len(devices)} devices.[/green]\n")
        return devices
    
    def _is_internal_device(self, usb_dev) -> bool:
        """Return True if USB device is internal (part of laptop) and should be skipped."""
        try:
            vendor_id = usb_dev.idVendor
            product_id = usb_dev.idProduct
            device_class = usb_dev.bDeviceClass
            if vendor_id in self.always_internal_vendors:
                return True
            if device_class == 0x09:  # USB Hub
                return True
            for (vid, pid), description in self.internal_device_ids.items():
                if vid == vendor_id:
                    if pid is None or pid == product_id:
                        return True
            if device_class in self.internal_usb_classes:
                return True
            if device_class == 0x03:  # HID
                try:
                    manufacturer = usb.util.get_string(usb_dev, usb_dev.iManufacturer) or ""
                    product = usb.util.get_string(usb_dev, usb_dev.iProduct) or ""
                    medical_keywords = ["glucose", "gluco", "diabetes", "insulin", "pump",
                                       "pressure", "bp", "pulse", "oximeter", "heart",
                                       "medical", "med", "patient", "vital"]
                    text = (manufacturer + " " + product).lower()
                    if any(keyword in text for keyword in medical_keywords):
                        return False
                    internal_hid_keywords = ["touchpad", "trackpad", "synaptics", "elan"]
                    if any(keyword in text for keyword in internal_hid_keywords):
                        return True
                except:
                    pass
            if platform.system() == "Linux":
                try:
                    pass
                except:
                    pass
            return False
        except Exception:
            return False
    
    def _scan_pyusb(self) -> List[Device]:
        """Scan USB with pyusb. Filter internal devices (keyboards, touchpads, built-in cameras). Returns list of Device."""
        devices: List[Device] = []
        try:
            usb_devices = usb.core.find(find_all=True)
            all_devices_list = list(usb_devices)
            filtered_count = 0
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Scanning USB devices...", total=None)
                for usb_dev in all_devices_list:
                    try:
                        if self._is_internal_device(usb_dev):
                            filtered_count += 1
                            continue
                        device = self._analyze_usb_device(usb_dev)
                        if device:
                            devices.append(device)
                            progress.update(task, description=f"✓ {device.name}")
                    except Exception as e:
                        continue
                progress.update(task, description="✅ Scan complete")
            if filtered_count > 0:
                console.print(f"[dim]   Skipped {filtered_count} internal devices (keyboards, touchpads, built-in cameras)[/dim]")
                console.print(f"[dim]   💡 These are laptop components connected internally via USB[/dim]")
            if len(devices) == 0 and filtered_count == 0:
                console.print("[dim]   💡 No external USB devices found – that’s OK[/dim]")
                console.print("[dim]   💡 Plug in a USB device and it will appear here[/dim]")
        except Exception as e:
            console.print(f"[red]❌ USB scan error: {e}[/red]")
            if platform.system() == "Linux":
                console.print("[yellow]   You may need: sudo or add user to group 'plugdev'[/yellow]\n")
        return devices
    
    def _is_internal_serial_port(self, port) -> bool:
        """Return True if serial port is internal (part of laptop) and should be skipped."""
        description = (port.description or "").lower()
        manufacturer = (port.manufacturer or "").lower()
        device_name = (port.device or "").lower()
        internal_keywords = [
            "bluetooth", "bluetooth serial", "modem", "internal",
            "pci", "pcie", "onboard", "embedded"
        ]
        text = f"{description} {manufacturer} {device_name}".lower()
        if any(keyword in text for keyword in internal_keywords):
            medical_keywords = ["glucose", "gluco", "diabetes", "insulin", "pump",
                               "pressure", "bp", "pulse", "oximeter", "heart",
                               "medical", "med", "patient", "vital"]
            if any(keyword in text for keyword in medical_keywords):
                return False
            return True
        if "bluetooth" in text and "serial" in text:
            return True
        return False
    
    def _scan_serial(self) -> List[Device]:
        """Scan serial (COM) ports with pyserial. Detect microcontrollers; filter internal ports. Returns list of Device."""
        devices: List[Device] = []
        try:
            ports = serial.tools.list_ports.comports()
            filtered_count = 0
            for port in ports:
                if self._is_internal_serial_port(port):
                    filtered_count += 1
                    continue
                
                is_medical = self._is_medical_device(port)
                is_microcontroller = self._is_microcontroller(port)
                
                if is_medical or is_microcontroller:
                    if is_microcontroller:
                        baudrate, messages = self._auto_detect_and_monitor(port.device)
                    else:
                        baudrate = None
                        messages = []
                    
                    metadata = {
                        "port": port.device,
                        "vid": port.vid,
                        "pid": port.pid,
                        "serial_number": port.serial_number,
                        "hwid": port.hwid
                    }
                    
                    if is_microcontroller and baudrate:
                        metadata.update({
                            "baudrate": baudrate,
                            "microcontroller": True,
                            "messages": messages[:10] if messages else [],
                            "message_count": len(messages) if messages else 0
                        })
                    
                    device = Device(
                        mac_address=f"USB-{port.hwid[:17]}",
                        name=port.description or port.device,
                        device_type=DeviceType.UNKNOWN,
                        protocol=Protocol.USB,
                        has_encryption=False,
                        encryption_type="No encryption (USB protocol)",
                        requires_pairing=False,
                        manufacturer=port.manufacturer,
                        metadata=metadata
                    )
                    
                    if is_microcontroller:
                        if messages:
                            device.name = f"{device.name} (Microcontroller – {len(messages)} messages)"
                            console.print(f"  [green]✓[/green] Detected microcontroller: {device.name} ({port.device})")
                            console.print(f"    [cyan]Baud: {baudrate} | Messages: {len(messages)}[/cyan]")
                            if messages:
                                last_msg = messages[-1]
                                display_msg = last_msg[:60] + "..." if len(last_msg) > 60 else last_msg
                                if "[TEST:" in last_msg:
                                    console.print(f"    [yellow]→ {display_msg}[/yellow]")
                                else:
                                    console.print(f"    [green]→ {display_msg}[/green]")
                        else:
                            device.name = f"{device.name} (Microcontroller – no messages)"
                            console.print(f"  [green]✓[/green] Detected microcontroller: {device.name} ({port.device})")
                            console.print(f"    [cyan]Baud: {baudrate} | Status: No messages[/cyan]")
                            console.print(f"    [dim]💡 Microcontroller may need a start command[/dim]")
                    else:
                        console.print(f"  [green]✓[/green] Detected: {device.name} ({port.device})")
                    
                    if device.device_type != DeviceType.UNKNOWN:
                        device.add_vulnerability("USB unencrypted – data may be intercepted")
                    
                    device.calculate_security_score()
                    devices.append(device)
            
            if filtered_count > 0:
                console.print(f"[dim]   Skipped {filtered_count} internal ports[/dim]")
        
        except Exception as e:
            console.print(f"[yellow]⚠️  Serial port scan error: {e}[/yellow]")
        
        return devices
    
    def _is_microcontroller(self, port) -> bool:
        """Return True if port is likely a microcontroller."""
        description = (port.description or "").lower()
        manufacturer = (port.manufacturer or "").lower()
        device_name = (port.device or "").lower()
        microcontroller_keywords = [
            "arduino", "esp32", "esp8266", "raspberry", "pi pico",
            "stm32", "atmega", "attiny", "pic", "msp430",
            "teensy", "adafruit", "feather", "trinket",
            "usb serial", "ch340", "cp210", "ftdi", "pl2303"
        ]
        try:
            test_serial = serial.Serial(port.device, timeout=0.1)
            test_serial.close()
        except:
            return False
        
        return any(keyword in description or keyword in manufacturer or keyword in device_name
                  for keyword in microcontroller_keywords)
    
    def _auto_detect_and_monitor(self, port_name: str, timeout: float = 3.0) -> tuple:
        """Auto-detect baudrate and capture messages from serial port. Returns (baudrate, list of messages)."""
        if not PYSERIAL_AVAILABLE:
            return None, []
        
        messages = []
        detected_baudrate = None
        for baudrate in self.common_baudrates:
            try:
                ser = serial.Serial(
                    port=port_name,
                    baudrate=baudrate,
                    timeout=0.5,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE
                )
                import time
                time.sleep(0.5)
                start_time = time.time()
                temp_messages = []
                while time.time() - start_time < timeout:
                    if ser.in_waiting > 0:
                        try:
                            line = ser.readline().decode('utf-8', errors='ignore').strip()
                            if line:
                                temp_messages.append(line)
                        except:
                            pass
                    time.sleep(0.1)
                if not temp_messages:
                    test_commands = ["AT\r\n", "HELLO\r\n", "?\r\n", "\r\n"]
                    for cmd in test_commands:
                        try:
                            ser.write(cmd.encode('utf-8'))
                            ser.flush()
                            time.sleep(0.3)
                            if ser.in_waiting > 0:
                                line = ser.readline().decode('utf-8', errors='ignore').strip()
                                if line:
                                    temp_messages.append(f"[TEST: {cmd.strip()}] -> {line}")
                        except:
                            pass
                
                ser.close()
                if temp_messages:
                    detected_baudrate = baudrate
                    messages = temp_messages
                    break
            except (serial.SerialException, OSError, ValueError):
                continue
            except Exception:
                continue
        if not detected_baudrate:
            detected_baudrate = 9600
        
        return detected_baudrate, messages
    
    def _analyze_usb_device(self, usb_dev) -> Optional[Device]:
        """Analyze USB device and return a Device or None."""
        try:
            vendor_id = usb_dev.idVendor
            product_id = usb_dev.idProduct
            try:
                manufacturer = usb.util.get_string(usb_dev, usb_dev.iManufacturer) or "Unknown"
                product = usb.util.get_string(usb_dev, usb_dev.iProduct) or "Unknown"
            except Exception:
                manufacturer = f"Vendor-{vendor_id:04X}"
                product = f"Product-{product_id:04X}"
            device_type = self._detect_device_type(manufacturer, product, vendor_id)
            has_encryption = False
            requires_pairing = False
            encryption_type = "No encryption (USB protocol)"
            if device_type != DeviceType.UNKNOWN:
                encryption_type = "Application-level encryption (if implemented)"
            # Create Device
            device = Device(
                mac_address=f"USB-{vendor_id:04X}-{product_id:04X}",
                name=product,
                device_type=device_type,
                protocol=Protocol.USB,
                has_encryption=has_encryption,
                encryption_type=encryption_type,
                requires_pairing=requires_pairing,
                manufacturer=manufacturer,
                metadata={
                    "vendor_id": f"0x{vendor_id:04X}",
                    "product_id": f"0x{product_id:04X}",
                    "usb_class": usb_dev.bDeviceClass,
                    "usb_subclass": usb_dev.bDeviceSubClass
                }
            )
            
            if not has_encryption and device_type != DeviceType.UNKNOWN:
                device.add_vulnerability("USB unencrypted – data may be intercepted")
            device.calculate_security_score()
            return device
        except Exception as e:
            return None
    
    def _detect_device_type(self, manufacturer: str, product: str, vendor_id: int) -> DeviceType:
        """Detect device type from USB manufacturer/product."""
        manufacturer_lower = manufacturer.lower()
        product_lower = product.lower()
        if any(word in product_lower for word in ["glucose", "gluco", "diabetes"]):
            return DeviceType.GLUCOSE_METER
        if any(word in product_lower for word in ["insulin", "pump"]):
            return DeviceType.INSULIN_PUMP
        if any(word in product_lower for word in ["pressure", "bp", "sphygmo"]):
            return DeviceType.BLOOD_PRESSURE
        if any(word in product_lower for word in ["pulse", "oximeter", "heart"]):
            return DeviceType.PULSE_OXIMETER
        medical_manufacturers = ["accu-chek", "freestyle", "onetouch", "omron", "withings"]
        if any(med in manufacturer_lower for med in medical_manufacturers):
            return DeviceType.UNKNOWN
        return DeviceType.UNKNOWN
    
    def _is_medical_device(self, port) -> bool:
        """Return True if serial port may be a medical device."""
        description = (port.description or "").lower()
        manufacturer = (port.manufacturer or "").lower()
        
        medical_keywords = [
            "glucose", "gluco", "diabetes", "insulin", "pump",
            "pressure", "bp", "pulse", "oximeter", "heart",
            "medical", "med", "patient", "vital"
        ]
        
        return any(keyword in description or keyword in manufacturer 
                  for keyword in medical_keywords)
    
    def get_all_devices(self) -> List[Device]:
        """Return all detected devices."""
        return self.scanned_devices


if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold cyan]🔍 Test: USB Scanner[/bold cyan]\n"
        "[dim]Scanning USB devices connected to this computer...[/dim]",
        style="cyan"
    ))
    console.print()
    scanner = USBScanner()
    devices = scanner.scan_usb_devices()
    console.print(f"\n[bold green]✅ Found {len(devices)} devices:[/bold green]\n")
    for device in devices:
        console.print(f"[cyan]{device.name}[/cyan] ({device.mac_address})")
        console.print(f"  Manufacturer: {device.manufacturer or 'Unknown'}")
        console.print(f"  Type: {device.device_type.value}")
        console.print(f"  Encryption: {'✅ Yes' if device.has_encryption else '❌ No'}")
        console.print(f"  Security Score: {device.security_score}/100")
        if device.vulnerabilities:
            console.print(f"  Vulnerabilities: {', '.join(device.vulnerabilities)}")
        console.print()
