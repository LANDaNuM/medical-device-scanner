#!/usr/bin/env python3
"""
Real WiFi scanner – detects medical devices on the local network.

Uses nmap and other tools to scan WiFi and detect medical devices
by open ports, services and network characteristics.
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

# Add src/ to Python path
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
        console.print("[dim]✅ Rust scanner available – using fast scan[/dim]")
except ImportError:
    RUST_SCANNER_AVAILABLE = False
    FastPortScanner = None

from device import Device, DeviceType, Protocol

console = Console()

# Ports commonly used by medical devices (see comments in PORT_VULNERABILITIES for details)
MEDICAL_PORTS = {
    443: "HTTPS - TLS/SSL, web interfaces for medical devices",
    8443: "HTTPS Alternative - Alternative HTTPS port, often used by medical devices",
    80: "HTTP - Unencrypted web, data in clear (security risk)",
    8080: "HTTP Alternative - Alternative HTTP, often used for device management",
    5000: "HL7 - Medical data exchange between hospital systems (EHR, EMR)",
    104: "DICOM - Standard DICOM port, medical imaging (X-ray, CT, MRI)",
    11112: "DICOM Alternative - Alternative DICOM port, some PACS systems",
    22: "SSH - Secure Shell, remote access (risk if not secured)",
    3389: "RDP - Remote Desktop (high risk if exposed)",
    1433: "MSSQL - Microsoft SQL Server, medical DBs (high data leak risk)",
    3306: "MySQL - MySQL, often in medical systems (high risk)",
}

# Vulnerabilities associated with medical and admin ports. These are THEORETICAL (known port weaknesses);
# real security tests are done by VulnerabilityTester (--audit in scanner.py). Use --audit for deeper analysis.
PORT_VULNERABILITIES = {
    104: [
        "DICOM without encryption – medical images can be intercepted",
        "DICOM without authorization – unauthorized access to medical images",
        "Legacy DICOM – may use insecure protocol versions",
        "DICOM port exposed – access to sensitive medical data from internet"
    ],
    11112: [
        "DICOM Alternative without encryption – alternative port may be less secured",
        "DICOM without authorization – unauthorized access to medical images",
        "DICOM port exposed – access to sensitive medical data"
    ],
    5000: [
        "HL7 without encryption – patient data can be intercepted",
        "HL7 without authorization – unauthorized access to EHR/EMR data",
        "Legacy HL7 – may use insecure versions (HL7v2)",
        "HL7 port exposed – patient data accessible from internet"
    ],
    80: [
        "HTTP without encryption – data in clear",
        "HTTP – data interception (sniffing)",
        "HTTP – man-in-the-middle attacks",
        "HTTP – passwords and medical data sent unencrypted"
    ],
    8080: [
        "HTTP Alternative without encryption – data in clear",
        "Port 8080 often used for management – unauthorized access risk",
        "HTTP Alternative – data interception"
    ],
    443: [
        "HTTPS with legacy TLS (TLS 1.0/1.1) – vulnerability",
        "HTTPS with invalid certificates – MITM risk",
        "HTTPS with weak ciphers – possible compromise"
    ],
    8443: [
        "HTTPS Alternative with legacy TLS – vulnerability",
        "HTTPS Alternative with invalid certificates – MITM risk"
    ],
    22: [
        "SSH with legacy protocol (SSHv1) – vulnerability",
        "SSH with weak keys – brute-force possible",
        "SSH without access limits – brute-force from internet",
        "SSH with default passwords – easy to crack",
        "SSH – man-in-the-middle possible"
    ],
    3389: [
        "RDP exposed – very high risk of takeover",
        "RDP without encryption – session interception",
        "RDP with weak passwords – easy to crack",
        "RDP – brute-force and exploits (BlueKeep, CVE-2019-0708)",
        "RDP – ransomware spread possible"
    ],
    1433: [
        "MSSQL exposed – very high patient data leak risk",
        "MSSQL with default passwords – easy to crack",
        "MSSQL without encryption – medical data can be intercepted",
        "MSSQL – SQL injection possible",
        "MSSQL – access to sensitive medical data (PII, PHI)"
    ],
    3306: [
        "MySQL exposed – very high patient data leak risk",
        "MySQL with default passwords – easy to crack",
        "MySQL without encryption – medical data can be intercepted",
        "MySQL – SQL injection possible",
        "MySQL – access to sensitive medical data (PII, PHI)"
    ],
    21: [
        "FTP without encryption – passwords and data in clear",
        "FTP – data interception",
        "FTP – brute-force attacks"
    ],
    23: [
        "Telnet without encryption – all data in clear",
        "Telnet – very high data interception risk",
        "Telnet – legacy and insecure protocol"
    ],
    445: [
        "SMB exposed – ransomware risk (WannaCry)",
        "SMB with legacy versions (SMBv1) – vulnerability",
        "SMB – malware spread possible"
    ],
    53: [
        "DNS exposed – DDoS amplification possible",
        "DNS – record manipulation",
        "DNS – can be abused for attacks"
    ],
    25: [
        "SMTP exposed – spam relay possible",
        "SMTP – email spoofing",
        "SMTP – can be abused for attacks"
    ],
}

# Typical medical device names on the network
MEDICAL_DEVICE_KEYWORDS = [
    "medical", "med", "hospital", "clinic", "patient", "monitor",
    "glucose", "gluco", "insulin", "pump", "dicom", "hl7",
    "pacs", "ris", "emr", "ehr", "vital", "signs"
]


class WiFiScanner:
    """
    WiFi scanner – detects devices on the local network.

    Uses multiple scan methods: tshark (Wireshark CLI), scapy (packet library),
    and basic ping+socket (no special privileges). Detects devices and analyzes
    security from open ports and services.
    """
    
    def __init__(self, max_ips_to_scan: int = 50, ping_timeout: float = 0.5, port_timeout: float = 0.2):
        """
        Inicjalizacja skanera WiFi.
        
        Args:
            max_ips_to_scan: Max IPs to scan (default 50)
            ping_timeout: Ping timeout in seconds (default 0.5s)
            port_timeout: Port scan timeout in seconds (default 0.2s)
        """
        self.scanned_devices: List[Device] = []
        self.mac_vendor_cache: Dict[str, str] = {}  # MAC -> manufacturer cache
        self.max_ips_to_scan = max_ips_to_scan
        self.ping_timeout = ping_timeout
        self.port_timeout = port_timeout
        
        # Init Rust scanner if available
        if RUST_SCANNER_AVAILABLE and FastPortScanner:
            self.rust_scanner = FastPortScanner(
                timeout_ms=int(port_timeout * 1000),
                max_concurrent=50
            )
        else:
            self.rust_scanner = None
    
    def scan_wifi_devices(self, network_range: Optional[str] = None) -> List[Device]:
        """
        Scan WiFi devices on local network. network_range: e.g. "192.168.1.0/24"; if None, auto-detect. Returns list of Device.
        """
        console.print("[cyan]🔍 Starting WiFi scan...[/cyan]")
        console.print("[dim]Scanning local network (active devices with open ports)...[/dim]")
        console.print("[dim]💡 Physical device: laptop WiFi adapter[/dim]")
        console.print("[dim]💡 Scans ONLY devices on the SAME WiFi you are connected to[/dim]")
        console.print("[dim]💡 Detects only devices that respond to ping and have open ports[/dim]\n")
        
        devices: List[Device] = []
        
        # Auto-detect network range if not given
        if network_range is None:
            network_range = self._detect_local_network()
        
        if not network_range:
            console.print("[red]❌ Could not detect local network[/red]")
            console.print("[yellow]   Provide range manually: scan_wifi_devices('192.168.1.0/24')[/yellow]\n")
            return devices
        
        console.print(f"[cyan]Scanning network: {network_range}[/cyan]\n")
        
        # Priority 1: Try tshark (Wireshark CLI)
        devices = self._scan_with_tshark(network_range)
        if devices:
            return devices
        
        # Priority 2: Use scapy (no external program)
        if SCAPY_AVAILABLE:
            try:
                devices = self._scan_with_scapy(network_range)
                if devices:
                    return devices
            except Exception as e:
                console.print(f"[yellow]⚠️  scapy failed: {e}[/yellow]")
                console.print("[dim]   Falling back to basic scan...[/dim]\n")
                pass
        
        # Priority 3: Basic ping + socket scan (no privileges)
        devices = self._scan_basic(network_range)
        
        # Deduplicate by MAC or IP
        unique_devices = []
        seen_macs = set()
        seen_ips = set()
        
        for device in devices:
            mac = device.mac_address
            ip = device.metadata.get('ip_address') if device.metadata else None
            
            # Check for duplicate
            is_duplicate = False
            
            # If MAC is generated (00:00:xx), check by IP
            if mac.startswith("00:00:"):
                if ip and ip in seen_ips:
                    is_duplicate = True
                elif ip:
                    seen_ips.add(ip)
            else:
                # For real MACs, check by MAC
                if mac in seen_macs:
                    is_duplicate = True
                else:
                    seen_macs.add(mac)
                    if ip:
                        seen_ips.add(ip)
            
            if not is_duplicate:
                unique_devices.append(device)
        
        if len(devices) > len(unique_devices):
            console.print(f"[dim]   Removed {len(devices) - len(unique_devices)} duplicate devices[/dim]")
        
        self.scanned_devices = unique_devices
        return unique_devices
    
    def _detect_local_network(self) -> Optional[str]:
        """Auto-detect local network range. Returns e.g. '192.168.1.0/24' or None."""
        try:
            # Connect to external server to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Get network base (e.g. 192.168.1.0/24)
            ip_parts = local_ip.split('.')
            network_base = '.'.join(ip_parts[:3])
            return f"{network_base}.0/24"
        except Exception as e:
            console.print(f"[yellow]⚠️  Could not detect local network: {e}[/yellow]")
            return None
    
    def _get_gateway_ip(self) -> Optional[str]:
        """Get default gateway IP. Used to filter proxy ARP 'ghosts'."""
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
                    # First IPv4-looking element is gateway
                    if part.count('.') == 3 and part.replace('.', '').isdigit():
                        return part
            # Fallback: route -n (e.g. on older systems)
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
        """Remove duplicates and proxy ARP 'ghosts'; one entry per MAC; skip .0 and .255."""
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
            # Skip network and broadcast addresses
            if ip.endswith(".0") or ip.endswith(".255"):
                continue
            # Proxy ARP: same MAC as gateway but different IP → likely ghost
            if gateway_mac_norm and mac == gateway_mac_norm and ip != gateway_ip_str:
                continue
            # One entry per MAC (first IP seen for this MAC)
            if mac not in seen_mac:
                seen_mac[mac] = h
                out.append(h)
        return out
    
    def _scan_with_scapy(self, network_range: str) -> List[Device]:
        """Scan network with scapy (no external program). Returns list of devices."""
        devices: List[Device] = []
        
        try:
            conf.verb = 0
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Scanning network with scapy...", total=None)
                
                # Step 1: ARP scan (needs root) or ping scan (no root)
                progress.update(task, description="Detecting active hosts...")
                console.print("[cyan]  Detecting active hosts...[/cyan]")
                
                active_hosts = []
                
                # Try ARP scan (needs root)
                try:
                    # Create ARP packet for whole network
                    arp_request = ARP(pdst=network_range)
                    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
                    arp_request_broadcast = broadcast / arp_request
                    
                    # Send and receive
                    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]
                    
                    # Get active hosts with MACs
                    for element in answered_list:
                        host_info = {
                            'ip': element[1].psrc,  # IP address
                            'mac': element[1].hwsrc  # MAC address
                        }
                        active_hosts.append(host_info)
                    
                except PermissionError:
                    # No privileges – use ping scan
                    network_base = network_range.split('/')[0].rsplit('.', 1)[0]
                    
                    # Ping scan – first N addresses (faster). Priority: .1 (router), .2-.20, rest
                    priority_ips = [1, 254]  # Routery
                    common_ips = list(range(2, min(21, self.max_ips_to_scan + 1)))  # Common devices
                    other_ips = list(range(21, min(255, self.max_ips_to_scan + 1)))  # Reszta
                    ips_to_scan = priority_ips + common_ips + other_ips
                    
                    # Parallel ping scan
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
                    
                    # Ping in parallel (max 20 at a time)
                    with ThreadPoolExecutor(max_workers=20) as executor:
                        futures = {executor.submit(ping_host, f"{network_base}.{i}"): i for i in ips_to_scan}
                        for future in as_completed(futures):
                            ip, is_alive = future.result()
                            if is_alive:
                                ping_results[ip] = True
                    
                    # Add all hosts that respond to ping (phones/TVs often have no open ports)
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
                    # Other error – use ping as fallback
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
                                # Verify device is actually active
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
                                
                                # Routers often respond to ping but block ports
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
                
                # One device = one MAC; remove proxy ARP ghosts and duplicates
                gateway_ip = self._get_gateway_ip()
                gateway_mac = self._get_mac_address(gateway_ip) if gateway_ip else None
                active_hosts = self._deduplicate_active_hosts(active_hosts, gateway_ip, gateway_mac)
                
                console.print(f"[cyan]  Found {len(active_hosts)} active hosts[/cyan]")
                
                if not active_hosts:
                    progress.update(task, description="✅ No active hosts")
                    return devices
                
                # Step 2: Scan ports for each host (use Rust if available)
                # Porty do skanowania: medyczne, administracyjne, webowe, bazy danych
                ports_to_scan = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 161, 162, 443, 445, 
                                993, 995, 104, 5000, 11112, 1433, 3306, 3389, 5432, 5900, 5901, 
                                8080, 8443, 27017]
                
                progress.update(task, description=f"Scanning ports on {len(active_hosts)} hosts...")
                
                # Use Rust scanner for all hosts at once if available
                if self.rust_scanner and len(active_hosts) > 1:
                    # Fast parallel scan of all IPs
                    ips = [h['ip'] for h in active_hosts]
                    all_results = self.rust_scanner.scan_multiple_ips(ips, ports_to_scan)
                    
                    for i, host_info in enumerate(active_hosts):
                        try:
                            ip = host_info['ip']
                            mac = host_info['mac']
                            progress.update(task, description=f"✓ {ip} ({i+1}/{len(active_hosts)})")
                            
                            open_ports = all_results.get(ip, [])
                            
                            # Analyze device – detect all devices (even without open ports)
                            hostname = self._get_hostname(ip, open_ports if open_ports else [])
                            device = self._analyze_host_scapy(ip, mac, hostname, open_ports)
                            if device:
                                devices.append(device)
                                if open_ports:
                                    progress.update(task, description=f"✓ {hostname} ({len(open_ports)} ports)")
                                else:
                                    progress.update(task, description=f"✓ {hostname} (active, no open ports)")
                        except Exception as e:
                            console.print(f"[yellow]  ⚠ Scan error {host_info.get('ip', 'unknown')}: {e}[/yellow]")
                            continue
                else:
                    # Fallback: sequential scan (slower)
                    for i, host_info in enumerate(active_hosts):
                        try:
                            ip = host_info['ip']
                            mac = host_info['mac']
                            progress.update(task, description=f"Scanning {ip} ({i+1}/{len(active_hosts)})...")
                            
                            open_ports = []
                            if self.rust_scanner:
                                open_ports = self.rust_scanner.scan_ports(ip, ports_to_scan)
                            else:
                                for port in ports_to_scan:
                                    try:
                                        response = sr1(IP(dst=ip) / TCP(dport=port, flags="S"), timeout=self.port_timeout, verbose=False)
                                        if response and response.haslayer(TCP):
                                            if response[TCP].flags == 18:  # SYN-ACK (port open)
                                                open_ports.append(port)
                                    except Exception:
                                        continue
                            
                            # Analyze device – detect all devices (even without open ports)
                            # Phones, TVs often have no open ports but are active
                            hostname = self._get_hostname(ip, open_ports if open_ports else [])
                            device = self._analyze_host_scapy(ip, mac, hostname, open_ports)
                            if device:
                                devices.append(device)
                                if open_ports:
                                    progress.update(task, description=f"✓ {hostname} ({len(open_ports)} ports)")
                                else:
                                    progress.update(task, description=f"✓ {hostname} (active, no open ports)")
                        
                        except Exception as e:
                            console.print(f"[yellow]  ⚠ Scan error {host_info.get('ip', 'unknown')}: {e}[/yellow]")
                            continue
                
                progress.update(task, description="✅ Scan complete")
            
            console.print(f"\n[green]✅ Scan complete. Found {len(devices)} devices.[/green]\n")
            return devices
            
        except Exception as e:
            console.print(f"[yellow]⚠️  scapy failed: {e}[/yellow]")
            console.print("[dim]   Falling back to basic scan...[/dim]\n")
            return []
    
    def _analyze_host_scapy(self, ip: str, mac: str, hostname: str, open_ports: List[int]) -> Optional[Device]:
        """Analyze host detected by scapy. Returns Device or None."""
        try:
            manufacturer = self._get_manufacturer_from_mac_api(mac)
            
            # Determine device type
            device_type = self._detect_device_type(hostname, open_ports)
            
            # Security from ports; WiFi has network-level encryption (WPA2/WPA3), we also check app ports
            # Encrypted ports: 443, 8443, 993, 995, 22
            encrypted_ports = [443, 8443, 993, 995, 22]
            has_encryption = any(port in open_ports for port in encrypted_ports)
            requires_pairing = True  # WiFi typically requires password (WPA2/WPA3)
            
            # Determine encryption type
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
                # WiFi has network-level encryption, so device is protected even without app ports
                if 80 in open_ports:
                    encryption_type = "Network-level encryption (WPA2/WPA3), HTTP unencrypted"
                else:
                    encryption_type = "Network-level encryption (WPA2/WPA3)"
                # Ustaw has_encryption na True, bo WiFi ma szyfrowanie sieciowe
                has_encryption = True
            
            # Check if router
            is_router = self._is_router_device(hostname, open_ports, ip)
            is_medical = self._is_medical_device(hostname, open_ports)
            
            # Create device
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
            
            # Add vulnerabilities only if real
            if not has_encryption and open_ports:
                if is_router:
                    if 443 in open_ports or 8443 in open_ports:
                        pass  # Ma HTTPS - OK
                    else:
                        device.add_vulnerability("HTTP without HTTPS – recommend HTTPS for router")
                else:
                    device.add_vulnerability("No encryption – data can be intercepted")
            
            # Test vulnerabilities for all open ports (with context)
            port_vulnerabilities = self._test_port_vulnerabilities(open_ports, is_router=is_router, is_medical=is_medical)
            for vuln in port_vulnerabilities:
                device.add_vulnerability(vuln)
            
            device.calculate_security_score()
            return device
        
        except Exception as e:
            console.print(f"[yellow]  ⚠ Analysis error {ip}: {e}[/yellow]")
            return None
    
    def _scan_basic(self, network_range: str) -> List[Device]:
        """Basic scan with ping and socket (no nmap). Returns list of devices."""
        devices: List[Device] = []
        
        # Extract IP base (e.g. 192.168.1)
        network_base = network_range.split('/')[0].rsplit('.', 1)[0]
        
        console.print(f"[yellow]⚠️  Using basic scan (ping + socket)[/yellow]")
        console.print(f"[dim]   Note: Basic scan may be slower and less accurate[/dim]\n")
        
        max_ips = min(self.max_ips_to_scan, 254)
        console.print(f"[dim]   Scanning {max_ips} IP addresses...[/dim]")
        
        # Parallel ping for speed
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
        
        # Ping in parallel (max 50 at a time)
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(ping_host, f"{network_base}.{i}"): i for i in range(1, max_ips + 1)}
            for future in as_completed(futures):
                ip, is_alive = future.result()
                if is_alive:
                    ping_results[ip] = True
        
        # Get MAC for each IP (for dedup and proxy ARP filter)
        active_hosts_raw = []
        for ip in ping_results.keys():
            try:
                mac = self._get_mac_address(ip)
                active_hosts_raw.append({'ip': ip, 'mac': mac})
            except Exception:
                continue
        
        # One device = one MAC; remove proxy ARP ghosts and duplicates
        gateway_ip = self._get_gateway_ip()
        gateway_mac = self._get_mac_address(gateway_ip) if gateway_ip else None
        active_hosts = self._deduplicate_active_hosts(active_hosts_raw, gateway_ip, gateway_mac)
        
        console.print(f"[dim]   After dedup (1 device = 1 MAC): {len(active_hosts)} hosts[/dim]\n")
        
        # Teraz przeanalizuj tylko zdeduplikowane hosty
        for host in active_hosts:
            ip = host.get('ip')
            if not ip:
                continue
            try:
                    # Host responds to ping – active device. Check open ports (phones/TVs often have none)
                    test_ports = [80, 443, 22, 23, 135, 139, 445, 161, 3389, 8080, 8443, 554, 8554, 5000, 7001, 7002]
                    open_ports = []
                    
                    for port in test_ports:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.2)  # Shorter timeout for speed
                        result_port = sock.connect_ex((ip, port))
                        sock.close()
                        if result_port == 0:
                            open_ports.append(port)
                    
                    # Detect all devices that respond to ping (even without open ports)
                    device = self._analyze_host_basic(ip)
                    if device:
                        # Zaktualizuj otwarte porty w metadanych
                        if open_ports:
                            device.metadata['open_ports'] = open_ports
                        devices.append(device)
                        if open_ports:
                            console.print(f"  [green]✓[/green] Detected: {device.name} ({ip}) - {len(open_ports)} open ports")
                        else:
                            console.print(f"  [green]✓[/green] Detected: {device.name} ({ip}) - active (no open ports)")
            
            except Exception:
                continue
        
        console.print(f"\n[green]✅ Scan complete. Found {len(devices)} devices.[/green]\n")
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
            # Try connecting to common ports (but do not require them)
            test_ports = [80, 443, 8080, 22, 3389, 554, 8554, 5000, 7001, 7002, 8443]
            open_ports = []
            
            for port in test_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.2)  # Short timeout for speed
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
            
            # Return device even without open ports – it responds to ping
            
            # Try to get real hostname (no sudo)
            hostname = None
            try:
                # Method 1: socket.gethostbyaddr() – works without sudo
                hostname = socket.gethostbyaddr(ip)[0]
            except (socket.herror, socket.gaierror, OSError):
                pass
            
            # Method 2: Try HTTP headers (if port 80/443 open)
            if not hostname and (80 in open_ports or 443 in open_ports):
                try:
                    import http.client
                    port = 443 if 443 in open_ports else 80
                    conn = http.client.HTTPConnection(ip, port, timeout=2)
                    conn.request("HEAD", "/")
                    response = conn.getresponse()
                    # Check Server or Host headers
                    server_header = response.getheader("Server", "")
                    if server_header:
                        # Extract name from Server header
                        hostname = server_header.split()[0] if server_header else None
                    conn.close()
                except Exception:
                    pass
            
            # Method 3: Try NetBIOS name (if port 445/139 open)
            if not hostname and (445 in open_ports or 139 in open_ports):
                try:
                    # NetBIOS may be available without sudo
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
            
            # Fallback: use IP as name
            if not hostname:
                hostname = f"Device-{ip.split('.')[-1]}"
            
            device_type = self._detect_device_type(hostname, open_ports)
            
            # Security from ports; WiFi has network-level encryption (WPA2/WPA3), we also check app ports
            # Encrypted ports: 443, 8443, 993, 995, 22
            encrypted_ports = [443, 8443, 993, 995, 22]
            has_encryption = any(port in open_ports for port in encrypted_ports)
            requires_pairing = True  # WiFi typically requires password (WPA2/WPA3)
            
            # Determine encryption type
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
                # WiFi has network-level encryption, so device is protected even without app ports
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
            
            # Test vulnerabilities for all open ports
            port_vulnerabilities = self._test_port_vulnerabilities(open_ports)
            for vuln in port_vulnerabilities:
                device.add_vulnerability(vuln)
            
            device.calculate_security_score()
            return device
        
        except Exception:
            return None
    
    def _detect_device_type(self, hostname: str, open_ports: List[int]) -> DeviceType:
        """Detect device type from name and ports. Returns DeviceType."""
        hostname_lower = hostname.lower()
        
        # Check hostname
        if any(keyword in hostname_lower for keyword in ["glucose", "gluco", "diabetes"]):
            return DeviceType.GLUCOSE_METER
        if any(keyword in hostname_lower for keyword in ["insulin", "pump"]):
            return DeviceType.INSULIN_PUMP
        if any(keyword in hostname_lower for keyword in ["monitor", "patient", "vital"]):
            return DeviceType.PULSE_OXIMETER
        if any(keyword in hostname_lower for keyword in ["pressure", "bp", "sphygmo"]):
            return DeviceType.BLOOD_PRESSURE
        
        # Check medical ports
        if 104 in open_ports or 11112 in open_ports:  # DICOM
            return DeviceType.UNKNOWN  # Medical but unknown type
        if 5000 in open_ports:  # HL7
            return DeviceType.UNKNOWN
        
        # Check if name contains medical keywords
        if any(keyword in hostname_lower for keyword in MEDICAL_DEVICE_KEYWORDS):
            return DeviceType.UNKNOWN
        
        return DeviceType.UNKNOWN
    
    def _analyze_security(self, open_ports: List[int], nm_host: Dict) -> tuple:
        """Analyze security from open ports. nm_host: host data from nmap.
        
        Returns:
            Tuple (has_encryption, requires_pairing)
        """
        has_encryption = False
        requires_pairing = True  # WiFi typically requires password
        
        # Check for HTTPS (encrypted) ports
        if 443 in open_ports or 8443 in open_ports:
            has_encryption = True
        
        # Check if only HTTP (unencrypted) ports
        if 80 in open_ports and 443 not in open_ports:
            has_encryption = False
        
        return has_encryption, requires_pairing
    
    def _is_router_device(self, hostname: str, open_ports: List[int], ip: str) -> bool:
        """Return True if device is router/gateway.
        
        Returns:

        """
        name_lower = hostname.lower()
        router_keywords = [
            "router", "gateway", "ap", "access point", "wifi", "wireless",
            "tp-link", "netgear", "asus", "linksys", "d-link", "zyxel",
            "fritz", "huawei", "zte", "cisco", "ubiquiti", "unifi"
        ]
        
        if any(keyword in name_lower for keyword in router_keywords):
            return True
        
        # Check IP – routers often end with .1
        if ip.endswith(".1") or ip.endswith(".254"):
            router_ports = [80, 443, 22, 161, 162]
            if any(p in open_ports for p in router_ports):
                if len(open_ports) <= 6:
                    return True
        
        return False
    
    def _is_medical_device(self, hostname: str, open_ports: List[int]) -> bool:
        """Return True if device is medical (by name and ports)."""
        name_lower = hostname.lower()
        medical_keywords = [
            "medical", "med", "hospital", "clinic", "patient", "monitor",
            "glucose", "gluco", "insulin", "pump", "dicom", "hl7",
            "pacs", "ris", "emr", "ehr", "vital", "signs", "health"
        ]
        
        if any(keyword in name_lower for keyword in medical_keywords):
            return True
        
        # Check medical ports
        medical_ports = [104, 11112, 5000]
        if any(p in open_ports for p in medical_ports):
            # If it has medical ports and few others, likely medical device
            if len(open_ports) <= 5:
                return True
        
        return False
    
    def _test_port_vulnerabilities(self, open_ports: List[int], is_router: bool = False, is_medical: bool = False) -> List[str]:
        """Analyze vulnerabilities for open ports (THEORETICAL). Real tests: VulnerabilityTester (--audit).
        Checks context (router vs medical vs home), adds only relevant vulnerabilities.
        
        Args:
            open_ports: List of open ports do przeanalizowania
            is_router: whether device is router/gateway
            is_medical: whether device is medical

        Returns:
            List of vulnerability strings
        """
        vulnerabilities = []
        
        for port in open_ports:
            if port in PORT_VULNERABILITIES:
                port_vulns = PORT_VULNERABILITIES[port]
                if port in [104, 11112]:  # DICOM
                    if is_medical:
                        vulnerabilities.extend([
                            f"Port DICOM ({port}) open – unauthorized access to medical images possible",
                            "DICOM may send data unencrypted – sensitive medical images at risk"
                        ])
                        vulnerabilities.extend(port_vulns)
                elif port == 5000:  # HL7
                    if is_medical:
                        vulnerabilities.extend([
                            f"Port HL7 ({port}) open – unauthorized access to patient data possible",
                            "HL7 may send data unencrypted – EHR/EMR data at risk"
                        ])
                        vulnerabilities.extend(port_vulns)
                elif port == 22:  # SSH
                    if not is_router:
                        port_name = "SSH"
                        vulnerabilities.extend([
                            f"Port {port} ({port_name}) open – check security configuration",
                            f"Port {port} – brute-force attacks possible if not secured"
                        ])
                        vulnerabilities.extend(port_vulns)
                
                elif port == 3389:  # RDP
                    if not is_router:
                        port_name = "RDP"
                        vulnerabilities.extend([
                            f"Port {port} ({port_name}) open – high unauthorized access risk",
                            f"Port {port} – brute-force and exploits possible"
                        ])
                        vulnerabilities.extend(port_vulns)
                
                elif port in [1433, 3306, 5432, 27017]:  # Databases
                    if not is_router:
                        db_name = {1433: "MSSQL", 3306: "MySQL", 5432: "PostgreSQL", 27017: "MongoDB"}.get(port, "Database")
                        vulnerabilities.extend([
                            f"Port {port} ({db_name}) open – very high data leak risk",
                            f"Port {port} – SQL injection and unauthorized access possible"
                        ])
                        vulnerabilities.extend(port_vulns)
                
                elif port in [80, 8080]:  # HTTP
                    # HTTP – check if HTTPS present
                    has_https = 443 in open_ports or 8443 in open_ports
                    if not has_https:
                        if is_router:
                            vulnerabilities.append(f"Port {port} (HTTP) without HTTPS – recommend HTTPS for router")
                        else:
                            vulnerabilities.extend([
                                f"Port {port} (HTTP) open without HTTPS – data sent unencrypted",
                                f"Port {port} – data interception (sniffing) possible",
                                f"Port {port} – man-in-the-middle attacks"
                            ])
                            vulnerabilities.extend(port_vulns)
                
                elif port == 21:  # FTP
                    if not is_router:
                        vulnerabilities.extend([
                            f"FTP without encryption – passwords and data in clear",
                            f"FTP – data interception possible",
                            f"FTP – brute-force attacks"
                        ])
                        vulnerabilities.extend(port_vulns)
                
                elif port == 23:  # Telnet
                    vulnerabilities.extend([
                        f"Telnet without encryption – all data in clear",
                        f"Telnet – very high data interception risk",
                        f"Telnet – legacy and insecure protocol"
                    ])
                    vulnerabilities.extend(port_vulns)
                
                elif port in [25, 53]:  # SMTP, DNS
                    if not is_router:
                        vulnerabilities.extend(port_vulns)
                
                elif port in [443, 8443]:  # HTTPS
                    if not is_router:
                        vulnerabilities.extend([
                            f"HTTPS with legacy TLS (TLS 1.0/1.1) – vulnerability",
                            f"HTTPS with invalid certificates – MITM risk",
                            f"HTTPS with weak ciphers – possible compromise"
                        ])
                
                elif port in [135, 139, 445]:  # SMB/NetBIOS
                    if not is_router:
                        vulnerabilities.extend(port_vulns)
                
                elif port in [161, 162]:  # SNMP
                    if not is_router:
                        vulnerabilities.extend(port_vulns)
                
                elif port in [5900, 5901]:  # VNC
                    if not is_router:
                        vulnerabilities.extend(port_vulns)
                
                # Other ports – leave to VulnerabilityTester
                # else:
                #     vulnerabilities.extend(port_vulns)
        
        # For routers, limit to critical vulnerabilities only
        if is_router:
            normal_router_ports = [80, 443, 22, 161, 162, 53, 25, 135, 139, 445]
            filtered_vulnerabilities = []
            for vuln in vulnerabilities:
                is_normal_port = False
                for port in normal_router_ports:
                    if str(port) in vuln and port in open_ports:
                        critical_keywords = ["telnet", "ftp", "rdp", "mssql", "mysql", "postgresql", "mongodb", "database"]
                        if not any(keyword in vuln.lower() for keyword in critical_keywords):
                            is_normal_port = True
                            break
                if not is_normal_port:
                    filtered_vulnerabilities.append(vuln)
            return filtered_vulnerabilities
        
        medical_ports = [104, 11112, 5000]
        has_medical_ports = any(port in open_ports for port in medical_ports)
        has_https = 443 in open_ports or 8443 in open_ports
        if has_medical_ports and not has_https and is_medical:
            vulnerabilities.append(
                "Medical ports (DICOM/HL7) open without HTTPS – medical data may be sent unencrypted"
            )
        admin_ports = [22, 3389]
        db_ports = [1433, 3306, 5432, 27017]
        has_admin = any(port in open_ports for port in admin_ports)
        has_db = any(port in open_ports for port in db_ports)
        if has_admin and has_db and not is_router:
            vulnerabilities.append(
                "Admin and database ports open together – very high risk of full compromise"
            )
        
        # Deduplicate preserving order
        seen = set()
        unique_vulns = []
        for vuln in vulnerabilities:
            if vuln not in seen:
                seen.add(vuln)
                unique_vulns.append(vuln)
        
        return unique_vulns
    
    def _get_hostname(self, ip: str, open_ports: List[int]) -> str:
        """
        Get device hostname using multiple methods (gethostbyaddr, HTTP, NetBIOS). Returns hostname or generated name.
        """
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            if hostname:
                return hostname
        except (socket.herror, socket.gaierror, OSError):
            pass
        
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
        
        return f"Device-{ip.split('.')[-1]}"
    
    def _get_mac_address(self, ip: str) -> str:
        """Get host MAC via ARP, or generate from IP for dedup only (do not use generated MAC for vendor lookup)."""
        try:
            result = subprocess.run(
                ['arp', '-n', ip],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0 and result.stdout:
                for line in result.stdout.split('\n'):
                    if ip in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            return parts[2]
        except Exception:
            pass
        ip_parts = ip.split('.')
        part2 = int(ip_parts[2]) if len(ip_parts) > 2 else 0
        part3 = int(ip_parts[3]) if len(ip_parts) > 3 else 0
        return f"00:00:{part2:02x}:{part3:02x}:00:00"
    
    def _get_manufacturer_from_mac_api(self, mac_address: str) -> Optional[str]:
        """Get manufacturer from MAC (OUI). Uses IEEE OUI first, then macvendors.com API. Returns None for generated MACs (00:00:xx)."""
        if mac_address.startswith("00:00:"):
            return None
        if mac_address in self.mac_vendor_cache:
            return self.mac_vendor_cache[mac_address]
        try:
            from oui_lookup import get_oui_lookup
            oui_lookup = get_oui_lookup()
            manufacturer = oui_lookup.lookup(mac_address)
            if manufacturer:
                self.mac_vendor_cache[mac_address] = manufacturer
                return manufacturer
        except Exception:
            pass
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            # Normalize MAC format
            mac_normalized = mac_address.replace("-", ":").replace(" ", ":").replace(".", ":").upper()
            
            # Skip random/private MAC
            first_byte = int(mac_normalized.split(":")[0], 16)
            is_random = (first_byte & 0x02) != 0
            if is_random:
                return None
            
            # Call API
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
        Scan network with tshark (Wireshark CLI). Returns list of devices or empty list if tshark unavailable.
        """
        devices: List[Device] = []
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
            console.print("[cyan]  Using tshark to scan network...[/cyan]")
            for i in range(1, 21):
                ip = f"{network_base}.{i}"
                
                try:
                    ping_result = subprocess.run(
                        ['ping', '-c', '1', '-W', '1', ip],
                        capture_output=True,
                        timeout=1
                    )
                    
                    if ping_result.returncode == 0:
                        mac = self._get_mac_address(ip)
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
                            hostname = None
                            try:
                                hostname = socket.gethostbyaddr(ip)[0]
                            except (socket.herror, socket.gaierror, OSError):
                                pass
                            
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
                            
                            device = self._analyze_host_scapy(ip, mac, hostname, open_ports)
                            if device:
                                devices.append(device)
                                console.print(f"  [green]✓[/green] Detected: {hostname} ({ip})")
                
                except Exception:
                    continue
            
            if devices:
                console.print(f"\n[green]✅ tshark scan complete. Found {len(devices)} devices.[/green]\n")
        
        except Exception:
            pass
        
        return devices
    
    def get_all_devices(self) -> List[Device]:
        """Return all detected devices."""
        return self.scanned_devices


if __name__ == "__main__":
    console.print(Panel.fit(
        "[bold cyan]🔍 Test: WiFi Scanner[/bold cyan]\n"
        "[dim]Scanning devices on local network...[/dim]",
        style="cyan"
    ))
    console.print()
    scanner = WiFiScanner()
    devices = scanner.scan_wifi_devices()
    console.print(f"\n[bold green]✅ Found {len(devices)} devices:[/bold green]\n")
    for device in devices:
        console.print(f"[cyan]{device.name}[/cyan] ({device.mac_address})")
        console.print(f"  IP: {device.metadata.get('ip_address', 'Unknown')}")
        console.print(f"  Type: {device.device_type.value}")
        console.print(f"  Encryption: {'✅ Yes' if device.has_encryption else '❌ No'}")
        console.print(f"  Security Score: {device.security_score}/100")
        if device.vulnerabilities:
            console.print(f"  Vulnerabilities: {', '.join(device.vulnerabilities)}")
        console.print()
