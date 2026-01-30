#!/usr/bin/env python3
"""
Lookup producentów urządzeń na podstawie adresu MAC używając oficjalnej bazy IEEE OUI.

IEEE OUI (Organizationally Unique Identifier) to oficjalna baza danych producentów
zarządzana przez IEEE. Pierwsze 3 bajty adresu MAC (OUI) jednoznacznie identyfikują
producenta urządzenia.

Źródło: https://standards-oui.ieee.org/oui/oui.txt
"""

import os
import sys
import re
import json
from typing import Optional, Dict
from pathlib import Path

# Dodaj katalog src/ do ścieżki Python
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Ścieżka do cache OUI
OUI_CACHE_DIR = Path(script_dir).parent / "data" / "cache"
OUI_CACHE_TXT = OUI_CACHE_DIR / "oui_cache.txt"  # Stary format (tekstowy)
OUI_CACHE_JSON = OUI_CACHE_DIR / "oui_cache.json"  # Nowy format (JSON)

# URL do oficjalnej bazy IEEE OUI
IEEE_OUI_URL = "https://standards-oui.ieee.org/oui/oui.txt"


class OUILookup:
    """
    Lookup producentów na podstawie adresu MAC używając oficjalnej bazy IEEE OUI.
    
    Baza IEEE OUI jest oficjalną bazą danych zarządzaną przez IEEE (Institute of Electrical
    and Electronics Engineers). Zawiera wszystkie zarejestrowane OUI (pierwsze 3 bajty MAC)
    i odpowiadające im nazwy producentów.
    
    Przykład:
    - MAC: A6:D7:3C:DD:05:13
    - OUI: A6:D7:3C
    - Producent: "Hewlett Packard" (przykład)
    """
    
    def __init__(self, cache_file: Optional[Path] = None):
        """
        Inicjalizacja lookup OUI.
        
        Args:
            cache_file: Ścieżka do pliku cache JSON (domyślnie: data/cache/oui_cache.json)
        """
        self.cache_file = cache_file or OUI_CACHE_JSON
        self.oui_db: Dict[str, str] = {}  # OUI -> Manufacturer
        self._load_cache()
    
    def _load_cache(self):
        """Ładuje bazę OUI z cache JSON lub konwertuje z TXT, lub pobiera z IEEE."""
        # Utwórz katalog cache jeśli nie istnieje
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # PRIORYTET 1: Spróbuj załadować z cache JSON (najszybsze)
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.oui_db = json.load(f)
                if self.oui_db:
                    return
            except Exception:
                pass  # Jeśli JSON jest uszkodzony, spróbuj konwersji
        
        # PRIORYTET 2: Spróbuj skonwertować stary plik TXT do JSON
        if OUI_CACHE_TXT.exists():
            try:
                self._parse_oui_file(OUI_CACHE_TXT)
                self._save_json_cache()
                return
            except Exception:
                pass  # Jeśli konwersja nie działa, pobierz nowy
        
        # PRIORYTET 3: Pobierz z IEEE i zapisz jako JSON
        if REQUESTS_AVAILABLE:
            self._download_oui_database()
            self._save_json_cache()
    
    def _download_oui_database(self):
        """
        Pobiera oficjalną bazę OUI z IEEE i zapisuje do cache JSON.
        
        Baza IEEE OUI jest aktualizowana regularnie i zawiera wszystkie zarejestrowane
        OUI (Organizationally Unique Identifier) wraz z nazwami producentów.
        """
        if not REQUESTS_AVAILABLE:
            return
        
        try:
            from rich.console import Console
            console = Console()
            console.print("[dim]📥 Pobieram bazę IEEE OUI (pierwsze uruchomienie może zająć chwilę)...[/dim]")
            
            response = requests.get(IEEE_OUI_URL, timeout=30, stream=True)
            response.raise_for_status()
            
            # Zapisz do tymczasowego pliku TXT
            temp_txt_file = OUI_CACHE_TXT
            with open(temp_txt_file, 'w', encoding='utf-8') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk.decode('utf-8', errors='ignore'))
            
            # Parsuj plik TXT i zapisz jako JSON
            self._parse_oui_file(temp_txt_file)
            self._save_json_cache()
            console.print("[green]✅ Baza IEEE OUI załadowana i zapisana jako JSON[/green]\n")
        
        except Exception as e:
            # Jeśli nie można pobrać, użyj pustej bazy
            pass
    
    def _save_json_cache(self):
        """Zapisuje bazę OUI do pliku JSON (szybsze niż parsowanie tekstu)."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.oui_db, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # Jeśli nie można zapisać, kontynuuj z pamięcią
    
    def _parse_oui_file(self, file_path: Path):
        """
        Parsuje plik OUI i buduje słownik OUI -> Manufacturer.
        
        Format pliku IEEE OUI:
        A6-D7-3C   (hex)		Hewlett Packard
        A6D73C     (base 16)		Hewlett Packard
        			Address...
        
        Args:
            file_path: Ścieżka do pliku OUI
        """
        self.oui_db = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    # Nie używaj strip() - potrzebujemy sprawdzić całą linię z tabulatorami
                    line = line.rstrip('\n\r')
                    
                    # Format: "28-6F-B9   (hex)		Nokia Shanghai Bell Co., Ltd."
                    # Szukaj linii z OUI w formacie XX-XX-XX, (hex), i nazwa producenta (może być po tabulatorze)
                    # Użyj \t lub \s+ dla białych znaków między (hex) a nazwą
                    match = re.match(r'^([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})\s+\(hex\)[\s\t]+(.+)', line)
                    if match:
                        oui_hex = f"{match.group(1)}:{match.group(2)}:{match.group(3)}".upper()
                        manufacturer = match.group(4).strip()
                        
                        # Usuń nadmiarowe spacje (ale zachowaj pojedyncze spacje w nazwie)
                        manufacturer = re.sub(r'\s+', ' ', manufacturer)
                        
                        # Pomiń jeśli to nie jest nazwa producenta
                        if manufacturer and len(manufacturer) > 1:
                            self.oui_db[oui_hex] = manufacturer
        
        except Exception:
            # Jeśli nie można sparsować, użyj pustej bazy
            self.oui_db = {}
    
    def lookup(self, mac_address: str) -> Optional[str]:
        """
        Wyszukuje producenta na podstawie adresu MAC.
        
        Args:
            mac_address: Adres MAC urządzenia (format: "AA:BB:CC:DD:EE:FF" lub "AA-BB-CC-DD-EE-FF")
        
        Returns:
            Nazwa producenta lub None jeśli nie znaleziono
        """
        try:
            # Normalizuj format MAC (usuń myślniki/spacje, dodaj dwukropki)
            mac_normalized = mac_address.replace("-", ":").replace(" ", ":").replace(".", ":").upper()
            
            # UWAGA: Nie pomijamy losowych adresów MAC
            # Większość nowoczesnych urządzeń (telefony, laptopy) używa losowych adresów MAC
            # dla prywatności, ale OUI (pierwsze 3 bajty) może być nadal ważny
            # i może być w bazie IEEE OUI lub macvendors.com
            
            # Wyodrębnij OUI (pierwsze 3 bajty)
            mac_parts = mac_normalized.split(":")
            if len(mac_parts) < 3:
                return None
            
            oui = f"{mac_parts[0]}:{mac_parts[1]}:{mac_parts[2]}"
            
            # Wyszukaj w bazie
            return self.oui_db.get(oui)
        
        except Exception:
            return None
    
    def update_cache(self):
        """Pobiera najnowszą wersję bazy OUI z IEEE i aktualizuje cache."""
        if REQUESTS_AVAILABLE:
            self._download_oui_database()


# Globalna instancja dla łatwego dostępu
_oui_lookup_instance: Optional[OUILookup] = None


def get_oui_lookup() -> OUILookup:
    """Zwraca globalną instancję OUILookup (singleton)."""
    global _oui_lookup_instance
    if _oui_lookup_instance is None:
        _oui_lookup_instance = OUILookup()
    return _oui_lookup_instance


if __name__ == "__main__":
    # Test lookup OUI
    from rich.console import Console
    console = Console()
    
    console.print("[bold cyan]🔍 Test: IEEE OUI Lookup[/bold cyan]\n")
    
    lookup = OUILookup()
    
    # Test z przykładowymi adresami MAC
    test_macs = [
        "A6:D7:3C:DD:05:13",  # Przykład
        "68:1A:47:00:00:00",  # Apple (z bazy)
        "00:19:77:00:00:00",  # Extreme Networks (z bazy)
    ]
    
    for mac in test_macs:
        manufacturer = lookup.lookup(mac)
        console.print(f"MAC: {mac}")
        console.print(f"  Producent: {manufacturer or 'Nie znaleziono'}\n")
