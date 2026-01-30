#!/usr/bin/env python3
"""
Prawdziwy skaner NFC - wykrywa urządzenia medyczne z NFC.

Ten moduł używa nfcpy lub innych bibliotek do wykrywania urządzeń NFC
i analizy ich właściwości bezpieczeństwa.
"""

import sys
import os
from typing import List, Optional, Dict
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

# Dodaj katalog src/ do ścieżki Python
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    import nfc
    NFC_AVAILABLE = True
except ImportError:
    NFC_AVAILABLE = False

# Alternatywnie użyj pyscard dla kart inteligentnych
try:
    from smartcard.System import readers
    from smartcard.util import toHexString
    PYSMCARD_AVAILABLE = True
except ImportError:
    PYSMCARD_AVAILABLE = False

from device import Device, DeviceType, Protocol

console = Console()


class NFCScanner:
    """
    Prawdziwy skaner NFC używający nfcpy lub pyscard.
    
    Wykrywa urządzenia NFC (karty, tagi) i analizuje ich właściwości
    bezpieczeństwa. Wymaga czytnika NFC.
    """
    
    def __init__(self):
        """Inicjalizacja skanera NFC."""
        if not NFC_AVAILABLE and not PYSMCARD_AVAILABLE:
            console.print("[yellow]⚠️  Biblioteki NFC nie są zainstalowane.[/yellow]")
            console.print("[yellow]   Zainstaluj: pip install nfcpy pyscard[/yellow]")
            console.print("[yellow]   Wymaga czytnika NFC (np. ACR122U)[/yellow]\n")
        self.scanned_devices: List[Device] = []
    
    def scan_nfc_devices(self, duration: int = 5) -> List[Device]:
        """
        Skanuje urządzenia NFC w zasięgu.
        
        Args:
            duration: Czas skanowania w sekundach
        
        Returns:
            Lista wykrytych urządzeń Device
        """
        console.print("[cyan]🔍 Rozpoczynam skanowanie NFC...[/cyan]")
        console.print("[dim]Zbliż urządzenie NFC do czytnika...[/dim]\n")
        
        devices: List[Device] = []
        
        if NFC_AVAILABLE:
            nfc_devices = self._scan_nfcpy(duration)
            devices.extend(nfc_devices)
        elif PYSMCARD_AVAILABLE:
            smartcard_devices = self._scan_smartcard()
            devices.extend(smartcard_devices)
        else:
            console.print("[yellow]⚠️  Brak dostępnych bibliotek NFC - nie można skanować[/yellow]")
            console.print("[yellow]   NFC wymaga specjalnego sprzętu (czytnik NFC)[/yellow]\n")
        
        self.scanned_devices = devices
        console.print(f"\n[green]✅ Skanowanie NFC zakończone. Znaleziono {len(devices)} urządzeń.[/green]\n")
        return devices
    
    def _scan_nfcpy(self, duration: int) -> List[Device]:
        """
        Skanuje urządzenia NFC używając biblioteki nfcpy.
        
        nfcpy to biblioteka Python do komunikacji z czytnikami NFC.
        Wymaga podłączonego czytnika NFC (np. ACR122U, PN532).
        
        Args:
            duration: Czas skanowania w sekundach (jak długo czekać na zbliżenie karty)
        
        Returns:
            Lista wykrytych urządzeń Device
        """
        devices: List[Device] = []
        
        try:
            # Połącz się z czytnikiem NFC przez USB
            # ContactlessFrontend to interfejs do komunikacji z czytnikiem
            clf = nfc.ContactlessFrontend('usb')
            
            if not clf:
                console.print("[yellow]⚠️  Nie znaleziono czytnika NFC[/yellow]")
                console.print("[yellow]   Sprawdź czy czytnik jest podłączony[/yellow]\n")
                return devices
            
            console.print("[green]✓ Czytnik NFC wykryty[/green]\n")
            
            # Skanuj przez określony czas
            import time
            start_time = time.time()
            
            while time.time() - start_time < duration:
                # Spróbuj odczytać tag/kartę
                tag = clf.connect(rdwr={'on-connect': self._on_nfc_connect})
                
                if tag:
                    device = self._analyze_nfc_tag(tag)
                    if device:
                        devices.append(device)
                        console.print(f"  [green]✓[/green] Wykryto: {device.name}")
                        break  # Znaleziono urządzenie, zakończ skanowanie
            
            clf.close()
        
        except Exception as e:
            console.print(f"[yellow]⚠️  Błąd skanowania NFC: {e}[/yellow]")
            console.print("[yellow]   Sprawdź czy czytnik NFC jest podłączony i działa[/yellow]\n")
        
        return devices
    
    def _scan_smartcard(self) -> List[Device]:
        """
        Skanuje karty inteligentne używając biblioteki pyscard.
        
        pyscard to biblioteka Python do komunikacji z czytnikami kart inteligentnych (PC/SC).
        Wymaga zainstalowanych bibliotek systemowych PCSC (libpcsclite-dev na Linux).
        
        Karty inteligentne (smart cards) to karty z chipem, które mogą przechowywać
        dane medyczne pacjenta lub służyć do autoryzacji dostępu.
        
        Returns:
            Lista wykrytych urządzeń Device
        """
        devices: List[Device] = []
        
        try:
            # Znajdź wszystkie dostępne czytniki kart PC/SC
            # readers() zwraca listę dostępnych czytników w systemie
            reader_list = readers()
            
            if not reader_list:
                console.print("[yellow]⚠️  Nie znaleziono czytników kart[/yellow]\n")
                return devices
            
            console.print(f"[green]✓ Znaleziono {len(reader_list)} czytnik(ów)[/green]\n")
            
            for reader in reader_list:
                try:
                    # Utwórz połączenie z kartą
                    connection = reader.createConnection()
                    connection.connect()
                    
                    # Odczytaj ATR (Answer To Reset) - identyfikator karty
                    # ATR to pierwsze dane wysyłane przez kartę po włożeniu do czytnika
                    # Zawiera informacje o typie karty i jej możliwościach
                    atr = connection.getATR()
                    
                    device = Device(
                        mac_address=f"NFC-{toHexString(atr)[:17]}",
                        name=f"NFC-Card-{toHexString(atr)[:8]}",
                        device_type=DeviceType.UNKNOWN,
                        protocol=Protocol.NFC,
                        has_encryption=True,  # Karty inteligentne zazwyczaj mają szyfrowanie
                        encryption_type="Basic encryption (smart card)",
                        requires_pairing=True,  # Wymagają autoryzacji
                        metadata={
                            "atr": toHexString(atr),
                            "reader": str(reader)
                        }
                    )
                    
                    device.calculate_security_score()
                    devices.append(device)
                    console.print(f"  [green]✓[/green] Wykryto: {device.name}")
                
                except Exception:
                    # Karta nie jest w czytniku
                    continue
        
        except Exception as e:
            console.print(f"[yellow]⚠️  Błąd skanowania kart: {e}[/yellow]\n")
        
        return devices
    
    def _on_nfc_connect(self, tag):
        """Callback wywoływany gdy wykryto tag NFC."""
        return True
    
    def _analyze_nfc_tag(self, tag) -> Optional[Device]:
        """
        Analizuje tag NFC i tworzy obiekt Device.
        
        Tag NFC to pasywny element (karta, brelok) który może przechowywać dane.
        W kontekście medycznym, tagi NFC mogą zawierać:
        - Dane pacjenta (ID, historia medyczna)
        - Informacje o lekach
        - Autoryzację dostępu do urządzeń medycznych
        
        Args:
            tag: Obiekt tag NFC z biblioteki nfcpy zawierający informacje o tagu
        
        Returns:
            Obiekt Device z analizą bezpieczeństwa tagu lub None jeśli analiza się nie powiodła
        """
        try:
            # Pobierz podstawowe informacje o tagu
            tag_type = str(tag.type)  # Typ tagu (np. "Type2Tag", "Type4Tag")
            identifier = tag.identifier.hex()  # Unikalny identyfikator tagu (UID)
            
            # Określ typ urządzenia
            # W większości przypadków tagi NFC nie są specyficznie medyczne,
            # więc oznaczamy jako UNKNOWN (można rozszerzyć o wykrywanie danych medycznych)
            device_type = DeviceType.UNKNOWN
            
            # Sprawdź bezpieczeństwo tagu
            # NFC zazwyczaj ma podstawowe szyfrowanie (szyfrowanie na poziomie protokołu)
            # W rzeczywistości można by odczytać dane z tagu i sprawdzić czy są zaszyfrowane
            has_encryption = True  # NFC zazwyczaj ma podstawowe szyfrowanie
            encryption_type = "Basic encryption (NFC tag)"
            requires_pairing = False  # NFC nie wymaga parowania (tylko zbliżenie do czytnika)
            
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
        """Zwraca wszystkie wykryte urządzenia."""
        return self.scanned_devices


if __name__ == "__main__":
    # Test skanera NFC
    console.print(Panel.fit(
        "[bold cyan]🔍 Test: Skaner NFC[/bold cyan]\n"
        "[dim]Zbliż urządzenie NFC do czytnika...[/dim]",
        style="cyan"
    ))
    console.print()
    
    scanner = NFCScanner()
    devices = scanner.scan_nfc_devices(duration=5)
    
    console.print(f"\n[bold green]✅ Znaleziono {len(devices)} urządzeń:[/bold green]\n")
    
    for device in devices:
        console.print(f"[cyan]{device.name}[/cyan] ({device.mac_address})")
        console.print(f"  Typ: {device.device_type.value}")
        console.print(f"  Szyfrowanie: {'✅ Tak' if device.has_encryption else '❌ Nie'}")
        console.print(f"  Security Score: {device.security_score}/100")
        console.print()
