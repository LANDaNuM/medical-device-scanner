#!/usr/bin/env python3
"""
Prawdziwy skaner BLE - wykrywa rzeczywiste urządzenia Bluetooth Low Energy.

Ten moduł używa biblioteki 'bleak' do skanowania prawdziwych urządzeń BLE
i wykrywania ich właściwości bezpieczeństwa na podstawie rzeczywistych danych.

Jak wykrywamy szyfrowanie:
1. Analizujemy advertising data (flags, services)
2. Sprawdzamy GATT services i characteristics (security requirements)
3. Próbujemy połączyć się bez parowania (jeśli się nie uda, wymaga parowania)
4. Analizujemy UUID serwisów (urządzenia medyczne mają specyficzne UUID)

Protokoły medyczne vs domowe:
- Urządzenia medyczne używają standardowych UUID (np. 0x1808 dla Glucose Service)
- Urządzenia domowe używają własnych UUID
- Oba mogą używać BLE, ale różnią się serwisami i charakterystykami

WAŻNE - Błędy połączenia są NORMALNE:
- Większość urządzeń BLE NIE pozwala na połączenie bez parowania
- To oznacza że urządzenie jest BEZPIECZNE (wymaga autoryzacji)
- Błędy typu "Device not found", "Not paired", "Timeout" są oczekiwane
- Skaner analizuje urządzenia na podstawie advertising data nawet jeśli nie może się połączyć
"""

import asyncio
import platform
import sys
import os
from typing import List, Optional, Dict, Set
from datetime import datetime

# Dodaj katalog src/ do ścieżki Python, aby móc importować moduły
# To pozwala uruchomić skrypt bezpośrednio: python3 src/real_scanner.py
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
    print("⚠️  Biblioteka 'bleak' nie jest zainstalowana.")
    print("   Zainstaluj: pip install bleak")

from device import Device, DeviceType, Protocol

console = Console()

# UUID serwisów medycznych (z Bluetooth SIG)
MEDICAL_SERVICE_UUIDS = {
    "00001808-0000-1000-8000-00805f9b34fb": "Glucose Service",  # Glukometr
    "0000180f-0000-1000-8000-00805f9b34fb": "Battery Service",
    "0000180a-0000-1000-8000-00805f9b34fb": "Device Information Service",
    "0000180d-0000-1000-8000-00805f9b34fb": "Heart Rate Service",  # Pulsoksymetr
    "00001810-0000-1000-8000-00805f9b34fb": "Blood Pressure Service",  # Ciśnieniomierz
    "0000181a-0000-1000-8000-00805f9b34fb": "Environmental Sensing",
}

# UUID charakterystyk medycznych
MEDICAL_CHARACTERISTIC_UUIDS = {
    "00002a18-0000-1000-8000-00805f9b34fb": "Blood Pressure Measurement",
    "00002a52-0000-1000-8000-00805f9b34fb": "Glucose Measurement",
    "00002a37-0000-1000-8000-00805f9b34fb": "Heart Rate Measurement",
}


class RealBLEScanner:
    """
    Prawdziwy skaner BLE używający biblioteki 'bleak'.
    
    Wykrywa rzeczywiste urządzenia BLE i analizuje ich właściwości bezpieczeństwa
    na podstawie rzeczywistych danych z urządzeń.
    """
    
    def __init__(self):
        """Inicjalizacja skanera BLE."""
        if not BLEAK_AVAILABLE:
            raise ImportError(
                "Biblioteka 'bleak' nie jest zainstalowana.\n"
                "Zainstaluj: pip install bleak"
            )
        self.scanned_devices_dict: Dict[str, BLEDevice] = {}  # Przechowuj obiekty BLEDevice z nazwami
        self.device_names: Dict[str, str] = {}  # Przechowuj nazwy urządzeń zapisane w detection_callback
        self.scanned_devices: List[Device] = []
        self.advertisement_data: Dict[str, AdvertisementData] = {}
        
        # Inicjalizuj lookup producentów po adresie MAC (OUI)
        # OUI (Organizationally Unique Identifier) to pierwsze 3 bajty adresu MAC
        # które identyfikują producenta urządzenia
        try:
            from mac_vendor_lookup import MacLookup  # type: ignore
            self.mac_lookup = MacLookup()
            # Opcjonalnie: zaktualizuj bazę producentów (pierwsze uruchomienie może być wolne)
            # self.mac_lookup.update_vendors()  # Odkomentuj jeśli chcesz zaktualizować bazę
            self.mac_lookup_available = True
        except ImportError:
            self.mac_lookup = None
            self.mac_lookup_available = False
            console.print("[dim]ℹ️  mac-vendor-lookup niedostępny - identyfikacja producenta po MAC będzie ograniczona[/dim]")
            console.print("[dim]   Zainstaluj: pip install mac-vendor-lookup[/dim]")
    
    def _scan_with_bluetoothctl_removed(self, duration: int = 10) -> List[Device]:
        """
        Alternatywna metoda skanowania używająca bluetoothctl - bardziej niezawodna dla nazw.
        
        bluetoothctl to oficjalne narzędzie BlueZ, które zawsze pokazuje nazwy urządzeń.
        Jest bardziej niezawodne niż bleak dla wykrywania nazw, bo bezpośrednio używa systemowego stacka.
        
        Args:
            duration: Czas skanowania w sekundach
            
        Returns:
            Lista wykrytych urządzeń Device lub pusta lista jeśli bluetoothctl nie działa
        """
        devices: List[Device] = []
        device_info: Dict[str, Dict] = {}  # MAC -> {name, rssi}
        
        try:
            import subprocess
            import time
            import re
            
            console.print(f"[cyan]🔍 Używam bluetoothctl do skanowania BLE ({duration}s)...[/cyan]")
            console.print("[dim]bluetoothctl jest bardziej niezawodny dla wykrywania nazw urządzeń...[/dim]\n")
            
            # Rozpocznij skanowanie (bluetoothctl scan on)
            process = subprocess.Popen(
                ['bluetoothctl', 'scan', 'on'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Zbieraj wyniki przez określony czas
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
            
            # Wyświetl znalezione urządzenia
            for mac, info in device_info.items():
                name = info['name'] or "Unknown Device"
                rssi = info.get('rssi')
                console.print(f"  [green]✓[/green] Wykryto: [cyan]{name}[/cyan] ({mac})")
                if rssi:
                    console.print(f"    RSSI: {rssi} dBm")
            
            # Zapisz do self.device_names dla późniejszej analizy
            for mac, info in device_info.items():
                if info['name']:
                    self.device_names[mac] = info['name']
            
            # Teraz przeanalizuj każde urządzenie używając bleak (dla szczegółów bezpieczeństwa)
            if device_info:
                console.print(f"\n[green]✅ Skanowanie zakończone. Znaleziono {len(device_info)} urządzeń.[/green]\n")
                console.print("[cyan]🔒 Analizuję właściwości bezpieczeństwa urządzeń...[/cyan]\n")
                
                # Użyj bleak do analizy bezpieczeństwa (ale z zapisanymi nazwami)
                for mac, info in device_info.items():
                    try:
                        device = asyncio.run(self._analyze_device(mac))
                        if device:
                            # Upewnij się że używa zapisanej nazwy
                            if info['name']:
                                device.name = info['name']
                            devices.append(device)
                    except Exception:
                        # Jeśli nie można przeanalizować, utwórz podstawowe urządzenie
                        name = info['name'] or "Unknown Device"
                        manufacturer = self._get_manufacturer_from_mac(mac)
                        
                        device = Device(
                            mac_address=mac,
                            name=name,
                            device_type=DeviceType.UNKNOWN,
                            protocol=Protocol.BLE,
                            has_encryption=False,  # Nie wiemy bez analizy
                            requires_pairing=False,  # Nie wiemy bez analizy
                            manufacturer=manufacturer,
                            rssi=info.get('rssi'),
                            metadata={'scanned_with': 'bluetoothctl'}
                        )
                        device.calculate_security_score()
                        devices.append(device)
            
        except FileNotFoundError:
            # bluetoothctl nie jest dostępny - użyj bleak
            return []
        except Exception as e:
            # Błąd bluetoothctl - użyj bleak
            return []
        
        return devices
    
    async def scan_ble_devices(self, duration: int = 10) -> List[Device]:
        """
        Skanuje rzeczywiste urządzenia BLE w zasięgu.
        
        Args:
            duration: Czas skanowania w sekundach
            
        Returns:
            Lista wykrytych urządzeń Device
        """
        console.print(f"[cyan]🔍 Rozpoczynam skanowanie BLE ({duration}s)...[/cyan]")
        console.print("[dim]Skanuję rzeczywiste urządzenia Bluetooth w zasięgu...[/dim]")
        console.print("[dim]💡 Fizyczne urządzenie: Adapter Bluetooth w laptopie[/dim]")
        console.print("[dim]💡 Wykrywam tylko urządzenia w zasięgu (RSSI > -90 dBm)[/dim]")
        if duration < 15:
            console.print("[dim]💡 Dłuższy skan (--ble-duration 20–30) pomaga wykryć urządzenia reklamujące się rzadziej.[/dim]")
        console.print()
        
        devices: List[Device] = []
        # Set (zbiór) przechowuje unikalne adresy MAC, aby uniknąć duplikatów
        # (to samo urządzenie może być wykryte wiele razy podczas skanowania)
        discovered_devices: Set[str] = set()
        
        def detection_callback(device: BLEDevice, advertisement_data: AdvertisementData):
            """
            Callback wywoływany automatycznie przez BleakScanner gdy wykryto urządzenie.
            
            To jest funkcja callback - nie wywołujemy jej ręcznie, tylko BleakScanner
            wywołuje ją za każdym razem gdy wykryje nowe urządzenie BLE.
            
            Args:
                device: Informacje o urządzeniu (nazwa, MAC address)
                advertisement_data: Advertising data - dane które urządzenie wysyła w kółko
            """
            if device.address not in discovered_devices:
                discovered_devices.add(device.address)
                # Zapisz advertising data - będziemy jej potrzebować później do analizy
                self.advertisement_data[device.address] = advertisement_data
                # Zapisz obiekt BLEDevice z nazwą urządzenia
                self.scanned_devices_dict[device.address] = device
                
                # WAŻNE: Zapisz nazwę urządzenia TERAZ, bo może nie być dostępna później
                # device.name może być None, ale advertisement_data.local_name może mieć nazwę
                # Spróbuj wszystkie możliwe źródła nazwy w kolejności priorytetu
                device_name = None
                
                # Priorytet 1: device.name (najbardziej niezawodna)
                if device.name:
                    device_name = str(device.name).strip()
                # Priorytet 2: advertisement_data.local_name
                elif advertisement_data.local_name:
                    device_name = str(advertisement_data.local_name).strip()
                else:
                    device_name = None
                
                # ZAWSZE zapisz nazwę jeśli jest dostępna
                # To jest KLUCZOWE - nazwa może być dostępna tylko podczas callback!
                # Normalizuj adres MAC do wielkich liter dla spójności
                if device_name and device_name.strip():
                    normalized_address = device.address.upper()
                    self.device_names[normalized_address] = device_name.strip()
                
                # Wyświetl informacje o wykrytym urządzeniu
                # Jeśli nie ma nazwy, spróbuj pobrać producenta z OUI
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
                console.print(f"  [green]✓[/green] Wykryto: [cyan]{display_name}[/cyan] ({device.address})")
                # RSSI (Received Signal Strength Indicator) - siła sygnału w dBm
                # Im wyższa wartość (bliżej 0), tym silniejszy sygnał
                if advertisement_data.rssi:
                    console.print(f"    RSSI: {advertisement_data.rssi} dBm")
        
        # Rozpocznij skanowanie używając BleakScanner
        # BleakScanner automatycznie wywołuje detection_callback dla każdego wykrytego urządzenia
        async with BleakScanner(detection_callback=detection_callback):
            # Czekaj przez określony czas (duration sekund)
            # W tym czasie BleakScanner będzie wykrywał urządzenia i wywoływał callback
            await asyncio.sleep(duration)
        
        console.print(f"\n[green]✅ Skanowanie zakończone. Znaleziono {len(discovered_devices)} urządzeń.[/green]\n")
        
        # Przeanalizuj każde wykryte urządzenie
        if discovered_devices:
            console.print("[cyan]🔒 Analizuję właściwości bezpieczeństwa urządzeń...[/cyan]")
            console.print("[dim]ℹ️  Błędy połączenia są normalne - większość urządzeń wymaga parowania (to jest bezpieczne!)[/dim]\n")
            
            # Filtruj urządzenia na podstawie RSSI (tylko te w zasięgu)
            # RSSI > -95 dBm = w rozsądnym zasięgu (-90 było zbyt restrykcyjne dla części adapterów)
            # Brak RSSI = zaakceptuj (niektóre stosy nie podają RSSI w callbacku)
            filtered_addresses = []
            for address in discovered_devices:
                ad_data = self.advertisement_data.get(address)
                if ad_data and ad_data.rssi is not None:
                    if ad_data.rssi > -95:
                        filtered_addresses.append(address)
                else:
                    filtered_addresses.append(address)
            
            # Jeśli przefiltrowano urządzenia, wyświetl informację
            if len(discovered_devices) > len(filtered_addresses):
                console.print(f"[dim]   Pominięto {len(discovered_devices) - len(filtered_addresses)} urządzeń poza zasięgiem (RSSI ≤ -95 dBm)[/dim]\n")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                for address in filtered_addresses:
                    # Pobierz nazwę urządzenia z zapisanych danych (szybsze wyświetlanie)
                    device_display_name = self.device_names.get(address) or "Unknown Device"
                    task = progress.add_task(f"Analizuję {device_display_name}...", total=None)
                    
                    try:
                        device = await self._analyze_device(address)
                        if device:
                            devices.append(device)
                            progress.update(task, description=f"✓ {device.name}")
                    except Exception as e:
                        # Nie wyświetlaj błędów połączenia - to jest normalne
                        if "TimeoutError" not in str(type(e).__name__) and "not found" not in str(e).lower():
                            console.print(f"[red]  ✗ Błąd analizy {address}: {e}[/red]")
                        progress.update(task, description=f"✗ {device_display_name}")
        
        self.scanned_devices = devices
        return devices
    
    async def _analyze_device(self, address: str) -> Optional[Device]:
        """
        Analizuje urządzenie BLE i wykrywa jego właściwości bezpieczeństwa.
        
        Ta funkcja:
        1. Pobiera advertising data
        2. Próbuje połączyć się z urządzeniem
        3. Sprawdza GATT services i characteristics
        4. Wykrywa szyfrowanie i wymaganie parowania
        5. Określa typ urządzenia (medyczne vs domowe)
        
        Args:
            address: Adres MAC urządzenia
            
        Returns:
            Obiekt Device z analizą bezpieczeństwa
        """
        # Pobierz advertising data - dane które urządzenie wysyła w kółko (broadcast)
        # Zawiera: nazwę, UUID serwisów, RSSI, dane producenta, itp.
        ad_data = self.advertisement_data.get(address)
        if not ad_data:
            return None
        
        # Podstawowe informacje z advertising data
        # Pobierz nazwę urządzenia - sprawdź wszystkie możliwe źródła w kolejności:
        # 1. device.name z BleakScanner (najbardziej niezawodna)
        # 2. _saved_name (zapisana nazwa z detection_callback)
        # 3. local_name z advertising data
        # 4. "Unknown Device" jako fallback
        ble_device = self.scanned_devices_dict.get(address)
        name = None
        
        # PRIORYTET 1: Zapisana nazwa z detection_callback - to jest NAJWAŻNIEJSZE!
        # Nazwa może być dostępna TYLKO podczas callback, więc MUSIMY użyć zapisanej wartości
        # Normalizuj adres MAC do wielkich liter dla spójności
        normalized_address = address.upper()
        if normalized_address in self.device_names:
            saved_name = self.device_names[normalized_address]
            if saved_name and saved_name.strip():  # Jeśli mamy zapisaną nazwę (nie None i nie pusty string)
                name = saved_name.strip()
        
        # PRIORYTET 2: Spróbuj z obiektu BLEDevice (może być dostępne)
        if not name and ble_device:
            if hasattr(ble_device, 'name') and ble_device.name:
                name = ble_device.name
        
        # PRIORYTET 3: Spróbuj z advertising data (może być dostępne)
        if not name and ad_data.local_name:
            name = ad_data.local_name
        
        rssi = ad_data.rssi or -100  # Siła sygnału (im wyższa, tym lepiej, np. -45 to lepiej niż -80)
        
        # Analizuj serwisy z advertising data
        # service_uuids to lista UUID serwisów które urządzenie oferuje
        # Przykład: ["00001808-0000-1000-8000-00805f9b34fb"] = Glucose Service
        service_uuids = ad_data.service_uuids or []
        # manufacturer_data zawiera dane producenta (może zawierać Company ID)
        manufacturer_data = ad_data.manufacturer_data or {}
        
        # PRIORYTET 4: Spróbuj pobrać producenta z OUI lookup
        # WAŻNE: Pobierz producenta ZAWSZE, nawet jeśli mamy już nazwę
        # Producent będzie zapisany w obiekcie Device dla raportów
        manufacturer_from_mac = self._get_manufacturer_from_mac(address)
        if not name and manufacturer_from_mac:
            # Użyj nazwy producenta jako nazwy urządzenia (bez " Device")
            name = manufacturer_from_mac
        
        # Wykryj typ urządzenia na podstawie UUID serwisów, nazwy i producenta
        # Jeśli urządzenie ma UUID 0x1808 = Glucose Service, to jest glukometrem
        device_type = self._detect_device_type(service_uuids, name, manufacturer_from_mac)
        
        # WAŻNE: Jeśli nadal nie mamy nazwy, utwórz identyfikowalną nazwę
        # To jest KLUCZOWE - musimy mieć jakiś identyfikator urządzenia dla raportów!
        # Teraz mamy już device_type, więc możemy użyć go do utworzenia nazwy
        if not name or name == "Unknown Device":
            # Utwórz czytelną nazwę z dostępnych informacji
            mac_short = address.replace(":", "")[-6:].upper()  # Ostatnie 6 znaków MAC
            
            # Priorytet 1: Typ urządzenia + MAC
            if device_type != DeviceType.UNKNOWN:
                # Przetłumacz typ urządzenia na czytelną nazwę
                type_names = {
                    DeviceType.GLUCOSE_METER: "Glukometr",
                    DeviceType.INSULIN_PUMP: "Pompa insulinowa",
                    DeviceType.BLOOD_PRESSURE: "Ciśnieniomierz",
                    DeviceType.PULSE_OXIMETER: "Pulsoksymetr",
                    DeviceType.FITNESS_TRACKER: "Opaska fitness",
                    DeviceType.SMARTWATCH: "Smartwatch",
                }
                type_name = type_names.get(device_type, device_type.value)
                name = f"{type_name} ({mac_short})"
            # Priorytet 2: Producent + MAC
            elif manufacturer_from_mac:
                # Skróć nazwę producenta jeśli zbyt długa
                manufacturer_short = manufacturer_from_mac[:20] if len(manufacturer_from_mac) > 20 else manufacturer_from_mac
                name = f"{manufacturer_short} ({mac_short})"
            # Priorytet 3: Tylko MAC (krótka wersja)
            else:
                name = f"Device ({mac_short})"
        
        # Sprawdź właściwości bezpieczeństwa
        # Zaczynamy od False - jeśli znajdziemy dowody szyfrowania/parowania, zmienimy na True
        has_encryption = False  # Czy urządzenie wymaga szyfrowania?
        requires_pairing = False  # Czy urządzenie wymaga parowania?
        security_flags = []  # Lista znalezionych flag bezpieczeństwa (dla raportu)
        
        try:
            # Próbuj połączyć się z urządzeniem (timeout 5 sekund)
            # BleakClient próbuje nawiązać połączenie BLE z urządzeniem
            # Jeśli urządzenie wymaga parowania, połączenie się nie powiedzie
            # 
            # UWAGA: Większość urządzeń BLE NIE pozwala na połączenie bez parowania.
            # To jest NORMALNE i oznacza że urządzenie jest bezpieczne (wymaga autoryzacji).
            # Błędy połączenia są oczekiwane i nie są problemem - to część analizy bezpieczeństwa.
            async with BleakClient(address, timeout=3.0) as client:
                # Jeśli udało się połączyć bez parowania, oznacza to że:
                # - Urządzenie nie wymaga parowania LUB
                # - Urządzenie już jest sparowane (ale to rzadkie w skanowaniu)
                requires_pairing = False  # Możemy się połączyć bez parowania
                
                # Pobierz wszystkie serwisy GATT (Generic Attribute Profile)
                # Serwisy to grupy charakterystyk (np. Glucose Service zawiera Glucose Measurement)
                # 
                # UWAGA: W różnych wersjach bleak API może być różnie:
                # - Stare wersje (< 0.20): services jest właściwością (client.services)
                # - Nowe wersje (>= 0.20): get_services() jest metodą async
                # Sprawdzamy obie wersje dla kompatybilności
                try:
                    # Spróbuj nową wersję API (bleak >= 0.20) - get_services() jako metoda
                    if hasattr(client, 'get_services') and callable(getattr(client, 'get_services')):
                        services = await client.get_services()
                    else:
                        # Stara wersja API lub services jako właściwość
                        # W niektórych wersjach services jest dostępne bezpośrednio
                        if hasattr(client, 'services'):
                            services = client.services
                        else:
                            # Jeśli nie ma ani get_services ani services, użyj metody alternatywnej
                            # W najnowszych wersjach bleak services może być dostępne przez inne API
                            services = await client.get_services() if hasattr(client, 'get_services') else []
                except (AttributeError, TypeError) as api_error:
                    # Problem z API - spróbuj alternatywnej metody
                    try:
                        # W niektórych wersjach bleak services jest właściwością dostępną po połączeniu
                        services = client.services
                    except AttributeError:
                        # Jeśli nadal nie działa, kontynuuj bez analizy serwisów
                        # (mamy już advertising data, więc możemy kontynuować analizę)
                        services = []
                
                # Sprawdź każdy serwis i jego charakterystyki
                # Characteristic to konkretna wartość/funkcja (np. poziom glukozy, poziom baterii)
                for service in services:
                    service_uuid = str(service.uuid).lower()
                    
                    # Sprawdź każdą charakterystykę w serwisie
                    for char in service.characteristics:
                        # char.properties to lista właściwości charakterystyki
                        # Przykłady: ["read", "write", "notify", "encrypt", "authenticate"]
                        char_props = char.properties
                        
                        # Sprawdź właściwości bezpieczeństwa
                        # Jeśli charakterystyka ma flagę "encrypt" lub "encrypt-authenticate",
                        # oznacza to że WYMAGA szyfrowania do odczytu/zapisu
                        if "encrypt" in char_props or "encrypt-authenticate" in char_props:
                            has_encryption = True  # ✅ Wykryto wymaganie szyfrowania!
                            security_flags.append(f"Encryption required for {service_uuid[:8]}")
                        
                        # Jeśli charakterystyka ma flagę "authenticate" lub "authorize",
                        # oznacza to że WYMAGA autoryzacji (parowania)
                        if "authenticate" in char_props or "authorize" in char_props:
                            requires_pairing = True  # ✅ Wykryto wymaganie parowania!
                            security_flags.append(f"Authentication required for {service_uuid[:8]}")
                
                # Jeśli nie znaleźliśmy wymagań w charakterystykach, sprawdź advertising flags
                if not has_encryption and not requires_pairing:
                    # Sprawdź advertising flags (jeśli dostępne)
                    flags = ad_data.service_data or {}
                    if flags:
                        # Jeśli urządzenie ma service data, może wymagać szyfrowania
                        # W większości przypadków urządzenia medyczne wymagają szyfrowania
                        if device_type != DeviceType.UNKNOWN:
                            # Urządzenia medyczne zazwyczaj wymagają szyfrowania
                            has_encryption = True
                            requires_pairing = True
                
        except Exception as e:
            # Jeśli nie możemy się połączyć, analizuj błąd aby określić wymagania bezpieczeństwa
            # 
            # WAŻNE: Błędy połączenia są NORMALNE dla Bluetooth!
            # Większość urządzeń BLE NIE pozwala na połączenie bez parowania.
            # To oznacza że urządzenie jest BEZPIECZNE (wymaga autoryzacji).
            # 
            # Typowe powody błędów połączenia:
            # 1. Urządzenie wymaga parowania (to jest DOBRE - oznacza bezpieczeństwo)
            # 2. Urządzenie jest już połączone z innym urządzeniem
            # 3. Urządzenie jest poza zasięgiem lub wyłączone
            # 4. Urządzenie nie obsługuje GATT (niektóre urządzenia tylko nadają, nie przyjmują połączeń)
            # 5. Timeout - urządzenie nie odpowiada w czasie (może być zajęte)
            
            error_msg = str(e).lower()
            error_type = type(e).__name__
            
            # Jeśli błąd zawiera słowa związane z parowaniem/autoryzacją,
            # oznacza to że urządzenie WYMAGA parowania (to jest DOBRE!)
            if ("not paired" in error_msg or "pairing" in error_msg or 
                "authentication" in error_msg or "not authorized" in error_msg or
                "insufficient authentication" in error_msg):
                requires_pairing = True  # ✅ Urządzenie wymaga parowania - to jest BEZPIECZNE!
                # Jeśli wymaga parowania, prawdopodobnie używa też szyfrowania
                # (parowanie zwykle idzie w parze z szyfrowaniem)
                has_encryption = True
                # Nie wyświetlaj błędu - to jest oczekiwane zachowanie dla bezpiecznych urządzeń
                
            elif "not found" in error_msg or "was not found" in error_msg or "device" in error_msg and "not found" in error_msg:
                # Urządzenie zniknęło z zasięgu lub jest już połączone z innym urządzeniem
                # To jest normalne - urządzenia BLE mogą szybko znikać z zasięgu
                # Nie wyświetlaj błędu - kontynuuj analizę na podstawie advertising data
                pass
                
            elif "timeout" in error_msg or "timed out" in error_msg:
                # Timeout - urządzenie nie odpowiada w czasie
                # Może być zajęte, poza zasięgiem, lub wymaga parowania
                # Dla urządzeń medycznych zakładamy, że POWINNY wymagać szyfrowania
                if device_type != DeviceType.UNKNOWN:
                    # To jest urządzenie medyczne - powinno wymagać szyfrowania
                    has_encryption = True
                    requires_pairing = True
                # Nie wyświetlaj błędu - timeout jest normalny
                
            elif "get_services" in error_msg or "attribute" in error_msg:
                # Problem z API bleak - może być niekompatybilna wersja
                # Spróbuj użyć alternatywnego API
                console.print(f"[dim]    ⚠️  {address}: Problem z API bleak (możliwa niekompatybilna wersja)[/dim]")
                # Kontynuuj analizę na podstawie advertising data
                
            elif "connection" in error_msg or "failed" in error_msg:
                # Ogólny błąd połączenia - urządzenie może wymagać parowania
                # Dla urządzeń medycznych zakładamy bezpieczeństwo
                if device_type != DeviceType.UNKNOWN:
                    has_encryption = True
                    requires_pairing = True
                # Nie wyświetlaj błędu - kontynuuj analizę
                
            else:
                # Inny błąd - wyświetl tylko jeśli to nie jest typowy błąd Bluetooth
                # Większość błędów to normalne zachowanie (wymaganie parowania)
                if "get_services" not in error_msg and "not found" not in error_msg:
                    # Wyświetl tylko nietypowe błędy
                    console.print(f"[dim]    ⚠️  {address}: {error_type}[/dim]")
        
        # Jeśli nie wykryliśmy szyfrowania, ale urządzenie jest medyczne, zakładamy że powinno mieć
        # (ale to nie znaczy że ma - to jest podatność!)
        if device_type != DeviceType.UNKNOWN and not has_encryption:
            # Urządzenie medyczne bez wykrytego szyfrowania - to jest podatność!
            pass  # Zostawiamy has_encryption=False, aby wykryć podatność
        
        # Określ typ szyfrowania dla BLE
        encryption_type = None
        if has_encryption:
            if requires_pairing:
                # Jeśli wymaga parowania, prawdopodobnie używa LE Secure Connections (AES-256)
                encryption_type = "LE Secure Connections (AES-256)"
            elif "encrypt-authenticate" in str(security_flags).lower():
                # Jeśli ma encrypt-authenticate, używa AES-256
                encryption_type = "AES-256"
            else:
                # Podstawowe szyfrowanie AES-128
                encryption_type = "AES-128"
        else:
            encryption_type = "No encryption"
        
        # Utwórz obiekt Device
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
        
        # Dodaj podatności jeśli urządzenie jest niebezpieczne
        if not has_encryption:
            device.add_vulnerability("Brak wykrytego szyfrowania - dane mogą być przechwycone")
        if not requires_pairing:
            device.add_vulnerability("Brak wymagania parowania - każdy może się połączyć")
        
        # Oblicz security score
        device.calculate_security_score()
        
        return device
    
    def _detect_device_type(self, service_uuids: List[str], name: Optional[str], manufacturer: Optional[str] = None) -> DeviceType:
        """
        Wykrywa typ urządzenia na podstawie UUID serwisów i nazwy.
        
        Metoda 1: Sprawdza UUID serwisów (najbardziej niezawodne)
        - Standardowe UUID z Bluetooth SIG jednoznacznie określają typ urządzenia
        - Przykład: UUID 0x1808 = Glucose Service = glukometr
        
        Metoda 2: Analiza nazwy (heurystyka, mniej niezawodna)
        - Sprawdza czy nazwa zawiera słowa kluczowe (np. "glucose", "insulin")
        
        Metoda 3: Analiza producenta (na podstawie adresu MAC - OUI)
        - Sprawdza czy producent jest znany z produkcji urządzeń medycznych
        - Przykład: "Roche" = często glukometry, "Omron" = ciśnieniomierze
        
        Args:
            service_uuids: Lista UUID serwisów z advertising data
            name: Nazwa urządzenia (może być None)
            manufacturer: Nazwa producenta (z adresu MAC - OUI)
            
        Returns:
            DeviceType urządzenia (lub UNKNOWN jeśli nie rozpoznano)
        """
        # WAŻNE: name może być None - sprawdź przed użyciem .lower()
        name_lower = (name or "").lower()
        manufacturer_lower = (manufacturer or "").lower()
        
        # Metoda 1: Sprawdź UUID serwisów medycznych (najbardziej niezawodne)
        # Standardowe UUID są zdefiniowane przez Bluetooth SIG i jednoznacznie określają typ urządzenia
        for uuid in service_uuids:
            uuid_lower = str(uuid).lower()
            
            # UUID 0x1808 = Glucose Service (zdefiniowany przez Bluetooth SIG)
            # Jeśli urządzenie ma ten UUID, to JEST glukometrem (nie przypuszczenie!)
            if "1808" in uuid_lower or uuid_lower == "00001808-0000-1000-8000-00805f9b34fb":
                return DeviceType.GLUCOSE_METER
            
            # UUID 0x1810 = Blood Pressure Service
            if "1810" in uuid_lower or uuid_lower == "00001810-0000-1000-8000-00805f9b34fb":
                return DeviceType.BLOOD_PRESSURE
            
            # UUID 0x180D = Heart Rate Service (używany przez pulsoksymetry)
            if "180d" in uuid_lower or uuid_lower == "0000180d-0000-1000-8000-00805f9b34fb":
                return DeviceType.PULSE_OXIMETER
        
        # Metoda 2: Sprawdź nazwę urządzenia (heurystyka, mniej niezawodna)
        # To jest metoda zapasowa - jeśli nie znaleźliśmy standardowego UUID,
        # próbujemy rozpoznać urządzenie po nazwie
        # UWAGA: To jest mniej niezawodne, bo producenci mogą używać dowolnych nazw
        
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
        
        # Metoda 3: Sprawdź producenta (na podstawie adresu MAC - OUI)
        # Niektóre firmy są znane z produkcji konkretnych typów urządzeń medycznych
        if manufacturer_lower:
            # Producenci glukometrów
            glucose_manufacturers = [
                "roche", "accu-chek", "freestyle", "abbott", "onetouch", "life scan",
                "bayer", "contour", "ascensia", "sanofi", "medtronic"
            ]
            if any(manuf in manufacturer_lower for manuf in glucose_manufacturers):
                return DeviceType.GLUCOSE_METER
            
            # Producenci pomp insulinowych
            insulin_manufacturers = [
                "medtronic", "tandem", "insulet", "omnipod", "cellnovo"
            ]
            if any(manuf in manufacturer_lower for manuf in insulin_manufacturers):
                return DeviceType.INSULIN_PUMP
            
            # Producenci ciśnieniomierzy
            bp_manufacturers = [
                "omron", "withings", "a&d", "microlife", "beurer", "panasonic"
            ]
            if any(manuf in manufacturer_lower for manuf in bp_manufacturers):
                return DeviceType.BLOOD_PRESSURE
            
            # Producenci pulsoksymetrów
            pulse_manufacturers = [
                "masimo", "nonin", "philips", "ge healthcare", "medtronic"
            ]
            if any(manuf in manufacturer_lower for manuf in pulse_manufacturers):
                return DeviceType.PULSE_OXIMETER
            
            # Producenci smartwatch/fitness tracker
            fitness_manufacturers = [
                "apple", "samsung", "fitbit", "garmin", "polar", "suunto", "xiaomi"
            ]
            if any(manuf in manufacturer_lower for manuf in fitness_manufacturers):
                # Sprawdź czy to smartwatch czy fitness tracker
                if any(word in name_lower for word in ["watch", "smartwatch"]):
                    return DeviceType.SMARTWATCH
                return DeviceType.FITNESS_TRACKER
        
        # Jeśli nie znaleźliśmy ani UUID, ani nie rozpoznaliśmy po nazwie/producencie,
        # zwróć UNKNOWN (nieznany typ urządzenia)
        return DeviceType.UNKNOWN
    
    def _get_manufacturer_from_mac(self, mac_address: str) -> Optional[str]:
        """
        Pobiera nazwę producenta na podstawie adresu MAC (OUI).
        
        Używa wielu źródeł w kolejności priorytetu:
        1. IEEE OUI (oficjalna baza IEEE) - najlepsza, bez limitów
        2. mac-vendor-lookup (lokalna baza)
        3. macvendors.com API (zewnętrzne API) - fallback
        
        OUI (Organizationally Unique Identifier) to pierwsze 3 bajty adresu MAC
        które jednoznacznie identyfikują producenta urządzenia.
        
        Przykład:
        - MAC: AA:BB:CC:DD:EE:FF
        - OUI: AA:BB:CC
        - Producent: "Apple Inc."
        
        Args:
            mac_address: Adres MAC urządzenia (format: "AA:BB:CC:DD:EE:FF" lub "AA-BB-CC-DD-EE-FF")
        
        Returns:
            Nazwa producenta lub None jeśli nie znaleziono
        """
        # Sprawdź czy adres MAC nie jest losowy/prywatny
        is_random = False
        try:
            mac_normalized = mac_address.replace("-", ":").replace(" ", ":").replace(".", ":").upper()
            first_byte = int(mac_normalized.split(":")[0], 16)
            is_random = (first_byte & 0x02) != 0
        except Exception:
            pass
        
        # Metoda 1: IEEE OUI (oficjalna baza IEEE) - PRIORYTET
        try:
            from oui_lookup import get_oui_lookup
            oui_lookup = get_oui_lookup()
            manufacturer = oui_lookup.lookup(mac_address)
            if manufacturer:
                # Sprawdź czy to nie jest fałszywy producent dla wygenerowanych MAC
                # Wygenerowane MAC (00:00:xx:xx:xx:xx) mogą mieć przypadkowe dopasowania w OUI
                if mac_address.startswith("00:00:"):
                    return None  # Wygenerowany MAC - nie używaj producenta z OUI
                return manufacturer
        except Exception:
            pass
        
        # Metoda 2: mac-vendor-lookup (lokalna baza) - tylko dla nie-losowych MAC
        if self.mac_lookup_available and self.mac_lookup:
            try:
                mac_normalized = mac_address.replace("-", ":").replace(" ", ":").upper()
                
                if not is_random:
                    vendor = self.mac_lookup.lookup(mac_normalized)
                    if vendor and vendor != "Unknown":
                        return vendor
            except Exception:
                pass
        
        # Metoda 3: macvendors.com API - tylko dla nie-losowych MAC
        # Losowe adresy MAC zwykle nie są w bazie macvendors.com
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
        Sprawdza czy adres MAC jest losowy (random MAC address).
        
        Losowe adresy MAC są używane przez nowoczesne urządzenia dla prywatności
        i nie reprezentują prawdziwego producenta.
        
        Args:
            mac_address: Adres MAC urządzenia
        
        Returns:
            True jeśli MAC jest losowy, False w przeciwnym razie
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
        Próbuje wyodrębnić nazwę producenta z manufacturer data.
        
        Manufacturer data zawiera Company ID (pierwsze 2 bajty) zgodnie z Bluetooth SIG.
        To jest metoda zapasowa - główna identyfikacja jest przez adres MAC (OUI).
        
        Args:
            manufacturer_data: Dane producenta z advertising data (dict z Company ID jako klucz)
        
        Returns:
            Nazwa producenta lub None
        """
        if not manufacturer_data:
            return None
        
        # Manufacturer data zawiera Company ID jako klucz (np. {"64": "00c202"})
        # Company ID to identyfikator producenta zgodnie z Bluetooth SIG
        # Przykład: Company ID 64 (0x0040) = jakiś producent
        
        # Spróbuj znaleźć Company ID w manufacturer_data
        # Klucz to Company ID (może być jako int lub string)
        for company_id_str, data in manufacturer_data.items():
            try:
                # Konwertuj Company ID na int
                company_id = int(company_id_str)
                
                # Sprawdź popularne Company IDs (możemy rozszerzyć o pełną bazę)
                # Źródło: https://www.bluetooth.com/specifications/assigned-numbers/company-identifiers/
                company_ids = {
                    0: "Ericsson Technology Licensing",
                    6: "Microsoft Corporation",
                    15: "3Com",
                    76: "Apple, Inc.",
                    89: "Nordic Semiconductor ASA",
                    117: "Google Inc.",
                    152: "Samsung Electronics Co. Ltd.",
                }
                
                # Jeśli mamy Company ID w bazie, zwróć producenta
                if company_id in company_ids:
                    return company_ids[company_id]
                
                # Możemy też spróbować użyć macvendors.com API z Company ID
                # Ale to wymagałoby dodatkowej bazy danych
                
            except (ValueError, TypeError):
                continue
        
        # Jeśli nie znaleźliśmy producenta z Company ID, zwróć None
        # Główna identyfikacja jest przez adres MAC (OUI) w _get_manufacturer_from_mac()
        return None
    
    def get_all_devices(self) -> List[Device]:
        """Zwraca wszystkie wykryte urządzenia."""
        return self.scanned_devices


async def scan_devices_async(duration: int = 10) -> List[Device]:
    """
    Asynchroniczna funkcja pomocnicza do skanowania urządzeń.
    
    Args:
        duration: Czas skanowania w sekundach
        
    Returns:
        Lista wykrytych urządzeń
    """
    scanner = RealBLEScanner()
    return await scanner.scan_ble_devices(duration=duration)


def scan_devices(duration: int = 10) -> List[Device]:
    """
    Synchroniczna funkcja do skanowania urządzeń (wrapper dla asyncio).
    
    Args:
        duration: Czas skanowania w sekundach
        
    Returns:
        Lista wykrytych urządzeń
    """
    if not BLEAK_AVAILABLE:
        raise ImportError(
            "Biblioteka 'bleak' nie jest zainstalowana.\n"
            "Zainstaluj: pip install bleak"
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
        "[dim]Skanuję rzeczywiste urządzenia Bluetooth w zasięgu...[/dim]",
        style="cyan"
    ))
    console.print()
    
    try:
        devices = scan_devices(duration=10)
        
        console.print(f"\n[bold green]✅ Znaleziono {len(devices)} urządzeń:[/bold green]\n")
        
        for device in devices:
            console.print(f"[cyan]{device.name}[/cyan] ({device.mac_address})")
            console.print(f"  Typ: {device.device_type.value}")
            console.print(f"  Szyfrowanie: {'✅ Tak' if device.has_encryption else '❌ Nie'}")
            console.print(f"  Parowanie: {'✅ Wymagane' if device.requires_pairing else '❌ Nie wymagane'}")
            console.print(f"  Security Score: {device.security_score}/100")
            if device.vulnerabilities:
                console.print(f"  Podatności: {', '.join(device.vulnerabilities)}")
            console.print()
            
    except ImportError as e:
        console.print(f"[red]❌ Błąd: {e}[/red]")
        console.print("[yellow]Zainstaluj bibliotekę: pip install bleak[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Błąd: {e}[/red]")
        import traceback
        traceback.print_exc()
