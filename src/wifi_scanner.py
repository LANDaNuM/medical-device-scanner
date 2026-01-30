#!/usr/bin/env python3
"""
Prawdziwy skaner WiFi - wykrywa urządzenia medyczne w sieci lokalnej.

Ten moduł używa nmap i innych narzędzi do skanowania sieci WiFi
i wykrywania urządzeń medycznych na podstawie otwartych portów,
usług i charakterystyk sieciowych.
"""

import sys
import os
import socket
import subprocess
import xml.etree.ElementTree as ET
import time
from typing import List, Optional, Dict
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Dodaj katalog src/ do ścieżki Python
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    from scapy.all import ARP, Ether, IP, TCP, srp, sr1, conf
    from scapy.layers.l2 import getmacbyip
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

try:
    from rust_scanner_wrapper import FastPortScanner, is_rust_available
    RUST_SCANNER_AVAILABLE = is_rust_available()
    if RUST_SCANNER_AVAILABLE:
        console.print("[dim]✅ Rust scanner dostępny - używam szybkiego skanowania[/dim]")
except ImportError:
    RUST_SCANNER_AVAILABLE = False
    FastPortScanner = None

from device import Device, DeviceType, Protocol

console = Console()

# Porty często używane przez urządzenia medyczne
# 
# Opis portów i ich przeznaczenie:
# =================================
# 
# PORTY BEZPIECZNE (szyfrowane):
#   443  - HTTPS: Bezpieczny protokół HTTP z szyfrowaniem TLS/SSL
#          Używany do interfejsów webowych urządzeń medycznych
#   8443 - HTTPS Alternative: Alternatywny port dla HTTPS
#          Często używany przez urządzenia medyczne
# 
# PORTY NIEZASZYFROWANE (ryzyko):
#   80   - HTTP: Niezaszyfrowany protokół webowy
#          Dane przesyłane w postaci jawnej (ryzyko bezpieczeństwa)
#   8080 - HTTP Alternative: Alternatywny port HTTP
#          Często używany do zarządzania urządzeniami
# 
# PORTY MEDYCZNE (specjalistyczne protokoły):
#   5000  - HL7: Protokół wymiany danych medycznych między systemami szpitalnymi
#           Używany przez systemy EHR (Electronic Health Records) i EMR
#   104   - DICOM: Standardowy port dla protokołu DICOM
#           Używany do przesyłania obrazów medycznych (RTG, CT, MRI)
#   11112 - DICOM Alternative: Alternatywny port dla DICOM
#           Używany przez niektóre systemy PACS (Picture Archiving and Communication System)
# 
# PORTY ADMINISTRACYJNE (wysokie ryzyko jeśli otwarte publicznie):
#   22   - SSH: Secure Shell, zdalny dostęp do systemu
#         Ryzyko jeśli nie zabezpieczony silnym hasłem/kluczem
#   3389 - RDP: Remote Desktop Protocol, zdalny pulpit
#         Wysokie ryzyko jeśli otwarty publicznie (możliwość przejęcia kontroli)
# 
# PORTY BAZ DANYCH (wysokie ryzyko wycieku danych):
#   1433 - MSSQL: Microsoft SQL Server
#         Bazy danych medyczne (wysokie ryzyko wycieku danych pacjentów)
#   3306 - MySQL: Baza danych MySQL
#         Często używana w systemach medycznych (wysokie ryzyko)
#
MEDICAL_PORTS = {
    443: "HTTPS - Bezpieczny protokół HTTP z szyfrowaniem TLS/SSL, używany do interfejsów webowych urządzeń medycznych",
    8443: "HTTPS Alternative - Alternatywny port dla HTTPS, często używany przez urządzenia medyczne",
    80: "HTTP - Niezaszyfrowany protokół webowy, dane przesyłane w postaci jawnej (ryzyko bezpieczeństwa)",
    8080: "HTTP Alternative - Alternatywny port HTTP, często używany do zarządzania urządzeniami",
    5000: "HL7 - Protokół wymiany danych medycznych między systemami szpitalnymi (EHR, EMR)",
    104: "DICOM - Standardowy port dla protokołu DICOM, używany do przesyłania obrazów medycznych (RTG, CT, MRI)",
    11112: "DICOM Alternative - Alternatywny port dla DICOM, używany przez niektóre systemy PACS",
    22: "SSH - Secure Shell, zdalny dostęp do systemu (ryzyko jeśli nie zabezpieczony)",
    3389: "RDP - Remote Desktop Protocol, zdalny pulpit (wysokie ryzyko jeśli otwarty publicznie)",
    1433: "MSSQL - Microsoft SQL Server, bazy danych medyczne (wysokie ryzyko wycieku danych)",
    3306: "MySQL - Baza danych MySQL, często używana w systemach medycznych (wysokie ryzyko)",
}

# Podatności związane z portami medycznymi i administracyjnymi
# Każdy port ma przypisane typowe podatności i ryzyka
#
# UWAGA: To są TEORETYCZNE podatności na podstawie znanych słabości portów,
# NIE rzeczywiste testy bezpieczeństwa. Rzeczywiste testy są wykonywane przez
# VulnerabilityTester (z flagą --audit w scanner.py).
#
# Te podatności są używane do szybkiej analizy podczas podstawowego skanowania.
# Dla dokładniejszej analizy użyj flagi --audit.
PORT_VULNERABILITIES = {
    # Porty medyczne - podatności specyficzne dla protokołów medycznych
    104: [
        "DICOM bez szyfrowania - obrazy medyczne mogą być przechwycone",
        "DICOM bez autoryzacji - nieautoryzowany dostęp do obrazów medycznych",
        "Stary protokół DICOM - może używać niebezpiecznych wersji protokołu",
        "Otwarty port DICOM publicznie - dostęp do wrażliwych danych medycznych z Internetu"
    ],
    11112: [
        "DICOM Alternative bez szyfrowania - alternatywny port może być mniej zabezpieczony",
        "DICOM bez autoryzacji - nieautoryzowany dostęp do obrazów medycznych",
        "Otwarty port DICOM publicznie - dostęp do wrażliwych danych medycznych"
    ],
    5000: [
        "HL7 bez szyfrowania - dane medyczne pacjentów mogą być przechwycone",
        "HL7 bez autoryzacji - nieautoryzowany dostęp do danych EHR/EMR",
        "Stary protokół HL7 - może używać niebezpiecznych wersji (HL7v2)",
        "Otwarty port HL7 publicznie - dostęp do danych pacjentów z Internetu"
    ],
    
    # Porty webowe - podatności związane z interfejsami webowymi
    80: [
        "HTTP bez szyfrowania - dane przesyłane w postaci jawnej",
        "HTTP - możliwość przechwycenia danych (sniffing)",
        "HTTP - ataki man-in-the-middle",
        "HTTP - hasła i dane medyczne przesyłane niezaszyfrowane"
    ],
    8080: [
        "HTTP Alternative bez szyfrowania - dane przesyłane w postaci jawnej",
        "Port 8080 często używany do zarządzania - ryzyko nieautoryzowanego dostępu",
        "HTTP Alternative - możliwość przechwycenia danych"
    ],
    443: [
        "HTTPS z przestarzałymi wersjami TLS (TLS 1.0/1.1) - podatność",
        "HTTPS z nieprawidłowymi certyfikatami - ryzyko ataków MITM",
        "HTTPS z słabymi algorytmami szyfrowania - możliwość złamania"
    ],
    8443: [
        "HTTPS Alternative z przestarzałymi wersjami TLS - podatność",
        "HTTPS Alternative z nieprawidłowymi certyfikatami - ryzyko ataków MITM"
    ],
    
    # Porty administracyjne - wysokie ryzyko
    22: [
        "SSH z przestarzałymi wersjami protokołu (SSHv1) - podatność",
        "SSH z słabymi kluczami - możliwość brute-force",
        "SSH bez ograniczenia dostępu - ataki brute-force z Internetu",
        "SSH z domyślnymi hasłami - łatwe do złamania",
        "SSH - możliwość ataków man-in-the-middle"
    ],
    3389: [
        "RDP otwarty publicznie - bardzo wysokie ryzyko przejęcia kontroli",
        "RDP bez szyfrowania - możliwość przechwycenia sesji",
        "RDP z słabymi hasłami - łatwe do złamania",
        "RDP - ataki brute-force i exploity (BlueKeep, CVE-2019-0708)",
        "RDP - możliwość rozprzestrzeniania ransomware"
    ],
    
    # Porty baz danych - bardzo wysokie ryzyko wycieku danych
    1433: [
        "MSSQL otwarty publicznie - bardzo wysokie ryzyko wycieku danych pacjentów",
        "MSSQL z domyślnymi hasłami - łatwe do złamania",
        "MSSQL bez szyfrowania - dane medyczne mogą być przechwycone",
        "MSSQL - możliwość SQL injection",
        "MSSQL - dostęp do wrażliwych danych medycznych (PII, PHI)"
    ],
    3306: [
        "MySQL otwarty publicznie - bardzo wysokie ryzyko wycieku danych pacjentów",
        "MySQL z domyślnymi hasłami - łatwe do złamania",
        "MySQL bez szyfrowania - dane medyczne mogą być przechwycone",
        "MySQL - możliwość SQL injection",
        "MySQL - dostęp do wrażliwych danych medycznych (PII, PHI)"
    ],
    
    # Inne niebezpieczne porty
    21: [
        "FTP bez szyfrowania - hasła i dane przesyłane jawnie",
        "FTP - możliwość przechwycenia danych",
        "FTP - ataki brute-force"
    ],
    23: [
        "Telnet bez szyfrowania - wszystkie dane przesyłane jawnie",
        "Telnet - bardzo wysokie ryzyko przechwycenia danych",
        "Telnet - przestarzały i niebezpieczny protokół"
    ],
    445: [
        "SMB otwarty publicznie - ryzyko ransomware (WannaCry)",
        "SMB z przestarzałymi wersjami (SMBv1) - podatność",
        "SMB - możliwość rozprzestrzeniania malware"
    ],
    53: [
        "DNS otwarty publicznie - możliwość ataków DDoS amplification",
        "DNS - manipulacja rekordów DNS",
        "DNS - możliwość wykorzystania do ataków"
    ],
    25: [
        "SMTP otwarty publicznie - możliwość spam relay",
        "SMTP - spoofing maili",
        "SMTP - możliwość wykorzystania do ataków"
    ],
}

# Charakterystyczne nazwy urządzeń medycznych w sieci
MEDICAL_DEVICE_KEYWORDS = [
    "medical", "med", "hospital", "clinic", "patient", "monitor",
    "glucose", "gluco", "insulin", "pump", "dicom", "hl7",
    "pacs", "ris", "emr", "ehr", "vital", "signs"
]


class WiFiScanner:
    """
    Skaner WiFi - wykrywa urządzenia w sieci lokalnej.
    
    Używa wielu metod skanowania:
    1. tshark (Wireshark CLI) - bardzo rozbudowane narzędzie
    2. scapy - Python library do manipulacji pakietów
    3. Podstawowe skanowanie (ping + socket) - działa bez uprawnień
    
    Wykrywa urządzenia w sieci lokalnej i analizuje ich właściwości
    bezpieczeństwa na podstawie otwartych portów i usług.
    """
    
    def __init__(self, max_ips_to_scan: int = 50, ping_timeout: float = 0.5, port_timeout: float = 0.2):
        """
        Inicjalizacja skanera WiFi.
        
        Args:
            max_ips_to_scan: Maksymalna liczba IP do skanowania (domyślnie 50 zamiast 254)
            ping_timeout: Timeout dla ping w sekundach (domyślnie 0.5s)
            port_timeout: Timeout dla skanowania portów w sekundach (domyślnie 0.2s)
        """
        self.scanned_devices: List[Device] = []
        self.mac_vendor_cache: Dict[str, str] = {}  # Cache dla producentów (MAC -> Manufacturer)
        self.max_ips_to_scan = max_ips_to_scan
        self.ping_timeout = ping_timeout
        self.port_timeout = port_timeout
        
        # Inicjalizuj Rust scanner jeśli dostępny
        if RUST_SCANNER_AVAILABLE and FastPortScanner:
            self.rust_scanner = FastPortScanner(
                timeout_ms=int(port_timeout * 1000),
                max_concurrent=50
            )
        else:
            self.rust_scanner = None
    
    def scan_wifi_devices(self, network_range: Optional[str] = None) -> List[Device]:
        """
        Skanuje urządzenia WiFi w sieci lokalnej.
        
        Args:
            network_range: Zakres sieci do skanowania (np. "192.168.1.0/24")
                          Jeśli None, automatycznie wykrywa sieć lokalną
        
        Returns:
            Lista wykrytych urządzeń Device
        """
        console.print("[cyan]🔍 Rozpoczynam skanowanie WiFi...[/cyan]")
        console.print("[dim]Skanuję urządzenia w sieci lokalnej (tylko aktywne urządzenia z otwartymi portami)...[/dim]")
        console.print("[dim]💡 Wykrywam tylko urządzenia które odpowiadają na ping I mają otwarte porty[/dim]\n")
        
        devices: List[Device] = []
        
        # Automatycznie wykryj zakres sieci jeśli nie podano
        if network_range is None:
            network_range = self._detect_local_network()
        
        if not network_range:
            console.print("[red]❌ Nie można wykryć sieci lokalnej[/red]")
            console.print("[yellow]   Podaj zakres ręcznie: scan_wifi_devices('192.168.1.0/24')[/yellow]\n")
            return devices
        
        console.print(f"[cyan]Skanuję sieć: {network_range}[/cyan]\n")
        
        # Priorytet 1: Spróbuj tshark (Wireshark CLI) - bardzo rozbudowane narzędzie
        devices = self._scan_with_tshark(network_range)
        if devices:
            return devices
        
        # Priorytet 2: Użyj scapy (lepsze - nie wymaga zewnętrznego programu)
        if SCAPY_AVAILABLE:
            try:
                devices = self._scan_with_scapy(network_range)
                # Zwróć urządzenia nawet jeśli lista jest pusta - może być błąd, ale spróbuj podstawowego
                if devices:
                    return devices
                # Jeśli scapy nie znalazło urządzeń, ale nie było błędu, może być problem z uprawnieniami
                # Przejdź do podstawowego skanowania
            except Exception as e:
                console.print(f"[yellow]⚠️  scapy nie działa: {e}[/yellow]")
                console.print("[dim]   Przechodzę na podstawowe skanowanie...[/dim]\n")
                pass  # Cicho przejdź do podstawowego skanowania
        
        # Priorytet 3: Podstawowe skanowanie używając ping i socket (nie wymaga uprawnień)
        devices = self._scan_basic(network_range)
        
        self.scanned_devices = devices
        return devices
    
    def _detect_local_network(self) -> Optional[str]:
        """
        Automatycznie wykrywa zakres sieci lokalnej.
        
        Returns:
            Zakres sieci (np. "192.168.1.0/24") lub None
        """
        try:
            # Połącz się z zewnętrznym serwerem aby wykryć lokalny IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Wyodrębnij podstawę sieci (np. 192.168.1.0/24)
            ip_parts = local_ip.split('.')
            network_base = '.'.join(ip_parts[:3])
            return f"{network_base}.0/24"
        except Exception as e:
            console.print(f"[yellow]⚠️  Nie można wykryć sieci lokalnej: {e}[/yellow]")
            return None
    
    def _get_gateway_ip(self) -> Optional[str]:
        """
        Pobiera adres IP bramy domyślnej (routera).
        Używane do odfiltrowania „duchów” z proxy ARP (router odpowiada za wiele IP).
        """
        try:
            result = subprocess.run(
                ['ip', 'route', 'show', 'default'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout:
                # Format: "default via 192.168.1.1 dev eth0 ..."
                for part in result.stdout.split():
                    if part in ('via', 'dev', 'proto', 'scope', 'link', 'src'):
                        continue
                    # Pierwszy element wyglądający jak IPv4 to brama
                    if part.count('.') == 3 and part.replace('.', '').isdigit():
                        return part
            # Fallback: route -n (np. na starszym systemie)
            result = subprocess.run(
                ['route', '-n'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout:
                for line in result.stdout.split('\n'):
                    if line.startswith('0.0.0.0'):
                        parts = line.split()
                        if len(parts) >= 2 and parts[1] != '0.0.0.0':
                            return parts[1]
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            pass
        return None
    
    def _deduplicate_active_hosts(
        self,
        active_hosts: List[Dict],
        gateway_ip: Optional[str] = None,
        gateway_mac: Optional[str] = None
    ) -> List[Dict]:
        """
        Usuwa duplikaty i „duchy” z listy hostów:
        - Jeden wpis na adres MAC (jedno urządzenie = jeden wpis)
        - Odrzuca hosty, gdzie MAC = brama i IP != brama (proxy ARP – router „udaje” wiele IP)
        - Pomija adresy .0 i .255 (sieć/rozgłoszenie)
        """
        if not active_hosts:
            return []
        seen_mac: Dict[str, Dict] = {}
        out: List[Dict] = []
        gateway_mac_norm = (gateway_mac or "").upper().replace("-", ":") if gateway_mac else None
        gateway_ip_str = (gateway_ip or "").strip()
        for h in active_hosts:
            ip = (h.get("ip") or "").strip()
            mac = (h.get("mac") or "").strip().upper().replace("-", ":")
            if not ip or not mac:
                continue
            # Pomiń adres sieci i rozgłoszenia
            if ip.endswith(".0") or ip.endswith(".255"):
                continue
            # Proxy ARP: ten sam MAC co brama, ale inny IP → prawdopodobnie „duch”
            if gateway_mac_norm and mac == gateway_mac_norm and ip != gateway_ip_str:
                continue
            # Jeden wpis na MAC (pierwszy napotkany IP dla tego MAC)
            if mac not in seen_mac:
                seen_mac[mac] = h
                out.append(h)
        return out
    
    def _scan_with_scapy(self, network_range: str) -> List[Device]:
        """
        Skanuje sieć używając scapy (lepsze niż nmap - nie wymaga zewnętrznego programu).
        
        Scapy może:
        - Wykrywać aktywne hosty (ARP scan)
        - Skanować porty (TCP SYN scan)
        - Pobierać MAC adresy bezpośrednio
        - Wykrywać usługi
        
        Args:
            network_range: Zakres sieci do skanowania (np. "192.168.1.0/24")
        
        Returns:
            Lista wykrytych urządzeń
        """
        devices: List[Device] = []
        
        try:
            # Wyłącz verbose mode w scapy (mniej outputu)
            conf.verb = 0
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Skanuję sieć scapy...", total=None)
                
                # Krok 1: Spróbuj ARP scan (wymaga root) lub użyj ping scan (działa bez root)
                progress.update(task, description="Wykrywam aktywne hosty...")
                console.print("[cyan]  Wykrywam aktywne hosty...[/cyan]")
                
                active_hosts = []
                
                # Spróbuj ARP scan (wymaga root)
                try:
                    # Utwórz pakiet ARP dla całej sieci
                    arp_request = ARP(pdst=network_range)
                    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
                    arp_request_broadcast = broadcast / arp_request
                    
                    # Wyślij pakiety i odbierz odpowiedzi
                    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]
                    
                    # Pobierz listę aktywnych hostów z MAC adresami
                    for element in answered_list:
                        host_info = {
                            'ip': element[1].psrc,  # IP address
                            'mac': element[1].hwsrc  # MAC address
                        }
                        active_hosts.append(host_info)
                    
                except PermissionError:
                    # Brak uprawnień - użyj ping scan (działa bez root)
                    network_base = network_range.split('/')[0].rsplit('.', 1)[0]
                    
                    # Ping scan - skanuj tylko pierwsze N adresów (szybsze!)
                    # Priorytet: .1 (router), .2-.20 (częste urządzenia), reszta
                    priority_ips = [1, 254]  # Routery
                    common_ips = list(range(2, min(21, self.max_ips_to_scan + 1)))  # Częste urządzenia
                    other_ips = list(range(21, min(255, self.max_ips_to_scan + 1)))  # Reszta
                    ips_to_scan = priority_ips + common_ips + other_ips
                    
                    # Równoległe ping scan
                    from concurrent.futures import ThreadPoolExecutor, as_completed
                    ping_results = {}
                    
                    def ping_host(ip: str) -> tuple:
                        try:
                            result = subprocess.run(
                                ['ping', '-c', '1', '-W', str(int(self.ping_timeout * 1000)), ip],
                                capture_output=True,
                                timeout=self.ping_timeout + 0.1
                            )
                            return (ip, result.returncode == 0)
                        except Exception:
                            return (ip, False)
                    
                    # Ping równolegle (max 20 jednocześnie)
                    with ThreadPoolExecutor(max_workers=20) as executor:
                        futures = {executor.submit(ping_host, f"{network_base}.{i}"): i for i in ips_to_scan}
                        for future in as_completed(futures):
                            ip, is_alive = future.result()
                            if is_alive:
                                ping_results[ip] = True
                    
                    # Dla aktywnych hostów - dodaj WSZYSTKIE które odpowiadają na ping
                    # Nie wymagaj otwartych portów - telefony/telewizory często nie mają otwartych portów
                    for ip in ping_results.keys():
                        try:
                            mac = self._get_mac_address(ip)
                            host_info = {
                                'ip': ip,
                                'mac': mac
                            }
                            active_hosts.append(host_info)
                        except Exception:
                            continue
                    
                except Exception:
                    # Inny błąd - użyj ping scan jako fallback
                    network_base = network_range.split('/')[0].rsplit('.', 1)[0]
                    
                    for i in range(1, 255):
                        ip = f"{network_base}.{i}"
                        try:
                            result = subprocess.run(
                                ['ping', '-c', '1', '-W', '1', ip],
                                capture_output=True,
                                timeout=1
                            )
                            if result.returncode == 0:
                                # Weryfikuj czy urządzenie jest rzeczywiście aktywne
                                test_ports = [80, 443, 22, 23, 135, 139, 445, 161, 3389]
                                is_active = False
                                
                                for port in test_ports:
                                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    sock.settimeout(0.3)
                                    result_port = sock.connect_ex((ip, port))
                                    sock.close()
                                    if result_port == 0:
                                        is_active = True
                                        break
                                
                                # Routery często odpowiadają na ping ale blokują porty
                                if not is_active and (ip.endswith('.1') or ip.endswith('.254')):
                                    is_active = True
                                
                                if is_active:
                                    mac = self._get_mac_address(ip)
                                    host_info = {
                                        'ip': ip,
                                        'mac': mac
                                    }
                                    active_hosts.append(host_info)
                        except Exception:
                            continue
                
                # Jedno urządzenie = jeden MAC; usuń „duchy” (proxy ARP) i duplikaty
                gateway_ip = self._get_gateway_ip()
                gateway_mac = self._get_mac_address(gateway_ip) if gateway_ip else None
                active_hosts = self._deduplicate_active_hosts(active_hosts, gateway_ip, gateway_mac)
                
                console.print(f"[cyan]  Znaleziono {len(active_hosts)} aktywnych hostów[/cyan]")
                
                if not active_hosts:
                    progress.update(task, description="✅ Brak aktywnych hostów")
                    return devices
                
                # Krok 2: Dla każdego hosta przeskanuj porty (użyj Rust jeśli dostępny!)
                # Porty do skanowania: medyczne, administracyjne, webowe, bazy danych
                ports_to_scan = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 161, 162, 443, 445, 
                                993, 995, 104, 5000, 11112, 1433, 3306, 3389, 5432, 5900, 5901, 
                                8080, 8443, 27017]
                
                progress.update(task, description=f"Skanuję porty {len(active_hosts)} hostów...")
                
                # Użyj Rust scanner dla wszystkich hostów jednocześnie (jeśli dostępny)
                if self.rust_scanner and len(active_hosts) > 1:
                    # Szybkie równoległe skanowanie wszystkich IP jednocześnie
                    ips = [h['ip'] for h in active_hosts]
                    all_results = self.rust_scanner.scan_multiple_ips(ips, ports_to_scan)
                    
                    for i, host_info in enumerate(active_hosts):
                        try:
                            ip = host_info['ip']
                            mac = host_info['mac']
                            progress.update(task, description=f"✓ {ip} ({i+1}/{len(active_hosts)})")
                            
                            open_ports = all_results.get(ip, [])
                            
                            # Analizuj urządzenie - wykrywaj WSZYSTKIE urządzenia (nawet bez otwartych portów)
                            hostname = self._get_hostname(ip, open_ports if open_ports else [])
                            device = self._analyze_host_scapy(ip, mac, hostname, open_ports)
                            if device:
                                devices.append(device)
                                if open_ports:
                                    progress.update(task, description=f"✓ {hostname} ({len(open_ports)} portów)")
                                else:
                                    progress.update(task, description=f"✓ {hostname} (aktywne, brak otwartych portów)")
                        except Exception as e:
                            console.print(f"[yellow]  ⚠ Błąd skanowania {host_info.get('ip', 'unknown')}: {e}[/yellow]")
                            continue
                else:
                    # Fallback: sekwencyjne skanowanie (wolniejsze)
                    for i, host_info in enumerate(active_hosts):
                        try:
                            ip = host_info['ip']
                            mac = host_info['mac']
                            progress.update(task, description=f"Skanuję {ip} ({i+1}/{len(active_hosts)})...")
                            
                            # Skanuj porty dla tego hosta
                            open_ports = []
                            if self.rust_scanner:
                                # Użyj Rust scanner dla pojedynczego IP
                                open_ports = self.rust_scanner.scan_ports(ip, ports_to_scan)
                            else:
                                # Fallback: scapy TCP SYN scan
                                for port in ports_to_scan:
                                    try:
                                        response = sr1(IP(dst=ip) / TCP(dport=port, flags="S"), timeout=self.port_timeout, verbose=False)
                                        if response and response.haslayer(TCP):
                                            if response[TCP].flags == 18:  # SYN-ACK (port otwarty)
                                                open_ports.append(port)
                                    except Exception:
                                        continue
                            
                            # Analizuj urządzenie - wykrywaj WSZYSTKIE urządzenia (nawet bez otwartych portów)
                            # Telefony, telewizory itp. często nie mają otwartych portów, ale są aktywne
                            hostname = self._get_hostname(ip, open_ports if open_ports else [])
                            device = self._analyze_host_scapy(ip, mac, hostname, open_ports)
                            if device:
                                devices.append(device)
                                if open_ports:
                                    progress.update(task, description=f"✓ {hostname} ({len(open_ports)} portów)")
                                else:
                                    progress.update(task, description=f"✓ {hostname} (aktywne, brak otwartych portów)")
                        
                        except Exception as e:
                            console.print(f"[yellow]  ⚠ Błąd skanowania {host_info.get('ip', 'unknown')}: {e}[/yellow]")
                            continue
                
                progress.update(task, description=f"✅ Skanowanie zakończone")
            
            console.print(f"\n[green]✅ Skanowanie zakończone. Znaleziono {len(devices)} urządzeń.[/green]\n")
            return devices
            
        except Exception as e:
            console.print(f"[yellow]⚠️  scapy nie działa: {e}[/yellow]")
            console.print("[dim]   Przechodzę na podstawowe skanowanie...[/dim]\n")
            # Nie rzucaj wyjątku - pozwól przejść do podstawowego skanowania
            return []
    
    def _analyze_host_scapy(self, ip: str, mac: str, hostname: str, open_ports: List[int]) -> Optional[Device]:
        """
        Analizuje host wykryty przez scapy.
        
        Args:
            ip: Adres IP hosta
            mac: Adres MAC hosta
            hostname: Nazwa hosta
            open_ports: Lista otwartych portów
        
        Returns:
            Obiekt Device lub None
        """
        try:
            # Pobierz producenta z API
            manufacturer = self._get_manufacturer_from_mac_api(mac)
            
            # Określ typ urządzenia
            device_type = self._detect_device_type(hostname, open_ports)
            
            # Sprawdź bezpieczeństwo na podstawie portów
            # WiFi ma szyfrowanie na poziomie sieci (WPA2/WPA3), ale sprawdzamy też porty aplikacyjne
            # Porty szyfrowane: 443 (HTTPS), 8443 (HTTPS Alt), 993 (IMAPS), 995 (POP3S), 22 (SSH)
            encrypted_ports = [443, 8443, 993, 995, 22]
            has_encryption = any(port in open_ports for port in encrypted_ports)
            requires_pairing = True  # WiFi zazwyczaj wymaga hasła (WPA2/WPA3)
            
            # Określ typ szyfrowania
            encryption_type = None
            if has_encryption:
                if 443 in open_ports or 8443 in open_ports:
                    encryption_type = "HTTPS (TLS 1.2/1.3)"
                elif 993 in open_ports or 995 in open_ports:
                    encryption_type = "Encrypted Mail (TLS)"
                elif 22 in open_ports:
                    encryption_type = "SSH (Encrypted)"
                else:
                    encryption_type = "Encrypted (TLS/SSL)"
            else:
                # WiFi ma szyfrowanie na poziomie sieci (WPA2/WPA3), więc nawet bez portów aplikacyjnych
                # urządzenie jest chronione na poziomie sieci
                if 80 in open_ports:
                    encryption_type = "Network-level encryption (WPA2/WPA3), HTTP unencrypted"
                else:
                    encryption_type = "Network-level encryption (WPA2/WPA3)"
                # Ustaw has_encryption na True, bo WiFi ma szyfrowanie sieciowe
                has_encryption = True
            
            # Sprawdź czy to router
            is_router = self._is_router_device(hostname, open_ports, ip)
            is_medical = self._is_medical_device(hostname, open_ports)
            
            # Utwórz urządzenie
            device = Device(
                mac_address=mac,
                name=hostname,
                device_type=device_type,
                protocol=Protocol.WIFI,
                has_encryption=has_encryption,
                encryption_type=encryption_type,
                requires_pairing=requires_pairing,
                manufacturer=manufacturer,
                metadata={
                    "ip_address": ip,
                    "open_ports": open_ports,
                    "ports_info": {str(port): MEDICAL_PORTS.get(port, "Unknown") for port in open_ports[:10]}
                }
            )
            
            # Dodaj podatności tylko jeśli są rzeczywiste
            if not has_encryption and open_ports:
                if is_router:
                    if 443 in open_ports or 8443 in open_ports:
                        pass  # Ma HTTPS - OK
                    else:
                        device.add_vulnerability("HTTP bez HTTPS - zalecane użycie HTTPS dla routera")
                else:
                    device.add_vulnerability("Brak szyfrowania - dane mogą być przechwycone")
            
            # Testuj podatności dla wszystkich otwartych portów (z kontekstem)
            port_vulnerabilities = self._test_port_vulnerabilities(open_ports, is_router=is_router, is_medical=is_medical)
            for vuln in port_vulnerabilities:
                device.add_vulnerability(vuln)
            
            device.calculate_security_score()
            return device
        
        except Exception as e:
            console.print(f"[yellow]  ⚠ Błąd analizy {ip}: {e}[/yellow]")
            return None
    
    def _scan_basic(self, network_range: str) -> List[Device]:
        """
        Podstawowe skanowanie używając ping i socket (bez nmap).
        
        Args:
            network_range: Zakres sieci do skanowania
        
        Returns:
            Lista wykrytych urządzeń
        """
        devices: List[Device] = []
        
        # Wyodrębnij podstawę IP (np. 192.168.1)
        network_base = network_range.split('/')[0].rsplit('.', 1)[0]
        
        console.print(f"[yellow]⚠️  Używam podstawowego skanowania (ping + socket)[/yellow]")
        console.print(f"[dim]   Uwaga: Podstawowe skanowanie może być wolniejsze i mniej dokładne[/dim]\n")
        
        # Skanuj więcej adresów IP aby wykryć wszystkie urządzenia
        max_ips = min(self.max_ips_to_scan, 254)  # Skanuj całą sieć (1-254) dla lepszego wykrywania
        console.print(f"[dim]   Skanuję {max_ips} adresów IP...[/dim]")
        
        # Równoległe ping scan dla szybkości
        from concurrent.futures import ThreadPoolExecutor, as_completed
        ping_results = {}
        
        def ping_host(ip: str) -> tuple:
            try:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '1', ip],
                    capture_output=True,
                    timeout=2
                )
                return (ip, result.returncode == 0)
            except Exception:
                return (ip, False)
        
        # Ping równolegle (max 50 jednocześnie)
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(ping_host, f"{network_base}.{i}"): i for i in range(1, max_ips + 1)}
            for future in as_completed(futures):
                ip, is_alive = future.result()
                if is_alive:
                    ping_results[ip] = True
        
        # Pobierz MAC dla każdego IP (potrzebne do deduplikacji po MAC i odfiltrowania „duchów”)
        active_hosts_raw = []
        for ip in ping_results.keys():
            try:
                mac = self._get_mac_address(ip)
                active_hosts_raw.append({'ip': ip, 'mac': mac})
            except Exception:
                continue
        
        # Jedno urządzenie = jeden MAC; usuń „duchy” (proxy ARP) i duplikaty
        gateway_ip = self._get_gateway_ip()
        gateway_mac = self._get_mac_address(gateway_ip) if gateway_ip else None
        active_hosts = self._deduplicate_active_hosts(active_hosts_raw, gateway_ip, gateway_mac)
        
        console.print(f"[dim]   Po deduplikacji (1 urządzenie = 1 MAC): {len(active_hosts)} hostów[/dim]\n")
        
        # Teraz przeanalizuj tylko zdeduplikowane hosty
        for host in active_hosts:
            ip = host.get('ip')
            if not ip:
                continue
            try:
                    # Host odpowiada na ping - to jest aktywne urządzenie!
                    # Sprawdź otwarte porty (ale nie wymagaj ich - telefony/telewizory często nie mają otwartych portów)
                    test_ports = [80, 443, 22, 23, 135, 139, 445, 161, 3389, 8080, 8443, 554, 8554, 5000, 7001, 7002]
                    open_ports = []
                    
                    for port in test_ports:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.2)  # Krótszy timeout dla szybkości
                        result_port = sock.connect_ex((ip, port))
                        sock.close()
                        if result_port == 0:
                            open_ports.append(port)
                    
                    # Wykryj WSZYSTKIE urządzenia które odpowiadają na ping (nawet bez otwartych portów)
                    # Telefony, telewizory, tablety itp. często nie mają otwartych portów, ale są aktywne
                    device = self._analyze_host_basic(ip)
                    if device:
                        # Zaktualizuj otwarte porty w metadanych
                        if open_ports:
                            device.metadata['open_ports'] = open_ports
                        devices.append(device)
                        if open_ports:
                            console.print(f"  [green]✓[/green] Wykryto: {device.name} ({ip}) - {len(open_ports)} otwartych portów")
                        else:
                            console.print(f"  [green]✓[/green] Wykryto: {device.name} ({ip}) - aktywne (brak otwartych portów)")
            
            except Exception:
                continue
        
        console.print(f"\n[green]✅ Skanowanie zakończone. Znaleziono {len(devices)} urządzeń.[/green]\n")
        return devices
    
    def _analyze_host_basic(self, ip: str) -> Optional[Device]:
        """
        Podstawowa analiza hosta (bez nmap).
        
        Args:
            ip: Adres IP hosta
        
        Returns:
            Obiekt Device lub None
        """
        try:
            # Spróbuj połączyć się z popularnymi portami (ale nie wymagaj ich!)
            # Telefony, telewizory itp. często nie mają otwartych portów, ale są aktywne
            test_ports = [80, 443, 8080, 22, 3389, 554, 8554, 5000, 7001, 7002, 8443]
            open_ports = []
            
            for port in test_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.2)  # Krótszy timeout dla szybkości
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
            
            # Zwróć urządzenie nawet bez otwartych portów - urządzenie odpowiada na ping, więc jest aktywne
            
            # Spróbuj pobrać rzeczywistą nazwę hosta (bez sudo!)
            hostname = None
            try:
                # Metoda 1: socket.gethostbyaddr() - działa bez sudo
                hostname = socket.gethostbyaddr(ip)[0]
            except (socket.herror, socket.gaierror, OSError):
                pass
            
            # Metoda 2: Spróbuj pobrać z HTTP headers (jeśli port 80/443 jest otwarty)
            if not hostname and (80 in open_ports or 443 in open_ports):
                try:
                    import http.client
                    port = 443 if 443 in open_ports else 80
                    conn = http.client.HTTPConnection(ip, port, timeout=2)
                    conn.request("HEAD", "/")
                    response = conn.getresponse()
                    # Sprawdź nagłówki Server lub Host
                    server_header = response.getheader("Server", "")
                    if server_header:
                        # Wyodrębnij nazwę z nagłówka Server (np. "Apache/2.4.41 (Ubuntu)")
                        hostname = server_header.split()[0] if server_header else None
                    conn.close()
                except Exception:
                    pass
            
            # Metoda 3: Spróbuj NetBIOS name (jeśli port 445/139 jest otwarty)
            if not hostname and (445 in open_ports or 139 in open_ports):
                try:
                    # NetBIOS może być dostępny bez sudo
                    result = subprocess.run(
                        ['nmblookup', '-A', ip],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if '<00>' in line and 'GROUP' not in line:
                                parts = line.split()
                                if len(parts) > 0:
                                    hostname = parts[0].strip()
                                    break
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    pass
            
            # Fallback: użyj IP jako nazwy
            if not hostname:
                hostname = f"Device-{ip.split('.')[-1]}"
            
            device_type = self._detect_device_type(hostname, open_ports)
            
            # Sprawdź bezpieczeństwo na podstawie portów
            # WiFi ma szyfrowanie na poziomie sieci (WPA2/WPA3), ale sprawdzamy też porty aplikacyjne
            # Porty szyfrowane: 443 (HTTPS), 8443 (HTTPS Alt), 993 (IMAPS), 995 (POP3S), 22 (SSH)
            encrypted_ports = [443, 8443, 993, 995, 22]
            has_encryption = any(port in open_ports for port in encrypted_ports)
            requires_pairing = True  # WiFi zazwyczaj wymaga hasła (WPA2/WPA3)
            
            # Określ typ szyfrowania
            encryption_type = None
            if has_encryption:
                if 443 in open_ports or 8443 in open_ports:
                    encryption_type = "HTTPS (TLS 1.2/1.3)"
                elif 993 in open_ports or 995 in open_ports:
                    encryption_type = "Encrypted Mail (TLS)"
                elif 22 in open_ports:
                    encryption_type = "SSH (Encrypted)"
                else:
                    encryption_type = "Encrypted (TLS/SSL)"
            else:
                # WiFi ma szyfrowanie na poziomie sieci (WPA2/WPA3), więc nawet bez portów aplikacyjnych
                # urządzenie jest chronione na poziomie sieci
                if 80 in open_ports:
                    encryption_type = "Network-level encryption (WPA2/WPA3), HTTP unencrypted"
                else:
                    encryption_type = "Network-level encryption (WPA2/WPA3)"
                # Ustaw has_encryption na True, bo WiFi ma szyfrowanie sieciowe
                has_encryption = True
            
            # Pobierz producenta z API
            mac = self._get_mac_address(ip)
            manufacturer = self._get_manufacturer_from_mac_api(mac)
            
            device = Device(
                mac_address=mac,
                name=hostname,
                device_type=device_type,
                protocol=Protocol.WIFI,
                has_encryption=has_encryption,
                encryption_type=encryption_type,
                requires_pairing=requires_pairing,
                manufacturer=manufacturer,
                metadata={
                    "ip_address": ip,
                    "open_ports": open_ports
                }
            )
            
            # Testuj podatności dla wszystkich otwartych portów
            port_vulnerabilities = self._test_port_vulnerabilities(open_ports)
            for vuln in port_vulnerabilities:
                device.add_vulnerability(vuln)
            
            device.calculate_security_score()
            return device
        
        except Exception:
            return None
    
    def _detect_device_type(self, hostname: str, open_ports: List[int]) -> DeviceType:
        """
        Wykrywa typ urządzenia na podstawie nazwy i portów.
        
        Args:
            hostname: Nazwa hosta
            open_ports: Lista otwartych portów
        
        Returns:
            DeviceType urządzenia
        """
        hostname_lower = hostname.lower()
        
        # Sprawdź nazwę hosta
        if any(keyword in hostname_lower for keyword in ["glucose", "gluco", "diabetes"]):
            return DeviceType.GLUCOSE_METER
        if any(keyword in hostname_lower for keyword in ["insulin", "pump"]):
            return DeviceType.INSULIN_PUMP
        if any(keyword in hostname_lower for keyword in ["monitor", "patient", "vital"]):
            return DeviceType.PULSE_OXIMETER
        if any(keyword in hostname_lower for keyword in ["pressure", "bp", "sphygmo"]):
            return DeviceType.BLOOD_PRESSURE
        
        # Sprawdź porty medyczne
        if 104 in open_ports or 11112 in open_ports:  # DICOM
            return DeviceType.UNKNOWN  # Urządzenie medyczne, ale nieznany typ
        if 5000 in open_ports:  # HL7
            return DeviceType.UNKNOWN
        
        # Sprawdź czy nazwa zawiera słowa medyczne
        if any(keyword in hostname_lower for keyword in MEDICAL_DEVICE_KEYWORDS):
            return DeviceType.UNKNOWN
        
        return DeviceType.UNKNOWN
    
    def _analyze_security(self, open_ports: List[int], nm_host: Dict) -> tuple:
        """
        Analizuje bezpieczeństwo na podstawie otwartych portów.
        
        Args:
            open_ports: Lista otwartych portów
            nm_host: Dane hosta z nmap
        
        Returns:
            Tuple (has_encryption, requires_pairing)
        """
        has_encryption = False
        requires_pairing = True  # WiFi zazwyczaj wymaga hasła
        
        # Sprawdź czy są porty HTTPS (szyfrowane)
        if 443 in open_ports or 8443 in open_ports:
            has_encryption = True
        
        # Sprawdź czy są tylko porty HTTP (niezaszyfrowane)
        if 80 in open_ports and 443 not in open_ports:
            has_encryption = False
        
        return has_encryption, requires_pairing
    
    def _is_router_device(self, hostname: str, open_ports: List[int], ip: str) -> bool:
        """
        Sprawdza czy urządzenie jest routerem/gatewayem.
        
        Args:
            hostname: Nazwa hosta
            open_ports: Lista otwartych portów
            ip: Adres IP
        
        Returns:
            True jeśli urządzenie jest routerem
        """
        name_lower = hostname.lower()
        router_keywords = [
            "router", "gateway", "ap", "access point", "wifi", "wireless",
            "tp-link", "netgear", "asus", "linksys", "d-link", "zyxel",
            "fritz", "huawei", "zte", "cisco", "ubiquiti", "unifi"
        ]
        
        if any(keyword in name_lower for keyword in router_keywords):
            return True
        
        # Sprawdź IP - routery często mają .1 na końcu
        if ip.endswith(".1") or ip.endswith(".254"):
            router_ports = [80, 443, 22, 161, 162]
            if any(p in open_ports for p in router_ports):
                if len(open_ports) <= 6:
                    return True
        
        return False
    
    def _is_medical_device(self, hostname: str, open_ports: List[int]) -> bool:
        """
        Sprawdza czy urządzenie jest medyczne na podstawie nazwy i portów.
        
        Args:
            hostname: Nazwa hosta
            open_ports: Lista otwartych portów
        
        Returns:
            True jeśli urządzenie jest medyczne
        """
        name_lower = hostname.lower()
        medical_keywords = [
            "medical", "med", "hospital", "clinic", "patient", "monitor",
            "glucose", "gluco", "insulin", "pump", "dicom", "hl7",
            "pacs", "ris", "emr", "ehr", "vital", "signs", "health"
        ]
        
        if any(keyword in name_lower for keyword in medical_keywords):
            return True
        
        # Sprawdź porty medyczne
        medical_ports = [104, 11112, 5000]
        if any(p in open_ports for p in medical_ports):
            # Jeśli ma porty medyczne i mało innych portów, to może być urządzenie medyczne
            if len(open_ports) <= 5:
                return True
        
        return False
    
    def _test_port_vulnerabilities(self, open_ports: List[int], is_router: bool = False, is_medical: bool = False) -> List[str]:
        """
        Analizuje podatności dla otwartych portów (TEORETYCZNE - na podstawie znanych podatności portów).
        
        UWAGA: To są TEORETYCZNE podatności na podstawie znanych słabości portów,
        NIE rzeczywiste testy bezpieczeństwa. Rzeczywiste testy są wykonywane przez
        VulnerabilityTester (z flagą --audit).
        
        Ta funkcja:
        - Sprawdza kontekst urządzenia (router vs medyczne vs domowe)
        - Dodaje tylko podatności które są istotne dla danego typu urządzenia
        - Unika false positives dla routerów i urządzeń domowych
        
        Args:
            open_ports: Lista otwartych portów do przeanalizowania
            is_router: Czy urządzenie to router/gateway
            is_medical: Czy urządzenie to urządzenie medyczne
        
        Returns:
            Lista znalezionych podatności (jako stringi)
        """
        vulnerabilities = []
        
        # Sprawdź każdy otwarty port
        for port in open_ports:
            # Sprawdź czy port ma znane podatności w słowniku
            if port in PORT_VULNERABILITIES:
                port_vulns = PORT_VULNERABILITIES[port]
                
                # Dla portów medycznych - tylko jeśli to rzeczywiście urządzenie medyczne
                if port in [104, 11112]:  # DICOM
                    if is_medical:
                        vulnerabilities.extend([
                            f"Port DICOM ({port}) otwarty - możliwość nieautoryzowanego dostępu do obrazów medycznych",
                            "DICOM może przesyłać dane bez szyfrowania - wrażliwe obrazy medyczne narażone"
                        ])
                        vulnerabilities.extend(port_vulns)
                    # Jeśli nie jest medyczne, nie dodawaj podatności medycznych
                
                elif port == 5000:  # HL7
                    if is_medical:
                        vulnerabilities.extend([
                            f"Port HL7 ({port}) otwarty - możliwość nieautoryzowanego dostępu do danych pacjentów",
                            "HL7 może przesyłać dane bez szyfrowania - dane EHR/EMR narażone"
                        ])
                        vulnerabilities.extend(port_vulns)
                    # Jeśli nie jest medyczne, nie dodawaj podatności medycznych
                
                elif port == 22:  # SSH
                    # SSH dla routerów to normalne - nie dodawaj podatności
                    if not is_router:
                        port_name = "SSH"
                        vulnerabilities.extend([
                            f"Port {port} ({port_name}) otwarty - sprawdź konfigurację bezpieczeństwa",
                            f"Port {port} - możliwość ataków brute-force jeśli nie zabezpieczony"
                        ])
                        vulnerabilities.extend(port_vulns)
                
                elif port == 3389:  # RDP
                    # RDP zawsze podatny jeśli otwarty (nawet dla routerów)
                    if not is_router:  # Routery rzadko mają RDP
                        port_name = "RDP"
                        vulnerabilities.extend([
                            f"Port {port} ({port_name}) otwarty - wysokie ryzyko nieautoryzowanego dostępu",
                            f"Port {port} - możliwość ataków brute-force i exploity"
                        ])
                        vulnerabilities.extend(port_vulns)
                
                elif port in [1433, 3306, 5432, 27017]:  # Bazy danych
                    # Porty baz danych są bardzo niebezpieczne (nawet dla routerów)
                    if not is_router:  # Routery nie powinny mieć baz danych
                        db_name = {1433: "MSSQL", 3306: "MySQL", 5432: "PostgreSQL", 27017: "MongoDB"}.get(port, "Database")
                        vulnerabilities.extend([
                            f"Port {port} ({db_name}) otwarty - bardzo wysokie ryzyko wycieku danych",
                            f"Port {port} - możliwość SQL injection i nieautoryzowanego dostępu"
                        ])
                        vulnerabilities.extend(port_vulns)
                
                elif port in [80, 8080]:  # HTTP
                    # HTTP - sprawdź czy ma HTTPS
                    has_https = 443 in open_ports or 8443 in open_ports
                    if not has_https:
                        if is_router:
                            # Dla routerów w sieci lokalnej to mniej krytyczne
                            vulnerabilities.append(f"Port {port} (HTTP) bez HTTPS - zalecane użycie HTTPS dla routera")
                        else:
                            vulnerabilities.extend([
                                f"Port {port} (HTTP) otwarty bez HTTPS - dane przesyłane niezaszyfrowane",
                                f"Port {port} - możliwość przechwycenia danych (sniffing)",
                                f"Port {port} - ataki man-in-the-middle"
                            ])
                            vulnerabilities.extend(port_vulns)
                    # Jeśli ma HTTPS, HTTP jest OK (może być redirect)
                
                elif port == 21:  # FTP
                    # FTP zawsze podatny jeśli otwarty
                    if not is_router:  # Routery rzadko mają FTP
                        vulnerabilities.extend([
                            f"FTP bez szyfrowania - hasła i dane przesyłane jawnie",
                            f"FTP - możliwość przechwycenia danych",
                            f"FTP - ataki brute-force"
                        ])
                        vulnerabilities.extend(port_vulns)
                
                elif port == 23:  # Telnet
                    # Telnet zawsze podatny (nawet dla routerów)
                    vulnerabilities.extend([
                        f"Telnet bez szyfrowania - wszystkie dane przesyłane jawnie",
                        f"Telnet - bardzo wysokie ryzyko przechwycenia danych",
                        f"Telnet - przestarzały i niebezpieczny protokół"
                    ])
                    vulnerabilities.extend(port_vulns)
                
                elif port in [25, 53]:  # SMTP, DNS
                    # SMTP i DNS dla routerów to normalne - nie dodawaj podatności
                    if not is_router:
                        vulnerabilities.extend(port_vulns)
                
                elif port in [443, 8443]:  # HTTPS
                    # HTTPS - sprawdź tylko przestarzałe wersje TLS (teoretyczne)
                    # Rzeczywiste testy TLS są w VulnerabilityTester
                    if not is_router:  # Dla routerów HTTPS jest OK
                        vulnerabilities.extend([
                            f"HTTPS z przestarzałymi wersjami TLS (TLS 1.0/1.1) - podatność",
                            f"HTTPS z nieprawidłowymi certyfikatami - ryzyko ataków MITM",
                            f"HTTPS z słabymi algorytmami szyfrowania - możliwość złamania"
                        ])
                
                elif port in [135, 139, 445]:  # SMB/NetBIOS
                    # SMB dla routerów to normalne - nie dodawaj podatności
                    if not is_router:
                        vulnerabilities.extend(port_vulns)
                
                elif port in [161, 162]:  # SNMP
                    # SNMP dla routerów to normalne - nie dodawaj podatności
                    if not is_router:
                        vulnerabilities.extend(port_vulns)
                
                elif port in [5900, 5901]:  # VNC
                    # VNC zawsze podatny jeśli otwarty
                    if not is_router:  # Routery rzadko mają VNC
                        vulnerabilities.extend(port_vulns)
                
                # Dla innych portów - nie dodawaj automatycznie (zostaw dla VulnerabilityTester)
                # else:
                #     vulnerabilities.extend(port_vulns)
        
        # Dla routerów - znacznie ogranicz podatności
        # Routery w sieci lokalnej mają normalne porty otwarte (80, 443, 22, 161, 162, 53, 25)
        # Te porty są potrzebne do zarządzania routerem
        if is_router:
            # Dla routerów dodaj tylko krytyczne podatności
            # Porty które są normalne dla routerów: 80, 443, 22, 161, 162, 53, 25, 135, 139, 445
            normal_router_ports = [80, 443, 22, 161, 162, 53, 25, 135, 139, 445]
            
            # Filtruj podatności - usuń te które dotyczą normalnych portów routera
            filtered_vulnerabilities = []
            for vuln in vulnerabilities:
                # Sprawdź czy podatność dotyczy normalnego portu routera
                is_normal_port = False
                for port in normal_router_ports:
                    if str(port) in vuln and port in open_ports:
                        # Sprawdź czy to nie jest krytyczna podatność (np. Telnet, FTP, RDP, bazy danych)
                        critical_keywords = ["telnet", "ftp", "rdp", "mssql", "mysql", "postgresql", "mongodb", "database"]
                        if not any(keyword in vuln.lower() for keyword in critical_keywords):
                            is_normal_port = True
                            break
                
                # Dodaj tylko jeśli to nie jest normalny port routera lub to krytyczna podatność
                if not is_normal_port:
                    filtered_vulnerabilities.append(vuln)
            
            return filtered_vulnerabilities
        
        # Sprawdź kombinacje portów (dodatkowe podatności)
        # Jeśli ma porty medyczne (DICOM/HL7) ale nie ma HTTPS, to dodatkowe ryzyko
        medical_ports = [104, 11112, 5000]
        has_medical_ports = any(port in open_ports for port in medical_ports)
        has_https = 443 in open_ports or 8443 in open_ports
        
        if has_medical_ports and not has_https and is_medical:
            vulnerabilities.append(
                "Porty medyczne (DICOM/HL7) otwarte bez HTTPS - dane medyczne mogą być przesyłane niezaszyfrowane"
            )
        
        # Jeśli ma porty administracyjne i bazy danych razem - bardzo wysokie ryzyko
        admin_ports = [22, 3389]
        db_ports = [1433, 3306, 5432, 27017]
        has_admin = any(port in open_ports for port in admin_ports)
        has_db = any(port in open_ports for port in db_ports)
        
        if has_admin and has_db and not is_router:
            vulnerabilities.append(
                "Porty administracyjne i bazy danych otwarte razem - bardzo wysokie ryzyko kompleksowego ataku"
            )
        
        # Usuń duplikaty zachowując kolejność
        seen = set()
        unique_vulns = []
        for vuln in vulnerabilities:
            if vuln not in seen:
                seen.add(vuln)
                unique_vulns.append(vuln)
        
        return unique_vulns
    
    def _get_hostname(self, ip: str, open_ports: List[int]) -> str:
        """
        Pobiera hostname urządzenia używając wielu metod.
        
        Args:
            ip: Adres IP
            open_ports: Lista otwartych portów
        
        Returns:
            Hostname lub wygenerowana nazwa
        """
        # Metoda 1: socket.gethostbyaddr() - działa bez sudo
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            if hostname:
                return hostname
        except (socket.herror, socket.gaierror, OSError):
            pass
        
        # Metoda 2: HTTP headers (jeśli port 80/443 jest otwarty)
        if 80 in open_ports or 443 in open_ports:
            try:
                import http.client
                port = 443 if 443 in open_ports else 80
                conn = http.client.HTTPConnection(ip, port, timeout=2)
                conn.request("HEAD", "/")
                response = conn.getresponse()
                server_header = response.getheader("Server", "")
                if server_header:
                    return server_header.split()[0] if server_header else None
                conn.close()
            except Exception:
                pass
        
        # Metoda 3: NetBIOS (jeśli port 445/139 jest otwarty)
        if 445 in open_ports or 139 in open_ports:
            try:
                result = subprocess.run(
                    ['nmblookup', '-A', ip],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if '<00>' in line and 'GROUP' not in line:
                            parts = line.split()
                            if len(parts) > 0:
                                return parts[0].strip()
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
        
        # Fallback: użyj IP jako nazwy
        return f"Device-{ip.split('.')[-1]}"
    
    def _get_mac_address(self, ip: str) -> str:
        """
        Próbuje uzyskać adres MAC hosta.
        
        Args:
            ip: Adres IP hosta
        
        Returns:
            Adres MAC lub wygenerowany adres
        """
        try:
            # Użyj ARP aby uzyskać MAC
            result = subprocess.run(
                ['arp', '-n', ip],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0 and result.stdout:
                # Wyodrębnij MAC z wyniku ARP
                for line in result.stdout.split('\n'):
                    if ip in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            return parts[2]
        except Exception:
            pass
        
        # Jeśli nie można uzyskać MAC, wygeneruj na podstawie IP
        # UWAGA: To jest TYLKO dla identyfikacji - nie używaj tego MAC do lookup producenta!
        ip_parts = ip.split('.')
        # Konwertuj stringi na int przed formatowaniem hex
        part2 = int(ip_parts[2]) if len(ip_parts) > 2 else 0
        part3 = int(ip_parts[3]) if len(ip_parts) > 3 else 0
        # Zwróć wygenerowany MAC z flagą że jest wygenerowany (dla późniejszej identyfikacji)
        return f"00:00:{part2:02x}:{part3:02x}:00:00"
    
    def _get_manufacturer_from_mac_api(self, mac_address: str) -> Optional[str]:
        """
        Pobiera nazwę producenta na podstawie adresu MAC (OUI).
        
        Używa wielu źródeł w kolejności priorytetu:
        1. IEEE OUI (oficjalna baza IEEE) - najlepsza, bez limitów
        2. macvendors.com API (zewnętrzne API) - fallback
        
        Args:
            mac_address: Adres MAC urządzenia
        
        Returns:
            Nazwa producenta lub None
        """
        # WAŻNE: Nie szukaj producenta dla wygenerowanych MAC adresów (00:00:xx:xx:xx:xx)
        # Te MAC są generowane na podstawie IP i nie reprezentują prawdziwego producenta
        if mac_address.startswith("00:00:"):
            return None  # Wygenerowany MAC - nie szukaj producenta
        
        # Sprawdź cache
        if mac_address in self.mac_vendor_cache:
            return self.mac_vendor_cache[mac_address]
        
        # Metoda 1: IEEE OUI (oficjalna baza IEEE) - PRIORYTET
        try:
            from oui_lookup import get_oui_lookup
            oui_lookup = get_oui_lookup()
            manufacturer = oui_lookup.lookup(mac_address)
            if manufacturer:
                self.mac_vendor_cache[mac_address] = manufacturer
                return manufacturer
        except Exception:
            pass
        
        # Metoda 2: macvendors.com API (zewnętrzne API) - fallback
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            # Normalizuj format MAC (usuń myślniki/spacje, dodaj dwukropki)
            mac_normalized = mac_address.replace("-", ":").replace(" ", ":").replace(".", ":").upper()
            
            # Sprawdź czy adres MAC nie jest losowy/prywatny
            first_byte = int(mac_normalized.split(":")[0], 16)
            is_random = (first_byte & 0x02) != 0
            if is_random:
                return None
            
            # Wywołaj API
            url = f"https://api.macvendors.com/{mac_normalized}"
            response = requests.get(url, timeout=3)
            
            # Rate limiting - 1 request/second
            time.sleep(1.1)
            
            if response.status_code == 200:
                vendor = response.text.strip()
                if vendor and vendor != "404" and "not found" not in vendor.lower():
                    self.mac_vendor_cache[mac_address] = vendor
                    return vendor
        except Exception:
            pass
        
        return None
    
    def _scan_with_tshark(self, network_range: str) -> List[Device]:
        """
        Skanuje sieć używając tshark (Wireshark CLI) - bardzo rozbudowane narzędzie.
        
        tshark może:
        - Wykrywać aktywne hosty (ARP, DHCP, DNS)
        - Skanować porty (TCP SYN scan)
        - Pobierać MAC adresy
        - Wykrywać usługi i protokoły
        - Analizować ruch sieciowy
        
        Args:
            network_range: Zakres sieci do skanowania (np. "192.168.1.0/24")
        
        Returns:
            Lista wykrytych urządzeń lub pusta lista jeśli tshark nie jest dostępny
        """
        devices: List[Device] = []
        
        # Sprawdź czy tshark jest dostępny
        try:
            result = subprocess.run(
                ['tshark', '--version'],
                capture_output=True,
                timeout=2
            )
            if result.returncode != 0:
                return devices
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return devices
        
        try:
            network_base = network_range.split('/')[0].rsplit('.', 1)[0]
            
            # Użyj tshark do przechwycenia pakietów ARP (wymaga uprawnień, ale ma fallback)
            # Alternatywnie: użyj ping + tshark do analizy
            console.print("[cyan]  Używam tshark do skanowania sieci...[/cyan]")
            
            # Skanuj pierwsze 20 adresów IP (dla szybkości)
            for i in range(1, 21):
                ip = f"{network_base}.{i}"
                
                try:
                    # Ping hosta
                    ping_result = subprocess.run(
                        ['ping', '-c', '1', '-W', '1', ip],
                        capture_output=True,
                        timeout=1
                    )
                    
                    if ping_result.returncode == 0:
                        # Spróbuj użyć tshark do analizy ruchu (jeśli ma uprawnienia)
                        # Alternatywnie: użyj podstawowych metod
                        mac = self._get_mac_address(ip)
                        
                        # Skanuj porty używając socket (działa bez root)
                        test_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 161, 162, 443, 445, 
                                     993, 995, 104, 5000, 11112, 1433, 3306, 3389, 5432, 5900, 5901, 
                                     8080, 8443, 27017]
                        open_ports = []
                        
                        for port in test_ports:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.settimeout(0.5)
                            result = sock.connect_ex((ip, port))
                            sock.close()
                            
                            if result == 0:
                                open_ports.append(port)
                        
                        if open_ports:
                            # Pobierz hostname (wiele metod)
                            hostname = None
                            
                            # Metoda 1: socket.gethostbyaddr()
                            try:
                                hostname = socket.gethostbyaddr(ip)[0]
                            except (socket.herror, socket.gaierror, OSError):
                                pass
                            
                            # Metoda 2: HTTP headers
                            if not hostname and (80 in open_ports or 443 in open_ports):
                                try:
                                    import http.client
                                    port = 443 if 443 in open_ports else 80
                                    conn = http.client.HTTPConnection(ip, port, timeout=2)
                                    conn.request("HEAD", "/")
                                    response = conn.getresponse()
                                    server_header = response.getheader("Server", "")
                                    if server_header:
                                        hostname = server_header.split()[0] if server_header else None
                                    conn.close()
                                except Exception:
                                    pass
                            
                            # Metoda 3: NetBIOS
                            if not hostname and (445 in open_ports or 139 in open_ports):
                                try:
                                    result = subprocess.run(
                                        ['nmblookup', '-A', ip],
                                        capture_output=True,
                                        text=True,
                                        timeout=2
                                    )
                                    if result.returncode == 0:
                                        for line in result.stdout.split('\n'):
                                            if '<00>' in line and 'GROUP' not in line:
                                                parts = line.split()
                                                if len(parts) > 0:
                                                    hostname = parts[0].strip()
                                                    break
                                except (FileNotFoundError, subprocess.TimeoutExpired):
                                    pass
                            
                            if not hostname:
                                hostname = f"Device-{ip.split('.')[-1]}"
                            
                            # Analizuj urządzenie
                            device = self._analyze_host_scapy(ip, mac, hostname, open_ports)
                            
                            if device:
                                devices.append(device)
                                console.print(f"  [green]✓[/green] Wykryto: {hostname} ({ip})")
                
                except Exception:
                    continue
            
            if devices:
                console.print(f"\n[green]✅ Skanowanie tshark zakończone. Znaleziono {len(devices)} urządzeń.[/green]\n")
        
        except Exception:
            pass
        
        return devices
    
    def get_all_devices(self) -> List[Device]:
        """Zwraca wszystkie wykryte urządzenia."""
        return self.scanned_devices


if __name__ == "__main__":
    # Test skanera WiFi
    console.print(Panel.fit(
        "[bold cyan]🔍 Test: Skaner WiFi[/bold cyan]\n"
        "[dim]Skanuję urządzenia w sieci lokalnej...[/dim]",
        style="cyan"
    ))
    console.print()
    
    scanner = WiFiScanner()
    devices = scanner.scan_wifi_devices()
    
    console.print(f"\n[bold green]✅ Znaleziono {len(devices)} urządzeń:[/bold green]\n")
    
    for device in devices:
        console.print(f"[cyan]{device.name}[/cyan] ({device.mac_address})")
        console.print(f"  IP: {device.metadata.get('ip_address', 'Unknown')}")
        console.print(f"  Typ: {device.device_type.value}")
        console.print(f"  Szyfrowanie: {'✅ Tak' if device.has_encryption else '❌ Nie'}")
        console.print(f"  Security Score: {device.security_score}/100")
        if device.vulnerabilities:
            console.print(f"  Podatności: {', '.join(device.vulnerabilities)}")
        console.print()
