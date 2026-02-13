#!/usr/bin/env python3
"""
Real-time monitoring: continuous background scanning, alerts for new devices and risk changes.
Example: --monitor --interval 300 (every 5 minutes).
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
    """Real-time monitoring manager."""
    
    def __init__(self,
                 scan_function: Callable,
                 interval: int = 300,
                 alert_on_new: bool = True,
                 alert_on_risk_change: bool = True,
                 email_notifier=None,
                 history_db: Optional[HistoryDB] = None):
        """scan_function: returns List[Device]; interval: seconds; alert_on_new/alert_on_risk_change; history_db optional. email_notifier deprecated."""
        self.scan_function = scan_function
        self.interval = interval
        self.alert_on_new = alert_on_new
        self.alert_on_risk_change = alert_on_risk_change
        self.email_notifier = email_notifier
        self.history_db = history_db or HistoryDB()
        
        self.running = False
        self.monitor_thread = None
        self.known_devices: Set[str] = set()
        self.device_scores: dict = {}
    
    def start(self, email_recipients: Optional[List[str]] = None):
        """Start monitoring in a background thread. email_recipients deprecated."""
        if self.running:
            console.print("[yellow]⚠️  Monitor already running[/yellow]")
            return
        self.running = True
        if self.history_db:
            try:
                stats = self.history_db.get_statistics()
                if stats['unique_devices'] > 0:
                    console.print(f"[dim]📚 Loaded {stats['unique_devices']} known devices from history[/dim]")
            except Exception:
                pass
        def run_monitor():
            scan_count = 0
            while self.running:
                try:
                    scan_count += 1
                    console.print(f"\n[cyan]🔍 Monitor: Scan #{scan_count} ({datetime.now().strftime('%H:%M:%S')})[/cyan]")
                    devices = self.scan_function()
                    if devices:
                        if self.alert_on_new:
                            new_devices = self._detect_new_devices(devices)
                            if new_devices:
                                self._handle_new_devices(new_devices)
                        if self.alert_on_risk_change:
                            risk_changes = self._detect_risk_changes(devices)
                            if risk_changes:
                                self._handle_risk_changes(risk_changes)
                        for device in devices:
                            self.known_devices.add(device.mac_address)
                            self.device_scores[device.mac_address] = device.security_score
                    console.print(f"[dim]⏳ Next scan in {self.interval} seconds...[/dim]")
                except Exception as e:
                    console.print(f"[red]❌ Monitoring error: {e}[/red]")
                for _ in range(self.interval):
                    if not self.running:
                        break
                    time.sleep(1)
        self.monitor_thread = threading.Thread(target=run_monitor, daemon=True)
        self.monitor_thread.start()
        console.print(f"[green]✅ Monitor started (interval: {self.interval}s)[/green]")
        console.print(f"[dim]   Alerts: new devices={self.alert_on_new}, risk changes={self.alert_on_risk_change}[/dim]")
    
    def stop(self):
        """Stop monitoring."""
        self.running = False
        console.print("[yellow]⏹️  Monitor stopped[/yellow]")
    
    def _detect_new_devices(self, current_devices: List[Device]) -> List[Device]:
        """Detect new devices."""
        if not self.known_devices:
            for device in current_devices:
                self.known_devices.add(device.mac_address)
            return []
        
        new_devices = [d for d in current_devices if d.mac_address not in self.known_devices]
        return new_devices
    
    def _detect_risk_changes(self, current_devices: List[Device]) -> List[dict]:
        """Detect significant security score changes."""
        changes = []
        for device in current_devices:
            mac = device.mac_address
            current_score = device.security_score
            previous_score = self.device_scores.get(mac)
            if previous_score is not None:
                if abs(current_score - previous_score) >= 20:
                    if current_score < previous_score:
                        changes.append({
                            'device': device,
                            'previous_score': previous_score,
                            'current_score': current_score,
                            'change': current_score - previous_score
                        })
        
        return changes
    
    def _handle_new_devices(self, new_devices: List[Device]):
        """Handle new device detection."""
        console.print(f"\n[bold yellow]🔔 DETECTED {len(new_devices)} NEW DEVICES![/bold yellow]")
        
        for device in new_devices:
            risk_icon = "🔴" if device.security_score < 50 else "🟡" if device.security_score < 80 else "🟢"
            console.print(f"  {risk_icon} {device.name} (MAC: {device.mac_address}, Score: {device.security_score}/100)")
        
    
    def _handle_risk_changes(self, changes: List[dict]):
        """Handle risk change alerts."""
        console.print(f"\n[bold red]⚠️  DETECTED {len(changes)} RISK CHANGES![/bold red]")
        for change in changes:
            device = change['device']
            console.print(f"  🔴 {device.name} (MAC: {device.mac_address})")
            console.print(f"     Score: {change['previous_score']}/100 → {change['current_score']}/100 (change: {change['change']:+d})")
        
