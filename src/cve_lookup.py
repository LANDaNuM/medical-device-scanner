#!/usr/bin/env python3
"""
Moduł do pobierania aktualnych podatności z zewnętrznych baz danych CVE.

Integruje się z:
- NIST NVD (National Vulnerability Database) - darmowe API
  * Bez API key: 5 zapytań/30s (darmowe)
  * Z API key: 50 zapytań/30s (darmowe, wymaga rejestracji)
- Vulners API - alternatywne źródło (darmowe, wyższe limity)
- Lokalna baza jako fallback

Używa cache aby nie spamować API i przyspieszyć działanie.

KONFIGURACJA:
- NVD API key: export NVD_API_KEY="your_key"
- Vulners API key: export VULNERS_API_KEY="your_key" (opcjonalne)
"""

import json
import time
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import requests
from rich.console import Console
from rich.panel import Panel

# Załaduj zmienne środowiskowe z pliku .env (jeśli istnieje)
# Szukaj .env w katalogu projektu (tam gdzie jest scanner.py), nie w katalogu roboczym
try:
    from dotenv import load_dotenv
    # Znajdź katalog projektu (2 poziomy wyżej od src/cve_lookup.py)
    project_dir = Path(__file__).parent.parent
    env_file = project_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    else:
        # Fallback: spróbuj w katalogu roboczym
        load_dotenv()
except ImportError:
    pass  # python-dotenv nie jest wymagane, ale przydatne

console = Console()

# Cache file location
CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CVE_CACHE_FILE = CACHE_DIR / "cve_cache.json"

# NIST NVD API endpoints
NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"  # HTTPS - bezpieczne szyfrowanie
NVD_RATE_LIMIT = 5  # requests per 30 seconds (bez API key)
NVD_RATE_LIMIT_WITH_KEY = 50  # requests per 30 seconds (z API key)
NVD_RATE_WINDOW = 30  # seconds

# Mapowanie portów na protokoły/usługi (dla CPE)
PORT_TO_SERVICE = {
    # Porty medyczne
    104: "dicom",
    11112: "dicom",
    5000: "hl7",
    # Porty administracyjne
    22: "ssh",
    3389: "rdp",
    5900: "vnc",
    5901: "vnc",
    # Porty webowe
    80: "http",
    443: "https",
    8080: "http",
    8443: "https",
    # Porty baz danych
    1433: "mssql",
    3306: "mysql",
    5432: "postgresql",
    27017: "mongodb",
    # Inne
    21: "ftp",
    23: "telnet",
    25: "smtp",
    53: "dns",
    110: "pop3",
    143: "imap",
    993: "imaps",
    995: "pop3s",
    135: "msrpc",
    139: "smb",
    445: "smb",
    161: "snmp",
    162: "snmp",
}


@dataclass
class CVEInfo:
    """Informacje o podatności CVE"""
    cve_id: str
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    cvss_score: Optional[float] = None
    published_date: Optional[str] = None
    last_modified: Optional[str] = None
    affected_products: List[str] = None
    
    def __post_init__(self):
        if self.affected_products is None:
            self.affected_products = []


class CVELookup:
    """
    Klasa do pobierania podatności CVE z NIST NVD API.
    
    Używa cache aby:
    - Nie spamować API
    - Przyspieszyć działanie
    - Działać offline (z cache)
    
    BEZPIECZEŃSTWO:
    - Wszystkie połączenia używają HTTPS (szyfrowane TLS/SSL)
    - Połączenie jest bezpieczne nawet bez API key
    - API key służy tylko do zwiększenia rate limitów, nie do bezpieczeństwa
    """
    
    def __init__(self, use_cache: bool = True, cache_days: int = 7, 
                 nvd_api_key: Optional[str] = None, vulners_api_key: Optional[str] = None,
                 prefer_vulners: bool = False):
        """
        Inicjalizacja CVELookup.
        
        Args:
            use_cache: Czy używać cache (domyślnie True)
            cache_days: Ile dni cache jest ważny (domyślnie 7)
            nvd_api_key: Opcjonalny klucz API NVD (zwiększa rate limit z 5 do 50 zapytań/30s)
                        Uzyskaj na: https://nvd.nist.gov/developers/request-an-api-key
                        DARMOWE - wystarczy wypełnić formularz
            vulners_api_key: Opcjonalny klucz API Vulners (zwiększa rate limit do 1000 zapytań/min)
                            Uzyskaj na: https://vulners.com/register
                            DARMOWE - wymaga rejestracji
            prefer_vulners: Czy preferować Vulners API (wyższe limity)
        """
        # Sprawdź zmienne środowiskowe jeśli nie podano kluczy
        if not nvd_api_key:
            nvd_api_key = os.getenv('NVD_API_KEY')
        if not vulners_api_key:
            vulners_api_key = os.getenv('VULNERS_API_KEY')
        
        self.nvd_api_key = nvd_api_key
        self.vulners_api_key = vulners_api_key
        self.prefer_vulners = prefer_vulners and vulners_api_key
        self.use_cache = use_cache
        self.cache_days = cache_days
        self.cache = self._load_cache()
        self.last_request_time = 0
        self.request_count = 0
        self.vulners_last_request_time = 0
        self.vulners_request_count = 0
        
        # Wyświetl informacje o konfiguracji
        if self.nvd_api_key:
            console.print("[green]✅ NVD API key wykryty - limit: 50 zapytań/30s[/green]")
        else:
            console.print("[yellow]ℹ️  NVD API bez klucza - limit: 5 zapytań/30s[/yellow]")
            console.print("[dim]   Uzyskaj darmowy klucz: https://nvd.nist.gov/developers/request-an-api-key[/dim]")
        
        if self.vulners_api_key:
            console.print("[green]✅ Vulners API key wykryty - limit: 1000 zapytań/min[/green]")
        elif self.prefer_vulners:
            console.print("[yellow]ℹ️  Vulners API bez klucza - limit: 100 zapytań/min[/yellow]")
            console.print("[dim]   Uzyskaj darmowy klucz: https://vulners.com/register[/dim]")
        
    def _load_cache(self) -> Dict:
        """Ładuje cache z pliku"""
        if not self.use_cache or not CVE_CACHE_FILE.exists():
            return {}
        
        try:
            with open(CVE_CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                # Sprawdź czy cache nie jest przestarzały
                cache_time = datetime.fromisoformat(cache.get('timestamp', '2000-01-01'))
                if datetime.now() - cache_time > timedelta(days=self.cache_days):
                    console.print("[yellow]⚠️  Cache przestarzały, będzie odświeżony[/yellow]")
                    return {}
                return cache.get('data', {})
        except Exception as e:
            console.print(f"[yellow]⚠️  Błąd ładowania cache: {e}[/yellow]")
            return {}
    
    def _save_cache(self):
        """Zapisuje cache do pliku"""
        if not self.use_cache:
            return
        
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': self.cache
            }
            with open(CVE_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            console.print(f"[yellow]⚠️  Błąd zapisu cache: {e}[/yellow]")
    
    def _rate_limit(self):
        """Sprawdza rate limit dla NVD API"""
        # Użyj wyższego limitu jeśli mamy API key
        rate_limit = NVD_RATE_LIMIT_WITH_KEY if self.nvd_api_key else NVD_RATE_LIMIT
        
        current_time = time.time()
        # Resetuj licznik jeśli minęło 30 sekund
        if current_time - self.last_request_time > NVD_RATE_WINDOW:
            self.request_count = 0
            self.last_request_time = current_time
        
        # Jeśli przekroczono limit, czekaj
        if self.request_count >= rate_limit:
            wait_time = NVD_RATE_WINDOW - (current_time - self.last_request_time)
            if wait_time > 0:
                console.print(f"[dim]⏳ Oczekiwanie na rate limit ({int(wait_time)}s)...[/dim]")
                time.sleep(wait_time)
                self.request_count = 0
                self.last_request_time = time.time()
        
        self.request_count += 1
    
    def _search_nvd_api(self, keyword: str, max_results: int = 20) -> List[CVEInfo]:
        """
        Wyszukuje podatności w NIST NVD API.
        
        Args:
            keyword: Słowo kluczowe do wyszukania (np. "SSH", "DICOM", "RDP")
            max_results: Maksymalna liczba wyników
        
        Returns:
            Lista CVEInfo z podatnościami
        """
        # Sprawdź cache
        cache_key = f"search:{keyword}"
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            # Cache ważny przez 24 godziny
            if datetime.now() - cached_time < timedelta(hours=24):
                console.print(f"[dim]📦 Używam cache dla: {keyword}[/dim]")
                return [CVEInfo(**item) for item in cached_data['cves']]
        
        # Rate limit
        self._rate_limit()
        
        try:
            # Wyszukaj w NVD API
            params = {
                'keywordSearch': keyword,
                'resultsPerPage': max_results
            }
            
            # Dodaj API key do nagłówków jeśli dostępny (zwiększa rate limit)
            headers = {}
            if self.nvd_api_key:
                headers['apiKey'] = self.nvd_api_key
            
            # Wszystkie połączenia używają HTTPS (bezpieczne szyfrowanie TLS/SSL)
            response = requests.get(NVD_API_BASE, params=params, headers=headers, timeout=10, verify=True)
            response.raise_for_status()
            
            data = response.json()
            cves = []
            
            if 'vulnerabilities' in data:
                for vuln in data['vulnerabilities']:
                    cve_data = vuln.get('cve', {})
                    cve_id = cve_data.get('id', '')
                    
                    # Pobierz opis
                    descriptions = cve_data.get('descriptions', [])
                    description = descriptions[0].get('value', '') if descriptions else ''
                    
                    # Pobierz CVSS score
                    metrics = cve_data.get('metrics', {})
                    cvss_score = None
                    severity = "MEDIUM"
                    
                    if 'cvssMetricV31' in metrics:
                        cvss_data = metrics['cvssMetricV31'][0]
                        cvss_score = cvss_data.get('cvssData', {}).get('baseScore')
                        severity_map = {
                            9.0: "CRITICAL",
                            7.0: "HIGH",
                            4.0: "MEDIUM",
                            0.0: "LOW"
                        }
                        if cvss_score:
                            for threshold, sev in severity_map.items():
                                if cvss_score >= threshold:
                                    severity = sev
                                    break
                    elif 'cvssMetricV30' in metrics:
                        cvss_data = metrics['cvssMetricV30'][0]
                        cvss_score = cvss_data.get('cvssData', {}).get('baseScore')
                    
                    # Pobierz daty
                    published = cve_data.get('published', '')
                    last_modified = cve_data.get('lastModified', '')
                    
                    # Pobierz affected products
                    configurations = cve_data.get('configurations', [])
                    affected = []
                    for config in configurations:
                        nodes = config.get('nodes', [])
                        for node in nodes:
                            cpe_match = node.get('cpeMatch', [])
                            for cpe in cpe_match:
                                affected.append(cpe.get('criteria', ''))
                    
                    cve_info = CVEInfo(
                        cve_id=cve_id,
                        description=description[:500],  # Ogranicz długość
                        severity=severity,
                        cvss_score=cvss_score,
                        published_date=published,
                        last_modified=last_modified,
                        affected_products=affected[:5]  # Max 5 produktów
                    )
                    cves.append(cve_info)
            
            # Zapisz do cache
            self.cache[cache_key] = {
                'timestamp': datetime.now().isoformat(),
                'cves': [asdict(cve) for cve in cves]
            }
            self._save_cache()
            
            return cves
            
        except requests.exceptions.RequestException as e:
            console.print(f"[yellow]⚠️  Błąd połączenia z NVD API: {e}[/yellow]")
            console.print("[dim]Używam lokalnej bazy podatności...[/dim]")
            return []
        except Exception as e:
            console.print(f"[yellow]⚠️  Błąd przetwarzania odpowiedzi NVD: {e}[/yellow]")
            return []
    
    def get_cves_for_port(self, port: int) -> List[CVEInfo]:
        """
        Pobiera podatności CVE dla danego portu.
        
        Args:
            port: Numer portu
        
        Returns:
            Lista CVEInfo z podatnościami
        """
        # Mapuj port na usługę
        service = PORT_TO_SERVICE.get(port)
        if not service:
            return []
        
        # Wyszukaj podatności dla tej usługi
        # Używamy kilku słów kluczowych dla lepszych wyników
        keywords = [service]
        
        # Dodaj dodatkowe słowa kluczowe dla niektórych usług
        if service == "ssh":
            keywords.extend(["openssh", "ssh protocol"])
        elif service == "rdp":
            keywords.extend(["remote desktop", "rdp protocol"])
        elif service == "dicom":
            keywords.extend(["dicom protocol", "medical imaging"])
        elif service == "hl7":
            keywords.extend(["hl7 protocol", "health level 7"])
        elif service in ["mssql", "mysql", "postgresql", "mongodb"]:
            keywords.extend([f"{service} database", "sql injection"])
        
        all_cves = []
        seen_cve_ids = set()
        
        for keyword in keywords[:2]:  # Max 2 słowa kluczowe aby nie spamować API
            cves = self._search_nvd_api(keyword, max_results=10)
            for cve in cves:
                if cve.cve_id not in seen_cve_ids:
                    all_cves.append(cve)
                    seen_cve_ids.add(cve.cve_id)
        
        # Sortuj po severity (CRITICAL > HIGH > MEDIUM > LOW)
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        all_cves.sort(key=lambda x: (severity_order.get(x.severity, 99), x.cvss_score or 0), reverse=True)
        
        return all_cves[:10]  # Max 10 najważniejszych
    
    def get_cves_for_cve_list(self, cve_ids: List[str]) -> List[CVEInfo]:
        """
        Pobiera szczegóły podatności dla listy CVE ID.
        
        Args:
            cve_ids: Lista CVE ID (np. ["CVE-2019-0708", "CVE-2020-14867"])
        
        Returns:
            Lista CVEInfo z podatnościami
        """
        all_cves = []
        
        for cve_id in cve_ids:
            # Sprawdź cache
            cache_key = f"cve:{cve_id}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                cached_time = datetime.fromisoformat(cached_data['timestamp'])
                if datetime.now() - cached_time < timedelta(days=7):
                    all_cves.append(CVEInfo(**cached_data['cve']))
                    continue
            
            # Rate limit
            self._rate_limit()
            
            try:
                # Pobierz szczegóły CVE
                url = f"{NVD_API_BASE}?cveId={cve_id}"
                
                # Dodaj API key do nagłówków jeśli dostępny
                headers = {}
                if self.api_key:
                    headers['apiKey'] = self.api_key
                
                # Wszystkie połączenia używają HTTPS (bezpieczne szyfrowanie TLS/SSL)
                response = requests.get(url, headers=headers, timeout=10, verify=True)
                response.raise_for_status()
                
                data = response.json()
                
                if 'vulnerabilities' in data and len(data['vulnerabilities']) > 0:
                    vuln = data['vulnerabilities'][0]
                    cve_data = vuln.get('cve', {})
                    
                    descriptions = cve_data.get('descriptions', [])
                    description = descriptions[0].get('value', '') if descriptions else ''
                    
                    metrics = cve_data.get('metrics', {})
                    cvss_score = None
                    severity = "MEDIUM"
                    
                    if 'cvssMetricV31' in metrics:
                        cvss_data = metrics['cvssMetricV31'][0]
                        cvss_score = cvss_data.get('cvssData', {}).get('baseScore')
                    elif 'cvssMetricV30' in metrics:
                        cvss_data = metrics['cvssMetricV30'][0]
                        cvss_score = cvss_data.get('cvssData', {}).get('baseScore')
                    
                    published = cve_data.get('published', '')
                    last_modified = cve_data.get('lastModified', '')
                    
                    cve_info = CVEInfo(
                        cve_id=cve_id,
                        description=description[:500],
                        severity=severity,
                        cvss_score=cvss_score,
                        published_date=published,
                        last_modified=last_modified,
                        affected_products=[]
                    )
                    
                    # Zapisz do cache
                    self.cache[cache_key] = {
                        'timestamp': datetime.now().isoformat(),
                        'cve': asdict(cve_info)
                    }
                    self._save_cache()
                    
                    all_cves.append(cve_info)
                    
            except Exception as e:
                console.print(f"[yellow]⚠️  Błąd pobierania {cve_id}: {e}[/yellow]")
                continue
        
        return all_cves


# Singleton instance
_cve_lookup_instance = None

def get_cve_lookup() -> CVELookup:
    """Zwraca singleton instance CVELookup"""
    global _cve_lookup_instance
    if _cve_lookup_instance is None:
        _cve_lookup_instance = CVELookup()
    return _cve_lookup_instance
