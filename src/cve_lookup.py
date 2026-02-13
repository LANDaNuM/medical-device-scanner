#!/usr/bin/env python3
"""
Fetch CVE data from external databases (NIST NVD, Vulners). Uses cache to limit API calls.

Config: NVD_API_KEY, VULNERS_API_KEY (optional). NVD: 5 req/30s without key, 50 with key.
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

# Cache file location
CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CVE_CACHE_FILE = CACHE_DIR / "cve_cache.json"

# NIST NVD API endpoints
NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"  # HTTPS
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
    """CVE vulnerability info."""
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
    """Fetch CVE data from NIST NVD API. Uses cache to limit calls and allow offline use. All connections use HTTPS."""
    
    def __init__(self, use_cache: bool = True, cache_days: int = 7, 
                 nvd_api_key: Optional[str] = None, vulners_api_key: Optional[str] = None,
                 prefer_vulners: bool = False):
        """use_cache: use file cache; cache_days: cache validity; nvd_api_key/vulners_api_key: optional API keys for higher rate limits."""
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
        
    def _load_cache(self) -> Dict:
        """Load cache from file."""
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
        except Exception as e:
            console.print(f"[yellow]⚠️  Error loading cache: {e}[/yellow]")
            return {}
    
    def _save_cache(self):
        """Save cache to file."""
        if not self.use_cache:
            return
        try:
            cache_data = {'timestamp': datetime.now().isoformat(), 'data': self.cache}
            with open(CVE_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            console.print(f"[yellow]⚠️  Error saving cache: {e}[/yellow]")
    
    def _rate_limit(self):
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
        """Search NIST NVD API for CVEs by keyword. Returns list of CVEInfo."""
        cache_key = f"search:{keyword}"
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cached_time < timedelta(hours=24):
                console.print(f"[dim]📦 Using cache for: {keyword}[/dim]")
                return [CVEInfo(**item) for item in cached_data['cves']]
        
        # Rate limit
        self._rate_limit()
        
        try:
            # Query NVD API
            params = {
                'keywordSearch': keyword,
                'resultsPerPage': max_results
            }
            
            headers = {}
            if self.nvd_api_key:
                headers['apiKey'] = self.nvd_api_key
            response = requests.get(NVD_API_BASE, params=params, headers=headers, timeout=10, verify=True)
            response.raise_for_status()
            
            data = response.json()
            cves = []
            
            if 'vulnerabilities' in data:
                for vuln in data['vulnerabilities']:
                    cve_data = vuln.get('cve', {})
                    cve_id = cve_data.get('id', '')
                    
                    # Get description
                    descriptions = cve_data.get('descriptions', [])
                    description = descriptions[0].get('value', '') if descriptions else ''
                    
                    # Get CVSS score
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
                    
                    # Get dates
                    published = cve_data.get('published', '')
                    last_modified = cve_data.get('lastModified', '')
                    
                    # Get affected products
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
            
        except requests.exceptions.RequestException as e:
            console.print(f"[yellow]⚠️  NVD API connection error: {e}[/yellow]")
            console.print("[dim]Using local vulnerability data...[/dim]")
            return []
        except Exception as e:
            console.print(f"[yellow]⚠️  NVD response processing error: {e}[/yellow]")
            return []
    
    def get_cves_for_port(self, port: int) -> List[CVEInfo]:
        """Get CVE list for a given port. Returns list of CVEInfo."""
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
        
        all_cves = []
        seen_cve_ids = set()
        
        for keyword in keywords[:2]:
            cves = self._search_nvd_api(keyword, max_results=10)
            for cve in cves:
                if cve.cve_id not in seen_cve_ids:
                    all_cves.append(cve)
                    seen_cve_ids.add(cve.cve_id)
        
        # Sortuj po severity (CRITICAL > HIGH > MEDIUM > LOW)
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        all_cves.sort(key=lambda x: (severity_order.get(x.severity, 99), x.cvss_score or 0), reverse=True)
        
        return all_cves[:10]
    
    def get_cves_for_cve_list(self, cve_ids: List[str]) -> List[CVEInfo]:
        """Fetch CVE details for a list of CVE IDs. Returns list of CVEInfo."""
        all_cves = []
        
        for cve_id in cve_ids:
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
                url = f"{NVD_API_BASE}?cveId={cve_id}"
                headers = {}
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
                    
                    self.cache[cache_key] = {
                        'timestamp': datetime.now().isoformat(),
                        'cve': asdict(cve_info)
                    }
                    self._save_cache()
                    
                    all_cves.append(cve_info)
                    
            except Exception as e:
                console.print(f"[yellow]⚠️  Error fetching {cve_id}: {e}[/yellow]")
                continue
        
        return all_cves


# Singleton instance
_cve_lookup_instance = None

def get_cve_lookup() -> CVELookup:
    """Return singleton CVELookup instance."""
    global _cve_lookup_instance
    if _cve_lookup_instance is None:
        _cve_lookup_instance = CVELookup()
    return _cve_lookup_instance
