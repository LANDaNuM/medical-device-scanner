#!/usr/bin/env python3
"""
Skrypt testowy do weryfikacji działania skanera.

Ten skrypt pomaga przetestować skaner w bezpieczny sposób:
1. Test WiFi - uruchamia prosty serwer HTTP z otwartymi portami (symulacja podatnego urządzenia)
2. Test BLE - instrukcje jak przetestować z telefonem
3. Test USB - instrukcje jak przetestować z prostym urządzeniem

UŻYCIE:
    python scripts/test_scanner.py --wifi    # Uruchom serwer testowy WiFi
    python scripts/test_scanner.py --help   # Pokaż wszystkie opcje
"""

import sys
import os
import socket
import subprocess
import time
import argparse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

# Dodaj katalog src/ do ścieżki
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class TestDeviceHandler(BaseHTTPRequestHandler):
    """Prosty handler HTTP dla symulacji podatnego urządzenia medycznego."""
    
    def do_GET(self):
        """Obsługuje żądania GET - symuluje urządzenie medyczne."""
        # Symuluj odpowiedź urządzenia medycznego
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Server', 'Medical-Device-Simulator/1.0')
        self.end_headers()
        
        # Symuluj dane medyczne (FAŁSZYWE - tylko do testów!)
        response = """
        <html>
        <head><title>Medical Device Simulator</title></head>
        <body>
            <h1>Medical Device Simulator (TEST ONLY)</h1>
            <p>This is a test device for scanner verification.</p>
            <p><strong>⚠️ WARNING:</strong> This is NOT a real medical device!</p>
            <p>Device Type: Glucose Meter Simulator</p>
            <p>Status: Active</p>
            <p>Security: ⚠️ Vulnerable (HTTP without HTTPS)</p>
        </body>
        </html>
        """
        self.wfile.write(response.encode())
    
    def log_message(self, format, *args):
        """Wycisz logi HTTP."""
        pass


def get_local_ip():
    """Pobiera lokalny adres IP."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def run_test_wifi_server(port=8080, duration=300):
    """
    Uruchamia prosty serwer HTTP jako symulacja podatnego urządzenia medycznego.
    
    Args:
        port: Port na którym uruchomić serwer (domyślnie 8080)
        duration: Czas działania serwera w sekundach (domyślnie 300 = 5 minut)
    """
    local_ip = get_local_ip()
    
    console.print(Panel.fit(
        "[bold cyan]🧪 Test WiFi - Symulacja Podatnego Urządzenia Medycznego[/bold cyan]\n"
        f"[green]Serwer testowy uruchomiony na:[/green] [bold]{local_ip}:{port}[/bold]\n"
        f"[dim]Czas działania: {duration} sekund (lub Ctrl+C aby zatrzymać)[/dim]\n"
        "[yellow]⚠️  To jest TYLKO symulacja - nie prawdziwe urządzenie medyczne![/yellow]",
        style="cyan"
    ))
    console.print()
    
    # Uruchom serwer HTTP
    server = HTTPServer((local_ip, port), TestDeviceHandler)
    
    console.print(f"[green]✅ Serwer testowy uruchomiony![/green]")
    console.print(f"[cyan]   Adres: http://{local_ip}:{port}[/cyan]")
    console.print(f"[cyan]   Status: Aktywny[/cyan]")
    console.print()
    console.print("[bold yellow]📋 INSTRUKCJE TESTU:[/bold yellow]")
    console.print("1. W drugim terminalu uruchom skaner:")
    console.print(f"   [cyan]python src/scanner.py --wifi[/cyan]")
    console.print()
    console.print("2. Skaner powinien wykryć:")
    console.print(f"   • Urządzenie na adresie {local_ip}")
    console.print(f"   • Port {port} (HTTP) - otwarty")
    console.print(f"   • Podatność: HTTP bez HTTPS")
    console.print()
    console.print("3. Po zakończeniu testu naciśnij [bold red]Ctrl+C[/bold red] aby zatrzymać serwer")
    console.print()
    
    try:
        # Uruchom serwer w osobnym wątku
        server_thread = Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        
        # Czekaj przez określony czas
        start_time = time.time()
        while time.time() - start_time < duration:
            time.sleep(1)
            elapsed = int(time.time() - start_time)
            remaining = duration - elapsed
            if remaining % 30 == 0:  # Co 30 sekund
                console.print(f"[dim]   Serwer działa... ({elapsed}s / {duration}s)[/dim]")
        
        console.print(f"\n[yellow]⏹️  Zatrzymywanie serwera po {duration} sekundach...[/yellow]")
        server.shutdown()
        console.print("[green]✅ Serwer zatrzymany[/green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⏹️  Zatrzymywanie serwera...[/yellow]")
        server.shutdown()
        console.print("[green]✅ Serwer zatrzymany[/green]")


def show_ble_test_instructions():
    """Pokazuje instrukcje testowania BLE z telefonem."""
    console.print(Panel.fit(
        "[bold cyan]📱 Test BLE - Instrukcje Testowania z Telefonem[/bold cyan]",
        style="cyan"
    ))
    console.print()
    
    console.print("[bold yellow]📋 INSTRUKCJE:[/bold yellow]")
    console.print()
    console.print("1. [cyan]Włącz Bluetooth na telefonie[/cyan]")
    console.print("   • Ustawienia → Bluetooth → Włącz")
    console.print()
    console.print("2. [cyan]Upewnij się że telefon jest w zasięgu[/cyan]")
    console.print("   • Telefon powinien być w odległości < 10 metrów")
    console.print()
    console.print("3. [cyan]Uruchom skaner BLE:[/cyan]")
    console.print("   [bold]python src/scanner.py --ble[/bold]")
    console.print()
    console.print("4. [green]Skaner powinien wykryć:[/green]")
    console.print("   • Twój telefon (nazwa urządzenia)")
    console.print("   • Adres MAC telefonu")
    console.print("   • RSSI (siła sygnału)")
    console.print()
    console.print("[yellow]💡 TIP:[/yellow] Jeśli telefon nie jest widoczny:")
    console.print("   • Sprawdź czy Bluetooth jest włączony")
    console.print("   • Sprawdź czy telefon nie jest w trybie 'Niewidoczny'")
    console.print("   • Spróbuj zbliżyć telefon do laptopa")
    console.print()


def show_usb_test_instructions():
    """Pokazuje instrukcje testowania USB."""
    console.print(Panel.fit(
        "[bold cyan]🔌 Test USB - Instrukcje Testowania[/bold cyan]",
        style="cyan"
    ))
    console.print()
    
    console.print("[bold yellow]📋 INSTRUKCJE:[/bold yellow]")
    console.print()
    console.print("1. [cyan]Podłącz dowolne urządzenie USB:[/cyan]")
    console.print("   • Pendrive USB")
    console.print("   • Zewnętrzna klawiatura/mysz")
    console.print("   • Telefon przez USB (tryb MTP)")
    console.print("   • Zewnętrzny dysk USB")
    console.print()
    console.print("2. [cyan]Uruchom skaner USB:[/cyan]")
    console.print("   [bold]python src/scanner.py --usb[/bold]")
    console.print()
    console.print("3. [green]Skaner powinien wykryć:[/green]")
    console.print("   • Podłączone urządzenie USB")
    console.print("   • Vendor ID i Product ID")
    console.print("   • Nazwę urządzenia")
    console.print()
    console.print("[yellow]💡 TIP:[/yellow] Jeśli urządzenie nie jest widoczne:")
    console.print("   • Sprawdź czy urządzenie jest podłączone")
    console.print("   • Sprawdź czy urządzenie jest zasilone")
    console.print("   • Spróbuj innego portu USB")
    console.print()


def show_full_test_guide():
    """Pokazuje pełny przewodnik testowania."""
    console.print(Panel.fit(
        "[bold cyan]🧪 Pełny Przewodnik Testowania Skanera[/bold cyan]",
        style="cyan"
    ))
    console.print()
    
    table = Table(title="Opcje Testowania", show_header=True, header_style="bold cyan")
    table.add_column("Protokół", style="cyan", width=15)
    table.add_column("Metoda Testu", style="green", width=40)
    table.add_column("Poziom Trudności", style="yellow", width=20)
    
    table.add_row("WiFi", "Serwer testowy (--wifi)", "🟢 Łatwe")
    table.add_row("BLE", "Telefon z Bluetooth", "🟢 Łatwe")
    table.add_row("USB", "Pendrive/urządzenie USB", "🟢 Łatwe")
    table.add_row("NFC", "Karta NFC/telefon", "🟡 Średnie")
    
    console.print(table)
    console.print()
    
    console.print("[bold yellow]📋 SZYBKI START:[/bold yellow]")
    console.print()
    console.print("1. [cyan]Test WiFi (najłatwiejszy):[/cyan]")
    console.print("   [bold]python scripts/test_scanner.py --wifi[/bold]")
    console.print("   (W drugim terminalu: python src/scanner.py --wifi)")
    console.print()
    console.print("2. [cyan]Test BLE (z telefonem):[/cyan]")
    console.print("   [bold]python src/scanner.py --ble[/bold]")
    console.print("   (Upewnij się że Bluetooth jest włączony na telefonie)")
    console.print()
    console.print("3. [cyan]Test USB (z pendrive):[/cyan]")
    console.print("   [bold]python src/scanner.py --usb[/bold]")
    console.print("   (Podłącz pendrive przed uruchomieniem)")
    console.print()


def main():
    """Główna funkcja."""
    parser = argparse.ArgumentParser(
        description='Skrypt testowy do weryfikacji działania skanera',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  python scripts/test_scanner.py --wifi          # Uruchom serwer testowy WiFi
  python scripts/test_scanner.py --ble           # Pokaż instrukcje testu BLE
  python scripts/test_scanner.py --usb           # Pokaż instrukcje testu USB
  python scripts/test_scanner.py --guide         # Pokaż pełny przewodnik
        """
    )
    
    parser.add_argument('--wifi', action='store_true',
                       help='Uruchom serwer testowy WiFi (symulacja podatnego urządzenia)')
    parser.add_argument('--port', type=int, default=8080,
                       help='Port dla serwera testowego WiFi (domyślnie 8080)')
    parser.add_argument('--duration', type=int, default=300,
                       help='Czas działania serwera w sekundach (domyślnie 300)')
    parser.add_argument('--ble', action='store_true',
                       help='Pokaż instrukcje testowania BLE')
    parser.add_argument('--usb', action='store_true',
                       help='Pokaż instrukcje testowania USB')
    parser.add_argument('--guide', action='store_true',
                       help='Pokaż pełny przewodnik testowania')
    
    args = parser.parse_args()
    
    # Jeśli nie podano żadnej opcji, pokaż pełny przewodnik
    if not any([args.wifi, args.ble, args.usb, args.guide]):
        show_full_test_guide()
        return
    
    # Wykonaj wybrane testy
    if args.wifi:
        run_test_wifi_server(port=args.port, duration=args.duration)
    elif args.ble:
        show_ble_test_instructions()
    elif args.usb:
        show_usb_test_instructions()
    elif args.guide:
        show_full_test_guide()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Przerwano przez użytkownika[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]❌ Błąd: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
