#!/usr/bin/env python3
"""
Główny moduł skanera urządzeń medycznych.

Ten moduł łączy wszystkie komponenty:
- Prawdziwy skaner BLE (Bluetooth Low Energy)
- Skaner WiFi (sieć lokalna)
- Skaner USB (urządzenia podłączone przez USB)
- Skaner NFC (karty i tagi NFC)
- Analiza bezpieczeństwa
- Testowanie podatności i symulacja ataków (audyt bezpieczeństwa)
- Raportowanie

UŻYCIE:
    python src/scanner.py                    # Skanuj wszystkie protokoły
    python src/scanner.py --ble              # Tylko BLE
    python src/scanner.py --wifi             # Tylko WiFi
    python src/scanner.py --usb              # Tylko USB
    python src/scanner.py --nfc              # Tylko NFC
    python src/scanner.py --ble --wifi        # BLE i WiFi
    python src/scanner.py --audit            # Pełny audyt bezpieczeństwa (testy podatności)
    python src/scanner.py --wifi --audit     # WiFi + audyt bezpieczeństwa
"""

import sys
import os

# Wycisz komunikaty TensorFlow o CUDA/GPU PRZED jakimkolwiek importem
# Musi być na samym początku, przed importem numpy i innych bibliotek
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Wycisz wszystkie komunikaty TensorFlow
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Wyłącz CUDA - wymusza użycie tylko CPU

import json
import csv
import time
from datetime import datetime
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np

# Załaduj zmienne środowiskowe z pliku .env (jeśli istnieje)
try:
    from dotenv import load_dotenv
    # Znajdź katalog projektu (tam gdzie jest .env)
    project_dir = Path(__file__).parent.parent
    env_file = project_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    else:
        # Fallback: spróbuj w katalogu roboczym
        load_dotenv()
except ImportError:
    pass  # python-dotenv nie jest wymagane, ale przydatne
import platform
from typing import List
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from device import Device, DeviceType

# Próbuj zaimportować wszystkie prawdziwe skanery
try:
    from real_scanner import RealBLEScanner
    BLE_SCANNER_AVAILABLE = True
except ImportError:
    BLE_SCANNER_AVAILABLE = False
    RealBLEScanner = None

try:
    from wifi_scanner import WiFiScanner
    WIFI_SCANNER_AVAILABLE = True
except ImportError:
    WIFI_SCANNER_AVAILABLE = False
    WiFiScanner = None

try:
    from usb_scanner import USBScanner
    USB_SCANNER_AVAILABLE = True
except ImportError:
    USB_SCANNER_AVAILABLE = False
    USBScanner = None

try:
    from nfc_scanner import NFCScanner
    NFC_SCANNER_AVAILABLE = True
except ImportError:
    NFC_SCANNER_AVAILABLE = False
    NFCScanner = None

try:
    from vulnerability_tester import VulnerabilityTester
    VULNERABILITY_TESTER_AVAILABLE = True
except ImportError:
    VULNERABILITY_TESTER_AVAILABLE = False
    VulnerabilityTester = None

try:
    from external_apis import ExternalAPIs
    EXTERNAL_APIS_AVAILABLE = True
except ImportError:
    EXTERNAL_APIS_AVAILABLE = False
    ExternalAPIs = None

try:
    from encryption_analyzer import EncryptionAnalyzer
    ENCRYPTION_ANALYZER_AVAILABLE = True
except ImportError:
    ENCRYPTION_ANALYZER_AVAILABLE = False
    EncryptionAnalyzer = None

try:
    from anomaly_detector import AnomalyDetector
    ANOMALY_DETECTOR_AVAILABLE = True
except ImportError:
    ANOMALY_DETECTOR_AVAILABLE = False
    AnomalyDetector = None

# Porównywanie skanów - usunięte (nie jest potrzebne)

# Rich console dla pięknego wyświetlania w terminalu
console = Console()


def make_json_serializable(obj: Any) -> Any:
    """
    Konwertuje obiekty numpy i inne niestandardowe typy na typy serializowalne do JSON.
    
    Args:
        obj: Obiekt do konwersji
        
    Returns:
        Obiekt serializowalny do JSON
    """
    if isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, dict):
        return {key: make_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj


class MedicalDeviceScanner:
    """
    Główna klasa skanera urządzeń medycznych.
    
    Ta klasa:
    1. Zarządza skanowaniem (BLE, WiFi, USB, NFC)
    2. Analizuje bezpieczeństwo urządzeń
    3. Generuje raporty
    4. Przechowuje wyniki
    """
    
    def __init__(self, protocols: List[str] = None):
        """
        Inicjalizacja skanera.
        
        Args:
            protocols: Lista protokołów do skanowania (['ble', 'wifi', 'usb', 'nfc'])
                      Jeśli None, skanuje wszystkie dostępne protokoły
        """
        # Inicjalizuj skanery dla każdego protokołu
        self.scanners = {}
        
        # Katalogi do zapisywania danych
        # Używamy Path do niezależnej od systemu ścieżki
        project_root = Path(__file__).parent.parent
        # Raporty i skany zapisujemy bezpośrednio w głównym katalogu projektu
        self.scans_dir = project_root / "reports"
        self.reports_dir = project_root / "reports"
        self.exports_dir = project_root / "exports"
        # Utwórz katalogi jeśli nie istnieją
        self.scans_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        self.exports_dir.mkdir(exist_ok=True)
        
        if protocols is None:
            protocols = ['ble', 'wifi', 'usb', 'nfc']
        
        # BLE Scanner
        if 'ble' in protocols:
            if BLE_SCANNER_AVAILABLE:
                try:
                    self.scanners['ble'] = RealBLEScanner()
                    console.print("[green]✅ Skaner BLE gotowy[/green]")
                except ImportError as e:
                    console.print(f"[yellow]⚠️  Skaner BLE niedostępny: {e}[/yellow]")
                    # Sprawdź czy to problem z venv (gdy używamy sudo)
                    venv_path = os.getenv('VIRTUAL_ENV')
                    if venv_path and 'venv' in str(venv_path):
                        console.print("[yellow]   Uwaga: Używasz sudo, który nie widzi bibliotek z venv![/yellow]")
                        console.print("[yellow]   Rozwiązanie 1 (ZALECANE - bez sudo dla BLE):[/yellow]")
                        console.print("[yellow]     python3 src/scanner.py --ble[/yellow]")
                        console.print("[yellow]   Rozwiązanie 2 (Z sudo dla scapy):[/yellow]")
                        console.print("[yellow]     source venv/bin/activate[/yellow]")
                        console.print("[yellow]     sudo -E python3 src/scanner.py --wifi[/yellow]")
                    else:
                        console.print("[yellow]   Zainstaluj: pip install bleak[/yellow]")
            else:
                console.print("[yellow]⚠️  Skaner BLE niedostępny (zainstaluj: pip install bleak)[/yellow]")
        
        # WiFi Scanner
        if 'wifi' in protocols:
            if WIFI_SCANNER_AVAILABLE:
                self.scanners['wifi'] = WiFiScanner()
                console.print("[green]✅ Skaner WiFi gotowy[/green]")
            else:
                console.print("[yellow]⚠️  Skaner WiFi niedostępny (zainstaluj: pip install python-nmap)[/yellow]")
        
        # USB Scanner
        if 'usb' in protocols:
            if USB_SCANNER_AVAILABLE:
                self.scanners['usb'] = USBScanner()
                console.print("[green]✅ Skaner USB gotowy[/green]")
            else:
                console.print("[yellow]⚠️  Skaner USB niedostępny (zainstaluj: pip install pyusb pyserial)[/yellow]")
        
        # NFC Scanner
        if 'nfc' in protocols:
            if NFC_SCANNER_AVAILABLE:
                self.scanners['nfc'] = NFCScanner()
                console.print("[green]✅ Skaner NFC gotowy[/green]")
            else:
                console.print("[yellow]⚠️  Skaner NFC niedostępny (zainstaluj: pip install nfcpy pyscard)[/yellow]")
        
        if not self.scanners:
            console.print("[red]❌ Brak dostępnych skanerów![/red]")
            console.print("[yellow]   Zainstaluj zależności: pip install -r requirements.txt[/yellow]\n")
        
        console.print()
        self.devices: List[Device] = []
        
        # Inicjalizuj tester podatności jeśli dostępny
        if VULNERABILITY_TESTER_AVAILABLE and VulnerabilityTester:
            try:
                from cve_lookup import CVELookup
                cve_lookup = CVELookup()
                use_cve_api = cve_lookup.nvd_api_key is not None
                self.vulnerability_tester = VulnerabilityTester(use_cve_api=use_cve_api)
            except Exception as e:
                console.print(f"[yellow]⚠️  Nie można zainicjalizować VulnerabilityTester: {e}[/yellow]")
                self.vulnerability_tester = None
        else:
            self.vulnerability_tester = None
        
        # Inicjalizuj zewnętrzne API (jeśli dostępne)
        if EXTERNAL_APIS_AVAILABLE and ExternalAPIs:
            try:
                self.external_apis = ExternalAPIs()
            except Exception as e:
                console.print(f"[yellow]⚠️  Nie można zainicjalizować ExternalAPIs: {e}[/yellow]")
                self.external_apis = None
        else:
            self.external_apis = None
        
        
        # Inicjalizuj analizator szyfrowania (jeśli dostępny)
        if ENCRYPTION_ANALYZER_AVAILABLE and EncryptionAnalyzer:
            try:
                self.encryption_analyzer = EncryptionAnalyzer()
            except Exception as e:
                console.print(f"[yellow]⚠️  Nie można zainicjalizować EncryptionAnalyzer: {e}[/yellow]")
                self.encryption_analyzer = None
        else:
            self.encryption_analyzer = None
        
        # Inicjalizuj detektor anomalii (jeśli dostępny)
        if ANOMALY_DETECTOR_AVAILABLE and AnomalyDetector:
            try:
                self.anomaly_detector = AnomalyDetector(contamination=0.1)
                # Spróbuj wczytać wcześniej wytrenowany model
                if self.anomaly_detector.load_model():
                    console.print("[green]✅ Detektor anomalii gotowy (wczytano model)[/green]")
                else:
                    console.print("[green]✅ Detektor anomalii gotowy (będzie trenowany przy pierwszym użyciu)[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠️  Nie można zainicjalizować AnomalyDetector: {e}[/yellow]")
                self.anomaly_detector = None
        else:
            self.anomaly_detector = None
    
    def scan_all(self) -> List[Device]:
        """
        Skanuje wszystkie dostępne protokoły (BLE, WiFi, USB, NFC).
        
        Returns:
            Lista wszystkich wykrytych urządzeń
        """
        console.print("[bold blue]🔍 Rozpoczynam kompleksowe skanowanie...[/bold blue]\n")
        
        all_devices = []
        
        # Skanuj BLE
        if 'ble' in self.scanners:
            console.print(Panel.fit("📡 Skanowanie Bluetooth Low Energy (BLE)", style="cyan"))
            ble_devices = self._scan_ble_async(duration=10)
            all_devices.extend(ble_devices)
            console.print()
        
        # Skanuj WiFi
        if 'wifi' in self.scanners:
            console.print(Panel.fit("📡 Skanowanie WiFi", style="cyan"))
            wifi_devices = self.scanners['wifi'].scan_wifi_devices()
            all_devices.extend(wifi_devices)
            console.print()
        
        # Skanuj USB
        if 'usb' in self.scanners:
            console.print(Panel.fit("🔌 Skanowanie USB", style="cyan"))
            usb_devices = self.scanners['usb'].scan_usb_devices()
            all_devices.extend(usb_devices)
            console.print()
        
        # Skanuj NFC
        if 'nfc' in self.scanners:
            console.print(Panel.fit("📱 Skanowanie NFC", style="cyan"))
            nfc_devices = self.scanners['nfc'].scan_nfc_devices(duration=5)
            all_devices.extend(nfc_devices)
            console.print()
        
        self.devices = all_devices
        
        console.print(f"[bold green]✅ Skanowanie zakończone![/bold green]")
        console.print(f"[green]Znaleziono łącznie {len(all_devices)} urządzeń medycznych[/green]\n")
        
        return all_devices
    
    def _scan_ble_async(self, duration: int = 10) -> List[Device]:
        """
        Wrapper do asynchronicznego skanowania BLE.
        
        Prawdziwy skaner BLE używa asynchronicznych funkcji (async/await),
        ale główny moduł scanner.py jest synchroniczny. Ta funkcja konwertuje
        asynchroniczne wywołanie na synchroniczne.
        
        Różnice między systemami:
        - Windows: Wymaga utworzenia nowego event loop
        - Linux/Mac: Można użyć asyncio.run() bezpośrednio
        
        Args:
            duration: Czas skanowania w sekundach
            
        Returns:
            Lista wykrytych urządzeń
        """
        if platform.system() == "Windows":
            # Windows wymaga innego event loop (to jest specyfika Windows)
            # Musimy utworzyć nowy event loop i użyć go
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Uruchom asynchroniczną funkcję w synchronicznym kontekście
                return loop.run_until_complete(self.scanners['ble'].scan_ble_devices(duration))
            finally:
                # Zawsze zamknij event loop, nawet jeśli wystąpił błąd
                loop.close()
        else:
            # Linux/Mac - możemy użyć asyncio.run() bezpośrednio
            # asyncio.run() automatycznie tworzy i zarządza event loop
            return asyncio.run(self.scanners['ble'].scan_ble_devices(duration))
    
    def analyze_security(self, run_vulnerability_tests: bool = False):
        """
        Analizuje bezpieczeństwo wszystkich wykrytych urządzeń.
        
        Ta funkcja:
        1. Oblicza security scores
        2. Wykrywa podatności (podstawowe - teoretyczne na podstawie znanych słabości portów)
        3. Sprawdza zgodność z FDA guidelines
        4. (Opcjonalnie) Wykonuje testy podatności i symulację ataków (z flagą --audit)
        
        UWAGA o podatnościach:
        - Podstawowe skanowanie: Podatności są TEORETYCZNE - na podstawie znanych słabości portów
          (np. "Port 22 otwarty - możliwość ataków brute-force"). To są ogólne ostrzeżenia.
        - Audyt (--audit): Wykonuje bardziej szczegółowe testy, sprawdza konfigurację,
          symuluje ataki (bez faktycznego atakowania), używa CVE i znanych exploity.
        
        Podatności są dodawane w dwóch miejscach:
        1. Podczas skanowania (wifi_scanner.py) - podstawowe, teoretyczne
        2. Podczas audytu (vulnerability_tester.py) - szczegółowe, kontekstowe
        
        Args:
            run_vulnerability_tests: Jeśli True, wykonuje pełny audyt bezpieczeństwa
        """
        console.print("[bold blue]🔒 Analizuję bezpieczeństwo urządzeń...[/bold blue]\n")
        
        for device in self.devices:
            # Oblicz wynik bezpieczeństwa
            device.calculate_security_score()
            
            # Sprawdź zgodność z FDA guidelines
            self._check_fda_compliance(device)
            
            # Wzbogać dane zewnętrznymi API (jeśli dostępne)
            if self.external_apis:
                self._enrich_device_with_external_apis(device)
            
            # Analizuj szyfrowanie (jeśli dostępne)
            if self.encryption_analyzer:
                self._analyze_encryption(device)
            
            # Wykonaj testy podatności jeśli włączone
            if run_vulnerability_tests and self.vulnerability_tester:
                self._run_vulnerability_tests(device)
        
        # Dla każdego urządzenia: na jakie ataki jest podatne (z audytu albo z portów/podatności)
        if self.vulnerability_tester:
            for device in self.devices:
                if "attack_susceptibility" not in (device.metadata or {}):
                    device.metadata = device.metadata or {}
                    device.metadata["attack_susceptibility"] = self.vulnerability_tester.get_attack_susceptibility(device)
        
        # Wykryj anomalie używając ML (jeśli dostępne) - zawsze włączone
        if self.anomaly_detector and len(self.devices) > 0:
            self._detect_anomalies()
        
        console.print("[bold green]✅ Analiza bezpieczeństwa zakończona[/bold green]\n")
    
    def _analyze_encryption(self, device: Device):
        """
        Analizuje szyfrowanie urządzenia i dodaje wyniki do metadanych.
        
        Args:
            device: Urządzenie do analizy
        """
        if not self.encryption_analyzer:
            return
        
        try:
            # Wykonaj analizę szyfrowania
            analysis = self.encryption_analyzer.analyze(
                encryption_type=device.encryption_type,
                has_encryption=device.has_encryption
            )
            
            # Zapisz wyniki w metadanych
            if not device.metadata:
                device.metadata = {}
            
            device.metadata["encryption_analysis"] = {
                "strength": analysis.strength.value,
                "is_weak": analysis.is_weak,
                "score": analysis.score,
                "issues": analysis.issues,
                "recommendations": analysis.recommendations
            }
            
            # Dodaj podatności jeśli szyfrowanie jest słabe
            if analysis.is_weak:
                for issue in analysis.issues:
                    device.add_vulnerability(f"Encryption: {issue}")
            
        except Exception as e:
            # Nie wyświetlaj błędów - analiza jest opcjonalna
            pass
    
    def _enrich_device_with_external_apis(self, device: Device):
        """
        Wzbogaca urządzenie danymi z zewnętrznych API (VirusTotal, Shodan).
        
        Args:
            device: Urządzenie do wzbogacenia
        """
        if not self.external_apis:
            return
        
        try:
            # Wyciągnij IP z metadanych (dla WiFi) lub z nazwy
            device_ip = None
            if device.metadata:
                device_ip = device.metadata.get('ip_address') or device.metadata.get('ip')
            
            # Jeśli nie ma IP w metadanych, spróbuj wyciągnąć z nazwy (dla WiFi)
            if not device_ip and device.protocol.value == "WiFi":
                # Często nazwa WiFi to IP (np. "192.168.1.1")
                import re
                ip_match = re.match(r'^(\d{1,3}\.){3}\d{1,3}$', device.name)
                if ip_match:
                    device_ip = device.name
            
            if device_ip:
                # Wzbogać danymi z API
                enriched = self.external_apis.enrich_device(
                    device_ip=device_ip,
                    device_mac=device.mac_address
                )
                
                # Dodaj do metadanych
                if not device.metadata:
                    device.metadata = {}
                
                device.metadata['external_apis'] = enriched
                
                # Dodaj podatności jeśli wykryto coś podejrzanego
                if enriched.get('virustotal'):
                    vt_data = enriched['virustotal']
                    if vt_data.get('malicious', 0) > 0:
                        # Dodaj szczegóły detekcji jeśli dostępne
                        detections = vt_data.get('detections', [])
                        if detections:
                            # Pokaż pierwsze 3 antywirusy które wykryły zagrożenie
                            engines = [d.get('engine', 'Unknown') for d in detections[:3]]
                            engines_str = ', '.join(engines)
                            if len(detections) > 3:
                                engines_str += f" (+{len(detections) - 3} więcej)"
                            device.add_vulnerability(
                                f"VirusTotal: IP flagged as malicious ({vt_data['malicious']} detections) - wykryte przez: {engines_str}"
                            )
                        else:
                            device.add_vulnerability(
                                f"VirusTotal: IP flagged as malicious ({vt_data['malicious']} detections)"
                            )
                    elif vt_data.get('suspicious', 0) > 0:
                        detections = vt_data.get('detections', [])
                        if detections:
                            engines = [d.get('engine', 'Unknown') for d in detections[:3]]
                            engines_str = ', '.join(engines)
                            if len(detections) > 3:
                                engines_str += f" (+{len(detections) - 3} więcej)"
                            device.add_vulnerability(
                                f"VirusTotal: IP flagged as suspicious ({vt_data['suspicious']} detections) - wykryte przez: {engines_str}"
                            )
                        else:
                            device.add_vulnerability(
                                f"VirusTotal: IP flagged as suspicious ({vt_data['suspicious']} detections)"
                            )
                
                if enriched.get('shodan'):
                    shodan_data = enriched['shodan']
                    if shodan_data.get('vulns'):
                        vuln_count = len(shodan_data['vulns'])
                        device.add_vulnerability(
                            f"Shodan: {vuln_count} known vulnerability/vulnerabilities detected"
                        )
        
        except Exception as e:
            # Nie wyświetlaj błędów - API są opcjonalne
            pass
    
    def _run_vulnerability_tests(self, device: Device):
        """
        Wykonuje testy podatności i symulację ataków na urządzeniu.
        
        Args:
            device: Urządzenie do przetestowania
        """
        if not self.vulnerability_tester:
            return
        
        try:
            # Wykonaj testy podatności
            test_results = self.vulnerability_tester.test_device(device)
            
            # Zapisz wyniki testów w metadanych urządzenia
            if test_results:
                device.metadata["vulnerability_tests"] = [
                    {
                        "name": t.name,
                        "severity": t.severity.value,
                        "attack_type": t.attack_type.value,
                        "is_vulnerable": t.is_vulnerable,
                        "details": t.details,
                        "recommendation": t.recommendation
                    }
                    for t in test_results
                ]
                
                # Na podstawie znanych podatności: na jakie ataki urządzenie jest podatne
                attack_susceptibility = self.vulnerability_tester.get_attack_susceptibility(device, test_results)
                device.metadata["attack_susceptibility"] = attack_susceptibility
                
                # Dodaj podatności do listy urządzenia
                for test in test_results:
                    if test.is_vulnerable:
                        device.add_vulnerability(f"{test.name}: {test.description}")
                
                # Przelicz security score z nowymi podatnościami
                device.calculate_security_score()
        except Exception as e:
            console.print(f"[yellow]⚠️  Błąd podczas testowania podatności dla {device.name}: {e}[/yellow]")
    
    def _detect_anomalies(self):
        """
        Wykrywa anomalie w urządzeniach używając Machine Learning.
        """
        if not self.anomaly_detector:
            return
        
        try:
            console.print("[bold cyan]🤖 Wykrywanie anomalii używając ML...[/bold cyan]")
            
            # Trenuj model jeśli nie jest wytrenowany (działa od 2 urządzeń wzwyż)
            if not self.anomaly_detector.trained:
                console.print("[dim]   Trenowanie modelu ML...[/dim]")
                train_result = self.anomaly_detector.train(self.devices)
                if not train_result.get('trained'):
                    console.print(f"[dim]   Model ML nie może być wytrenowany: {train_result.get('reason', 'Unknown')}[/dim]")
                    console.print("[dim]   Używam heurystyki do wykrywania anomalii...[/dim]")
            
            # Wykryj anomalie
            anomaly_results = self.anomaly_detector.detect_anomalies(self.devices, use_ensemble=True)
            
            # Statystyki
            stats = self.anomaly_detector.get_anomaly_statistics(anomaly_results)
            
            # Zapisz wyniki w metadanych urządzeń
            anomalies_found = 0
            for result in anomaly_results:
                device = result['device']
                if not device.metadata:
                    device.metadata = {}
                
                device.metadata['anomaly_detection'] = {
                    'is_anomaly': result['is_anomaly'],
                    'anomaly_score': result['anomaly_score'],
                    'method': result['method'],
                    'reason': result['reason'],
                    'scores': result.get('scores', {})
                }
                
                if result['is_anomaly']:
                    anomalies_found += 1
                    # Dodaj podatność jeśli anomalia
                    device.add_vulnerability(f"ML Anomaly Detection: {result['reason']}")
            
            # Wyświetl szczegółowe wyniki AI
            method_used = "Ensemble ML" if self.anomaly_detector.trained else "Heurystyka"
            method_details = "Isolation Forest + LOF + One-Class SVM" if self.anomaly_detector.trained else "Security score + vulnerabilities"
            
            console.print(f"\n[bold cyan]🤖 Wyniki analizy AI:[/bold cyan]")
            console.print(f"  📊 Przeanalizowano: {len(self.devices)} urządzeń")
            console.print(f"  📈 Metoda: {method_used} ({method_details})")
            
            if anomalies_found > 0:
                console.print(f"\n  [yellow]⚠️  Wykryto {anomalies_found} anomalii ({stats['anomalies_percentage']:.1f}%)[/yellow]")
                console.print(f"  [dim]   Średni anomaly score: {stats['avg_anomaly_score']:.2f}[/dim]")
                
                # Pokaż szczegóły anomalii
                console.print(f"\n  [bold yellow]🔍 Wykryte anomalie:[/bold yellow]")
                for result in anomaly_results:
                    if result['is_anomaly']:
                        device = result['device']
                        console.print(f"    • [yellow]{device.name}[/yellow] (Score: {result['anomaly_score']:.2f})")
                        console.print(f"      Metoda: {result['method']}")
                        console.print(f"      Powód: {result['reason']}")
                        if result.get('scores'):
                            scores_str = ", ".join([f"{k}: {v:.2f}" for k, v in result['scores'].items()])
                            console.print(f"      Szczegóły: {scores_str}")
            else:
                console.print(f"\n  [green]✅ Nie wykryto anomalii - wszystkie urządzenia są normalne[/green]")
                console.print(f"  [dim]   Średni anomaly score: {stats['avg_anomaly_score']:.2f}[/dim]")
            
            console.print()  # Pusta linia
            
        except Exception as e:
            console.print(f"[yellow]⚠️  Błąd wykrywania anomalii: {e}[/yellow]")
    
    def _check_fda_compliance(self, device: Device):
        """
        Sprawdza zgodność urządzenia z FDA Cybersecurity Guidance.
        
        FDA (Food and Drug Administration) to amerykańska agencja regulująca urządzenia medyczne.
        FDA wymaga, aby urządzenia medyczne miały odpowiednie zabezpieczenia:
        
        Wymagania FDA:
        - Szyfrowanie danych: Dane medyczne muszą być szyfrowane podczas transmisji
        - Autoryzacja dostępu: Tylko autoryzowane urządzenia mogą się połączyć (parowanie)
        - Aktualizacje bezpieczeństwa: Urządzenia muszą mieć możliwość aktualizacji firmware
        - Logowanie zdarzeń: Logowanie prób dostępu i użycia urządzenia
        
        Jeśli urządzenie nie spełnia wymagań FDA, dodajemy podatność.
        
        UWAGA: Sprawdzamy TYLKO urządzenia medyczne - nie dodajemy false positives dla urządzeń domowych.
        
        Args:
            device: Urządzenie do sprawdzenia
        """
        # Sprawdź czy to rzeczywiście urządzenie medyczne
        is_medical = self._is_medical_device(device)
        
        if not is_medical:
            # To nie jest urządzenie medyczne - nie sprawdzaj FDA
            device.metadata["fda_compliance"] = None  # Nie dotyczy
            return
        
        compliance_issues = []
        
        # Sprawdź szyfrowanie
        # FDA wymaga szyfrowania danych medycznych
        if not device.has_encryption:
            compliance_issues.append("FDA: Brak szyfrowania danych")
            device.add_vulnerability("FDA Non-compliance: Encryption")
        
        # Sprawdź autoryzację
        # FDA wymaga autoryzacji dostępu (parowanie)
        # UWAGA: Dla WiFi hasło do sieci to już autoryzacja, więc nie sprawdzamy requires_pairing
        if device.protocol.value == "WIFI":
            # WiFi wymaga hasła do sieci - to jest autoryzacja
            pass
        elif not device.requires_pairing:
            compliance_issues.append("FDA: Brak autoryzacji dostępu")
            device.add_vulnerability("FDA Non-compliance: Authentication")
        
        # Zapisz wynik zgodności w metadanych urządzenia
        if compliance_issues:
            device.metadata["fda_compliance"] = False
            device.metadata["fda_issues"] = compliance_issues
        else:
            device.metadata["fda_compliance"] = True
    
    def _is_medical_device(self, device: Device) -> bool:
        """
        Sprawdza czy urządzenie jest rzeczywiście medyczne.
        
        Args:
            device: Urządzenie do sprawdzenia
        
        Returns:
            True jeśli urządzenie jest medyczne
        """
        # Sprawdź typ urządzenia
        medical_types = [
            DeviceType.GLUCOSE_METER,
            DeviceType.INSULIN_PUMP,
            DeviceType.PULSE_OXIMETER,
            DeviceType.BLOOD_PRESSURE
        ]
        if device.device_type in medical_types:
            return True
        
        # Sprawdź nazwę urządzenia
        name_lower = device.name.lower()
        medical_keywords = [
            "medical", "med", "hospital", "clinic", "patient", "monitor",
            "glucose", "gluco", "insulin", "pump", "dicom", "hl7",
            "pacs", "ris", "emr", "ehr", "vital", "signs", "health"
        ]
        if any(keyword in name_lower for keyword in medical_keywords):
            return True
        
        # Sprawdź porty medyczne w metadanych
        open_ports = device.metadata.get("open_ports", [])
        medical_ports = [104, 11112, 5000]
        if any(p in open_ports for p in medical_ports):
            # Jeśli ma porty medyczne i mało innych portów, to może być urządzenie medyczne
            if len(open_ports) <= 5:
                return True
        
        return False
    
    def display_results(self):
        """Wyświetla wyniki skanowania w formie kart urządzeń"""
        if not self.devices:
            console.print("[red]❌ Nie znaleziono żadnych urządzeń[/red]")
            return
        
        # Podsumowanie statystyk
        total_devices = len(self.devices)
        high_risk = [d for d in self.devices if d.security_score < 50]
        medium_risk = [d for d in self.devices if 50 <= d.security_score < 80]
        low_risk = [d for d in self.devices if d.security_score >= 80]
        
        # Wyświetl podsumowanie
        summary_panel = Panel.fit(
            f"[bold]📊 Podsumowanie skanowania[/bold]\n\n"
            f"Total urządzeń: [bold cyan]{total_devices}[/bold cyan]\n"
            f"🔴 Wysokie ryzyko (score < 50): [bold red]{len(high_risk)}[/bold red]\n"
            f"🟡 Średnie ryzyko (50-79): [bold yellow]{len(medium_risk)}[/bold yellow]\n"
            f"🟢 Niskie ryzyko (≥80): [bold green]{len(low_risk)}[/bold green]",
            style="cyan",
            title="📈 Statystyki"
        )
        console.print(summary_panel)
        console.print()
        
        # Grupuj urządzenia według ryzyka i protokołu
        risk_groups = [
            ("🔴 WYSOKIE RYZYKO", high_risk, "red"),
            ("🟡 ŚREDNIE RYZYKO", medium_risk, "yellow"),
            ("🟢 NISKIE RYZYKO", low_risk, "green")
        ]
        
        protocol_names = {
            "BLE": "📶 Bluetooth Low Energy",
            "WiFi": "📡 WiFi (Sieć lokalna)",
            "USB": "🔌 USB",
            "NFC": "📱 NFC"
        }
        
        for group_title, devices_list, color in risk_groups:
            if not devices_list:
                continue
            
            console.print(f"\n[bold {color}]{group_title}[/bold {color}] ({len(devices_list)} urządzeń)\n")
            
            # Grupuj według protokołu
            by_protocol = {}
            for device in devices_list:
                protocol = device.protocol.value
                if protocol not in by_protocol:
                    by_protocol[protocol] = []
                by_protocol[protocol].append(device)
            
            # Wyświetl według protokołu
            for protocol in ["BLE", "WiFi", "USB", "NFC"]:
                if protocol not in by_protocol:
                    continue
                
                protocol_devices = by_protocol[protocol]
                protocol_label = protocol_names.get(protocol, protocol)
                console.print(f"  [dim]{protocol_label}: {len(protocol_devices)} urządzeń[/dim]\n")
                
                # Wyświetl każde urządzenie jako kartę
                for device in protocol_devices:
                    self._display_device_card(device, color)
                
                console.print()  # Pusta linia między protokołami
        
        # Wyświetl analizę szyfrowania jeśli dostępna
        if self.encryption_analyzer:
            self._display_encryption_analysis()
    
    def _display_device_card(self, device: Device, risk_color: str):
        """
        Wyświetla pojedyncze urządzenie jako kartę.
        
        Args:
            device: Urządzenie do wyświetlenia
            risk_color: Kolor ryzyka (red/yellow/green)
        """
        # Określ styl na podstawie ryzyka
        if device.security_score >= 80:
            panel_style = "green"
            risk_icon = "🟢"
        elif device.security_score >= 50:
            panel_style = "yellow"
            risk_icon = "🟡"
        else:
            panel_style = "red"
            risk_icon = "🔴"
        
        # Nagłówek karty - ulepszona nazwa
        device_display_name = device.name
        if device.name == "Unknown" or device.name.startswith("Product-"):
            # Dla urządzeń USB z generycznymi nazwami, użyj bardziej opisowej nazwy
            if device.protocol.value == "USB":
                if device.device_type.value == "USB_DEVICE":
                    device_display_name = f"Urządzenie USB ({device.mac_address[-5:]})"
                else:
                    device_display_name = f"{device.device_type.value.replace('_', ' ')} ({device.mac_address[-5:]})"
            elif device.protocol.value == "BLE":
                device_display_name = f"Urządzenie BLE ({device.mac_address[-5:]})"
            elif device.protocol.value == "WiFi":
                device_display_name = f"Urządzenie WiFi ({device.mac_address[-5:]})"
            else:
                device_display_name = f"Urządzenie {device.protocol.value} ({device.mac_address[-5:]})"
        
        # Nagłówek karty
        header = f"{risk_icon} [bold]{device_display_name}[/bold]"
        if device.manufacturer and device.manufacturer != "N/A":
            # Sprawdź czy producent nie jest fałszywy (dla losowych MAC)
            show_manufacturer = True
            if device.protocol.value == "BLE" and device.mac_address:
                try:
                    first_byte = int(device.mac_address.split(":")[0], 16)
                    is_random = (first_byte & 0x02) != 0
                    if is_random:
                        show_manufacturer = False
                except Exception:
                    pass
            
            # Dla WiFi - nie pokazuj producenta jeśli MAC jest wygenerowany (00:00:xx)
            if device.protocol.value == "WiFi" and device.mac_address.startswith("00:00:"):
                show_manufacturer = False
            
            if show_manufacturer:
                header += f" [dim]({device.manufacturer})[/dim]"
        
        header += f"  [bold {panel_style}]Score: {device.security_score}/100[/bold {panel_style}]"
        
        # Informacje podstawowe
        info_lines = []
        protocol_emoji = {
            "BLE": "📶",
            "WiFi": "📡",
            "USB": "🔌",
            "NFC": "📱"
        }.get(device.protocol.value, "🌐")
        
        info_lines.append(f"{protocol_emoji} Protokół: [bold cyan]{device.protocol.value}[/bold cyan]  |  Typ: {device.device_type.value}")
        info_lines.append(f"MAC: [yellow]{device.mac_address}[/yellow]")
        
        # IP address (jeśli dostępne)
        if device.metadata and device.metadata.get('ip_address'):
            info_lines.append(f"IP: [cyan]{device.metadata['ip_address']}[/cyan]")
        
        # Szyfrowanie i autoryzacja
        encryption_status = "✅ Szyfrowanie: Tak" if device.has_encryption else "❌ Szyfrowanie: Nie"
        pairing_status = "✅ Autoryzacja: Tak" if device.requires_pairing else "❌ Autoryzacja: Nie"
        
        if device.encryption_type:
            enc_type = device.encryption_type
            # Skróć jeśli zbyt długie
            if len(enc_type) > 30:
                enc_type = enc_type[:27] + "..."
            encryption_status += f" ({enc_type})"
        
        info_lines.append(f"{encryption_status}  |  {pairing_status}")
        
        # Podatności (usuń duplikaty)
        unique_vulns = list(set(device.vulnerabilities)) if device.vulnerabilities else []
        vuln_count = len(unique_vulns)
        if vuln_count > 0:
            vuln_text = f"⚠️  [bold red]{vuln_count} podatności[/bold red]"
            info_lines.append(vuln_text)
            
            # Pokaż pierwsze 3 unikalne podatności
            for vuln in unique_vulns[:3]:
                info_lines.append(f"  • [red]{vuln}[/red]")
            if vuln_count > 3:
                info_lines.append(f"  ... i {vuln_count - 3} więcej (zobacz raport)")
        else:
            info_lines.append("[green]✅ Brak wykrytych podatności[/green]")
        
        # Podatność na ataki (na podstawie znanych podatności i portów)
        attack_sus = (device.metadata or {}).get("attack_susceptibility", [])
        if attack_sus:
            attack_types = list({a.get("attack_type", "") for a in attack_sus if a.get("attack_type")})
            if attack_types:
                info_lines.append(f"[yellow]🎯 Podatność na ataki:[/yellow] {', '.join(attack_types[:5])}{'…' if len(attack_types) > 5 else ''}")
        
        # Analiza szyfrowania (jeśli dostępna)
        if device.metadata and "encryption_analysis" in device.metadata:
            enc_analysis = device.metadata["encryption_analysis"]
            strength = enc_analysis.get("strength", "unknown")
            if strength != "unknown":
                strength_emoji = {
                    "strong": "🟢",
                    "moderate": "🟡",
                    "weak": "🟠",
                    "none": "🔴"
                }.get(strength, "⚪")
                info_lines.append(f"{strength_emoji} Szyfrowanie: {strength.upper()} (Score: {enc_analysis.get('score', 0)}/100)")
        
        # FDA Compliance (jeśli dotyczy)
        if device.metadata and device.metadata.get("fda_compliance") is not None:
            if device.metadata["fda_compliance"]:
                info_lines.append("[green]✅ Zgodne z FDA[/green]")
            else:
                info_lines.append("[red]❌ Niezgodne z FDA[/red]")
                if device.metadata.get("fda_issues"):
                    for issue in device.metadata["fda_issues"][:2]:
                        info_lines.append(f"  • [red]{issue}[/red]")
        
        # Komunikaty z mikrokontrolera (jeśli dostępne)
        if device.metadata and device.metadata.get("microcontroller"):
            baudrate = device.metadata.get("baudrate", "N/A")
            messages = device.metadata.get("messages", [])
            message_count = device.metadata.get("message_count", 0)
            port = device.metadata.get('port', 'N/A')
            
            info_lines.append(f"\n[cyan]🔧 Mikrokontroler (USB Serial)[/cyan]")
            info_lines.append(f"  Port: {port}")
            info_lines.append(f"  Prędkość: {baudrate} baud")
            info_lines.append(f"  Status: {'✅ Aktywny' if messages else '⚠️  Brak komunikatów'}")
            info_lines.append(f"  Komunikaty: {message_count}")
            
            if messages:
                info_lines.append(f"  [dim]Ostatnie komunikaty:[/dim]")
                for msg in messages[:5]:  # Pokaż pierwsze 5
                    # Skróć długie komunikaty
                    display_msg = msg[:70] + "..." if len(msg) > 70 else msg
                    # Sprawdź czy to odpowiedź na komendę testową
                    if "[TEST:" in msg:
                        info_lines.append(f"    [yellow]→ {display_msg}[/yellow]")
                    else:
                        info_lines.append(f"    [green]→ {display_msg}[/green]")
                if len(messages) > 5:
                    info_lines.append(f"    [dim]... i {len(messages) - 5} więcej[/dim]")
            else:
                info_lines.append(f"  [dim]💡 Mikrokontroler wykryty, ale nie wysyła komunikatów[/dim]")
                info_lines.append(f"  [dim]   Może wymagać komendy startowej lub jest w trybie uśpienia[/dim]")
        
        # Utwórz panel
        card_content = "\n".join(info_lines)
        panel = Panel(
            card_content,
            title=header,
            border_style=panel_style,
            padding=(1, 2)
        )
        console.print(panel)
    
    def _calculate_encryption_stats(self) -> Dict:
        """
        Oblicza statystyki szyfrowania dla raportu.
        
        Returns:
            Słownik ze statystykami szyfrowania
        """
        if not self.devices:
            return {}
        
        total = len(self.devices)
        strong = 0
        moderate = 0
        weak = 0
        none = 0
        weak_algorithms = 0
        total_encryption_score = 0
        
        for device in self.devices:
            enc_analysis = device.metadata.get('encryption_analysis', {})
            if enc_analysis:
                strength = enc_analysis.get('strength', 'unknown')
                if strength == 'strong':
                    strong += 1
                elif strength == 'moderate':
                    moderate += 1
                elif strength == 'weak':
                    weak += 1
                elif strength == 'none':
                    none += 1
                
                if enc_analysis.get('is_weak', False):
                    weak_algorithms += 1
                
                total_encryption_score += enc_analysis.get('score', 0)
            else:
                # Jeśli brak analizy, sprawdź has_encryption
                if not device.has_encryption:
                    none += 1
                else:
                    moderate += 1  # Założenie domyślne
        
        return {
            "strong_encryption": strong,
            "moderate_encryption": moderate,
            "weak_encryption": weak,
            "no_encryption": none,
            "weak_algorithms_count": weak_algorithms,
            "average_encryption_score": total_encryption_score / total if total > 0 else 0
        }
    
    def _display_encryption_analysis(self):
        """
        Wyświetla krótkie podsumowanie analizy szyfrowania urządzeń.
        """
        if not self.devices:
            return
        
        # Zbierz proste statystyki
        total = len(self.devices)
        without_encryption = sum(1 for d in self.devices if not d.has_encryption)
        weak_count = 0
        
        for device in self.devices:
            if device.metadata and "encryption_analysis" in device.metadata:
                analysis = device.metadata["encryption_analysis"]
                if analysis.get("is_weak", False):
                    weak_count += 1
        
        # Wyświetl tylko krótkie podsumowanie jeśli są problemy
        if weak_count > 0 or without_encryption > 0:
            console.print(f"[dim]🔐 Szyfrowanie: {without_encryption} bez szyfrowania, {weak_count} ze słabym szyfrowaniem[/dim]")
    
    def save_scan_results(self) -> str:
        """
        Zapisuje surowe dane ze skanowania do pliku JSON w głównym katalogu projektu.
        
        Plik zawiera wszystkie wykryte urządzenia z pełnymi informacjami,
        włącznie z metadanymi, podatnościami i wynikami analizy bezpieczeństwa.
        
        Returns:
            Ścieżka do zapisanego pliku lub pusty string jeśli błąd
        """
        if not self.devices:
            console.print("[yellow]⚠️  Brak urządzeń do zapisania[/yellow]")
            return ""
        
        # Utwórz nazwę pliku z timestampem
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"scan_{timestamp}.json"
        filepath = self.scans_dir / filename
        
        # Przygotuj dane do zapisania
        scan_data = {
            "scan_timestamp": datetime.now().isoformat(),
            "total_devices": len(self.devices),
            "protocols_scanned": list(self.scanners.keys()),
            "devices": [device.to_dict() for device in self.devices]
        }
        
        # Zapisz do pliku JSON
        try:
            # Konwertuj wszystkie wartości na serializowalne do JSON
            scan_data_serializable = make_json_serializable(scan_data)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(scan_data_serializable, f, indent=2, ensure_ascii=False)
            
            console.print(f"[green]✅ Zapisano wyniki skanowania: {filepath}[/green]")
            return str(filepath)
        except Exception as e:
            console.print(f"[red]❌ Błąd zapisywania wyników: {e}[/red]")
            return ""
    
    def generate_report(self) -> dict:
        """
        Generuje raport z analizy bezpieczeństwa i zapisuje do data/reports/.
        
        Tworzy raporty w formatach:
        - JSON: Dane strukturalne do dalszej analizy
        
        Returns:
            Słownik ze ścieżkami do wygenerowanych raportów {'json': path}
        """
        if not self.devices:
            console.print("[yellow]⚠️  Brak urządzeń do raportowania[/yellow]")
            return {}
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_paths = {}
        
        # Generuj raport JSON
        json_path = self._generate_json_report(timestamp)
        if json_path:
            report_paths['json'] = json_path
        
        return report_paths
    
    def export_to_csv(self, output_path: Optional[str] = None) -> str:
        """
        Eksportuje wyniki skanowania do pliku CSV.
        
        CSV zawiera wszystkie urządzenia z kluczowymi informacjami:
        - Podstawowe dane (nazwa, MAC, typ, protokół)
        - Informacje o bezpieczeństwie (score, szyfrowanie, autoryzacja)
        - Lista podatności (oddzielone średnikami)
        - Metadane (producent, model, firmware)
        
        Args:
            output_path: Opcjonalna ścieżka do pliku CSV. Jeśli None, używa głównego katalogu projektu
        
        Returns:
            Ścieżka do zapisanego pliku CSV lub pusty string jeśli błąd
        """
        if not self.devices:
            console.print("[yellow]⚠️  Brak urządzeń do eksportu[/yellow]")
            return ""
        
        # Utwórz nazwę pliku z timestampem
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        if output_path:
            filepath = Path(output_path)
        else:
            filename = f"report_{timestamp}.csv"
            filepath = self.reports_dir / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                # Define CSV columns (English)
                fieldnames = [
                    'Name',
                    'MAC Address',
                    'Device Type',
                    'Protocol',
                    'Manufacturer',
                    'Model',
                    'Firmware',
                    'Security Score',
                    'Encryption',
                    'Encryption Type',
                    'Encryption Strength',
                    'Encryption Score',
                    'Encryption Issues',
                    'Encryption Recommendations',
                    'Requires Pairing',
                    'RSSI',
                    'Vulnerability Count',
                    'Vulnerabilities',
                    'FDA Compliance',
                    'First Seen',
                    'Last Seen',
                ]
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                # Write each device as a row
                for device in self.devices:
                    # Prepare vulnerabilities as text (separated by semicolons)
                    vulnerabilities_text = '; '.join(device.vulnerabilities) if device.vulnerabilities else ''
                    
                    # Prepare encryption analysis data
                    enc_analysis = device.metadata.get('encryption_analysis', {})
                    enc_issues = '; '.join(enc_analysis.get('issues', [])) if enc_analysis.get('issues') else 'N/A'
                    enc_recommendations = '; '.join(enc_analysis.get('recommendations', [])) if enc_analysis.get('recommendations') else 'N/A'
                    
                    # Prepare values
                    row = {
                        'Name': device.name or 'N/A',
                        'MAC Address': device.mac_address,
                        'Device Type': device.device_type.value,
                        'Protocol': device.protocol.value,
                        'Manufacturer': device.manufacturer or 'N/A',
                        'Model': device.model or 'N/A',
                        'Firmware': device.firmware_version or 'N/A',
                        'Security Score': device.security_score,
                        'Encryption': 'Yes' if device.has_encryption else 'No',
                        'Encryption Type': device.encryption_type or 'N/A',
                        'Encryption Strength': enc_analysis.get('strength', 'N/A').upper() if enc_analysis else 'N/A',
                        'Encryption Score': enc_analysis.get('score', 'N/A') if enc_analysis else 'N/A',
                        'Encryption Issues': enc_issues,
                        'Encryption Recommendations': enc_recommendations,
                        'Requires Pairing': 'Yes' if device.requires_pairing else 'No',
                        'RSSI': device.rssi if device.rssi is not None else 'N/A',
                        'Vulnerability Count': len(device.vulnerabilities),
                        'Vulnerabilities': vulnerabilities_text,
                        'FDA Compliance': 'Yes' if device.metadata.get('fda_compliance', False) else 'No' if device.metadata.get('fda_compliance') is False else 'N/A',
                        'First Seen': device.first_seen.strftime('%Y-%m-%d %H:%M:%S'),
                        'Last Seen': device.last_seen.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                    
                    writer.writerow(row)
            
            # Nie wyświetlaj komunikatu - będzie wyświetlony w main()
            return str(filepath)
        except Exception as e:
            console.print(f"[red]❌ Błąd eksportu do CSV: {e}[/red]")
            return ""
    
    def _generate_json_report(self, timestamp: str) -> str:
        """
        Generuje raport JSON z analizą bezpieczeństwa.
        
        Args:
            timestamp: Timestamp używany w nazwie pliku
        
        Returns:
            Ścieżka do zapisanego pliku lub pusty string jeśli błąd
        """
        filename = f"report_{timestamp}.json"
        filepath = self.reports_dir / filename
        
        # Przygotuj dane raportu
        total_devices = len(self.devices)
        high_risk = [d for d in self.devices if d.security_score < 50]
        medium_risk = [d for d in self.devices if 50 <= d.security_score < 80]
        low_risk = [d for d in self.devices if d.security_score >= 80]
        
        devices_without_encryption = [d for d in self.devices if not d.has_encryption]
        devices_without_pairing = [d for d in self.devices if not d.requires_pairing]
        fda_non_compliant = [d for d in self.devices if not d.metadata.get("fda_compliance", True)]
        
        # Oblicz statystyki szyfrowania
        encryption_stats = self._calculate_encryption_stats()
        
        report_data = {
            "report_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_devices": total_devices,
                "high_risk_count": len(high_risk),
                "medium_risk_count": len(medium_risk),
                "low_risk_count": len(low_risk),
                "devices_without_encryption": len(devices_without_encryption),
                "devices_without_pairing": len(devices_without_pairing),
                "fda_non_compliant": len(fda_non_compliant),
                "average_security_score": sum(d.security_score for d in self.devices) / total_devices if total_devices > 0 else 0,
                "encryption_stats": encryption_stats
            },
            "devices": [device.to_dict() for device in self.devices],
            "risk_groups": {
                "high_risk": [d.to_dict() for d in high_risk],
                "medium_risk": [d.to_dict() for d in medium_risk],
                "low_risk": [d.to_dict() for d in low_risk]
            },
            "vulnerabilities": {
                "no_encryption": [d.to_dict() for d in devices_without_encryption],
                "no_pairing": [d.to_dict() for d in devices_without_pairing],
                "fda_non_compliant": [d.to_dict() for d in fda_non_compliant]
            }
        }
        
        try:
            # Konwertuj wszystkie wartości na serializowalne do JSON
            report_data_serializable = make_json_serializable(report_data)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data_serializable, f, indent=2, ensure_ascii=False)
            
            console.print(f"[green]✅ Wygenerowano raport JSON: {filepath}[/green]")
            return str(filepath)
        except Exception as e:
            console.print(f"[red]❌ Błąd generowania raportu JSON: {e}[/red]")
            return ""
    
    def generate_combined_report(self, threat_intel_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Generuje jeden kompleksowy plik JSON łączący wszystkie dane:
        - Surowe dane ze skanowania (scan)
        - Analiza bezpieczeństwa (report)
        - Threat intelligence (jeśli dostępne)
        
        Args:
            threat_intel_data: Dane threat intelligence (opcjonalne)
        
        Returns:
            Ścieżka do zapisanego pliku lub pusty string jeśli błąd
        """
        if not self.devices:
            console.print("[yellow]⚠️  Brak urządzeń do raportowania[/yellow]")
            return ""
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"combined_report_{timestamp}.json"
        filepath = self.reports_dir / filename
        
        # Przygotuj dane ze skanowania (surowe)
        scan_data = {
            "scan_timestamp": datetime.now().isoformat(),
            "total_devices": len(self.devices),
            "protocols_scanned": list(self.scanners.keys()),
            "devices": [device.to_dict() for device in self.devices]
        }
        
        # Przygotuj dane z analizy bezpieczeństwa (report)
        total_devices = len(self.devices)
        high_risk = [d for d in self.devices if d.security_score < 50]
        medium_risk = [d for d in self.devices if 50 <= d.security_score < 80]
        low_risk = [d for d in self.devices if d.security_score >= 80]
        
        devices_without_encryption = [d for d in self.devices if not d.has_encryption]
        devices_without_pairing = [d for d in self.devices if not d.requires_pairing]
        fda_non_compliant = [d for d in self.devices if not d.metadata.get("fda_compliance", True)]
        
        encryption_stats = self._calculate_encryption_stats()
        
        report_data = {
            "summary": {
                "total_devices": total_devices,
                "high_risk_count": len(high_risk),
                "medium_risk_count": len(medium_risk),
                "low_risk_count": len(low_risk),
                "devices_without_encryption": len(devices_without_encryption),
                "devices_without_pairing": len(devices_without_pairing),
                "fda_non_compliant": len(fda_non_compliant),
                "average_security_score": sum(d.security_score for d in self.devices) / total_devices if total_devices > 0 else 0,
                "encryption_stats": encryption_stats
            },
            "risk_groups": {
                "high_risk": [d.to_dict() for d in high_risk],
                "medium_risk": [d.to_dict() for d in medium_risk],
                "low_risk": [d.to_dict() for d in low_risk]
            },
            "vulnerabilities": {
                "no_encryption": [d.to_dict() for d in devices_without_encryption],
                "no_pairing": [d.to_dict() for d in devices_without_pairing],
                "fda_non_compliant": [d.to_dict() for d in fda_non_compliant]
            }
        }
        
        # Powiąż threat intelligence z urządzeniami
        # Dodaj informacje o threat intelligence do każdego urządzenia
        devices_with_threat_intel = []
        for device in self.devices:
            device_dict = device.to_dict()
            
            # Znajdź threat intelligence dla tego urządzenia
            device_ip = device_dict.get('ip_address') or device.metadata.get('ip_address') or device.metadata.get('ip')
            if device_ip and threat_intel_data:
                threat_info = threat_intel_data.get(device_ip)
                if threat_info:
                    # Dodaj threat intelligence bezpośrednio do urządzenia
                    device_dict['threat_intelligence'] = threat_info
                    device_dict['threat_intelligence_linked'] = True
                else:
                    device_dict['threat_intelligence_linked'] = False
            else:
                device_dict['threat_intelligence_linked'] = False
            
            devices_with_threat_intel.append(device_dict)
        
        # Zaktualizuj scan_data z urządzeniami zawierającymi threat intelligence
        scan_data["devices"] = devices_with_threat_intel
        
        # Połącz wszystkie dane w jeden plik
        combined_data = {
            "report_timestamp": datetime.now().isoformat(),
            "scan": scan_data,
            "analysis": report_data,
            "threat_intelligence": threat_intel_data if threat_intel_data else {}
        }
        
        # Dodaj informację o threat intelligence
        if threat_intel_data:
            threats_found = sum(1 for r in threat_intel_data.values() if r.get('is_threat', False))
            # Dodaj mapowanie IP -> urządzenia dla łatwego wyszukiwania
            ip_to_devices = {}
            for device in devices_with_threat_intel:
                device_ip = device.get('ip_address')
                if device_ip:
                    if device_ip not in ip_to_devices:
                        ip_to_devices[device_ip] = []
                    ip_to_devices[device_ip].append({
                        'display_name': device.get('display_name', device.get('name', 'Unknown')),
                        'mac_address': device.get('mac_address'),
                        'device_fingerprint': device.get('device_fingerprint'),
                        'protocol': device.get('protocol')
                    })
            
            combined_data["threat_intelligence_summary"] = {
                "total_ips_checked": len(threat_intel_data),
                "threats_found": threats_found,
                "clean_ips": len(threat_intel_data) - threats_found,
                "ip_to_devices": ip_to_devices  # Mapowanie IP -> urządzenia
            }
        else:
            combined_data["threat_intelligence_summary"] = {
                "total_ips_checked": 0,
                "threats_found": 0,
                "clean_ips": 0,
                "note": "Threat intelligence not available or disabled"
            }
        
        try:
            # Konwertuj wszystkie wartości na serializowalne do JSON
            combined_data_serializable = make_json_serializable(combined_data)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(combined_data_serializable, f, indent=2, ensure_ascii=False)
            
            console.print(f"[green]✅ Wygenerowano kompleksowy raport: {filepath}[/green]")
            console.print(f"[dim]   Zawiera: skanowanie + analiza + threat intelligence[/dim]")
            return str(filepath)
        except Exception as e:
            console.print(f"[red]❌ Błąd generowania kompleksowego raportu: {e}[/red]")
            return ""
    
    def export_to_pdf(self, output_path: Optional[str] = None) -> str:
        """
        Eksportuje wyniki skanowania do pliku PDF.
        
        PDF zawiera:
        - Profesjonalny layout z nagłówkiem
        - Podsumowanie statystyk
        - Tabelę wszystkich urządzeń
        - Listę podatności dla każdego urządzenia
        - Informacje o zgodności z FDA
        
        Args:
            output_path: Opcjonalna ścieżka do pliku PDF. Jeśli None, używa głównego katalogu projektu
        
        Returns:
            Ścieżka do zapisanego pliku PDF lub pusty string jeśli błąd
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
        except ImportError:
            console.print("[yellow]⚠️  Biblioteka 'reportlab' nie jest zainstalowana.[/yellow]")
            console.print("   Zainstaluj: pip install reportlab")
            return ""
        
        if not self.devices:
            console.print("[yellow]⚠️  Brak urządzeń do eksportu[/yellow]")
            return ""
        
        # Utwórz nazwę pliku z timestampem
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        if output_path:
            filepath = Path(output_path)
        else:
            filename = f"report_{timestamp}.pdf"
            filepath = self.reports_dir / filename
        
        try:
            # Utwórz dokument PDF
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            story = []
            
            # Style
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#0066CC'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#0066CC'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            # Header
            story.append(Paragraph("🏥 Medical Device Security Scanner", title_style))
            story.append(Paragraph(f"Security Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Summary
            total_devices = len(self.devices)
            high_risk = [d for d in self.devices if d.security_score < 50]
            medium_risk = [d for d in self.devices if 50 <= d.security_score < 80]
            low_risk = [d for d in self.devices if d.security_score >= 80]
            avg_score = sum(d.security_score for d in self.devices) / total_devices if total_devices > 0 else 0
            
            story.append(Paragraph("📊 Summary", heading_style))
            summary_data = [
                ['Metric', 'Value'],
                ['Total Devices', str(total_devices)],
                ['🔴 High Risk (score < 50)', str(len(high_risk))],
                ['🟡 Medium Risk (50-79)', str(len(medium_risk))],
                ['🟢 Low Risk (≥80)', str(len(low_risk))],
                ['Average Security Score', f"{avg_score:.1f}/100"],
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066CC')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Devices table
            story.append(Paragraph("📱 Devices", heading_style))
            
            # Prepare data for table
            device_data = [['Name', 'MAC', 'Type', 'Score', 'Encrypt', 'Pairing', 'Vulns']]
            
            for device in self.devices:
                encryption = '✅' if device.has_encryption else '❌'
                pairing = '✅' if device.requires_pairing else '❌'
                vuln_count = len(device.vulnerabilities)
                
                # Skróć nazwę jeśli zbyt długa
                name = device.name[:30] + '...' if len(device.name) > 30 else device.name
                mac = device.mac_address[:12] + '...' if len(device.mac_address) > 12 else device.mac_address
                
                device_data.append([
                    name,
                    mac,
                    device.device_type.value[:15],
                    f"{device.security_score}/100",
                    encryption,
                    pairing,
                    str(vuln_count)
                ])
            
            # Utwórz tabelę (maksymalnie 20 wierszy na stronę)
            max_rows_per_page = 20
            for i in range(0, len(device_data), max_rows_per_page):
                page_data = device_data[i:i+max_rows_per_page]
                if i > 0:
                    page_data = [device_data[0]] + page_data  # Dodaj nagłówek
                
                device_table = Table(page_data, colWidths=[1.5*inch, 1.2*inch, 1*inch, 0.8*inch, 0.6*inch, 0.8*inch, 0.7*inch])
                device_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066CC')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Score wyśrodkowany
                    ('ALIGN', (4, 1), (6, -1), 'CENTER'),  # Ikony wyśrodkowane
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]))
                story.append(device_table)
                if i + max_rows_per_page < len(device_data):
                    story.append(PageBreak())
            
            story.append(Spacer(1, 0.3*inch))
            
            # High-risk devices
            if high_risk:
                story.append(Paragraph("⚠️ High-Risk Devices", heading_style))
                for device in high_risk:
                    story.append(Paragraph(f"<b>{device.name}</b> ({device.mac_address}) - Score: {device.security_score}/100", styles['Normal']))
                    if device.vulnerabilities:
                        story.append(Paragraph("Vulnerabilities:", styles['Normal']))
                        for vuln in device.vulnerabilities[:5]:  # Maximum 5 vulnerabilities
                            story.append(Paragraph(f"  • {vuln}", styles['Normal']))
                        if len(device.vulnerabilities) > 5:
                            story.append(Paragraph(f"  ... and {len(device.vulnerabilities) - 5} more", styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
            
            # Footer
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Paragraph("Medical Device Security Scanner - Open Source Tool", styles['Normal']))
            
            # Zbuduj PDF
            doc.build(story)
            
            # Nie wyświetlaj komunikatu - będzie wyświetlony w main()
            return str(filepath)
        except Exception as e:
            console.print(f"[red]❌ Błąd eksportu do PDF: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
            return ""
    
    def get_devices_by_risk(self) -> dict:
        """
        Grupuje urządzenia według poziomu ryzyka.
        
        Returns:
            Słownik z urządzeniami pogrupowanymi według ryzyka
        """
        high_risk = [d for d in self.devices if d.security_score < 50]
        medium_risk = [d for d in self.devices if 50 <= d.security_score < 80]
        low_risk = [d for d in self.devices if d.security_score >= 80]
        
        return {
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk
        }


def _export_to_siem_jsonl(devices: List[Device], output_file: str, timestamp: str) -> str:
    """
    Eksportuje urządzenia do SIEM w formacie JSON Lines (wbudowane w scanner.py).
    
    Args:
        devices: Lista urządzeń
        output_file: Nazwa pliku wyjściowego (bez ścieżki)
        timestamp: Timestamp skanowania
    
    Returns:
        Ścieżka do wygenerowanego pliku
    """
    # Zapisz w katalogu exports/
    project_root = Path(__file__).parent.parent
    exports_dir = project_root / "exports"
    exports_dir.mkdir(exist_ok=True)
    output_path = exports_dir / output_file
    lines = []
    for device in devices:
        event = {
            '@timestamp': timestamp,
            'event': {
                'kind': 'event',
                'category': 'network',
                'type': 'device_scan',
                'severity': 'Low' if device.security_score >= 80 else 'Medium' if device.security_score >= 50 else 'High' if device.security_score >= 30 else 'Critical'
            },
            'device': {
                'name': device.name,
                'mac_address': device.mac_address,
                'ip_address': device.metadata.get('ip_address'),
                'type': device.device_type.value,
                'protocol': device.protocol.value,
                'manufacturer': device.manufacturer,
                'security_score': device.security_score,
                'has_encryption': device.has_encryption,
                'encryption_type': device.encryption_type,
                'requires_pairing': device.requires_pairing,
                'vulnerabilities': device.vulnerabilities,
                'vulnerability_count': len(device.vulnerabilities),
                'open_ports': device.metadata.get('open_ports', [])
            },
            'scan': {
                'timestamp': timestamp,
                'scanner': 'Medical Device Security Scanner'
            }
        }
        lines.append(json.dumps(event, ensure_ascii=False))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return str(output_path)


def _check_threat_intelligence(devices: List[Device]) -> Dict[str, Any]:
    """
    Sprawdza threat intelligence dla urządzeń (wbudowane w scanner.py).
    
    Args:
        devices: Lista urządzeń
    
    Returns:
        Słownik z wynikami threat intelligence
    """
    results = {}
    
    # Sprawdź czy AbuseIPDB API key jest dostępny
    abuseipdb_key = os.getenv("ABUSEIPDB_API_KEY")
    if not abuseipdb_key:
        return results  # Brak klucza - pomiń
    
    # Zbierz unikalne IP
    ips_to_check = set()
    for device in devices:
        ip = device.metadata.get('ip_address')
        if ip and ip not in ['N/A', 'Unknown', '']:
            ips_to_check.add(ip)
    
    if not ips_to_check:
        return results
    
    # Sprawdź AbuseIPDB (z rate limiting)
    try:
        import requests
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        def check_ip(ip: str) -> tuple:
            try:
                url = "https://api.abuseipdb.com/api/v2/check"
                headers = {'Key': abuseipdb_key, 'Accept': 'application/json'}
                params = {'ipAddress': ip, 'maxAgeInDays': 90, 'verbose': ''}
                
                response = requests.get(url, headers=headers, params=params, timeout=5)
                time.sleep(1.1)  # Rate limit: 1 req/second
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data:
                        abuse_data = data['data']
                        return (ip, {
                            'ip': ip,
                            'is_threat': abuse_data.get('abuseConfidencePercentage', 0) > 25,
                            'abuse_score': abuse_data.get('abuseConfidencePercentage', 0),
                            'reputation': 'malicious' if abuse_data.get('abuseConfidencePercentage', 0) > 25 else 'clean',
                            'sources': {'abuseipdb': abuse_data}
                        })
            except Exception:
                pass
            return (ip, {'ip': ip, 'is_threat': False, 'error': 'check_failed'})
        
        # Sprawdź równolegle (max 3 jednocześnie dla rate limiting)
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(check_ip, ip): ip for ip in ips_to_check}
            for future in as_completed(futures):
                ip, result = future.result()
                results[ip] = result
    except ImportError:
        pass  # requests nie dostępne
    except Exception:
        pass
    
    return results


 HEAD

=======
>>>>>>> b6ada5a362eeb9ab5f698bccde631164f6286147
def _send_report_email(to_addr: str, filepath: str) -> None:
    """Wysyła raport (combined_report JSON) emailem. SMTP z .env (jak ESP32)."""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email import encoders
    except ImportError:
        console.print("[yellow]⚠️  Brak modułu email/smtplib – pomijam wysyłkę raportu.[/yellow]")
        return
    smtp_server = os.getenv("SMTP_SERVER") or os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    from_addr = os.getenv("EMAIL_FROM") or user
    if not smtp_server or not user or not password or not to_addr:
        console.print("[yellow]⚠️  Brak SMTP_SERVER/SMTP_USER/SMTP_PASSWORD lub adresu. Sprawdź .env[/yellow]")
        return
    if not filepath or not os.path.isfile(filepath):
        console.print("[yellow]⚠️  Brak pliku raportu do wysłania.[/yellow]")
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            body_json = f.read()
    except Exception as e:
        console.print(f"[red]❌ Nie można odczytać raportu: {e}[/red]")
        return
    msg = MIMEMultipart()
    msg["Subject"] = f"[Scanner] Raport audytu {os.path.basename(filepath)}"
    msg["From"] = from_addr
    msg["To"] = to_addr
    summary = f"Raport skanowania/audytu załączony: {os.path.basename(filepath)}\n\nKonfiguracja SMTP jak dla ESP32 (Proton itd.): docs/CRON_PROTON_ESP32.md"
    msg.attach(MIMEText(summary, "plain", "utf-8"))
    part = MIMEBase("application", "json")
    part.set_payload(body_json.encode("utf-8"))
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment", filename=os.path.basename(filepath))
    msg.attach(part)
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(from_addr, to_addr, msg.as_string())
        console.print(f"[green]✅ Raport wysłany emailem na {to_addr}[/green]")
    except Exception as e:
        console.print(f"[red]❌ Błąd SMTP (sprawdź .env, token Proton, sieć): {e}[/red]")

<<<<<<< HEAD
=======

>>>>>>> b6ada5a362eeb9ab5f698bccde631164f6286147
def main():
    """Główna funkcja - punkt wejścia programu"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Medical Device Security Scanner')
    parser.add_argument('--ble', action='store_true', help='Skanuj tylko BLE')
    parser.add_argument('--wifi', action='store_true', help='Skanuj tylko WiFi')
    parser.add_argument('--usb', action='store_true', help='Skanuj tylko USB')
    parser.add_argument('--nfc', action='store_true', help='Skanuj tylko NFC')
    parser.add_argument('--audit', action='store_true', help='Pełny audyt bezpieczeństwa (testy podatności)')
    parser.add_argument('--api', action='store_true', help='Uruchom API server po skanowaniu')
    parser.add_argument('--api-port', type=int, default=5000, help='Port dla API server (domyślnie 5000)')
    parser.add_argument('--no-wifi', action='store_true', help='Pomiń skanowanie WiFi (tylko urządzenia bezpośrednio podłączone)')
    parser.add_argument('--no-siem', action='store_true', help='Wyłącz automatyczny eksport do SIEM (domyślnie włączony)')
    parser.add_argument('--no-threat-intel', action='store_true', help='Wyłącz automatyczne sprawdzanie threat intelligence (domyślnie włączone)')
    parser.add_argument('--legacy-reports', action='store_true', help='Twórz również stare pliki (scan_*.json, report_*.json) - domyślnie tylko combined_report_*.json')
    
    # Nowe funkcjonalności
    parser.add_argument('--schedule', type=str, help='Zaplanuj skanowanie (np. "daily 09:00", "hourly", "every 30 minutes")')
    parser.add_argument('--monitor', action='store_true', help='Uruchom monitoring w czasie rzeczywistym')
<<<<<<< HEAD
    parser.add_argument('--interval', type=int, default=300, help='Interwał monitoringu w sekundach (domyślnie 300 = 5 minut)')	
    parser.add_argument('--report-email', metavar='ADR', default=None, help='Po zakończeniu skanowania wyślij raport (combined_report) emailem (SMTP z .env, jak ESP32)')

=======
    parser.add_argument('--interval', type=int, default=300, help='Interwał monitoringu w sekundach (domyślnie 300 = 5 minut)')
    parser.add_argument('--report-email', metavar='ADR', default=None, help='Po zakończeniu skanowania wyślij raport (combined_report) emailem (SMTP z .env, jak ESP32)')
    
>>>>>>> b6ada5a362eeb9ab5f698bccde631164f6286147
    args = parser.parse_args()
    
    console.print(Panel.fit(
        "[bold cyan]🏥 Medical Device Security Scanner[/bold cyan]\n"
        "[dim]Narzędzie do audytu bezpieczeństwa urządzeń medycznych IoT[/dim]",
        style="cyan"
    ))
    console.print()
    
    # Określ protokoły do skanowania
    protocols = []
    if args.ble:
        protocols.append('ble')
    if args.wifi:
        protocols.append('wifi')
    if args.usb:
        protocols.append('usb')
    if args.nfc:
        protocols.append('nfc')
    
    # Jeśli nie wybrano żadnego protokołu, skanuj wszystkie (oprócz WiFi jeśli --no-wifi)
    if not protocols:
        protocols = ['ble', 'usb', 'nfc']
        if not args.no_wifi:
            protocols.append('wifi')
    
    run_vulnerability_tests = args.audit
    
    # Utwórz skaner
    scanner = MedicalDeviceScanner(protocols=protocols)
    
    # Skanuj urządzenia
    devices = scanner.scan_all()
    
    # Sprawdź czy znaleziono urządzenia
    if not devices:
        console.print("[yellow]⚠️  Nie znaleziono żadnych urządzeń[/yellow]")
        console.print("[dim]💡 Wskazówka: WiFi skanuje całą sieć lokalną (wszystkie urządzenia w sieci WiFi)[/dim]")
        console.print("[dim]   Użyj --no-wifi aby skanować tylko urządzenia bezpośrednio podłączone (USB, BLE)[/dim]\n")
    else:
        # Analizuj bezpieczeństwo
        scanner.analyze_security(run_vulnerability_tests=run_vulnerability_tests)
        
        # Wyświetl wyniki
        scanner.display_results()
        
        # Pokaż urządzenia wysokiego ryzyka (uproszczone, czytelne)
        risk_groups = scanner.get_devices_by_risk()
        if risk_groups["high_risk"]:
            console.print("\n[bold red]⚠️  URZĄDZENIA WYSOKIEGO RYZYKA:[/bold red]\n")
            
            # Grupuj według protokołu
            by_protocol = {}
            for device in risk_groups["high_risk"]:
                protocol = device.protocol.value
                if protocol not in by_protocol:
                    by_protocol[protocol] = []
                by_protocol[protocol].append(device)
            
            # Wyświetl według protokołu
            protocol_names = {
                "BLE": "📶 Bluetooth Low Energy (BLE)",
                "WiFi": "📡 WiFi (Sieć lokalna)",
                "USB": "🔌 USB (Podłączone bezpośrednio)",
                "NFC": "📱 NFC (Karty/Tagi)"
            }
            
            for protocol, devices in by_protocol.items():
                protocol_label = protocol_names.get(protocol, f"🌐 {protocol}")
                console.print(f"[bold cyan]{protocol_label}[/bold cyan] ({len(devices)} urządzeń):")
                
                # Grupuj duplikaty (te same nazwy)
                name_groups = {}
                for device in devices:
                    name = device.name if device.name != "Unknown" else f"Unknown-{device.mac_address[-5:]}"
                    if name not in name_groups:
                        name_groups[name] = []
                    name_groups[name].append(device)
                
                for name, device_list in name_groups.items():
                    # Jeśli tylko jedno urządzenie z tą nazwą
                    if len(device_list) == 1:
                        device = device_list[0]
                        console.print(f"  • [yellow]{name}[/yellow]")
                        console.print(f"    MAC: {device.mac_address} | Score: {device.security_score}/100")
                        if device.vulnerabilities:
                            # Pokaż unikalne podatności
                            unique_vulns = list(set(device.vulnerabilities))
                            console.print(f"    ⚠️  Podatności ({len(unique_vulns)}):")
                            for vuln in unique_vulns[:3]:
                                console.print(f"      - {vuln}")
                            if len(unique_vulns) > 3:
                                console.print(f"      ... i {len(unique_vulns) - 3} więcej")
                    else:
                        # Wiele urządzeń z tą samą nazwą - pokaż razem
                        console.print(f"  • [yellow]{name}[/yellow] ({len(device_list)} urządzeń)")
                        unique_vulns = set()
                        for device in device_list:
                            unique_vulns.update(device.vulnerabilities)
                        if unique_vulns:
                            console.print(f"    ⚠️  Podatności ({len(unique_vulns)}):")
                            for vuln in list(unique_vulns)[:3]:
                                console.print(f"      - {vuln}")
                            if len(unique_vulns) > 3:
                                console.print(f"      ... i {len(unique_vulns) - 3} więcej")
                        console.print(f"    [dim]MAC adresy: {', '.join([d.mac_address for d in device_list[:3]])}[/dim]")
                        if len(device_list) > 3:
                            console.print(f"    [dim]... i {len(device_list) - 3} więcej[/dim]")
                
                console.print()  # Pusta linia między protokołami
        
        # Zapisz wyniki
        # Domyślnie tworzymy tylko combined_report_*.json (wszystkie dane w jednym pliku)
        # Stare pliki (scan_*.json, report_*.json) są tworzone tylko jeśli --legacy-reports
        if args.legacy_reports:
            scan_file = scanner.save_scan_results()
            report_files = scanner.generate_report()
            console.print("[dim]   Utworzono również stare pliki (scan_*.json, report_*.json) dla kompatybilności wstecznej[/dim]")
        else:
            scan_file = ""
            report_files = {}
            console.print("[dim]   Tworzę tylko combined_report_*.json (wszystkie dane w jednym pliku)[/dim]")
        
        # Zapisz do historii (jeśli dostępne)
        try:
            from history_db import HistoryDB
            history_db = HistoryDB()
            scan_id = history_db.save_scan(devices, protocols)
            console.print(f"[dim]💾 Zapisano do historii (scan_id: {scan_id})[/dim]")
        except Exception as e:
            console.print(f"[dim]⚠️  Nie można zapisać do historii: {e}[/dim]")
            history_db = None
        
        # Automatyczny eksport do SIEM (domyślnie włączony, format JSON Lines - uniwersalny)
        if not args.no_siem:
            try:
                timestamp_str = datetime.now().isoformat()
                file_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                siem_file = f"siem_export_{file_timestamp}.jsonl"
                
                console.print("[cyan]📤 Eksportuję do SIEM (JSON Lines)...[/cyan]")
                export_file = _export_to_siem_jsonl(scanner.devices, siem_file, timestamp_str)
                console.print(f"[green]✅ Zapisano: {export_file}[/green]")
                # Aktualizuj ścieżkę dla import_to_splunk.sh
                console.print(f"[dim]💡 Import do Splunk: ./scripts/import_to_splunk.sh[/dim]")
                console.print(f"[dim]   💡 Prostsze: użyj --api aby zobaczyć wyniki w przeglądarce[/dim]")
                console.print(f"[dim]   💡 Lub zaimportuj do Splunk/ELK Stack - zobacz REKOMENDACJE_SIEM.md[/dim]")
            except Exception:
                pass  # Cicho pomiń jeśli błąd
        
        # Zapisz do historii (jeśli dostępne)
        try:
            from history_db import HistoryDB
            history_db = HistoryDB()
            scan_id = history_db.save_scan(devices, protocols)
            console.print(f"[dim]💾 Zapisano do historii (scan_id: {scan_id})[/dim]")
        except Exception as e:
            console.print(f"[dim]⚠️  Nie można zapisać do historii: {e}[/dim]")
            history_db = None
        
        # Funkcja do wykonania skanowania (dla scheduler/monitor)
        def perform_scan():
            """Wykonuje pełne skanowanie - używane przez scheduler/monitor"""
            # Utwórz nowy skaner
            scan_scanner = MedicalDeviceScanner(protocols=protocols)
            
            # Skanuj
            scan_devices = scan_scanner.scan_all()
            
            if scan_devices:
                # Analizuj
                scan_scanner.analyze_security(run_vulnerability_tests=run_vulnerability_tests)
                
                # Zapisz do historii
                try:
                    from history_db import HistoryDB
                    scan_history_db = HistoryDB()
                    scan_history_db.save_scan(scan_devices, protocols)
                except Exception:
                    pass
                
            
            return scan_devices
        
        # Zaplanowane skanowania (--schedule)
        if args.schedule:
            try:
                from scheduler import ScanScheduler
                scheduler = ScanScheduler()
                scheduler.add_schedule(args.schedule, perform_scan)
                scheduler.start()
                
                console.print("\n[green]✅ Scheduler uruchomiony[/green]")
                console.print("[dim]   Naciśnij Ctrl+C aby zatrzymać[/dim]\n")
                
                # Czekaj w nieskończoność
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    scheduler.stop()
                    console.print("\n[yellow]⏹️  Zatrzymano scheduler[/yellow]")
                    return
            except Exception as e:
                console.print(f"[red]❌ Błąd schedulera: {e}[/red]")
        
        # Monitoring w czasie rzeczywistym (--monitor)
        if args.monitor:
            try:
                from monitor import RealTimeMonitor
                from history_db import HistoryDB
                
                monitor_history_db = HistoryDB()
                
                monitor = RealTimeMonitor(
                    scan_function=perform_scan,
                    interval=args.interval,
                    alert_on_new=True,
                    alert_on_risk_change=True,
                    email_notifier=None,
                    history_db=monitor_history_db
                )
                
                monitor.start(email_recipients=[])
                
                console.print("\n[green]✅ Monitor uruchomiony[/green]")
                console.print("[dim]   Naciśnij Ctrl+C aby zatrzymać[/dim]\n")
                
                # Czekaj w nieskończoność
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    monitor.stop()
                    console.print("\n[yellow]⏹️  Zatrzymano monitor[/yellow]")
                    return
            except Exception as e:
                console.print(f"[red]❌ Błąd monitora: {e}[/red]")
        
        # Automatyczne sprawdzanie Threat Intelligence (jeśli klucz API dostępny)
        threat_intel_results = {}
        if not args.no_threat_intel:
            try:
                import threading
                import queue
                
                # Użyj queue do przekazania wyników z wątku
                threat_queue = queue.Queue()
                
                def check_threats():
                    try:
                        results = _check_threat_intelligence(scanner.devices)
                        threat_queue.put(results)
                        
                        if results:
                            threats_found = sum(1 for r in results.values() if r.get('is_threat', False))
                            if threats_found > 0:
                                console.print(f"[yellow]⚠️  Threat Intelligence: Znaleziono {threats_found} podejrzanych IP![/yellow]")
                    except Exception:
                        threat_queue.put({})  # Pusta wartość jeśli błąd
                
                # Uruchom w tle (nie blokuje)
                threat_thread = threading.Thread(target=check_threats, daemon=True)
                threat_thread.start()
                console.print("[cyan]🔍 Sprawdzam threat intelligence (w tle)...[/cyan]")
                # Wyświetl komunikat tylko jeśli klucz nie jest dostępny
                abuseipdb_key = os.getenv("ABUSEIPDB_API_KEY")
                if not abuseipdb_key:
                    console.print(f"[dim]   💡 Dodaj ABUSEIPDB_API_KEY do .env dla pełnej funkcjonalności[/dim]")
                
                # Poczekaj chwilę na zakończenie threat intelligence (max 30 sekund)
                threat_thread.join(timeout=30)
                
                # Pobierz wyniki z queue (jeśli są dostępne)
                try:
                    threat_intel_results = threat_queue.get(timeout=1)
                except queue.Empty:
                    threat_intel_results = {}  # Brak wyników
            except Exception:
                pass  # Cicho pomiń jeśli błąd
        
        # Generuj kompleksowy raport łączący wszystkie dane
        combined_report = scanner.generate_combined_report(threat_intel_data=threat_intel_results if threat_intel_results else None)
<<<<<<< HEAD

        if args.report_email and combined_report and os.path.isfile(combined_report):
            _send_report_email(args.report_email, combined_report)

=======
        
        # Wyślij raport emailem jeśli podano --report-email (SMTP z .env, jak ESP32)
        if args.report_email and combined_report and os.path.isfile(combined_report):
            _send_report_email(args.report_email, combined_report)
        
>>>>>>> b6ada5a362eeb9ab5f698bccde631164f6286147
        console.print("[bold green]✅ Skanowanie zakończone![/bold green]\n")
        
        # Uruchom API server jeśli żądane
        if args.api:
            console.print(f"[cyan]🌐 Uruchamiam API server na porcie {args.api_port}...[/cyan]")
            console.print(f"[dim]Otwórz w przeglądarce: http://localhost:{args.api_port}[/dim]\n")
            
            try:
                from api_server import app, shutdown_event, last_request_time
                import threading
                import webbrowser
                import time
                
                # Uruchom serwer w osobnym wątku
                def run_server():
                    app.run(host='0.0.0.0', port=args.api_port, debug=False, use_reloader=False, threaded=True)
                
                server_thread = threading.Thread(target=run_server, daemon=True)
                server_thread.start()
                
                # Poczekaj chwilę na uruchomienie
                time.sleep(2)
                
                # Otwórz przeglądarkę
                try:
                    webbrowser.open(f'http://localhost:{args.api_port}')
                except:
                    pass
                
                console.print("[green]✅ API Server uruchomiony![/green]")
                console.print(f"[cyan]   Endpointy:[/cyan]")
                console.print(f"   • http://localhost:{args.api_port}/")
                console.print(f"   • http://localhost:{args.api_port}/dashboard")
                console.print(f"   • http://localhost:{args.api_port}/devices")
                console.print(f"   • http://localhost:{args.api_port}/stats")
                console.print(f"\n[dim]💡 Zamknij przeglądarkę aby automatycznie zakończyć skanowanie[/dim]")
                console.print(f"[yellow]   Naciśnij Ctrl+C aby zatrzymać ręcznie[/yellow]\n")
                
                # Czekaj na zamknięcie przeglądarki (shutdown) lub Ctrl+C
                # Sprawdzaj czy przeglądarka nadal wysyła heartbeat
                try:
                    import time as time_module
                    
                    heartbeat_timeout = 3  # Skrócony timeout - jeśli brak heartbeat przez 3 sekundy, zamknij
                    first_request = True
                    last_heartbeat_time = time_module.time()
                    
                    while not shutdown_event.is_set():
                        time.sleep(0.5)
                        
                        # Sprawdź czy przeglądarka nadal wysyła heartbeat
                        current_time = time_module.time()
                        time_since_heartbeat = current_time - last_request_time
                        
                        # Jeśli był jakiś request (heartbeat lub normalny), zaktualizuj czas
                        if time_since_heartbeat < 1.5:
                            if first_request:
                                first_request = False
                            last_heartbeat_time = current_time
                        
                        # Jeśli brak heartbeat przez timeout (i był wcześniej request), zamknij
                        if not first_request:
                            time_since_last_heartbeat = current_time - last_heartbeat_time
                            if time_since_last_heartbeat > heartbeat_timeout:
                                console.print("\n[dim]🔌 Wykryto zamknięcie przeglądarki (brak heartbeat) - zamykam serwer...[/dim]")
                                shutdown_event.set()
                                break
                    
                    console.print("\n[dim]🔌 Zamykam serwer...[/dim]")
                    time.sleep(0.5)  # Daj czas na zamknięcie
                    console.print("[green]✅ Skanowanie zakończone[/green]")
                except KeyboardInterrupt:
                    console.print("\n[yellow]⚠️  Zatrzymywanie...[/yellow]")
                    shutdown_event.set()
                except Exception as e:
                    console.print(f"\n[yellow]⚠️  Błąd: {e}[/yellow]")
                    shutdown_event.set()
                finally:
                    shutdown_event.set()  # Upewnij się że event jest ustawiony
                    # Wymuś zamknięcie procesu
                    os._exit(0)
                    
            except ImportError:
                console.print("[red]❌ Nie można uruchomić API server - Flask nie jest zainstalowany[/red]")
                console.print("[yellow]   Zainstaluj: pip install flask[/yellow]")
            except Exception as e:
                console.print(f"[red]❌ Błąd uruchamiania API: {e}[/red]")
        
        # Informacja o pełnym audycie
        if not run_vulnerability_tests:
            console.print("\n[dim]ℹ️  Tip: Use --audit flag for detailed vulnerability testing[/dim]")
            console.print("[dim]   Example: python3 src/scanner.py --wifi --audit[/dim]")
        
        # Pokaż wyniki audytu bezpieczeństwa jeśli wykonano testy
        if run_vulnerability_tests and scanner.vulnerability_tester:
            console.print("\n[bold cyan]🔍 DETAILED VULNERABILITY AUDIT RESULTS:[/bold cyan]\n")
            console.print("[dim]ℹ️  Full security audit was performed with --audit flag[/dim]\n")
            
            total_vulnerable_devices = 0
            for device in scanner.devices:
                if "vulnerability_tests" in device.metadata:
                    tests = device.metadata["vulnerability_tests"]
                    # Filtruj tylko rzeczywiste podatności
                    vulnerable_tests = [t for t in tests if t.get("is_vulnerable", False)]
                    
                    if not vulnerable_tests:
                        continue
                    
                    total_vulnerable_devices += 1
                    
                    # Podziel na porty medyczne i resztę
                    medical_ports = [104, 11112, 5000]
                    medical_tests = [t for t in vulnerable_tests if t.get("port") in medical_ports or t.get("protocol") in ["DICOM", "HL7"]]
                    other_tests = [t for t in vulnerable_tests if t not in medical_tests]
                    
                    critical_medical = [t for t in medical_tests if t["severity"] == "Krytyczna"]
                    high_medical = [t for t in medical_tests if t["severity"] == "Wysoka"]
                    critical_other = [t for t in other_tests if t["severity"] == "Krytyczna"]
                    high_other = [t for t in other_tests if t["severity"] == "Wysoka"]
                    
                    # Sprawdź czy to router
                    is_router = False
                    if scanner.vulnerability_tester:
                        is_router = scanner.vulnerability_tester._is_router(device)
                    
                    console.print(f"[bold yellow]📋 {device.name}[/bold yellow] (Score: {device.security_score}/100)")
                    if is_router:
                        console.print(f"  [dim]🏠 Router/Gateway - niektóre porty (80, 443, 22, 161) są normalne[/dim]")
                    console.print(f"  IP: {device.metadata.get('ip_address', 'N/A')}")
                    
                    # Porty medyczne
                    if critical_medical or high_medical:
                        console.print(f"\n  [cyan]🏥 PORTY MEDYCZNE:[/cyan]")
                        if critical_medical:
                            console.print(f"    [red]🔴 Krytyczne ({len(critical_medical)}):[/red]")
                            for test in critical_medical:
                                console.print(f"      • Port {test.get('port', 'N/A')}: {test['name']}")
                        if high_medical:
                            console.print(f"    [yellow]🟠 Wysokie ({len(high_medical)}):[/yellow]")
                            for test in high_medical:
                                console.print(f"      • Port {test.get('port', 'N/A')}: {test['name']}")
                    else:
                        console.print(f"  [green]✅ Porty medyczne: Brak podatności[/green]")
                    
                    # Inne porty
                    if critical_other or high_other:
                        console.print(f"\n  [blue]🔌 INNE PORTY:[/blue]")
                        if critical_other:
                            console.print(f"    [red]🔴 Krytyczne ({len(critical_other)}):[/red]")
                            for test in critical_other:
                                console.print(f"      • Port {test.get('port', 'N/A')}: {test['name']}")
                        if high_other:
                            console.print(f"    [yellow]🟠 Wysokie ({len(high_other)}):[/yellow]")
                            for test in high_other:
                                console.print(f"      • Port {test.get('port', 'N/A')}: {test['name']}")
                    else:
                        console.print(f"  [green]✅ Inne porty: Brak podatności[/green]")
                    
                    # Podatność na ataki (na podstawie znanych podatności)
                    attack_sus = device.metadata.get("attack_susceptibility", [])
                    if attack_sus:
                        console.print(f"\n  [yellow]🎯 PODATNOŚĆ NA ATAKI:[/yellow]")
                        for a in attack_sus[:8]:
                            console.print(f"    • {a.get('attack_type', 'N/A')}: [dim]{a.get('reason', '')}[/dim]")
                        if len(attack_sus) > 8:
                            console.print(f"    [dim]... i {len(attack_sus) - 8} więcej[/dim]")
                    
                    console.print()  # Pusta linia między urządzeniami
            
            if total_vulnerable_devices == 0:
                console.print("[green]✅ Brak podatności we wszystkich urządzeniach![/green]\n")
    
    # Pokaż wyniki audytu bezpieczeństwa jeśli wykonano testy
    if devices and run_vulnerability_tests and scanner.vulnerability_tester:
        console.print("\n[bold cyan]🔍 DETAILED VULNERABILITY AUDIT RESULTS:[/bold cyan]\n")
        console.print("[dim]ℹ️  Full security audit was performed with --audit flag[/dim]\n")
        
        total_vulnerable_devices = 0
        for device in scanner.devices:
            if "vulnerability_tests" in device.metadata:
                tests = device.metadata["vulnerability_tests"]
                # Filtruj tylko rzeczywiste podatności
                vulnerable_tests = [t for t in tests if t.get("is_vulnerable", False)]
                
                if not vulnerable_tests:
                    continue
                
                total_vulnerable_devices += 1
                
                # Podziel na porty medyczne i resztę
                medical_ports = [104, 11112, 5000]
                medical_tests = [t for t in vulnerable_tests if t.get("port") in medical_ports or t.get("protocol") in ["DICOM", "HL7"]]
                other_tests = [t for t in vulnerable_tests if t not in medical_tests]
                
                critical_medical = [t for t in medical_tests if t["severity"] == "Krytyczna"]
                high_medical = [t for t in medical_tests if t["severity"] == "Wysoka"]
                critical_other = [t for t in other_tests if t["severity"] == "Krytyczna"]
                high_other = [t for t in other_tests if t["severity"] == "Wysoka"]
                
                # Sprawdź czy to router
                is_router = False
                if scanner.vulnerability_tester:
                    is_router = scanner.vulnerability_tester._is_router(device)
                
                console.print(f"[bold yellow]📋 {device.name}[/bold yellow] (Score: {device.security_score}/100)")
                if is_router:
                    console.print(f"  [dim]🏠 Router/Gateway - niektóre porty (80, 443, 22, 161) są normalne[/dim]")
                console.print(f"  IP: {device.metadata.get('ip_address', 'N/A')}")
                
                # Porty medyczne
                if critical_medical or high_medical:
                    console.print(f"\n  [cyan]🏥 PORTY MEDYCZNE:[/cyan]")
                    if critical_medical:
                        console.print(f"    [red]🔴 Krytyczne ({len(critical_medical)}):[/red]")
                        for test in critical_medical:
                            console.print(f"      • Port {test.get('port', 'N/A')}: {test['name']}")
                    if high_medical:
                        console.print(f"    [yellow]🟠 Wysokie ({len(high_medical)}):[/yellow]")
                        for test in high_medical:
                            console.print(f"      • Port {test.get('port', 'N/A')}: {test['name']}")
                else:
                    console.print(f"  [green]✅ Porty medyczne: Brak podatności[/green]")
                
                # Inne porty
                if critical_other or high_other:
                    console.print(f"\n  [blue]🔌 INNE PORTY:[/blue]")
                    if critical_other:
                        console.print(f"    [red]🔴 Krytyczne ({len(critical_other)}):[/red]")
                        for test in critical_other:
                            console.print(f"      • Port {test.get('port', 'N/A')}: {test['name']}")
                    if high_other:
                        console.print(f"    [yellow]🟠 Wysokie ({len(high_other)}):[/yellow]")
                        for test in high_other:
                            console.print(f"      • Port {test.get('port', 'N/A')}: {test['name']}")
                else:
                    console.print(f"  [green]✅ Inne porty: Brak podatności[/green]")
                
                # Podatność na ataki
                attack_sus = device.metadata.get("attack_susceptibility", [])
                if attack_sus:
                    console.print(f"\n  [yellow]🎯 PODATNOŚĆ NA ATAKI:[/yellow]")
                    for a in attack_sus[:8]:
                        console.print(f"    • {a.get('attack_type', 'N/A')}: [dim]{a.get('reason', '')}[/dim]")
                    if len(attack_sus) > 8:
                        console.print(f"    [dim]... i {len(attack_sus) - 8} więcej[/dim]")
                
                console.print()  # Pusta linia między urządzeniami
        
        if total_vulnerable_devices == 0:
            console.print("[green]✅ Brak podatności we wszystkich urządzeniach![/green]\n")
    
    


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Przerwano przez użytkownika[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]❌ Błąd: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
