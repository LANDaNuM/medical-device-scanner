#!/usr/bin/env python3
"""
Skrypt do sprawdzania szczegółów adresu IP w VirusTotal.

Użycie:
    python3 scripts/check_ip_details.py <IP_ADDRESS>
    python3 scripts/check_ip_details.py 192.168.1.100
"""

import sys
import os
from pathlib import Path

# Dodaj ścieżkę do src
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir / "src"))

try:
    from external_apis import ExternalAPIs
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
except ImportError as e:
    print(f"❌ Błąd importu: {e}")
    print("   Zainstaluj zależności: pip install -r requirements.txt")
    sys.exit(1)

console = Console()


def check_ip_details(ip_address: str):
    """Sprawdza szczegóły IP w VirusTotal."""
    console.print(f"\n[bold cyan]🔍 Sprawdzam szczegóły IP: {ip_address}[/bold cyan]\n")
    
    # Inicjalizuj API
    apis = ExternalAPIs()
    
    if not apis.virustotal:
        console.print("[red]❌ VirusTotal API niedostępne[/red]")
        console.print("[yellow]   Dodaj VIRUSTOTAL_API_KEY do pliku .env[/yellow]")
        console.print("[dim]   Rejestracja: https://www.virustotal.com/gui/join-us[/dim]")
        return
    
    # Sprawdź IP
    result = apis.virustotal.check_ip(ip_address)
    
    if not result:
        console.print("[red]❌ Nie można pobrać danych z VirusTotal[/red]")
        console.print("[yellow]   Sprawdź czy IP jest poprawne i czy masz dostęp do API[/yellow]")
        return
    
    # Wyświetl podstawowe informacje
    console.print(Panel.fit(
        f"[bold]📊 Podsumowanie[/bold]\n\n"
        f"Reputacja: [cyan]{result.get('reputation', 0)}[/cyan]\n"
        f"🔴 Malicious: [red]{result.get('malicious', 0)}[/red]\n"
        f"🟡 Suspicious: [yellow]{result.get('suspicious', 0)}[/yellow]\n"
        f"🟢 Harmless: [green]{result.get('harmless', 0)}[/green]\n"
        f"⚪ Undetected: [dim]{result.get('undetected', 0)}[/dim]",
        title="VirusTotal Results",
        border_style="cyan"
    ))
    
    # Informacje o sieci
    if result.get('asn') or result.get('country') or result.get('network'):
        network_info = []
        if result.get('asn'):
            network_info.append(f"ASN: {result.get('asn')}")
        if result.get('country'):
            network_info.append(f"Kraj: {result.get('country')}")
        if result.get('network'):
            network_info.append(f"Sieć: {result.get('network')}")
        
        if network_info:
            console.print(f"\n[bold]🌐 Informacje o sieci:[/bold] {' | '.join(network_info)}")
    
    # Szczegóły detekcji
    detections = result.get('detections', [])
    if detections:
        console.print(f"\n[bold red]⚠️  Szczegóły detekcji ({len(detections)} antywirusów wykryło zagrożenie):[/bold red]\n")
        
        # Tabela z detekcjami
        table = Table(title="Detekcje antywirusów", box=box.ROUNDED, show_header=True, header_style="bold red")
        table.add_column("Antywirus", style="cyan", no_wrap=True)
        table.add_column("Kategoria", style="yellow")
        table.add_column("Wynik", style="red")
        table.add_column("Metoda", style="dim")
        
        for detection in detections:
            engine = detection.get('engine', 'Unknown')
            category = detection.get('category', 'unknown')
            result_text = detection.get('result', 'detected')
            method = detection.get('method', 'N/A')
            
            # Koloruj kategorię
            if category == 'malicious':
                category_style = "[red]malicious[/red]"
            elif category == 'suspicious':
                category_style = "[yellow]suspicious[/yellow]"
            else:
                category_style = category
            
            table.add_row(engine, category_style, result_text, method)
        
        console.print(table)
        
        # Link do VirusTotal
        console.print(f"\n[dim]💡 Więcej szczegółów: https://www.virustotal.com/gui/ip-address/{ip_address}[/dim]")
    else:
        if result.get('malicious', 0) > 0 or result.get('suspicious', 0) > 0:
            console.print("\n[yellow]⚠️  Wykryto zagrożenie, ale szczegóły detekcji nie są dostępne[/yellow]")
            console.print(f"[dim]💡 Sprawdź szczegóły: https://www.virustotal.com/gui/ip-address/{ip_address}[/dim]")
        else:
            console.print("\n[green]✅ Brak wykrytych zagrożeń[/green]")
    
    # Data ostatniej analizy
    if result.get('last_analysis_date'):
        from datetime import datetime
        analysis_date = datetime.fromtimestamp(result.get('last_analysis_date'))
        console.print(f"\n[dim]📅 Ostatnia analiza: {analysis_date.strftime('%Y-%m-%d %H:%M:%S')}[/dim]")


def main():
    """Główna funkcja."""
    if len(sys.argv) < 2:
        console.print("[red]❌ Błąd: Podaj adres IP[/red]")
        console.print("[yellow]Użycie: python3 scripts/check_ip_details.py <IP_ADDRESS>[/yellow]")
        console.print("[dim]Przykład: python3 scripts/check_ip_details.py 192.168.1.100[/dim]")
        sys.exit(1)
    
    ip_address = sys.argv[1]
    
    # Podstawowa walidacja IP
    import re
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(ip_pattern, ip_address):
        console.print(f"[red]❌ Nieprawidłowy format adresu IP: {ip_address}[/red]")
        sys.exit(1)
    
    check_ip_details(ip_address)


if __name__ == "__main__":
    main()
