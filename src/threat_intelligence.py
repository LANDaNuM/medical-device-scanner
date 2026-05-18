#!/usr/bin/env python3
"""
Threat Intelligence: check IPs against threat DBs (AbuseIPDB, VirusTotal, Shodan). Uses cache. Usage: ThreatIntelligence().check_ip("192.168.1.1")
"""

import os
import time
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

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

from device import Device

# API Keys
ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY")

# Cache
CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
THREAT_CACHE = CACHE_DIR / "threat_intel_cache.json"


class ThreatIntelligence:
    """Check IPs against AbuseIPDB, VirusTotal, Shodan; uses cache."""
    
    def __init__(self):
        """Initialize Threat Intelligence."""
        self.abuseipdb_key = ABUSEIPDB_API_KEY
        self.cache = self._load_cache()
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 request/second dla AbuseIPDB free tier
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from file."""
        if THREAT_CACHE.exists():
            try:
                with open(THREAT_CACHE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            with open(THREAT_CACHE, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    def check_ip(self, ip: str) -> Dict[str, Any]:
        """Check IP against threat intelligence DBs. Returns result dict."""
        # Check cache
        if ip in self.cache:
            cached_result = self.cache[ip]
            # Cache valid 24h
            if time.time() - cached_result.get('cached_at', 0) < 86400:
                return cached_result
        
        result = {
            'ip': ip,
            'is_threat': False,
            'sources': {},
            'abuse_score': 0,
            'reputation': 'unknown',
            'checked_at': time.time()
        }
        
        # Check AbuseIPDB if available
        if self.abuseipdb_key and REQUESTS_AVAILABLE:
            abuse_result = self._check_abuseipdb(ip)
            if abuse_result:
                result['sources']['abuseipdb'] = abuse_result
                result['abuse_score'] = abuse_result.get('abuseConfidencePercentage', 0)
                result['is_threat'] = abuse_result.get('abuseConfidencePercentage', 0) > 25
                result['reputation'] = 'malicious' if result['is_threat'] else 'clean'
        
        # Check VirusTotal if available
        try:
            from external_apis import ExternalAPIs
            apis = ExternalAPIs()
            if apis.virustotal:
                vt_result = apis.virustotal.check_ip(ip)
                if vt_result:
                    result['sources']['virustotal'] = {
                        'reputation': vt_result.get('reputation', 'unknown'),
                        'detections': vt_result.get('detections', 0)
                    }
                    if vt_result.get('detections', 0) > 0:
                        result['is_threat'] = True
        except Exception:
            pass
        
        # Check Shodan if available (public IPs only)
        try:
            # Skip private IPs (Shodan only has public IPs)
            def is_private_ip(ip_addr: str) -> bool:
                try:
                    parts = ip_addr.split('.')
                    if len(parts) != 4:
                        return False
                    first = int(parts[0])
                    second = int(parts[1])
                    return (first == 10 or 
                           (first == 172 and 16 <= second <= 31) or
                           (first == 192 and second == 168) or
                           first == 127 or
                           (first == 169 and second == 254))
                except:
                    return False
            
            # Skip private IPs
            if not is_private_ip(ip):
                from external_apis import ExternalAPIs
                apis = ExternalAPIs()
                if apis.shodan:
                    shodan_result = apis.shodan.host_info(ip)
                    if shodan_result:
                        result['sources']['shodan'] = {
                            'ports': shodan_result.get('ports', []),
                            'vulns': shodan_result.get('vulns', [])
                        }
                        if shodan_result.get('vulns'):
                            result['is_threat'] = True
        except Exception:
            pass
        
        # Zapisz do cache
        result['cached_at'] = time.time()
        self.cache[ip] = result
        self._save_cache()
        
        return result
    
    def _check_abuseipdb(self, ip: str) -> Optional[Dict[str, Any]]:
        """
        Sprawdza IP w AbuseIPDB.
        
        Args:
            ip: Adres IP
        
        Returns:
            Wynik z AbuseIPDB lub None
        """
        if not self.abuseipdb_key or not REQUESTS_AVAILABLE:
            return None
        
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        try:
            url = "https://api.abuseipdb.com/api/v2/check"
            headers = {
                'Key': self.abuseipdb_key,
                'Accept': 'application/json'
            }
            params = {
                'ipAddress': ip,
                'maxAgeInDays': 90,
                'verbose': ''
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    return data['data']
        except Exception:
            pass
        
        return None
    
    def check_devices_async(self, devices: List[Device], max_workers: int = 5) -> Dict[str, Dict[str, Any]]:
        """Check multiple devices asynchronously. Returns dict IP -> threat intel result."""
        results = {}
        ips_to_check = set()
        for device in devices:
            ip = device.metadata.get('ip_address')
            if ip and ip not in ['N/A', 'Unknown', '']:
                ips_to_check.add(ip)
        
        if not ips_to_check:
            return results
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.check_ip, ip): ip for ip in ips_to_check}
            
            for future in as_completed(futures):
                ip = futures[future]
                try:
                    result = future.result()
                    results[ip] = result
                except Exception as e:
                    results[ip] = {'ip': ip, 'error': str(e)}
        
        return results


if __name__ == "__main__":
    # Test
    ti = ThreatIntelligence()
    
    result = ti.check_ip("8.8.8.8")
    print(f"Result for 8.8.8.8: {json.dumps(result, indent=2, ensure_ascii=False)}")
