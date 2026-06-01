#!/usr/bin/env python3
"""
Real-time monitoring of medical devices for security changes and anomalies.
Detects new devices and alerts on security score changes.
"""

import threading
import time
from typing import List, Dict, Optional, Set, Callable, Any
from datetime import datetime
from rich.console import Console

console = Console()

class HistoryDB:
    """Placeholder for history database."""
    def get_statistics(self) -> Dict[str, int]:
        return {'unique_devices': 0}
    
    def save_device(self, device: Any) -> None:
        pass


class DeviceMonitor:
    """
    Monitors medical devices in real-time.
    
    Features:
    - Detects new devices on network
    - Tracks security score changes
    - Thread-safe with locks
    - Graceful shutdown handling
    """
    
    def __init__(self,
                 scan_function: Callable[[], List[Any]],
                 interval: int = 300,
                 alert_on_new: bool = True,
                 alert_on_risk_change: bool = True,
                 email_notifier: Optional[Any] = None,
                 history_db: Optional[HistoryDB] = None) -> None:
        """
        Initialize device monitor.
        
        Args:
            scan_function: Function that returns List[Device]
            interval: Scan interval in seconds (default: 300)
            alert_on_new: Alert on new devices (default: True)
            alert_on_risk_change: Alert on security score changes (default: True)
            email_notifier: Optional email notifier (deprecated)
            history_db: Optional history database
        """
        self.scan_function: Callable[[], List[Any]] = scan_function
        self.interval: int = interval
        self.alert_on_new: bool = alert_on_new
        self.alert_on_risk_change: bool = alert_on_risk_change
        self.email_notifier: Optional[Any] = email_notifier
        self.history_db: HistoryDB = history_db or HistoryDB()
        
        self.running: bool = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.known_devices: Set[str] = set()
        self.device_scores: Dict[str, int] = {}
        self._lock: threading.Lock = threading.Lock()
    
    def start(self, email_recipients: Optional[List[str]] = None) -> None:
        """
        Start monitoring in a background thread (thread-safe).
        
        Args:
            email_recipients: Optional email recipients list (deprecated)
        """
        with self._lock:
            if self.running:
                console.print("[yellow]⚠️  Monitor already running[/yellow]")
                return
            self.running = True
        
        # Load history if available
        if self.history_db:
            try:
                stats = self.history_db.get_statistics()
                if stats['unique_devices'] > 0:
                    console.print(f"[dim]📚 Loaded {stats['unique_devices']} known devices from history[/dim]")
            except Exception as e:
                console.print(f"[yellow]⚠️  Error loading history: {type(e).__name__}: {e}[/yellow]")
        
        def run_monitor() -> None:
            """Main monitoring loop (thread-safe)."""
            scan_count = 0
            while True:
                # Check if should stop (thread-safe)
                with self._lock:
                    if not self.running:
                        break
                
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
                        
                        # Update known devices (thread-safe)
                        with self._lock:
                            for device in devices:
                                self.known_devices.add(device.mac_address)
                                self.device_scores[device.mac_address] = device.security_score
                    
                    console.print(f"[dim]⏳ Next scan in {self.interval} seconds...[/dim]")
                
                except KeyboardInterrupt:
                    console.print("[yellow]⚠️  Monitor interrupted by user[/yellow]")
                    with self._lock:
                        self.running = False
                    break
                except Exception as e:
                    console.print(f"[red]❌ Monitoring error: {type(e).__name__}: {e}[/red]")
                
                # Sleep with periodic checks (allows quick shutdown)
                for _ in range(self.interval):
                    with self._lock:
                        if not self.running:
                            break
                    time.sleep(1)
        
        self.monitor_thread = threading.Thread(target=run_monitor, daemon=True)
        self.monitor_thread.start()
        console.print(f"[green]✅ Monitor started (interval: {self.interval}s)[/green]")
        console.print(f"[dim]   Alerts: new_devices={self.alert_on_new}, risk_changes={self.alert_on_risk_change}[/dim]")
    
    def stop(self) -> None:
        """Stop monitoring (thread-safe)."""
        with self._lock:
            self.running = False
        console.print("[yellow]⏹️  Monitor stopped[/yellow]")
    
    def _detect_new_devices(self, current_devices: List[Any]) -> List[Any]:
        """
        Detect new devices (thread-safe read).
        
        Args:
            current_devices: List of currently scanned devices
            
        Returns:
            List of newly detected devices
        """
        with self._lock:
            if not self.known_devices:
                for device in current_devices:
                    self.known_devices.add(device.mac_address)
                return []
            
            new_devices = [d for d in current_devices if d.mac_address not in self.known_devices]
        
        return new_devices
    
    def _detect_risk_changes(self, current_devices: List[Any]) -> List[Dict[str, Any]]:
        """
        Detect significant security score changes (thread-safe).
        
        Args:
            current_devices: List of currently scanned devices
            
        Returns:
            List of devices with significant security score changes
        """
        changes: List[Dict[str, Any]] = []
        
        with self._lock:
            for device in current_devices:
                mac = device.mac_address
                if mac in self.device_scores:
                    old_score = self.device_scores[mac]
                    new_score = device.security_score
                    
                    # Alert on significant changes (>= 10 points)
                    if abs(old_score - new_score) >= 10:
                        changes.append({
                            'mac_address': mac,
                            'device_name': device.name,
                            'old_score': old_score,
                            'new_score': new_score,
                            'change': new_score - old_score,
                            'timestamp': datetime.now().isoformat()
                        })
        
        return changes
    
    def _handle_new_devices(self, devices: List[Any]) -> None:
        """
        Handle detection of new devices.
        
        Args:
            devices: List of newly detected devices
        """
        console.print(f"\n[yellow]🚨 ALERT: {len(devices)} new device(s) detected![/yellow]")
        for device in devices:
            console.print(f"  • {device.name} ({device.mac_address})")
            console.print(f"    Security Score: {device.security_score}/100")
    
    def _handle_risk_changes(self, changes: List[Dict[str, Any]]) -> None:
        """
        Handle security score changes.
        
        Args:
            changes: List of devices with score changes
        """
        console.print(f"\n[yellow]⚠️  ALERT: {len(changes)} device(s) with security changes![/yellow]")
        for change in changes:
            direction = "↑ IMPROVED" if change['change'] > 0 else "↓ DEGRADED"
            console.print(f"  • {change['device_name']}: {change['old_score']} → {change['new_score']} ({direction})")


if __name__ == "__main__":
    console.print("[cyan]DeviceMonitor module loaded[/cyan]")
