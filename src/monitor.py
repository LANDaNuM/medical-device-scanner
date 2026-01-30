#!/usr/bin/env python3
"""
Moduł do monitoringu w czasie rzeczywistym (real-time monitoring).

Umożliwia:
- Ciągłe skanowanie w tle
- Alerty o nowych urządzeniach
- Alerty o zmianach bezpieczeństwa
- Przykład: --monitor --interval 300 (co 5 minut)
"""

import threading
import time
from datetime import datetime
from typing import List, Optional, Callable, Set
from rich.console import Console

from device import Device
from history_db import HistoryDB

console = Console()


class RealTimeMonitor:
    """Zarządza monitoringiem w czasie rzeczywistym"""
    
    def __init__(self,
                 scan_function: Callable,
                 interval: int = 300,
                 alert_on_new: bool = True,
                 alert_on_risk_change: bool = True,
                 email_notifier=None,
                 history_db: Optional[HistoryDB] = None):
        # email_notifier jest deprecated - zostawiamy dla kompatybilności ale nie używamy
        """
        Inicjalizacja monitora.
        
        Args:
            scan_function: Funkcja do skanowania (powinna zwracać List[Device])
            interval: Interwał skanowania w sekundach (domyślnie 300 = 5 minut)
            alert_on_new: Czy alertować o nowych urządzeniach
            alert_on_risk_change: Czy alertować o zmianach ryzyka
            email_notifier: Instancja EmailNotifier (opcjonalne)
            history_db: Instancja HistoryDB (opcjonalne)
        """
        self.scan_function = scan_function
        self.interval = interval
        self.alert_on_new = alert_on_new
        self.alert_on_risk_change = alert_on_risk_change
        self.email_notifier = email_notifier
        self.history_db = history_db or HistoryDB()
        
        self.running = False
        self.monitor_thread = None
        self.known_devices: Set[str] = set()  # Znane MAC adresy
        self.device_scores: dict = {}  # MAC -> ostatni security score
    
    def start(self, email_recipients: Optional[List[str]] = None):
        """
        Uruchamia monitoring w osobnym wątku.
        
        Args:
            email_recipients: Deprecated - nie używane (zostawione dla kompatybilności)
        """
        if self.running:
            console.print("[yellow]⚠️  Monitor już działa[/yellow]")
            return
        
        self.running = True
        
        # Załaduj znane urządzenia z historii
        if self.history_db:
            try:
                stats = self.history_db.get_statistics()
                if stats['unique_devices'] > 0:
                    console.print(f"[dim]📚 Załadowano {stats['unique_devices']} znanych urządzeń z historii[/dim]")
            except Exception:
                pass
        
        def run_monitor():
            scan_count = 0
            while self.running:
                try:
                    scan_count += 1
                    console.print(f"\n[cyan]🔍 Monitor: Skanowanie #{scan_count} ({datetime.now().strftime('%H:%M:%S')})[/cyan]")
                    
                    # Wykonaj skanowanie
                    devices = self.scan_function()
                    
                    if devices:
                        # Sprawdź nowe urządzenia
                        if self.alert_on_new:
                            new_devices = self._detect_new_devices(devices)
                            if new_devices:
                                self._handle_new_devices(new_devices)
                        
                        # Sprawdź zmiany ryzyka
                        if self.alert_on_risk_change:
                            risk_changes = self._detect_risk_changes(devices)
                            if risk_changes:
                                self._handle_risk_changes(risk_changes)
                        
                        # Zaktualizuj znane urządzenia
                        for device in devices:
                            self.known_devices.add(device.mac_address)
                            self.device_scores[device.mac_address] = device.security_score
                    
                    console.print(f"[dim]⏳ Następne skanowanie za {self.interval} sekund...[/dim]")
                    
                except Exception as e:
                    console.print(f"[red]❌ Błąd podczas monitoringu: {e}[/red]")
                
                # Czekaj na następne skanowanie
                for _ in range(self.interval):
                    if not self.running:
                        break
                    time.sleep(1)
        
        self.monitor_thread = threading.Thread(target=run_monitor, daemon=True)
        self.monitor_thread.start()
        console.print(f"[green]✅ Monitor uruchomiony (interwał: {self.interval}s)[/green]")
        console.print(f"[dim]   Alerty: nowe urządzenia={self.alert_on_new}, zmiany ryzyka={self.alert_on_risk_change}[/dim]")
    
    def stop(self):
        """Zatrzymuje monitoring"""
        self.running = False
        console.print("[yellow]⏹️  Monitor zatrzymany[/yellow]")
    
    def _detect_new_devices(self, current_devices: List[Device]) -> List[Device]:
        """Wykrywa nowe urządzenia"""
        if not self.known_devices:
            # Pierwsze skanowanie - wszystkie są nowe, ale nie alertujemy
            for device in current_devices:
                self.known_devices.add(device.mac_address)
            return []
        
        new_devices = [d for d in current_devices if d.mac_address not in self.known_devices]
        return new_devices
    
    def _detect_risk_changes(self, current_devices: List[Device]) -> List[dict]:
        """Wykrywa zmiany w security score"""
        changes = []
        
        for device in current_devices:
            mac = device.mac_address
            current_score = device.security_score
            previous_score = self.device_scores.get(mac)
            
            if previous_score is not None:
                # Sprawdź czy nastąpiła znacząca zmiana (więcej niż 20 punktów)
                if abs(current_score - previous_score) >= 20:
                    # Sprawdź czy zmiana jest na gorsze (score spadł)
                    if current_score < previous_score:
                        changes.append({
                            'device': device,
                            'previous_score': previous_score,
                            'current_score': current_score,
                            'change': current_score - previous_score
                        })
        
        return changes
    
    def _handle_new_devices(self, new_devices: List[Device]):
        """Obsługuje wykrycie nowych urządzeń"""
        console.print(f"\n[bold yellow]🔔 WYKRYTO {len(new_devices)} NOWYCH URZĄDZEŃ![/bold yellow]")
        
        for device in new_devices:
            risk_icon = "🔴" if device.security_score < 50 else "🟡" if device.security_score < 80 else "🟢"
            console.print(f"  {risk_icon} {device.name} (MAC: {device.mac_address}, Score: {device.security_score}/100)")
        
    
    def _handle_risk_changes(self, changes: List[dict]):
        """Obsługuje zmiany ryzyka"""
        console.print(f"\n[bold red]⚠️  WYKRYTO {len(changes)} ZMIAN RYZYKA![/bold red]")
        
        for change in changes:
            device = change['device']
            console.print(f"  🔴 {device.name} (MAC: {device.mac_address})")
            console.print(f"     Score: {change['previous_score']}/100 → {change['current_score']}/100 (zmiana: {change['change']:+d})")
        
