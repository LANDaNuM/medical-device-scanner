#!/usr/bin/env python3
"""
Moduł integracji z zewnętrznymi API dla wzbogacenia danych o urządzeniach.

Obsługuje:
- VirusTotal API: Sprawdzanie reputacji IP, domen, hashów
- Shodan API: Wyszukiwanie informacji o urządzeniach w internecie

Wymagane API keys (opcjonalne, ale zalecane):
- VIRUSTOTAL_API_KEY: https://www.virustotal.com/gui/join-us
- SHODAN_API_KEY: https://account.shodan.io/register
"""

import os
import time
import hashlib
from typing import Optional, Dict, List, Any
from pathlib import Path
import json

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from dotenv import load_dotenv
    # Załaduj .env z katalogu projektu
    project_dir = Path(__file__).parent.parent
    env_file = project_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    else:
        load_dotenv()
except ImportError:
    pass

# API Keys
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
# MISP API - nie jest zaimplementowane (placeholder)
# MISP_API_KEY = os.getenv("MISP_API_KEY")
# MISP_URL = os.getenv("MISP_URL")

# Rate limits
VIRUSTOTAL_RATE_LIMIT = 4  # requests per minute (free tier)
SHODAN_RATE_LIMIT = 1  # requests per second (free tier)

# Cache
CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
VIRUSTOTAL_CACHE = CACHE_DIR / "virustotal_cache.json"
SHODAN_CACHE = CACHE_DIR / "shodan_cache.json"


class VirusTotalAPI:
    """Integracja z VirusTotal API do sprawdzania reputacji IP, domen, hashów."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicjalizuje VirusTotal API.
        
        Args:
            api_key: Klucz API VirusTotal (opcjonalny, można też ustawić w .env)
        """
        self.api_key = api_key or VIRUSTOTAL_API_KEY
        self.base_url = "https://www.virustotal.com/api/v3"
        self.cache = self._load_cache()
        self.last_request_time = 0
        self.request_count = 0
        self.request_window_start = time.time()
        
    def _load_cache(self) -> Dict:
        """Ładuje cache z pliku."""
        if VIRUSTOTAL_CACHE.exists():
            try:
                with open(VIRUSTOTAL_CACHE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_cache(self):
        """Zapisuje cache do pliku."""
        try:
            with open(VIRUSTOTAL_CACHE, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"⚠️  Błąd zapisu cache VirusTotal: {e}")
    
    def _rate_limit(self):
        """Obsługuje rate limiting dla VirusTotal API."""
        current_time = time.time()
        
        # Resetuj licznik co minutę
        if current_time - self.request_window_start >= 60:
            self.request_count = 0
            self.request_window_start = current_time
        
        # Sprawdź limit
        if self.request_count >= VIRUSTOTAL_RATE_LIMIT:
            wait_time = 60 - (current_time - self.request_window_start)
            if wait_time > 0:
                time.sleep(wait_time)
                self.request_count = 0
                self.request_window_start = time.time()
        
        self.request_count += 1
    
    def check_ip(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Sprawdza reputację adresu IP w VirusTotal.
        
        Args:
            ip_address: Adres IP do sprawdzenia
        
        Returns:
            Słownik z wynikami lub None jeśli błąd
        """
        if not self.api_key:
            return None
        
        if not REQUESTS_AVAILABLE:
            return None
        
        # Sprawdź cache
        cache_key = f"ip_{ip_address}"
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            # Cache ważny przez 24h
            if time.time() - cached_data.get('timestamp', 0) < 86400:
                return cached_data.get('data')
        
        try:
            self._rate_limit()
            
            headers = {
                "x-apikey": self.api_key
            }
            
            response = requests.get(
                f"{self.base_url}/ip_addresses/{ip_address}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    'reputation': data.get('data', {}).get('attributes', {}).get('reputation', 0),
                    'harmless': data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {}).get('harmless', 0),
                    'malicious': data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {}).get('malicious', 0),
                    'suspicious': data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {}).get('suspicious', 0),
                    'undetected': data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {}).get('undetected', 0),
                    'asn': data.get('data', {}).get('attributes', {}).get('asn', None),
                    'country': data.get('data', {}).get('attributes', {}).get('country', None),
                    'network': data.get('data', {}).get('attributes', {}).get('network', None),
                }
                
                # Zapisz do cache
                self.cache[cache_key] = {
                    'data': result,
                    'timestamp': time.time()
                }
                self._save_cache()
                
                return result
            elif response.status_code == 401:
                error_msg = response.json().get('error', {}).get('message', 'Invalid API key')
                print(f"⚠️  VirusTotal: Nieprawidłowy klucz API - {error_msg}")
                print(f"   Sprawdź swój klucz API na: https://www.virustotal.com/gui/join-us")
                return None
            elif response.status_code == 403:
                error_msg = response.json().get('error', {}).get('message', 'Forbidden')
                print(f"⚠️  VirusTotal: Brak uprawnień - {error_msg}")
                print(f"   Sprawdź swój klucz API i limity na: https://www.virustotal.com/gui/join-us")
                return None
            elif response.status_code == 429:
                print(f"⚠️  VirusTotal: Rate limit exceeded, waiting...")
                time.sleep(60)
                return None
            else:
                error_msg = "Unknown error"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', f"Status code: {response.status_code}")
                except:
                    error_msg = f"Status code: {response.status_code}"
                print(f"⚠️  VirusTotal API: {error_msg}")
                return None
                
        except Exception as e:
            print(f"⚠️  Błąd VirusTotal API: {e}")
            return None
    
    def get_reputation_summary(self, ip_address: str) -> str:
        """
        Zwraca czytelne podsumowanie reputacji IP.
        
        Args:
            ip_address: Adres IP
        
        Returns:
            String z podsumowaniem
        """
        result = self.check_ip(ip_address)
        if not result:
            return "No data available"
        
        reputation = result.get('reputation', 0)
        malicious = result.get('malicious', 0)
        suspicious = result.get('suspicious', 0)
        harmless = result.get('harmless', 0)
        
        if malicious > 0:
            return f"🔴 Malicious ({malicious} detections)"
        elif suspicious > 0:
            return f"🟡 Suspicious ({suspicious} detections)"
        elif reputation > 0:
            return f"🟢 Clean (reputation: {reputation})"
        else:
            return "⚪ Unknown"


class ShodanAPI:
    """Integracja z Shodan API do wyszukiwania informacji o urządzeniach."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicjalizuje Shodan API.
        
        Args:
            api_key: Klucz API Shodan (opcjonalny, można też ustawić w .env)
        """
        self.api_key = api_key or SHODAN_API_KEY
        self.base_url = "https://api.shodan.io"
        self.cache = self._load_cache()
        self.last_request_time = 0
        self.error_cache = {}  # Cache błędów aby nie wyświetlać ich wielokrotnie
        
    def _load_cache(self) -> Dict:
        """Ładuje cache z pliku."""
        if SHODAN_CACHE.exists():
            try:
                with open(SHODAN_CACHE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_cache(self):
        """Zapisuje cache do pliku."""
        try:
            with open(SHODAN_CACHE, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"⚠️  Błąd zapisu cache Shodan: {e}")
    
    def _rate_limit(self):
        """Obsługuje rate limiting dla Shodan API."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < (1.0 / SHODAN_RATE_LIMIT):
            wait_time = (1.0 / SHODAN_RATE_LIMIT) - time_since_last
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def _is_private_ip(self, ip_address: str) -> bool:
        """
        Sprawdza czy IP jest prywatne (RFC 1918).
        
        Shodan działa tylko dla publicznych IP, więc prywatne IP są pomijane.
        
        Args:
            ip_address: Adres IP do sprawdzenia
        
        Returns:
            True jeśli IP jest prywatne
        """
        try:
            parts = ip_address.split('.')
            if len(parts) != 4:
                return False
            
            first_octet = int(parts[0])
            second_octet = int(parts[1])
            
            # 10.0.0.0/8
            if first_octet == 10:
                return True
            
            # 172.16.0.0/12
            if first_octet == 172 and 16 <= second_octet <= 31:
                return True
            
            # 192.168.0.0/16
            if first_octet == 192 and second_octet == 168:
                return True
            
            # 127.0.0.0/8 (localhost)
            if first_octet == 127:
                return True
            
            # 169.254.0.0/16 (link-local)
            if first_octet == 169 and second_octet == 254:
                return True
            
            return False
        except (ValueError, IndexError):
            return False
    
    def host_info(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Pobiera informacje o hoście z Shodan.
        
        Args:
            ip_address: Adres IP do sprawdzenia
        
        Returns:
            Słownik z wynikami lub None jeśli błąd
        """
        if not self.api_key:
            return None
        
        if not REQUESTS_AVAILABLE:
            return None
        
        # Shodan działa tylko dla publicznych IP - pomiń prywatne IP
        if self._is_private_ip(ip_address):
            return None  # Cicho pomiń prywatne IP
        
        # Sprawdź cache
        cache_key = f"host_{ip_address}"
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            # Cache ważny przez 7 dni
            if time.time() - cached_data.get('timestamp', 0) < 604800:
                return cached_data.get('data')
        
        try:
            self._rate_limit()
            
            response = requests.get(
                f"{self.base_url}/shodan/host/{ip_address}",
                params={"key": self.api_key},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    'ip': data.get('ip_str'),
                    'hostnames': data.get('hostnames', []),
                    'country': data.get('country_name'),
                    'city': data.get('city'),
                    'org': data.get('org'),
                    'os': data.get('os'),
                    'ports': data.get('ports', []),
                    'vulns': data.get('vulns', []),
                    'tags': data.get('tags', []),
                    'services': []
                }
                
                # Wyciągnij informacje o usługach
                for service in data.get('data', [])[:5]:  # Max 5 usług
                    result['services'].append({
                        'port': service.get('port'),
                        'product': service.get('product'),
                        'version': service.get('version'),
                        'banner': service.get('data', '')[:100]  # Pierwsze 100 znaków
                    })
                
                # Zapisz do cache
                self.cache[cache_key] = {
                    'data': result,
                    'timestamp': time.time()
                }
                self._save_cache()
                
                return result
            elif response.status_code == 401:
                # Wyświetl błąd tylko raz (cache błędów)
                if '401' not in self.error_cache:
                    error_msg = response.json().get('error', 'Invalid API key')
                    print(f"⚠️  Shodan: Nieprawidłowy klucz API - {error_msg}")
                    print(f"   Sprawdź swój klucz API na: https://account.shodan.io/register")
                    self.error_cache['401'] = True
                return None
            elif response.status_code == 403:
                # Wyświetl błąd tylko raz (cache błędów)
                if '403' not in self.error_cache:
                    error_msg = response.json().get('error', 'Forbidden')
                    print(f"⚠️  Shodan: Brak uprawnień - {error_msg}")
                    print(f"   💡 Shodan wymaga płatnego konta dla pełnej funkcjonalności")
                    print(f"   💡 Prywatne IP (192.168.x.x) są automatycznie pomijane")
                    print(f"   Sprawdź limity na: https://account.shodan.io/")
                    self.error_cache['403'] = True
                return None
            elif response.status_code == 429:
                # Wyświetl błąd tylko raz (cache błędów)
                if '429' not in self.error_cache:
                    print("⚠️  Shodan: Rate limit exceeded - czekam...")
                    self.error_cache['429'] = True
                return None
            elif response.status_code == 400:
                # "Invalid IP" - prawdopodobnie prywatne IP (powinno być już odfiltrowane, ale na wszelki wypadek)
                # Cicho pomiń - nie wyświetlaj błędu
                return None
            else:
                error_msg = "Unknown error"
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', f"Status code: {response.status_code}")
                except:
                    error_msg = f"Status code: {response.status_code}"
                # Wyświetl błąd tylko raz (cache błędów)
                error_key = f"other_{response.status_code}"
                if error_key not in self.error_cache:
                    print(f"⚠️  Shodan API: {error_msg}")
                    self.error_cache[error_key] = True
                return None
                
        except Exception as e:
            # Wyświetl błąd tylko raz (cache błędów)
            error_key = f"exception_{type(e).__name__}"
            if error_key not in self.error_cache:
                print(f"⚠️  Błąd Shodan API: {e}")
                self.error_cache[error_key] = True
            return None
    
    def get_host_summary(self, ip_address: str) -> str:
        """
        Zwraca czytelne podsumowanie informacji o hoście.
        
        Args:
            ip_address: Adres IP
        
        Returns:
            String z podsumowaniem
        """
        result = self.host_info(ip_address)
        if not result:
            return "No data available"
        
        parts = []
        if result.get('org'):
            parts.append(f"Org: {result['org']}")
        if result.get('country'):
            parts.append(f"Country: {result['country']}")
        if result.get('ports'):
            parts.append(f"Ports: {len(result['ports'])}")
        if result.get('vulns'):
            parts.append(f"⚠️ Vulnerabilities: {len(result['vulns'])}")
        
        return " | ".join(parts) if parts else "No additional info"


class ExternalAPIs:
    """
    Główna klasa zarządzająca wszystkimi integracjami zewnętrznymi.
    
    Użycie:
        apis = ExternalAPIs()
        vt_result = apis.virustotal.check_ip("192.168.1.1")
        shodan_result = apis.shodan.host_info("192.168.1.1")
    """
    
    def __init__(self):
        """Inicjalizuje wszystkie dostępne API."""
        self.virustotal = VirusTotalAPI() if VIRUSTOTAL_API_KEY else None
        self.shodan = ShodanAPI() if SHODAN_API_KEY else None
        
        # Wyświetl status
        if self.virustotal:
            print("✅ VirusTotal API dostępne")
        else:
            print("⚠️  VirusTotal API niedostępne (brak klucza)")
        
        if self.shodan:
            print("✅ Shodan API dostępne")
        else:
            print("⚠️  Shodan API niedostępne (brak klucza)")
    
    def enrich_device(self, device_ip: Optional[str] = None, device_mac: Optional[str] = None) -> Dict[str, Any]:
        """
        Wzbogaca informacje o urządzeniu używając zewnętrznych API.
        
        Args:
            device_ip: Adres IP urządzenia
            device_mac: Adres MAC urządzenia (opcjonalnie)
        
        Returns:
            Słownik z wzbogaconymi danymi
        """
        enriched_data = {
            'virustotal': None,
            'shodan': None
        }
        
        if device_ip:
            # VirusTotal (działa dla wszystkich IP)
            if self.virustotal:
                enriched_data['virustotal'] = self.virustotal.check_ip(device_ip)
            
            # Shodan (tylko dla publicznych IP - prywatne są automatycznie pomijane)
            if self.shodan:
                # host_info() automatycznie pomija prywatne IP
                enriched_data['shodan'] = self.shodan.host_info(device_ip)
        
        return enriched_data
