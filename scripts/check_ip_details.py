#!/usr/bin/env python3
"""
Check IP address details in VirusTotal.

Usage:
    python3 scripts/check_ip_details.py <IP_ADDRESS>
    python3 scripts/check_ip_details.py 192.168.1.100
"""

import sys
import os
from pathlib import Path

# Add src to path
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir / "src"))

try:
    from external_apis import ExternalAPIs
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Install dependencies: pip install -r requirements.txt")
    sys.exit(1)

console = Console()


def check_ip_details(ip_address: str):
    """Check IP details in VirusTotal."""
    console.print(f"\n[bold cyan]🔍 Checking IP: {ip_address}[/bold cyan]\n")
    
    # Initialize API
    apis = ExternalAPIs()
    
    if not apis.virustotal:
        console.print("[red]❌ VirusTotal API not available[/red]")
        console.print("[yellow]   Add VIRUSTOTAL_API_KEY to .env[/yellow]")
        console.print("[dim]   Register: https://www.virustotal.com/gui/join-us[/dim]")
        return
    
    # Check IP
    result = apis.virustotal.check_ip(ip_address)
    
    if not result:
        console.print("[red]❌ Could not fetch data from VirusTotal[/red]")
        console.print("[yellow]   Check the IP is valid and you have API access[/yellow]")
        return
    
    # Basic info
    console.print(Panel.fit(
        f"[bold]📊 Summary[/bold]\n\n"
        f"Reputation: [cyan]{result.get('reputation', 0)}[/cyan]\n"
        f"🔴 Malicious: [red]{result.get('malicious', 0)}[/red]\n"
        f"🟡 Suspicious: [yellow]{result.get('suspicious', 0)}[/yellow]\n"
        f"🟢 Harmless: [green]{result.get('harmless', 0)}[/green]\n"
        f"⚪ Undetected: [dim]{result.get('undetected', 0)}[/dim]",
        title="VirusTotal Results",
        border_style="cyan"
    ))
    
    # Network info
    if result.get('asn') or result.get('country') or result.get('network'):
        network_info = []
        if result.get('asn'):
            network_info.append(f"ASN: {result.get('asn')}")
        if result.get('country'):
            network_info.append(f"Country: {result.get('country')}")
        if result.get('network'):
            network_info.append(f"Network: {result.get('network')}")
        
        if network_info:
            console.print(f"\n[bold]🌐 Network info:[/bold] {' | '.join(network_info)}")
    
    # Detection details
    detections = result.get('detections', [])
    if detections:
        console.print(f"\n[bold red]⚠️  Detection details ({len(detections)} engines flagged):[/bold red]\n")
        
        table = Table(title="Antivirus detections", box=box.ROUNDED, show_header=True, header_style="bold red")
        table.add_column("Engine", style="cyan", no_wrap=True)
        table.add_column("Category", style="yellow")
        table.add_column("Result", style="red")
        table.add_column("Method", style="dim")
        
        for detection in detections:
            engine = detection.get('engine', 'Unknown')
            category = detection.get('category', 'unknown')
            result_text = detection.get('result', 'detected')
            method = detection.get('method', 'N/A')
            
            if category == 'malicious':
                category_style = "[red]malicious[/red]"
            elif category == 'suspicious':
                category_style = "[yellow]suspicious[/yellow]"
            else:
                category_style = category
            
            table.add_row(engine, category_style, result_text, method)
        
        console.print(table)
        console.print(f"\n[dim]💡 More details: https://www.virustotal.com/gui/ip-address/{ip_address}[/dim]")
    else:
        if result.get('malicious', 0) > 0 or result.get('suspicious', 0) > 0:
            console.print("\n[yellow]⚠️  Threat detected but detection details not available[/yellow]")
            console.print(f"[dim]💡 Check: https://www.virustotal.com/gui/ip-address/{ip_address}[/dim]")
        else:
            console.print("\n[green]✅ No threats detected[/green]")
    
    if result.get('last_analysis_date'):
        from datetime import datetime
        analysis_date = datetime.fromtimestamp(result.get('last_analysis_date'))
        console.print(f"\n[dim]📅 Last analysis: {analysis_date.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        console.print("[red]❌ Error: Provide an IP address[/red]")
        console.print("[yellow]Usage: python3 scripts/check_ip_details.py <IP_ADDRESS>[/yellow]")
        console.print("[dim]Example: python3 scripts/check_ip_details.py 192.168.1.100[/dim]")
        sys.exit(1)
    
    ip_address = sys.argv[1]
    
    import re
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(ip_pattern, ip_address):
        console.print(f"[red]❌ Invalid IP format: {ip_address}[/red]")
        sys.exit(1)
    
    check_ip_details(ip_address)


if __name__ == "__main__":
    main()
