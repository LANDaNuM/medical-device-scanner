#!/usr/bin/env python3
"""
Test script to verify scanner behaviour.

Helps test the scanner safely:
1. WiFi test – runs a simple HTTP server with open ports (simulates a vulnerable device)
2. BLE test – instructions for testing with a phone
3. USB test – instructions for testing with a simple USB device

USAGE:
    python scripts/test_scanner.py --wifi    # Run WiFi test server
    python scripts/test_scanner.py --help    # Show all options
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

# Add src/ to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class TestDeviceHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler to simulate a vulnerable medical device."""
    
    def do_GET(self):
        """Handle GET requests – simulate a medical device."""
        # Simulate medical device response
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Server', 'Medical-Device-Simulator/1.0')
        self.end_headers()
        
        # Simulate medical data (FAKE – for testing only!)
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
        """Suppress HTTP logs."""
        pass


def get_local_ip():
    """Get local IP address."""
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
    Run a simple HTTP server to simulate a vulnerable medical device.
    
    Args:
        port: Port to run the server on (default 8080)
        duration: Server run time in seconds (default 300 = 5 minutes)
    """
    local_ip = get_local_ip()
    
    console.print(Panel.fit(
        "[bold cyan]🧪 WiFi test – vulnerable medical device simulator[/bold cyan]\n"
        f"[green]Test server running at:[/green] [bold]{local_ip}:{port}[/bold]\n"
        f"[dim]Duration: {duration} seconds (or Ctrl+C to stop)[/dim]\n"
        "[yellow]⚠️  This is ONLY a simulation – not a real medical device![/yellow]",
        style="cyan"
    ))
    console.print()
    
    # Start HTTP server
    server = HTTPServer((local_ip, port), TestDeviceHandler)
    
    console.print(f"[green]✅ Test server started![/green]")
    console.print(f"[cyan]   Address: http://{local_ip}:{port}[/cyan]")
    console.print(f"[cyan]   Status: Active[/cyan]")
    console.print()
    console.print("[bold yellow]📋 TEST INSTRUCTIONS:[/bold yellow]")
    console.print("1. In a second terminal run the scanner:")
    console.print(f"   [cyan]python src/scanner.py --wifi[/cyan]")
    console.print()
    console.print("2. The scanner should detect:")
    console.print(f"   • Device at address {local_ip}")
    console.print(f"   • Port {port} (HTTP) – open")
    console.print(f"   • Vulnerability: HTTP without HTTPS")
    console.print()
    console.print("3. When done, press [bold red]Ctrl+C[/bold red] to stop the server")
    console.print()
    
    try:
        # Run server in a separate thread
        server_thread = Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        
        # Wait for the specified duration
        start_time = time.time()
        while time.time() - start_time < duration:
            time.sleep(1)
            elapsed = int(time.time() - start_time)
            remaining = duration - elapsed
            if remaining % 30 == 0:  # Every 30 seconds
                console.print(f"[dim]   Server running... ({elapsed}s / {duration}s)[/dim]")
        
        console.print(f"\n[yellow]⏹️  Stopping server after {duration} seconds...[/yellow]")
        server.shutdown()
        console.print("[green]✅ Server stopped[/green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⏹️  Stopping server...[/yellow]")
        server.shutdown()
        console.print("[green]✅ Server stopped[/green]")


def show_ble_test_instructions():
    """Show BLE testing instructions (using a phone)."""
    console.print(Panel.fit(
        "[bold cyan]📱 BLE test – instructions with phone[/bold cyan]",
        style="cyan"
    ))
    console.print()
    
    console.print("[bold yellow]📋 INSTRUCTIONS:[/bold yellow]")
    console.print()
    console.print("1. [cyan]Turn on Bluetooth on your phone[/cyan]")
    console.print("   • Settings → Bluetooth → On")
    console.print()
    console.print("2. [cyan]Keep the phone in range[/cyan]")
    console.print("   • Phone should be within 10 metres")
    console.print()
    console.print("3. [cyan]Run the BLE scanner:[/cyan]")
    console.print("   [bold]python src/scanner.py --ble[/bold]")
    console.print()
    console.print("4. [green]The scanner should detect:[/green]")
    console.print("   • Your phone (device name)")
    console.print("   • Phone MAC address")
    console.print("   • RSSI (signal strength)")
    console.print()
    console.print("[yellow]💡 TIP:[/yellow] If the phone is not visible:")
    console.print("   • Check Bluetooth is on")
    console.print("   • Check the phone is not in 'Hidden' mode")
    console.print("   • Move the phone closer to the laptop")
    console.print()


def show_usb_test_instructions():
    """Show USB testing instructions."""
    console.print(Panel.fit(
        "[bold cyan]🔌 USB test – instructions[/bold cyan]",
        style="cyan"
    ))
    console.print()
    
    console.print("[bold yellow]📋 INSTRUCTIONS:[/bold yellow]")
    console.print()
    console.print("1. [cyan]Connect any USB device:[/cyan]")
    console.print("   • USB flash drive")
    console.print("   • External keyboard/mouse")
    console.print("   • Phone via USB (MTP mode)")
    console.print("   • External USB disk")
    console.print()
    console.print("2. [cyan]Run the USB scanner:[/cyan]")
    console.print("   [bold]python src/scanner.py --usb[/bold]")
    console.print()
    console.print("3. [green]The scanner should detect:[/green]")
    console.print("   • Connected USB device")
    console.print("   • Vendor ID and Product ID")
    console.print("   • Device name")
    console.print()
    console.print("[yellow]💡 TIP:[/yellow] If the device is not visible:")
    console.print("   • Check the device is connected")
    console.print("   • Check the device is powered")
    console.print("   • Try another USB port")
    console.print()


def show_full_test_guide():
    """Show full testing guide."""
    console.print(Panel.fit(
        "[bold cyan]🧪 Scanner testing guide[/bold cyan]",
        style="cyan"
    ))
    console.print()
    
    table = Table(title="Test options", show_header=True, header_style="bold cyan")
    table.add_column("Protocol", style="cyan", width=15)
    table.add_column("Test method", style="green", width=40)
    table.add_column("Difficulty", style="yellow", width=20)
    
    table.add_row("WiFi", "Test server (--wifi)", "🟢 Easy")
    table.add_row("BLE", "Phone with Bluetooth", "🟢 Easy")
    table.add_row("USB", "Flash drive / USB device", "🟢 Easy")
    table.add_row("NFC", "NFC card / phone", "🟡 Medium")
    
    console.print(table)
    console.print()
    
    console.print("[bold yellow]📋 QUICK START:[/bold yellow]")
    console.print()
    console.print("1. [cyan]WiFi test (easiest):[/cyan]")
    console.print("   [bold]python scripts/test_scanner.py --wifi[/bold]")
    console.print("   (In a second terminal: python src/scanner.py --wifi)")
    console.print()
    console.print("2. [cyan]BLE test (with phone):[/cyan]")
    console.print("   [bold]python src/scanner.py --ble[/bold]")
    console.print("   (Make sure Bluetooth is on on the phone)")
    console.print()
    console.print("3. [cyan]USB test (with flash drive):[/cyan]")
    console.print("   [bold]python src/scanner.py --usb[/bold]")
    console.print("   (Connect the drive before running)")
    console.print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test script to verify scanner behaviour',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/test_scanner.py --wifi    # Run WiFi test server
  python scripts/test_scanner.py --ble     # Show BLE test instructions
  python scripts/test_scanner.py --usb     # Show USB test instructions
  python scripts/test_scanner.py --guide   # Show full guide
        """
    )
    
    parser.add_argument('--wifi', action='store_true',
                       help='Run WiFi test server (vulnerable device simulation)')
    parser.add_argument('--port', type=int, default=8080,
                       help='Port for WiFi test server (default 8080)')
    parser.add_argument('--duration', type=int, default=300,
                       help='Server run time in seconds (default 300)')
    parser.add_argument('--ble', action='store_true',
                       help='Show BLE testing instructions')
    parser.add_argument('--usb', action='store_true',
                       help='Show USB testing instructions')
    parser.add_argument('--guide', action='store_true',
                       help='Show full testing guide')
    
    args = parser.parse_args()
    
    # If no option given, show full guide
    if not any([args.wifi, args.ble, args.usb, args.guide]):
        show_full_test_guide()
        return
    
    # Run selected tests
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
        console.print("\n[yellow]⚠️  Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
