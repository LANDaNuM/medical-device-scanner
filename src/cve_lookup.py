#!/usr/bin/env python3
"""
CVE (Common Vulnerabilities and Exposures) lookup from NIST NVD and Vulners.

Features:
- Fetch CVE data from NIST NVD API
- Cache CVE data locally (reduces API calls)
- Rate limiting (respects API quotas)
- Optional Vulners API support
- Comprehensive error handling with specific exception types
"""

import json
import time
import os
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import requests
from rich.console import Console
from rich.panel import Panel

try:
    from dotenv import load_dotenv
    project_dir = Path(__file__).parent.parent
    env_file = project_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    else:
        load_dotenv()
except ImportError:
    pass

console = Console()

# Cache configuration
CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CVE_CACHE_FILE = CACHE_DIR / "cve_cache.json"

# NIST NVD API configuration
NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NVD_RATE_LIMIT = 5  # requests per 30 seconds (without API key)
NVD_RATE_LIMIT_WITH_KEY = 50  # requests per 30 seconds (with API key)
NVD_RATE_WINDOW = 30  # seconds

PORT_TO_SERVICE = {
    104: "dicom",
    11112: "dicom",
    5000: "hl7",
    # Admin ports
    22: "ssh",
    3389: "rdp",
    5900: "vnc",
    5901: "vnc",
    # Web ports
    80: "http",
    443: "https",
    8080: "http",
    8443: "https",
    # Database ports
    1433: "mssql",
    3306: "mysql",
    5432: "postgresql",
    27017: "mongodb",
    # Other
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
    """CVE (Common Vulnerabilities and Exposures) information."""
    cve_id: str
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    cvss_score: Optional[float] = None
    published_date: Optional[str] = None
    last_modified: Optional[str] = None
    affected_products: List[str] = None
    
    def __post_init__(self) -> None:
        if self.affected_products is None:
            self.affected_products = []


class CVELookup:
    """
    Fetch CVE data from NIST NVD API.
    
    Features:
    - Local caching to minimize API calls
    - Automatic rate limiting
    - Support for API keys (higher quotas)
    - Comprehensive error handling
    - All connections use HTTPS
    """
    
    def __init__(self, use_cache: bool = True, cache_days: int = 7, 
                 nvd_api_key: Optional[str] = None, vulners_api_key: Optional[str] = None,
                 prefer_vulners: bool = False) -> None:
        """
        Initialize CVE lookup.
        
        Args:
            use_cache: Use file cache (default: True)
            cache_days: Cache validity in days (default: 7)
            nvd_api_key: Optional NVD API key for higher rate limits
            vulners_api_key: Optional Vulners API key
            prefer_vulners: Prefer Vulners API if key available
        """
        if not nvd_api_key:
            nvd_api_key = os.getenv('NVD_API_KEY')
        if not vulners_api_key:
            vulners_api_key = os.getenv('VULNERS_API_KEY')
        
        self.nvd_api_key: Optional[str] = nvd_api_key
        self.vulners_api_key: Optional[str] = vulners_api_key
        self.prefer_vulners: bool = prefer_vulners and bool(vulners_api_key)
        self.use_cache: bool = use_cache
        self.cache_days: int = cache_days
        self.cache: Dict[str, Any] = self._load_cache()
        self.last_request_time: float = 0
        self.request_count: int = 0
        self.vulners_last_request_time: float = 0
        self.vulners_request_count: int = 0
        
        if self.nvd_api_key:
            console.print("[green]✅ NVD API key detected – limit: 50 req/30s[/green]")
        else:
            console.print("[yellow]ℹ️  NVD API without key – limit: 5 req/30s[/yellow]")
            console.print("[dim]   Get free key: https://nvd.nist.gov/developers/request-an-api-key[/dim]")
        if self.vulners_api_key:
            console.print("[green]✅ Vulners API key detected – limit: 1000 req/min[/green]")
        elif self.prefer_vulners:
            console.print("[yellow]ℹ️  Vulners API without key – limit: 100 req/min[/yellow]")
            console.print("[dim]   Get free key: https://vulners.com/register[/dim]")
        
    def _load_cache(self) -> Dict[str, Any]:
        """
        Load cache from file.
        
        Returns:
            Dictionary with cached CVE data or empty dict
        """
        if not self.use_cache or not CVE_CACHE_FILE.exists():
            return {}
        try:
            with open(CVE_CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
                cache_time = datetime.fromisoformat(cache.get('timestamp', '2000-01-01'))
                if datetime.now() - cache_time > timedelta(days=self.cache_days):
                    console.print("[yellow]⚠️  Cache expired, will refresh[/yellow]")
                    return {}
                return cache.get('data', {})
        except FileNotFoundError:
            console.print("[dim]📦 Cache file not found, starting fresh[/dim]")
            return {}
        except json.JSONDecodeError as e:
            console.print(f"[yellow]⚠️  Invalid cache JSON: {e}[/yellow]")
            return {}
        except ValueError as e:
            console.print(f"[yellow]⚠️  Invalid cache timestamp: {e}[/yellow]")
            return {}
        except Exception as e:
            console.print(f"[red]❌ Unexpected error loading cache: {type(e).__name__}: {e}[/red]")
            return {}
    
    def _save_cache(self) -> None:
        """Save cache to file."""
        if not self.use_cache:
            return
        try:
            cache_data = {'timestamp': datetime.now().isoformat(), 'data': self.cache}
            with open(CVE_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            console.print(f"[yellow]⚠️  Cannot write cache file: {e}[/yellow]")
        except Exception as e:
            console.print(f"[red]❌ Unexpected error saving cache: {type(e).__name__}: {e}[/red]")
    
    def _rate_limit(self) -> None:
        """Implement rate limiting for NVD API."""
        rate_limit = NVD_RATE_LIMIT_WITH_KEY if self.nvd_api_key else NVD_RATE_LIMIT
        current_time = time.time()
        if current_time - self.last_request_time > NVD_RATE_WINDOW:
            self.request_count = 0
            self.last_request_time = current_time
        if self.request_count >= rate_limit:
            wait_time = NVD_RATE_WINDOW - (current_time - self.last_request_time)
            if wait_time > 0:
                console.print(f"[dim]⏳ Waiting for rate limit ({int(wait_time)}s)...[/dim]")
                time.sleep(wait_time)
                self.request_count = 0
                self.last_request_time = time.time()
        
        self.request_count += 1
    
    def _search_nvd_api(self, keyword: str, max_results: int = 20) -> List[CVEInfo]:
        """
        Search NIST NVD API for CVEs by keyword.
        
        Args:
            keyword: Search keyword
            max_results: Maximum results per query
            
        Returns:
            List of CVEInfo objects
        """
        cache_key = f"search:{keyword}"
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            try:
                cached_time = datetime.fromisoformat(cached_data['timestamp'])
                if datetime.now() - cached_time < timedelta(hours=24):
                    console.print(f"[dim]📦 Using cache for: {keyword}[/dim]")
                    return [CVEInfo(**item) for item in cached_data['cves']]
            except (ValueError, KeyError) as e:
                console.print(f"[yellow]⚠️  Invalid cached entry: {e}[/yellow]")
        
        # Rate limit
        self._rate_limit()
        
        try:
            # Query NVD API
            params = {
                'keywordSearch': keyword,
                'resultsPerPage': max_results
            }
            
            headers: Dict[str, str] = {}
            if self.nvd_api_key:
                headers['apiKey'] = self.nvd_api_key
            response = requests.get(NVD_API_BASE, params=params, headers=headers, timeout=10, verify=True)
            response.raise_for_status()
            
            data = response.json()
            cves: List[CVEInfo] = []
            
            if 'vulnerabilities' in data:
                for vuln in data['vulnerabilities']:
                    cve_data = vuln.get('cve', {})
                    cve_id = cve_data.get('id', '')
                    
                    # Extract description
                    descriptions = cve_data.get('descriptions', [])
                    description = descriptions[0].get('value', '') if descriptions else ''
                    
                    # Extract CVSS score and severity
                    metrics = cve_data.get('metrics', {})
                    cvss_score: Optional[float] = None
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
                    
                    # Extract dates
                    published = cve_data.get('published', '')
                    last_modified = cve_data.get('lastModified', '')
                    
                    # Extract affected products
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
                        description=description[:500],
                        severity=severity,
                        cvss_score=cvss_score,
                        published_date=published,
                        last_modified=last_modified,
                        affected_products=affected[:5]
                    )
                    cves.append(cve_info)
            
            self.cache[cache_key] = {
                'timestamp': datetime.now().isoformat(),
                'cves': [asdict(cve) for cve in cves]
            }
            self._save_cache()
            
            return cves
            
        except requests.exceptions.Timeout:
            console.print(f"[yellow]⚠️  NVD API timeout[/yellow]")
            console.print("[dim]Using local vulnerability data...[/dim]")
            return []
        except requests.exceptions.ConnectionError as e:
            console.print(f"[yellow]⚠️  NVD API connection error: {e}[/yellow]")
            console.print("[dim]Using local vulnerability data...[/dim]")
            return []
        except requests.exceptions.RequestException as e:
            console.print(f"[yellow]⚠️  NVD API request error: {e}[/yellow]")
            console.print("[dim]Using local vulnerability data...[/dim]")
            return []
        except Exception as e:
            console.print(f"[red]❌ Unexpected NVD error: {type(e).__name__}: {e}[/red]")
            return []
    
    def get_cves_for_port(self, port: int) -> List[CVEInfo]:
        """
        Get CVE list for a given port number.
        
        Args:
            port: Port number (e.g., 22 for SSH, 3306 for MySQL)
            
        Returns:
            List of CVEInfo objects for that service
        """
        service = PORT_TO_SERVICE.get(port)
        if not service:
            return []
        keywords = [service]
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
        
        all_cves: List[CVEInfo] = []
        seen_cve_ids: set[str] = set()
        
        for keyword in keywords[:2]:
            cves = self._search_nvd_api(keyword, max_results=10)
            for cve in cves:
                if cve.cve_id not in seen_cve_ids:
                    all_cves.append(cve)
                    seen_cve_ids.add(cve.cve_id)
        
        # Sort by severity (CRITICAL > HIGH > MEDIUM > LOW)
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        all_cves.sort(key=lambda x: (severity_order.get(x.severity, 99), x.cvss_score or 0), reverse=True)
        
        return all_cves[:10]
    
    def get_cves_for_cve_list(self, cve_ids: List[str]) -> List[CVEInfo]:
        """
        Fetch CVE details for a list of CVE IDs.
        
        Args:
            cve_ids: List of CVE identifiers (e.g., ["CVE-2024-0001", "CVE-2024-0002"])
            
        Returns:
            List of CVEInfo objects
        """
        all_cves: List[CVEInfo] = []
        
        for cve_id in cve_ids:
            cache_key = f"cve:{cve_id}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                try:
                    cached_time = datetime.fromisoformat(cached_data['timestamp'])
                    if datetime.now() - cached_time < timedelta(days=7):
                        all_cves.append(CVEInfo(**cached_data['cve']))
                        continue
                except (ValueError, KeyError) as e:
                    console.print(f"[yellow]⚠️  Invalid cached CVE entry: {e}[/yellow]")
            
            # Rate limit
            self._rate_limit()
            
            try:
                url = f"{NVD_API_BASE}?cveId={cve_id}"
                headers: Dict[str, str] = {}
                if self.nvd_api_key:
                    headers['apiKey'] = self.nvd_api_key
                response = requests.get(url, headers=headers, timeout=10, verify=True)
                response.raise_for_status()
                
                data = response.json()
                
                if 'vulnerabilities' in data and len(data['vulnerabilities']) > 0:
                    vuln = data['vulnerabilities'][0]
                    cve_data = vuln.get('cve', {})
                    
                    descriptions = cve_data.get('descriptions', [])
                    description = descriptions[0].get('value', '') if descriptions else ''
                    
                    metrics = cve_data.get('metrics', {})
                    cvss_score: Optional[float] = None
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
                    
                    self.cache[cache_key] = {
                        'timestamp': datetime.now().isoformat(),
                        'cve': asdict(cve_info)
                    }
                    self._save_cache()
                    
                    all_cves.append(cve_info)
                    
            except requests.exceptions.Timeout:
                console.print(f"[yellow]⚠️  Timeout fetching {cve_id}[/yellow]")
            except requests.exceptions.RequestException as e:
                console.print(f"[yellow]⚠️  Error fetching {cve_id}: {e}[/yellow]")
            except Exception as e:
                console.print(f"[red]❌ Unexpected error fetching {cve_id}: {type(e).__name__}: {e}[/red]")
        
        return all_cves


# Singleton instance
_cve_lookup_instance: Optional[CVELookup] = None

def get_cve_lookup() -> CVELookup:
    """
    Get singleton CVELookup instance.
    
    Returns:
        CVELookup instance
    """
    global _cve_lookup_instance
    if _cve_lookup_instance is None:
        _cve_lookup_instance = CVELookup()
    return _cve_lookup_instance
