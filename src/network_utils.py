#!/usr/bin/env python3
"""
Network utilities for medical device scanner.

Provides functions for network detection and validation:
- Automatic local network detection
- IPv4/IPv6 validation
- CIDR range validation
- Socket timeout handling
"""

import socket
import ipaddress
from typing import Optional
from rich.console import Console

console = Console()


def detect_local_network() -> Optional[str]:
    """
    Detect local network range automatically using system routing.
    
    This function determines the local network CIDR range by connecting
    to an external server (Google DNS 8.8.8.8). It doesn't actually send
    any data - just uses the OS routing to find which interface would be used.
    
    Returns:
        Network range in CIDR notation (e.g., "192.168.1.0/24") or None if:
        - IPv6 is detected (not supported)
        - Invalid IP format detected
        - Network timeout occurs
        - Socket error occurs
        
    Raises:
        Nothing - all exceptions are handled gracefully
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set timeout to prevent hanging
        s.settimeout(2)
        try:
            # Connect to external server to determine local interface
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        finally:
            s.close()
        
        # Validate: check if IPv6 (contains colons)
        if ':' in local_ip:
            console.print("[yellow]⚠️  IPv6 detected, WiFi scan may not work[/yellow]")
            return None
        
        # Validate: parse as IPv4 address
        try:
            ip_obj = ipaddress.IPv4Address(local_ip)
        except ipaddress.AddressValueError as e:
            console.print(f"[red]❌ Invalid IPv4 address: {local_ip}[/red]")
            return None
        
        # Extract network base (first 3 octets)
        ip_parts = str(ip_obj).split('.')
        if len(ip_parts) != 4:
            console.print(f"[red]❌ Invalid IPv4 format: {local_ip}[/red]")
            return None
        
        # Build CIDR network range
        network_base = '.'.join(ip_parts[:3])
        network_range = f"{network_base}.0/24"
        
        # Validate: check CIDR notation validity
        try:
            ipaddress.ip_network(network_range, strict=False)
        except ValueError as e:
            console.print(f"[red]❌ Invalid network range: {e}[/red]")
            return None
        
        return network_range
        
    except socket.timeout:
        console.print("[yellow]⚠️  Network detection timeout (socket)[/yellow]")
        return None
    except socket.error as e:
        console.print(f"[yellow]⚠️  Socket error during network detection: {e}[/yellow]")
        return None
    except Exception as e:
        console.print(f"[red]❌ Unexpected error detecting network: {type(e).__name__}: {e}[/red]")
        return None


def validate_ipv4(ip_address: str) -> bool:
    """
    Validate if string is a valid IPv4 address.
    
    Args:
        ip_address: IP address string to validate
        
    Returns:
        True if valid IPv4, False otherwise
    """
    try:
        ipaddress.IPv4Address(ip_address)
        return True
    except (ipaddress.AddressValueError, ValueError):
        return False


def validate_cidr_range(cidr_range: str) -> bool:
    """
    Validate if string is a valid CIDR network range.
    
    Args:
        cidr_range: CIDR range string (e.g., "192.168.1.0/24")
        
    Returns:
        True if valid CIDR range, False otherwise
    """
    try:
        ipaddress.ip_network(cidr_range, strict=False)
        return True
    except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError):
        return False


if __name__ == "__main__":
    network = detect_local_network()
    if network:
        console.print(f"[green]✅ Detected local network: {network}[/green]")
    else:
        console.print("[red]❌ Could not detect local network[/red]")
