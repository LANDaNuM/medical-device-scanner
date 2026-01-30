"""
Medical Device Security Scanner

Główny pakiet aplikacji do skanowania i analizy bezpieczeństwa urządzeń medycznych IoT.

Ten pakiet zawiera:
- device.py: Klasa Device reprezentująca urządzenie medyczne
- scanner.py: Główny moduł skanera łączący wszystkie komponenty
- real_scanner.py: Prawdziwy skaner BLE używający biblioteki bleak
- wifi_scanner.py: Skaner WiFi używający nmap
- usb_scanner.py: Skaner USB używający pyusb i pyserial
- nfc_scanner.py: Skaner NFC używający nfcpy i pyscard
"""

__version__ = "0.1.0"
__author__ = "Medical Device Security Scanner Team"
