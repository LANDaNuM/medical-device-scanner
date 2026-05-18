#!/usr/bin/env python3
"""
Scheduled scans: run scans at set times (cron-like). Example: --schedule "0 9 * * *" (daily at 9:00).
"""

import schedule
import time
import threading
from datetime import datetime
from typing import List, Optional, Callable
from rich.console import Console

console = Console()


class ScanScheduler:
    """Manages scheduled scans."""
    
    def __init__(self):
        """Initialize scheduler."""
        self.running = False
        self.scheduler_thread = None
        self.scan_callback: Optional[Callable] = None
    
    def add_schedule(self, schedule_str: str, scan_function: Callable, description: Optional[str] = None):
        """Add scheduled scan. schedule_str: 'daily HH:MM', 'hourly', 'every N minutes/hours', or crontab-style."""
        self.scan_callback = scan_function
        if schedule_str.startswith("daily"):
            parts = schedule_str.split()
            if len(parts) >= 2:
                time_str = parts[1]
                schedule.every().day.at(time_str).do(self._run_scheduled_scan)
                console.print(f"[green]✅ Scheduled: daily at {time_str}[/green]")
            else:
                console.print("[red]❌ Invalid format: daily HH:MM[/red]")
        elif schedule_str == "hourly":
            schedule.every().hour.do(self._run_scheduled_scan)
            console.print("[green]✅ Scheduled: hourly[/green]")
        elif schedule_str.startswith("every"):
            parts = schedule_str.split()
            if len(parts) >= 3:
                try:
                    interval = int(parts[1])
                    unit = parts[2].lower()
                    if unit.startswith("minute"):
                        schedule.every(interval).minutes.do(self._run_scheduled_scan)
                        console.print(f"[green]✅ Scheduled: every {interval} minutes[/green]")
                    elif unit.startswith("hour"):
                        schedule.every(interval).hours.do(self._run_scheduled_scan)
                        console.print(f"[green]✅ Scheduled: every {interval} hours[/green]")
                    else:
                        console.print("[red]❌ Invalid time unit (minutes/hours)[/red]")
                except ValueError:
                    console.print("[red]❌ Invalid interval[/red]")
            else:
                console.print("[red]❌ Invalid format: every N minutes/hours[/red]")
        elif len(schedule_str.split()) == 5:
            console.print("[yellow]⚠️  Crontab format not fully supported yet[/yellow]")
            console.print("[dim]   Use: 'daily HH:MM', 'hourly', or 'every N minutes'[/dim]")
        else:
            console.print(f"[red]❌ Invalid schedule format: {schedule_str}[/red]")
    
    def _run_scheduled_scan(self):
        """Internal: run scheduled scan."""
        if self.scan_callback:
            console.print(f"\n[cyan]⏰ Running scheduled scan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/cyan]")
            try:
                self.scan_callback()
            except Exception as e:
                console.print(f"[red]❌ Scheduled scan error: {e}[/red]")
    
    def start(self):
        """Start scheduler in a background thread."""
        if self.running:
            console.print("[yellow]⚠️  Scheduler already running[/yellow]")
            return
        
        self.running = True
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        console.print("[green]✅ Scheduler started[/green]")
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        schedule.clear()
        console.print("[yellow]⏹️  Scheduler stopped[/yellow]")
    
    def list_schedules(self):
        """List scheduled scans."""
        jobs = schedule.get_jobs()
        if jobs:
            console.print("\n[cyan]📅 Scheduled scans:[/cyan]")
            for job in jobs:
                console.print(f"  • {job}")
        else:
            console.print("[dim]No scheduled scans[/dim]")
