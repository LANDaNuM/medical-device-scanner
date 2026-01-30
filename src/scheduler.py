#!/usr/bin/env python3
"""
Moduł do zaplanowanych skanowań (scheduled scans).

Umożliwia:
- Automatyczne skanowanie o określonych godzinach
- Cron-like scheduling
- Przykład: --schedule "0 9 * * *" (codziennie o 9:00)
"""

import schedule
import time
import threading
from datetime import datetime
from typing import List, Optional, Callable
from rich.console import Console

console = Console()


class ScanScheduler:
    """Zarządza zaplanowanymi skanowaniami"""
    
    def __init__(self):
        """Inicjalizacja schedulera"""
        self.running = False
        self.scheduler_thread = None
        self.scan_callback: Optional[Callable] = None
    
    def add_schedule(self, 
                    schedule_str: str,
                    scan_function: Callable,
                    description: Optional[str] = None):
        """
        Dodaje zaplanowane skanowanie.
        
        Args:
            schedule_str: Crontab-like string (np. "0 9 * * *" = codziennie o 9:00)
                         Lub proste formaty: "daily 09:00", "hourly", "every 30 minutes"
            scan_function: Funkcja do wywołania (powinna przyjmować brak argumentów)
            description: Opis skanowania (opcjonalne)
        
        Przykłady:
            "0 9 * * *" - codziennie o 9:00
            "0 */6 * * *" - co 6 godzin
            "daily 09:00" - codziennie o 9:00
            "hourly" - co godzinę
            "every 30 minutes" - co 30 minut
        """
        self.scan_callback = scan_function
        
        # Parsuj schedule string
        if schedule_str.startswith("daily"):
            # Format: "daily HH:MM"
            parts = schedule_str.split()
            if len(parts) >= 2:
                time_str = parts[1]
                schedule.every().day.at(time_str).do(self._run_scheduled_scan)
                console.print(f"[green]✅ Zaplanowano skanowanie: codziennie o {time_str}[/green]")
            else:
                console.print("[red]❌ Nieprawidłowy format: daily HH:MM[/red]")
        
        elif schedule_str == "hourly":
            schedule.every().hour.do(self._run_scheduled_scan)
            console.print("[green]✅ Zaplanowano skanowanie: co godzinę[/green]")
        
        elif schedule_str.startswith("every"):
            # Format: "every N minutes/hours"
            parts = schedule_str.split()
            if len(parts) >= 3:
                try:
                    interval = int(parts[1])
                    unit = parts[2].lower()
                    
                    if unit.startswith("minute"):
                        schedule.every(interval).minutes.do(self._run_scheduled_scan)
                        console.print(f"[green]✅ Zaplanowano skanowanie: co {interval} minut[/green]")
                    elif unit.startswith("hour"):
                        schedule.every(interval).hours.do(self._run_scheduled_scan)
                        console.print(f"[green]✅ Zaplanowano skanowanie: co {interval} godzin[/green]")
                    else:
                        console.print("[red]❌ Nieprawidłowa jednostka czasu (minutes/hours)[/red]")
                except ValueError:
                    console.print("[red]❌ Nieprawidłowy interwał[/red]")
            else:
                console.print("[red]❌ Nieprawidłowy format: every N minutes/hours[/red]")
        
        elif len(schedule_str.split()) == 5:
            # Crontab format: "minute hour day month weekday"
            # TODO: Implementacja pełnego parsowania crontab
            console.print("[yellow]⚠️  Crontab format nie jest jeszcze w pełni obsługiwany[/yellow]")
            console.print("[dim]   Użyj: 'daily HH:MM', 'hourly', lub 'every N minutes'[/dim]")
        else:
            console.print(f"[red]❌ Nieprawidłowy format schedule: {schedule_str}[/red]")
    
    def _run_scheduled_scan(self):
        """Wewnętrzna funkcja wywoływana przez scheduler"""
        if self.scan_callback:
            console.print(f"\n[cyan]⏰ Uruchamiam zaplanowane skanowanie: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/cyan]")
            try:
                self.scan_callback()
            except Exception as e:
                console.print(f"[red]❌ Błąd podczas zaplanowanego skanowania: {e}[/red]")
    
    def start(self):
        """Uruchamia scheduler w osobnym wątku"""
        if self.running:
            console.print("[yellow]⚠️  Scheduler już działa[/yellow]")
            return
        
        self.running = True
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        console.print("[green]✅ Scheduler uruchomiony[/green]")
    
    def stop(self):
        """Zatrzymuje scheduler"""
        self.running = False
        schedule.clear()
        console.print("[yellow]⏹️  Scheduler zatrzymany[/yellow]")
    
    def list_schedules(self):
        """Wyświetla listę zaplanowanych skanowań"""
        jobs = schedule.get_jobs()
        if jobs:
            console.print("\n[cyan]📅 Zaplanowane skanowania:[/cyan]")
            for job in jobs:
                console.print(f"  • {job}")
        else:
            console.print("[dim]Brak zaplanowanych skanowań[/dim]")
