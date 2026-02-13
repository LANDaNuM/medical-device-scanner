#!/usr/bin/env python3
"""
Look up device manufacturers by MAC address using the official IEEE OUI database.

IEEE OUI (Organizationally Unique Identifier) is the official IEEE database; the first 3 bytes of MAC (OUI) identify the manufacturer. Source: https://standards-oui.ieee.org/oui/oui.txt
"""

import os
import sys
import re
import json
from typing import Optional, Dict
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

OUI_CACHE_DIR = Path(script_dir).parent / "data" / "cache"
OUI_CACHE_TXT = OUI_CACHE_DIR / "oui_cache.txt"
OUI_CACHE_JSON = OUI_CACHE_DIR / "oui_cache.json"
IEEE_OUI_URL = "https://standards-oui.ieee.org/oui/oui.txt"


class OUILookup:
    """Look up manufacturers by MAC address using the official IEEE OUI database (OUI = first 3 bytes of MAC)."""
    
    def __init__(self, cache_file: Optional[Path] = None):
        """cache_file: path to JSON cache (default: data/cache/oui_cache.json)."""
        self.cache_file = cache_file or OUI_CACHE_JSON
        self.oui_db: Dict[str, str] = {}  # OUI -> Manufacturer
        self._load_cache()
    
    def _load_cache(self):
        """Load OUI DB from JSON cache, or convert from TXT, or fetch from IEEE."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.oui_db = json.load(f)
                if self.oui_db:
                    return
            except Exception:
                pass
        if OUI_CACHE_TXT.exists():
            try:
                self._parse_oui_file(OUI_CACHE_TXT)
                self._save_json_cache()
                return
            except Exception:
                pass
        if REQUESTS_AVAILABLE:
            self._download_oui_database()
            self._save_json_cache()
    
    def _download_oui_database(self):
        """Download official IEEE OUI database and save to JSON cache."""
        if not REQUESTS_AVAILABLE:
            return
        try:
            from rich.console import Console
            console = Console()
            console.print("[dim]📥 Downloading IEEE OUI database (first run may take a moment)...[/dim]")
            response = requests.get(IEEE_OUI_URL, timeout=30, stream=True)
            response.raise_for_status()
            temp_txt_file = OUI_CACHE_TXT
            with open(temp_txt_file, 'w', encoding='utf-8') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk.decode('utf-8', errors='ignore'))
            self._parse_oui_file(temp_txt_file)
            self._save_json_cache()
            console.print("[green]✅ IEEE OUI database loaded and saved as JSON[/green]\n")
        except Exception:
            pass
    
    def _save_json_cache(self):
        """Save OUI DB to JSON file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.oui_db, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def _parse_oui_file(self, file_path: Path):
        """Parse IEEE OUI file and build OUI -> Manufacturer dict."""
        self.oui_db = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.rstrip('\n\r')
                    match = re.match(r'^([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})-([0-9A-Fa-f]{2})\s+\(hex\)[\s\t]+(.+)', line)
                    if match:
                        oui_hex = f"{match.group(1)}:{match.group(2)}:{match.group(3)}".upper()
                        manufacturer = match.group(4).strip()
                        manufacturer = re.sub(r'\s+', ' ', manufacturer)
                        if manufacturer and len(manufacturer) > 1:
                            self.oui_db[oui_hex] = manufacturer
        
        except Exception:
            self.oui_db = {}
    
    def lookup(self, mac_address: str) -> Optional[str]:
        """Look up manufacturer by MAC address (format AA:BB:CC:DD:EE:FF or AA-BB-CC-DD-EE-FF). Returns manufacturer name or None."""
        try:
            mac_normalized = mac_address.replace("-", ":").replace(" ", ":").replace(".", ":").upper()
            mac_parts = mac_normalized.split(":")
            if len(mac_parts) < 3:
                return None
            
            oui = f"{mac_parts[0]}:{mac_parts[1]}:{mac_parts[2]}"
            return self.oui_db.get(oui)
        
        except Exception:
            return None
    
    def update_cache(self):
        """Fetch latest IEEE OUI database and update cache."""
        if REQUESTS_AVAILABLE:
            self._download_oui_database()


_oui_lookup_instance: Optional[OUILookup] = None


def get_oui_lookup() -> OUILookup:
    """Return global OUILookup singleton."""
    global _oui_lookup_instance
    if _oui_lookup_instance is None:
        _oui_lookup_instance = OUILookup()
    return _oui_lookup_instance


if __name__ == "__main__":
    from rich.console import Console
    console = Console()
    console.print("[bold cyan]🔍 Test: IEEE OUI Lookup[/bold cyan]\n")
    lookup = OUILookup()
    test_macs = [
        "A6:D7:3C:DD:05:13",
        "68:1A:47:00:00:00",
        "00:19:77:00:00:00",
    ]
    for mac in test_macs:
        manufacturer = lookup.lookup(mac)
        console.print(f"MAC: {mac}")
        console.print(f"  Manufacturer: {manufacturer or 'Not found'}\n")
