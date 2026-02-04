#!/usr/bin/env python3
"""
Prawdziwy skaner USB - wykrywa urządzenia medyczne podłączone przez USB.

Ten moduł używa pyusb i innych narzędzi do wykrywania urządzeń USB
i analizy ich właściwości bezpieczeństwa.
"""

import sys
import os
import platform
from typing import List, Optional, Dict
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

# Dodaj katalog src/ do ścieżki Python
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    import usb.core
    import usb.util
    PYUSB_AVAILABLE = True
except ImportError:
    PYUSB_AVAILABLE = False

# Alternatywnie użyj pyserial dla urządzeń szeregowych
try:
    import serial
    import serial.tools.list_ports
    PYSERIAL_AVAILABLE = True
except ImportError:
    PYSERIAL_AVAILABLE = False
    serial = None

from device import Device, DeviceType, Protocol

console = Console()

# Vendor IDs urządzeń medycznych (często używane)
MEDICAL_VENDOR_IDS = {
    0x0A5C: "Broadcom (często używane w urządzeniach medycznych)",
    0x04E6: "Xerox (niektóre urządzenia medyczne)",
    0x046D: "Logitech (niektóre urządzenia medyczne)",
}

# Class codes USB dla urządzeń medycznych
MEDICAL_USB_CLASSES = {
    0x01: "Audio",  # Czasami używane w urządzeniach medycznych
    0x03: "HID (Human Interface Device)",  # Glukometry, ciśnieniomierze
    0x08: "Mass Storage",  # Urządzenia do przechowywania danych
    0xFF: "Vendor Specific",  # Własne protokoły producentów
}


class USBScanner:
    """
    Prawdziwy skaner USB używający pyusb i pyserial.
    
    Wykrywa urządzenia USB podłączone do komputera i analizuje
    ich właściwości bezpieczeństwa.
    """
    
    def __init__(self):
        """Inicjalizacja skanera USB."""
        if not PYUSB_AVAILABLE and not PYSERIAL_AVAILABLE:
            console.print("[yellow]⚠️  Biblioteki USB nie są zainstalowane.[/yellow]")
            console.print("[yellow]   Zainstaluj: pip install pyusb pyserial[/yellow]")
            console.print("[yellow]   Na Linuxie może być potrzebne: sudo apt-get install libusb-1.0-0-dev[/yellow]\n")
        self.scanned_devices: List[Device] = []
        # Typowe prędkości dla mikrokontrolerów (do automatycznego wykrywania)
        self.common_baudrates = [9600, 19200, 38400, 57600, 115200, 230400, 460800]
        
        # Vendor IDs i Product IDs znanych urządzeń wewnętrznych (klawiatury, touchpady, kamery wbudowane)
        # Te urządzenia są częścią laptopa i nie powinny być pokazywane jako zewnętrzne urządzenia USB
        self.internal_device_ids = {
            # Klawiatury wewnętrzne (HID)
            (0x046D, 0xC077): "Logitech Keyboard (internal)",
            (0x046D, 0xC07D): "Logitech Keyboard (internal)",
            # Touchpady
            (0x06CB, None): "Synaptics Touchpad",  # Synaptics - wszystkie produkty
            (0x04F3, None): "Elan Touchpad",  # Elan - wszystkie produkty
            # Kamery wbudowane
            (0x0C45, None): "Microdia Camera (internal)",  # Wiele kamer wbudowanych
            (0x174F, None): "Syntek Camera (internal)",
            (0x5986, None): "Acer Camera (internal)",
            (0x0BDA, None): "Realtek Camera (internal)",  # Realtek - wiele kamer
            # Kontrolery USB (hubs) - ZAWSZE wewnętrzne
            (0x1D6B, 0x0001): "Linux USB Hub Controller",
            (0x1D6B, 0x0002): "Linux USB Hub Controller",
            (0x1D6B, 0x0003): "Linux USB Hub Controller",
            # Kontrolery audio wewnętrzne
            (0x8086, None): "Intel Audio Controller",  # Intel - wiele urządzeń audio
            (0x10EC, None): "Realtek Audio Controller",  # Realtek - wiele urządzeń audio
            # Kontrolery Bluetooth wewnętrzne
            (0x0A5C, None): "Broadcom Bluetooth (internal)",  # Broadcom - wiele urządzeń BT
            (0x8087, None): "Intel Bluetooth Controller",  # Intel - kontrolery BT
            # Kontrolery WiFi wewnętrzne
            (0x168C, None): "Qualcomm WiFi (internal)",  # Qualcomm/Atheros WiFi
            (0x10EC, None): "Realtek WiFi (internal)",  # Realtek WiFi
        }
        
        # USB Class codes dla urządzeń wewnętrznych (które zwykle są częścią laptopa)
        self.internal_usb_classes = {
            0x09: "USB Hub",  # Huby USB są ZAWSZE wewnętrzne
            0x0E: "Video",  # Kamery wbudowane
            0x01: "Audio",  # Kontrolery audio wewnętrzne
        }
        
        # Vendor IDs które są ZAWSZE wewnętrzne (część laptopa)
        self.always_internal_vendors = {
            0x1D6B,  # Linux Foundation (kontrolery USB)
            0x8086,  # Intel (kontrolery wewnętrzne)
            0x8087,  # Intel (kontrolery USB)
        }
    
    def scan_usb_devices(self) -> List[Device]:
        """
        Skanuje urządzenia USB podłączone do komputera.
        
        WAŻNE - Jak działa skanowanie USB:
        ====================================
        Skanowanie jest wykonywane przez KONTROLERY USB w laptopie (część płyty głównej).
        Kontrolery USB skanują WSZYSTKIE urządzenia USB w systemie, w tym:
        - Urządzenia zewnętrzne (podłączone przez porty USB)
        - Urządzenia wewnętrzne (część laptopa: kamery, Bluetooth, huby USB, czytniki kart)
        
        Dlatego skaner wykrywa urządzenia nawet gdy nic nie jest podłączone zewnętrznie -
        wykrywa wewnętrzne komponenty laptopa, które są połączone przez USB wewnętrznie.
        
        Skaner automatycznie filtruje urządzenia wewnętrzne, aby pokazać tylko zewnętrzne.
        
        Returns:
            Lista wykrytych urządzeń Device (tylko zewnętrzne)
        """
        console.print("[cyan]🔍 Rozpoczynam skanowanie USB...[/cyan]")
        console.print("[dim]Skanuję urządzenia USB podłączone do komputera...[/dim]")
        console.print("[dim]💡 Fizyczne urządzenie: Kontrolery USB w laptopie (część płyty głównej)[/dim]")
        console.print("[dim]💡 WAŻNE: Z powodu topologii laptopa wykrywam WSZYSTKIE urządzenia USB w systemie:[/dim]")
        console.print("[dim]      • Urządzenia zewnętrzne (podłączone przez porty USB) ✅[/dim]")
        console.print("[dim]      • Urządzenia wewnętrzne (kamery, Bluetooth, huby USB - część laptopa) ⚠️[/dim]")
        console.print("[dim]💡 Automatycznie filtruję wewnętrzne, aby pokazać tylko zewnętrzne urządzenia[/dim]\n")
        
        devices: List[Device] = []
        
        # Skanuj urządzenia USB
        if PYUSB_AVAILABLE:
            usb_devices = self._scan_pyusb()
            devices.extend(usb_devices)
        
        # Skanuj urządzenia szeregowe (COM ports)
        if PYSERIAL_AVAILABLE:
            serial_devices = self._scan_serial()
            devices.extend(serial_devices)
        
        if not PYUSB_AVAILABLE and not PYSERIAL_AVAILABLE:
            console.print("[yellow]⚠️  Brak dostępnych bibliotek USB - nie można skanować[/yellow]\n")
        
        self.scanned_devices = devices
        console.print(f"\n[green]✅ Skanowanie USB zakończone. Znaleziono {len(devices)} urządzeń.[/green]\n")
        return devices
    
    def _is_internal_device(self, usb_dev) -> bool:
        """
        Sprawdza czy urządzenie USB jest wewnętrzne (część laptopa).
        
        Args:
            usb_dev: Obiekt urządzenia USB z pyusb
        
        Returns:
            True jeśli urządzenie jest wewnętrzne i powinno być pominięte
        """
        try:
            vendor_id = usb_dev.idVendor
            product_id = usb_dev.idProduct
            device_class = usb_dev.bDeviceClass
            
            # PRIORYTET 1: Sprawdź czy vendor jest ZAWSZE wewnętrzny
            if vendor_id in self.always_internal_vendors:
                return True
            
            # PRIORYTET 2: Sprawdź czy to hub USB (ZAWSZE wewnętrzny)
            if device_class == 0x09:  # USB Hub
                return True
            
            # PRIORYTET 3: Sprawdź czy to znane urządzenie wewnętrzne (po Vendor/Product ID)
            for (vid, pid), description in self.internal_device_ids.items():
                if vid == vendor_id:
                    if pid is None or pid == product_id:
                        return True
            
            # PRIORYTET 4: Sprawdź klasę USB (huby i kamery są zwykle wewnętrzne)
            if device_class in self.internal_usb_classes:
                return True
            
            # Sprawdź czy to urządzenie HID (klawiatura/mysz) - może być wewnętrzne
            # Ale nie filtruj wszystkich HID, bo niektóre urządzenia medyczne też są HID
            if device_class == 0x03:  # HID
                # Sprawdź czy to może być urządzenie medyczne
                try:
                    manufacturer = usb.util.get_string(usb_dev, usb_dev.iManufacturer) or ""
                    product = usb.util.get_string(usb_dev, usb_dev.iProduct) or ""
                    
                    # Jeśli ma słowa kluczowe medyczne, nie filtruj
                    medical_keywords = ["glucose", "gluco", "diabetes", "insulin", "pump",
                                       "pressure", "bp", "pulse", "oximeter", "heart",
                                       "medical", "med", "patient", "vital"]
                    text = (manufacturer + " " + product).lower()
                    if any(keyword in text for keyword in medical_keywords):
                        return False  # To może być urządzenie medyczne - nie filtruj
                    
                    # Filtruj tylko znane urządzenia wewnętrzne (touchpady, klawiatury wbudowane)
                    # Nie filtruj wszystkich HID - mogą być zewnętrzne urządzenia medyczne
                    internal_hid_keywords = ["touchpad", "trackpad", "synaptics", "elan"]
                    if any(keyword in text for keyword in internal_hid_keywords):
                        # To jest prawdopodobnie touchpad - filtruj
                        return True
                except:
                    pass
            
            # Sprawdź ścieżkę urządzenia (na Linuxie)
            if platform.system() == "Linux":
                try:
                    # Wewnętrzne urządzenia są często na określonych busach
                    # Ale nie możemy tego łatwo sprawdzić przez pyusb bezpośrednio
                    # Więc polegamy na Vendor/Product ID i klasach
                    pass
                except:
                    pass
            
            return False  # Nie wiemy na pewno - pokaż urządzenie
        
        except Exception:
            # Jeśli nie możemy sprawdzić, nie filtruj (bezpieczniejsze)
            return False
    
    def _scan_pyusb(self) -> List[Device]:
        """
        Skanuje urządzenia USB używając pyusb.
        Filtruje urządzenia wewnętrzne (klawiatury, touchpady, kamery wbudowane).
        
        Returns:
            Lista wykrytych urządzeń USB (tylko zewnętrzne)
        """
        devices: List[Device] = []
        
        try:
            # Znajdź wszystkie urządzenia USB
            usb_devices = usb.core.find(find_all=True)
            
            # Zlicz wszystkie urządzenia do wyświetlenia
            all_devices_list = list(usb_devices)
            filtered_count = 0
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Skanuję urządzenia USB...", total=None)
                
                for usb_dev in all_devices_list:
                    try:
                        # Pomiń urządzenia wewnętrzne (część laptopa)
                        if self._is_internal_device(usb_dev):
                            filtered_count += 1
                            continue
                        
                        device = self._analyze_usb_device(usb_dev)
                        if device:
                            devices.append(device)
                            progress.update(task, description=f"✓ {device.name}")
                    except Exception as e:
                        # Niektóre urządzenia mogą być niedostępne (brak uprawnień)
                        continue
                
                progress.update(task, description="✅ Skanowanie zakończone")
            
            # Wyświetl informację o przefiltrowanych urządzeniach
            if filtered_count > 0:
                console.print(f"[dim]   Pominięto {filtered_count} urządzeń wewnętrznych (klawiatury, touchpady, kamery wbudowane)[/dim]")
                console.print(f"[dim]   💡 To są komponenty laptopa połączone wewnętrznie przez USB (nie zewnętrzne urządzenia)[/dim]")
            
            # Jeśli nie znaleziono żadnych urządzeń, wyjaśnij dlaczego
            if len(devices) == 0 and filtered_count == 0:
                console.print("[dim]   💡 Nie znaleziono zewnętrznych urządzeń USB - wszystko OK![/dim]")
                console.print("[dim]   💡 Jeśli podłączysz urządzenie USB, pojawi się tutaj[/dim]")
        
        except Exception as e:
            console.print(f"[red]❌ Błąd skanowania USB: {e}[/red]")
            if platform.system() == "Linux":
                console.print("[yellow]   Może być potrzebne: sudo lub dodanie użytkownika do grupy 'plugdev'[/yellow]\n")
        
        return devices
    
    def _is_internal_serial_port(self, port) -> bool:
        """
        Sprawdza czy port szeregowy jest wewnętrzny (część laptopa).
        
        Args:
            port: Port szeregowy z pyserial
        
        Returns:
            True jeśli port jest wewnętrzny i powinien być pominięty
        """
        description = (port.description or "").lower()
        manufacturer = (port.manufacturer or "").lower()
        device_name = (port.device or "").lower()
        
        # Porty wewnętrzne (część laptopa)
        internal_keywords = [
            "bluetooth", "bluetooth serial", "modem", "internal",
            "pci", "pcie", "onboard", "embedded"
        ]
        
        # Sprawdź czy to port wewnętrzny
        text = f"{description} {manufacturer} {device_name}".lower()
        if any(keyword in text for keyword in internal_keywords):
            # Ale nie filtruj jeśli to może być urządzenie medyczne
            medical_keywords = ["glucose", "gluco", "diabetes", "insulin", "pump",
                               "pressure", "bp", "pulse", "oximeter", "heart",
                               "medical", "med", "patient", "vital"]
            if any(keyword in text for keyword in medical_keywords):
                return False  # To może być urządzenie medyczne - nie filtruj
            return True
        
        # Porty wirtualne (np. Bluetooth Serial) są zwykle wewnętrzne
        if "bluetooth" in text and "serial" in text:
            return True
        
        return False
    
    def _scan_serial(self) -> List[Device]:
        """
        Skanuje urządzenia szeregowe (COM ports) używając pyserial.
        Automatycznie wykrywa mikrokontrolery i monitoruje ich komunikaty.
        Filtruje porty wewnętrzne (część laptopa).
        
        Returns:
            Lista wykrytych urządzeń szeregowych (tylko zewnętrzne)
        """
        devices: List[Device] = []
        
        try:
            # Znajdź wszystkie porty szeregowe
            ports = serial.tools.list_ports.comports()
            
            filtered_count = 0
            
            for port in ports:
                # Pomiń porty wewnętrzne
                if self._is_internal_serial_port(port):
                    filtered_count += 1
                    continue
                
                # Sprawdź czy port może być urządzeniem medycznym lub mikrokontrolerem
                is_medical = self._is_medical_device(port)
                is_microcontroller = self._is_microcontroller(port)
                
                # Skanuj wszystkie dostępne porty szeregowe (które nie są wewnętrzne)
                if is_medical or is_microcontroller:
                    # Automatycznie wykryj prędkość i monitoruj komunikaty (tylko dla mikrokontrolerów)
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
                    
                    # Dodaj informacje o mikrokontrolerze jeśli wykryto
                    if is_microcontroller and baudrate:
                        metadata.update({
                            "baudrate": baudrate,
                            "microcontroller": True,
                            "messages": messages[:10] if messages else [],  # Ostatnie 10 komunikatów
                            "message_count": len(messages) if messages else 0
                        })
                    
                    device = Device(
                        mac_address=f"USB-{port.hwid[:17]}",
                        name=port.description or port.device,
                        device_type=DeviceType.UNKNOWN,
                        protocol=Protocol.USB,
                        has_encryption=False,  # USB zazwyczaj nie używa szyfrowania na poziomie protokołu
                        encryption_type="No encryption (USB protocol)",
                        requires_pairing=False,  # USB nie wymaga parowania
                        manufacturer=port.manufacturer,
                        metadata=metadata
                    )
                    
                    # Jeśli to mikrokontroler, dodaj informacje o komunikatach
                    if is_microcontroller:
                        if messages:
                            device.name = f"{device.name} (Mikrokontroler - {len(messages)} komunikatów)"
                            console.print(f"  [green]✓[/green] Wykryto mikrokontroler: {device.name} ({port.device})")
                            console.print(f"    [cyan]Prędkość: {baudrate} baud | Komunikaty: {len(messages)}[/cyan]")
                            if messages:
                                last_msg = messages[-1]
                                # Skróć jeśli zbyt długi
                                display_msg = last_msg[:60] + "..." if len(last_msg) > 60 else last_msg
                                if "[TEST:" in last_msg:
                                    console.print(f"    [yellow]→ {display_msg}[/yellow]")
                                else:
                                    console.print(f"    [green]→ {display_msg}[/green]")
                        else:
                            device.name = f"{device.name} (Mikrokontroler - brak komunikatów)"
                            console.print(f"  [green]✓[/green] Wykryto mikrokontroler: {device.name} ({port.device})")
                            console.print(f"    [cyan]Prędkość: {baudrate} baud | Status: Brak komunikatów[/cyan]")
                            console.print(f"    [dim]💡 Mikrokontroler może wymagać komendy startowej[/dim]")
                    else:
                        console.print(f"  [green]✓[/green] Wykryto: {device.name} ({port.device})")
                    
                    # USB zazwyczaj nie ma szyfrowania - to jest podatność dla urządzeń medycznych
                    if device.device_type != DeviceType.UNKNOWN:
                        device.add_vulnerability("USB bez szyfrowania - dane mogą być przechwycone")
                    
                    device.calculate_security_score()
                    devices.append(device)
            
            # Wyświetl informację o przefiltrowanych portach
            if filtered_count > 0:
                console.print(f"[dim]   Pominięto {filtered_count} portów wewnętrznych[/dim]")
        
        except Exception as e:
            console.print(f"[yellow]⚠️  Błąd skanowania portów szeregowych: {e}[/yellow]")
        
        return devices
    
    def _is_microcontroller(self, port) -> bool:
        """
        Sprawdza czy port może być mikrokontrolerem.
        
        Args:
            port: Port szeregowy z pyserial
        
        Returns:
            True jeśli może być mikrokontrolerem
        """
        description = (port.description or "").lower()
        manufacturer = (port.manufacturer or "").lower()
        device_name = (port.device or "").lower()
        
        # Typowe nazwy mikrokontrolerów
        microcontroller_keywords = [
            "arduino", "esp32", "esp8266", "raspberry", "pi pico",
            "stm32", "atmega", "attiny", "pic", "msp430",
            "teensy", "adafruit", "feather", "trinket",
            "usb serial", "ch340", "cp210", "ftdi", "pl2303"
        ]
        
        # Sprawdź czy port jest dostępny (nie zajęty)
        try:
            test_serial = serial.Serial(port.device, timeout=0.1)
            test_serial.close()
        except:
            return False
        
        return any(keyword in description or keyword in manufacturer or keyword in device_name
                  for keyword in microcontroller_keywords)
    
    def _auto_detect_and_monitor(self, port_name: str, timeout: float = 3.0) -> tuple:
        """
        Automatycznie wykrywa prędkość (baudrate) i monitoruje komunikaty z mikrokontrolera.
        Dodatkowo próbuje wysłać komendy testowe aby sprawdzić interakcję.
        
        Args:
            port_name: Nazwa portu (np. /dev/ttyUSB0, COM3)
            timeout: Czas monitorowania dla każdej prędkości (sekundy)
        
        Returns:
            Tuple (baudrate, lista_komunikatów)
        """
        if not PYSERIAL_AVAILABLE:
            return None, []
        
        messages = []
        detected_baudrate = None
        
        # Próbuj różne prędkości
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
                
                # Poczekaj chwilę na inicjalizację
                import time
                time.sleep(0.5)
                
                # Próbuj czytać komunikaty przez krótki czas
                start_time = time.time()
                temp_messages = []
                
                # Najpierw czytaj istniejące komunikaty
                while time.time() - start_time < timeout:
                    if ser.in_waiting > 0:
                        try:
                            line = ser.readline().decode('utf-8', errors='ignore').strip()
                            if line:
                                temp_messages.append(line)
                        except:
                            pass
                    time.sleep(0.1)
                
                # Jeśli nie ma komunikatów, spróbuj wysłać komendy testowe
                if not temp_messages:
                    test_commands = ["AT\r\n", "HELLO\r\n", "?\r\n", "\r\n"]
                    for cmd in test_commands:
                        try:
                            ser.write(cmd.encode('utf-8'))
                            ser.flush()
                            time.sleep(0.3)
                            
                            # Czytaj odpowiedź
                            if ser.in_waiting > 0:
                                line = ser.readline().decode('utf-8', errors='ignore').strip()
                                if line:
                                    temp_messages.append(f"[TEST: {cmd.strip()}] -> {line}")
                        except:
                            pass
                
                ser.close()
                
                # Jeśli znaleziono komunikaty, użyj tej prędkości
                if temp_messages:
                    detected_baudrate = baudrate
                    messages = temp_messages
                    break
                    
            except (serial.SerialException, OSError, ValueError):
                # Port może być zajęty lub nieprawidłowa prędkość
                continue
            except Exception:
                continue
        
        # Jeśli nie wykryto prędkości, użyj domyślnej (9600)
        if not detected_baudrate:
            detected_baudrate = 9600
        
        return detected_baudrate, messages
    
    def _analyze_usb_device(self, usb_dev) -> Optional[Device]:
        """
        Analizuje urządzenie USB.
        
        Args:
            usb_dev: Obiekt urządzenia USB z pyusb
        
        Returns:
            Obiekt Device lub None
        """
        try:
            # Pobierz informacje o urządzeniu
            vendor_id = usb_dev.idVendor
            product_id = usb_dev.idProduct
            
            # Spróbuj pobrać stringi (nazwa, producent)
            try:
                manufacturer = usb.util.get_string(usb_dev, usb_dev.iManufacturer) or "Unknown"
                product = usb.util.get_string(usb_dev, usb_dev.iProduct) or "Unknown"
            except Exception:
                manufacturer = f"Vendor-{vendor_id:04X}"
                product = f"Product-{product_id:04X}"
            
            # Określ typ urządzenia
            device_type = self._detect_device_type(manufacturer, product, vendor_id)
            
            # Sprawdź bezpieczeństwo
            # USB zazwyczaj nie używa szyfrowania na poziomie protokołu
            # (szyfrowanie musi być implementowane na poziomie aplikacji)
            has_encryption = False
            requires_pairing = False
            encryption_type = "No encryption (USB protocol)"
            
            # Dla urządzeń medycznych może być szyfrowanie na poziomie aplikacji
            if device_type != DeviceType.UNKNOWN:
                encryption_type = "Application-level encryption (if implemented)"
            
            # Utwórz obiekt Device
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
            
            # Dodaj podatności
            if not has_encryption and device_type != DeviceType.UNKNOWN:
                device.add_vulnerability("USB bez szyfrowania - dane mogą być przechwycone")
            
            device.calculate_security_score()
            return device
        
        except Exception as e:
            # Niektóre urządzenia mogą być niedostępne
            return None
    
    def _detect_device_type(self, manufacturer: str, product: str, vendor_id: int) -> DeviceType:
        """
        Wykrywa typ urządzenia na podstawie informacji USB.
        
        Args:
            manufacturer: Nazwa producenta
            product: Nazwa produktu
            vendor_id: Vendor ID USB
        
        Returns:
            DeviceType urządzenia
        """
        manufacturer_lower = manufacturer.lower()
        product_lower = product.lower()
        
        # Sprawdź nazwy
        if any(word in product_lower for word in ["glucose", "gluco", "diabetes"]):
            return DeviceType.GLUCOSE_METER
        if any(word in product_lower for word in ["insulin", "pump"]):
            return DeviceType.INSULIN_PUMP
        if any(word in product_lower for word in ["pressure", "bp", "sphygmo"]):
            return DeviceType.BLOOD_PRESSURE
        if any(word in product_lower for word in ["pulse", "oximeter", "heart"]):
            return DeviceType.PULSE_OXIMETER
        
        # Sprawdź producentów medycznych
        medical_manufacturers = ["accu-chek", "freestyle", "onetouch", "omron", "withings"]
        if any(med in manufacturer_lower for med in medical_manufacturers):
            return DeviceType.UNKNOWN  # Urządzenie medyczne, ale nieznany typ
        
        return DeviceType.UNKNOWN
    
    def _is_medical_device(self, port) -> bool:
        """
        Sprawdza czy port szeregowy może być urządzeniem medycznym.
        
        Args:
            port: Port szeregowy z pyserial
        
        Returns:
            True jeśli może być urządzeniem medycznym
        """
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
        """Zwraca wszystkie wykryte urządzenia."""
        return self.scanned_devices


if __name__ == "__main__":
    # Test skanera USB
    console.print(Panel.fit(
        "[bold cyan]🔍 Test: Skaner USB[/bold cyan]\n"
        "[dim]Skanuję urządzenia USB podłączone do komputera...[/dim]",
        style="cyan"
    ))
    console.print()
    
    scanner = USBScanner()
    devices = scanner.scan_usb_devices()
    
    console.print(f"\n[bold green]✅ Znaleziono {len(devices)} urządzeń:[/bold green]\n")
    
    for device in devices:
        console.print(f"[cyan]{device.name}[/cyan] ({device.mac_address})")
        console.print(f"  Producent: {device.manufacturer or 'Unknown'}")
        console.print(f"  Typ: {device.device_type.value}")
        console.print(f"  Szyfrowanie: {'✅ Tak' if device.has_encryption else '❌ Nie'}")
        console.print(f"  Security Score: {device.security_score}/100")
        if device.vulnerabilities:
            console.print(f"  Podatności: {', '.join(device.vulnerabilities)}")
        console.print()
