#!/usr/bin/env python3
"""
Main medical device scanner module.

This module ties together:
- BLE scanner (Bluetooth Low Energy)
- WiFi scanner (local network)
- USB scanner (USB-attached devices)
- NFC scanner (cards and tags)
- Security analysis
- Vulnerability testing and audit
- Reporting

USAGE:
    python src/scanner.py                    # Scan all protocols
    python src/scanner.py --ble              # BLE only
    python src/scanner.py --wifi             # WiFi only
    python src/scanner.py --usb              # USB only
    python src/scanner.py --nfc              # NFC only
    python src/scanner.py --ble --wifi       # BLE and WiFi
    python src/scanner.py --audit            # Full security audit (vulnerability tests)
    python src/scanner.py --wifi --audit     # WiFi + audit
"""

import sys
import os

# Silence TensorFlow CUDA/GPU messages before any other imports
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Use CPU only

import json
import csv
import time
from datetime import datetime
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np

# Load env from .env if present
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
import platform
from typing import List
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from device import Device, DeviceType

# Import real scanner modules
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

# Rich console for terminal output
console = Console()


def make_json_serializable(obj: Any) -> Any:
    """
    Convert numpy and other custom types to JSON-serializable types.
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
    Main medical device scanner class.
    Manages scanning (BLE, WiFi, USB, NFC), security analysis, reporting, and results.
    """
    
    def __init__(self, protocols: List[str] = None):
        """
        Initialize scanner.
        Args:
            protocols: Protocols to scan (['ble', 'wifi', 'usb', 'nfc']). If None, scan all.
        """
        self.scanners = {}
        project_root = Path(__file__).parent.parent
        self.scans_dir = project_root / "reports"
        self.reports_dir = project_root / "reports"
        self.exports_dir = project_root / "exports"
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
                    console.print("[green]✅ BLE scanner ready[/green]")
                except ImportError as e:
                    console.print(f"[yellow]⚠️  BLE scanner unavailable: {e}[/yellow]")
                    venv_path = os.getenv('VIRTUAL_ENV')
                    if venv_path and 'venv' in str(venv_path):
                        console.print("[yellow]   Note: sudo may not see venv libraries.[/yellow]")
                        console.print("[yellow]   Option 1 (recommended for BLE): python3 src/scanner.py --ble[/yellow]")
                        console.print("[yellow]   Option 2 (with sudo for scapy): source venv/bin/activate; sudo -E python3 src/scanner.py --wifi[/yellow]")
                    else:
                        console.print("[yellow]   Install: pip install bleak[/yellow]")
            else:
                console.print("[yellow]⚠️  BLE scanner unavailable (install: pip install bleak)[/yellow]")
        
        # WiFi Scanner
        if 'wifi' in protocols:
            if WIFI_SCANNER_AVAILABLE:
                self.scanners['wifi'] = WiFiScanner()
                console.print("[green]✅ WiFi scanner ready[/green]")
            else:
                console.print("[yellow]⚠️  WiFi scanner unavailable (install: pip install python-nmap)[/yellow]")
        
        # USB Scanner
        if 'usb' in protocols:
            if USB_SCANNER_AVAILABLE:
                self.scanners['usb'] = USBScanner()
                console.print("[green]✅ USB scanner ready[/green]")
            else:
                console.print("[yellow]⚠️  USB scanner unavailable (install: pip install pyusb pyserial)[/yellow]")
        
        # NFC Scanner
        if 'nfc' in protocols:
            if NFC_SCANNER_AVAILABLE:
                self.scanners['nfc'] = NFCScanner()
                console.print("[green]✅ NFC scanner ready[/green]")
            else:
                console.print("[yellow]⚠️  NFC scanner unavailable (install: pip install nfcpy pyscard)[/yellow]")
        
        if not self.scanners:
            console.print("[red]❌ No scanners available![/red]")
            console.print("[yellow]   Install dependencies: pip install -r requirements.txt[/yellow]\n")
        
        console.print()
        self.devices: List[Device] = []
        
        # Vulnerability tester
        if VULNERABILITY_TESTER_AVAILABLE and VulnerabilityTester:
            try:
                from cve_lookup import CVELookup
                cve_lookup = CVELookup()
                use_cve_api = cve_lookup.nvd_api_key is not None
                self.vulnerability_tester = VulnerabilityTester(use_cve_api=use_cve_api)
            except Exception as e:
                console.print(f"[yellow]⚠️  Could not init VulnerabilityTester: {e}[/yellow]")
                self.vulnerability_tester = None
        else:
            self.vulnerability_tester = None
        
        # External APIs
        if EXTERNAL_APIS_AVAILABLE and ExternalAPIs:
            try:
                self.external_apis = ExternalAPIs()
            except Exception as e:
                console.print(f"[yellow]⚠️  Could not init ExternalAPIs: {e}[/yellow]")
                self.external_apis = None
        else:
            self.external_apis = None
        
        
        # Encryption analyzer
        if ENCRYPTION_ANALYZER_AVAILABLE and EncryptionAnalyzer:
            try:
                self.encryption_analyzer = EncryptionAnalyzer()
            except Exception as e:
                console.print(f"[yellow]⚠️  Could not init EncryptionAnalyzer: {e}[/yellow]")
                self.encryption_analyzer = None
        else:
            self.encryption_analyzer = None
        
        # Init anomaly detector if available
        if ANOMALY_DETECTOR_AVAILABLE and AnomalyDetector:
            try:
                self.anomaly_detector = AnomalyDetector(contamination=0.1)
                # Try to load a previously trained model
                if self.anomaly_detector.load_model():
                    console.print("[green]✅ Anomaly detector ready (model loaded)[/green]")
                else:
                    console.print("[green]✅ Anomaly detector ready (will train on first use)[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠️  Could not init AnomalyDetector: {e}[/yellow]")
                self.anomaly_detector = None
        else:
            self.anomaly_detector = None
    
    def scan_all(self, ble_duration: Optional[int] = None) -> List[Device]:
        """
        Scan all available protocols (BLE, WiFi, USB, NFC).
        ble_duration: BLE scan duration in seconds (None = default from --ble-duration or 20).
        Returns list of all detected devices.
        """
        console.print("[bold blue]🔍 Starting full scan...[/bold blue]\n")
        
        all_devices = []
        _ble_sec = 20 if ble_duration is None else ble_duration
        
        # Scan BLE
        if 'ble' in self.scanners:
            console.print(Panel.fit("📡 Scanning Bluetooth Low Energy (BLE)", style="cyan"))
            ble_devices = self._scan_ble_async(duration=_ble_sec)
            all_devices.extend(ble_devices)
            console.print()
        
        # Scan WiFi
        if 'wifi' in self.scanners:
            console.print(Panel.fit("📡 Scanning WiFi", style="cyan"))
            wifi_devices = self.scanners['wifi'].scan_wifi_devices()
            all_devices.extend(wifi_devices)
            console.print()
        
        # Scan USB
        if 'usb' in self.scanners:
            console.print(Panel.fit("🔌 Scanning USB", style="cyan"))
            usb_devices = self.scanners['usb'].scan_usb_devices()
            all_devices.extend(usb_devices)
            console.print()
        
        # Scan NFC
        if 'nfc' in self.scanners:
            console.print(Panel.fit("📱 Scanning NFC", style="cyan"))
            nfc_devices = self.scanners['nfc'].scan_nfc_devices(duration=5)
            all_devices.extend(nfc_devices)
            console.print()
        
        self.devices = all_devices
        
        console.print(f"[bold green]✅ Scan complete![/bold green]")
        console.print(f"[green]Found {len(all_devices)} devices in total[/green]\n")
        
        return all_devices
    
    def _scan_ble_async(self, duration: int = 10) -> List[Device]:
        """
        Wrapper for async BLE scanning. BLE scanner uses async; this converts to sync.
        Windows: needs a new event loop. Linux/Mac: asyncio.run().
        """
        if platform.system() == "Windows":
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.scanners['ble'].scan_ble_devices(duration))
            finally:
                loop.close()
        else:
            return asyncio.run(self.scanners['ble'].scan_ble_devices(duration))
    
    def analyze_security(self, run_vulnerability_tests: bool = False):
        """
        Analyze security of all detected devices: security scores, vulnerabilities,
        FDA compliance, optional audit (--audit). Vulnerabilities come from scanning
        (basic) and/or vulnerability_tester (detailed).
        """
        console.print("[bold blue]🔒 Analyzing device security...[/bold blue]\n")
        
        for device in self.devices:
            device.calculate_security_score()
            self._check_fda_compliance(device)
            if self.external_apis:
                self._enrich_device_with_external_apis(device)
            if self.encryption_analyzer:
                self._analyze_encryption(device)
            if run_vulnerability_tests and self.vulnerability_tester:
                self._run_vulnerability_tests(device)
        
        if self.vulnerability_tester:
            for device in self.devices:
                if "attack_susceptibility" not in (device.metadata or {}):
                    device.metadata = device.metadata or {}
                    device.metadata["attack_susceptibility"] = self.vulnerability_tester.get_attack_susceptibility(device)
        
        if self.anomaly_detector and len(self.devices) > 0:
            self._detect_anomalies()
        
        console.print("[bold green]✅ Security analysis complete[/bold green]\n")
    
    def _analyze_encryption(self, device: Device):
        """Analyze device encryption and add results to metadata."""
        if not self.encryption_analyzer:
            return
        try:
            analysis = self.encryption_analyzer.analyze(
                encryption_type=device.encryption_type,
                has_encryption=device.has_encryption
            )
            
            # Store results in metadata
            if not device.metadata:
                device.metadata = {}
            
            device.metadata["encryption_analysis"] = {
                "strength": analysis.strength.value,
                "is_weak": analysis.is_weak,
                "score": analysis.score,
                "issues": analysis.issues,
                "recommendations": analysis.recommendations
            }
            
            if analysis.is_weak:
                for issue in analysis.issues:
                    device.add_vulnerability(f"Encryption: {issue}")
            
        except Exception as e:
            pass
    
    def _enrich_device_with_external_apis(self, device: Device):
        """Enrich device with external API data (VirusTotal, Shodan)."""
        if not self.external_apis:
            return
        try:
            device_ip = None
            if device.metadata:
                device_ip = device.metadata.get('ip_address') or device.metadata.get('ip')
            
            if not device_ip and device.protocol.value == "WiFi":
                import re
                ip_match = re.match(r'^(\d{1,3}\.){3}\d{1,3}$', device.name)
                if ip_match:
                    device_ip = device.name
            
            if device_ip:
                enriched = self.external_apis.enrich_device(
                    device_ip=device_ip,
                    device_mac=device.mac_address
                )
                
                # Add to metadata
                if not device.metadata:
                    device.metadata = {}
                
                device.metadata['external_apis'] = enriched
                
                if enriched.get('virustotal'):
                    vt_data = enriched['virustotal']
                    if vt_data.get('malicious', 0) > 0:
                        # Add detection details if available
                        detections = vt_data.get('detections', [])
                        if detections:
                            # Show first 3 engines that detected threat
                            engines = [d.get('engine', 'Unknown') for d in detections[:3]]
                            engines_str = ', '.join(engines)
                            if len(detections) > 3:
                                engines_str += f" (+{len(detections) - 3} more)"
                            device.add_vulnerability(
                                f"VirusTotal: IP flagged as malicious ({vt_data['malicious']} detections) – by: {engines_str}"
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
                                engines_str += f" (+{len(detections) - 3} more)"
                            device.add_vulnerability(
                                f"VirusTotal: IP flagged as suspicious ({vt_data['suspicious']} detections) – by: {engines_str}"
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
            # Do not show errors - APIs are optional
            pass
    
    def _run_vulnerability_tests(self, device: Device):
        """
        Run vulnerability tests and attack simulation on the device."""
        if not self.vulnerability_tester:
            return
        
        try:
            # Run vulnerability tests
            test_results = self.vulnerability_tester.test_device(device)
            
            # Store test results in device metadata
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
                
                # From known vulnerabilities: which attacks the device is susceptible to
                attack_susceptibility = self.vulnerability_tester.get_attack_susceptibility(device, test_results)
                device.metadata["attack_susceptibility"] = attack_susceptibility
                
                # Add vulnerabilities to device list
                for test in test_results:
                    if test.is_vulnerable:
                        device.add_vulnerability(f"{test.name}: {test.description}")
                
                # Recalculate security score with new vulnerabilities
                device.calculate_security_score()
        except Exception as e:
            console.print(f"[yellow]⚠️  Vulnerability test error for {device.name}: {e}[/yellow]")
    
    def _detect_anomalies(self):
        """
        Detect anomalies in devices using ML.
        """
        if not self.anomaly_detector:
            return
        
        try:
            console.print("[bold cyan]🤖 Detecting anomalies with ML...[/bold cyan]")
            
            # Train model if not yet trained (needs at least 2 devices)
            if not self.anomaly_detector.trained:
                console.print("[dim]   Training ML model...[/dim]")
                train_result = self.anomaly_detector.train(self.devices)
                if not train_result.get('trained'):
                    console.print(f"[dim]   ML model cannot be trained: {train_result.get('reason', 'Unknown')}[/dim]")
                    console.print("[dim]   Using heuristics for anomaly detection...[/dim]")
            
            # Detect anomalies
            anomaly_results = self.anomaly_detector.detect_anomalies(self.devices, use_ensemble=True)
            
            # Statistics
            stats = self.anomaly_detector.get_anomaly_statistics(anomaly_results)
            
            # Store results in device metadata
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
                    # Add vulnerability if anomaly
                    device.add_vulnerability(f"ML Anomaly Detection: {result['reason']}")
            
            # Show detailed AI results
            method_used = "Ensemble ML" if self.anomaly_detector.trained else "Heuristics"
            method_details = "Isolation Forest + LOF + One-Class SVM" if self.anomaly_detector.trained else "Security score + vulnerabilities"
            
            console.print(f"\n[bold cyan]🤖 AI analysis results:[/bold cyan]")
                    console.print(f"  📊 Analyzed: {len(self.devices)} devices")
            console.print(f"  📈 Method: {method_used} ({method_details})")
            
            if anomalies_found > 0:
                console.print(f"\n  [yellow]⚠️  Detected {anomalies_found} anomalies ({stats['anomalies_percentage']:.1f}%)[/yellow]")
                console.print(f"  [dim]   Avg anomaly score: {stats['avg_anomaly_score']:.2f}[/dim]")
                
                # Show anomaly details
                console.print(f"\n  [bold yellow]🔍 Detected anomalies:[/bold yellow]")
                for result in anomaly_results:
                    if result['is_anomaly']:
                        device = result['device']
                        console.print(f"    • [yellow]{device.name}[/yellow] (Score: {result['anomaly_score']:.2f})")
                        console.print(f"      Method: {result['method']}")
                        console.print(f"      Reason: {result['reason']}")
                        if result.get('scores'):
                            scores_str = ", ".join([f"{k}: {v:.2f}" for k, v in result['scores'].items()])
                            console.print(f"      Details: {scores_str}")
            else:
                console.print(f"\n  [green]✅ No anomalies – all devices normal[/green]")
                console.print(f"  [dim]   Avg anomaly score: {stats['avg_anomaly_score']:.2f}[/dim]")
            
            console.print()  # Blank line
            
        except Exception as e:
            console.print(f"[yellow]⚠️  Anomaly detection error: {e}[/yellow]")
    
    def _check_fda_compliance(self, device: Device):
        """
        Check device compliance with FDA Cybersecurity Guidance (encryption, auth, updates, logging).
        Only applied to medical devices to avoid false positives.
        """
        # Check if this is actually a medical device
        is_medical = self._is_medical_device(device)
        
        if not is_medical:
            # Not a medical device – skip FDA check
            device.metadata["fda_compliance"] = None  # N/A
            return
        
        compliance_issues = []
        
        # Check encryption (FDA requires medical data encryption)
        if not device.has_encryption:
            compliance_issues.append("FDA: No data encryption")
            device.add_vulnerability("FDA Non-compliance: Encryption")
        
        # Check authorization (FDA requires access auth / pairing). For WiFi, network password counts.
        if device.protocol.value == "WIFI":
            # WiFi requires network password – that counts as auth
            pass
        elif not device.requires_pairing:
            compliance_issues.append("FDA: No access authorization")
            device.add_vulnerability("FDA Non-compliance: Authentication")
        
        # Store compliance result in device metadata
        if compliance_issues:
            device.metadata["fda_compliance"] = False
            device.metadata["fda_issues"] = compliance_issues
        else:
            device.metadata["fda_compliance"] = True
    
    def _is_medical_device(self, device: Device) -> bool:
        """
        Return True if the device is considered medical."""
        # Check device type
        medical_types = [
            DeviceType.GLUCOSE_METER,
            DeviceType.INSULIN_PUMP,
            DeviceType.PULSE_OXIMETER,
            DeviceType.BLOOD_PRESSURE
        ]
        if device.device_type in medical_types:
            return True
        
        # Check device name
        name_lower = device.name.lower()
        medical_keywords = [
            "medical", "med", "hospital", "clinic", "patient", "monitor",
            "glucose", "gluco", "insulin", "pump", "dicom", "hl7",
            "pacs", "ris", "emr", "ehr", "vital", "signs", "health"
        ]
        if any(keyword in name_lower for keyword in medical_keywords):
            return True
        
        # Check medical ports in metadata
        open_ports = device.metadata.get("open_ports", [])
        medical_ports = [104, 11112, 5000]
        if any(p in open_ports for p in medical_ports):
            # If it has medical ports and few others, it may be a medical device
            if len(open_ports) <= 5:
                return True
        
        return False
    
    def display_results(self):
        """Display scan results as device cards."""
        if not self.devices:
            console.print("[red]❌ No devices found[/red]")
            return
        
        # Summary stats
        total_devices = len(self.devices)
        high_risk = [d for d in self.devices if d.security_score < 50]
        medium_risk = [d for d in self.devices if 50 <= d.security_score < 80]
        low_risk = [d for d in self.devices if d.security_score >= 80]
        
        # Show summary
        summary_panel = Panel.fit(
            f"[bold]📊 Scan summary[/bold]\n\n"
            f"Total devices: [bold cyan]{total_devices}[/bold cyan]\n"
            f"🔴 High risk (score < 50): [bold red]{len(high_risk)}[/bold red]\n"
            f"🟡 Medium risk (50-79): [bold yellow]{len(medium_risk)}[/bold yellow]\n"
            f"🟢 Low risk (≥80): [bold green]{len(low_risk)}[/bold green]",
            style="cyan",
            title="📈 Stats"
        )
        console.print(summary_panel)
        console.print()
        
        # Group devices by risk and protocol
        risk_groups = [
            ("🔴 HIGH RISK", high_risk, "red"),
            ("🟡 MEDIUM RISK", medium_risk, "yellow"),
            ("🟢 LOW RISK", low_risk, "green")
        ]
        
        protocol_names = {
            "BLE": "📶 Bluetooth Low Energy",
            "WiFi": "📡 WiFi (Local network)",
            "USB": "🔌 USB",
            "NFC": "📱 NFC"
        }
        
        for group_title, devices_list, color in risk_groups:
            if not devices_list:
                continue
            
            console.print(f"\n[bold {color}]{group_title}[/bold {color}] ({len(devices_list)} devices)\n")
            
            # Group by protocol
            by_protocol = {}
            for device in devices_list:
                protocol = device.protocol.value
                if protocol not in by_protocol:
                    by_protocol[protocol] = []
                by_protocol[protocol].append(device)
            
            # Show by protocol
            for protocol in ["BLE", "WiFi", "USB", "NFC"]:
                if protocol not in by_protocol:
                    continue
                
                protocol_devices = by_protocol[protocol]
                protocol_label = protocol_names.get(protocol, protocol)
                console.print(f"  [dim]{protocol_label}: {len(protocol_devices)} devices[/dim]\n")
                
                # Show each device as a card
                for device in protocol_devices:
                    self._display_device_card(device, color)
                
                console.print()  # Blank line between protocols
        
        # Show encryption analysis if available
        if self.encryption_analyzer:
            self._display_encryption_analysis()
    
    def _display_device_card(self, device: Device, risk_color: str):
        """Display a single device as a card. risk_color: red/yellow/green."""
        # Style by risk
        if device.security_score >= 80:
            panel_style = "green"
            risk_icon = "🟢"
        elif device.security_score >= 50:
            panel_style = "yellow"
            risk_icon = "🟡"
        else:
            panel_style = "red"
            risk_icon = "🔴"
        
        # Card header – improved name
        device_display_name = device.name
        if device.name == "Unknown" or device.name.startswith("Product-"):
            # For USB devices with generic names, use a more descriptive name
            if device.protocol.value == "USB":
                if device.device_type.value == "USB_DEVICE":
                    device_display_name = f"USB device ({device.mac_address[-5:]})"
                else:
                    device_display_name = f"{device.device_type.value.replace('_', ' ')} ({device.mac_address[-5:]})"
            elif device.protocol.value == "BLE":
                device_display_name = f"BLE device ({device.mac_address[-5:]})"
            elif device.protocol.value == "WiFi":
                device_display_name = f"WiFi device ({device.mac_address[-5:]})"
            else:
                device_display_name = f"{device.protocol.value} device ({device.mac_address[-5:]})"
        
        # Card header
        header = f"{risk_icon} [bold]{device_display_name}[/bold]"
        if device.manufacturer and device.manufacturer != "N/A":
            # Check if manufacturer is fake (for random MACs)
            show_manufacturer = True
            if device.protocol.value == "BLE" and device.mac_address:
                try:
                    first_byte = int(device.mac_address.split(":")[0], 16)
                    is_random = (first_byte & 0x02) != 0
                    if is_random:
                        show_manufacturer = False
                except Exception:
                    pass
            
            # For WiFi – do not show manufacturer if MAC is generated (00:00:xx)
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
        
        info_lines.append(f"{protocol_emoji} Protocol: [bold cyan]{device.protocol.value}[/bold cyan]  |  Type: {device.device_type.value}")
        info_lines.append(f"MAC: [yellow]{device.mac_address}[/yellow]")
        
        # IP address (if available)
        if device.metadata and device.metadata.get('ip_address'):
            info_lines.append(f"IP: [cyan]{device.metadata['ip_address']}[/cyan]")
        
        # Encryption and authorization
        encryption_status = "✅ Encryption: Yes" if device.has_encryption else "❌ Encryption: No"
        pairing_status = "✅ Auth: Yes" if device.requires_pairing else "❌ Auth: No"
        
        if device.encryption_type:
            enc_type = device.encryption_type
            # Truncate if too long
            if len(enc_type) > 30:
                enc_type = enc_type[:27] + "..."
            encryption_status += f" ({enc_type})"
        
        info_lines.append(f"{encryption_status}  |  {pairing_status}")
        
        # Vulnerabilities (deduplicate)
        unique_vulns = list(set(device.vulnerabilities)) if device.vulnerabilities else []
        vuln_count = len(unique_vulns)
        if vuln_count > 0:
            vuln_text = f"⚠️  [bold red]{vuln_count} vulnerabilities[/bold red]"
            info_lines.append(vuln_text)
            
            # Show first 3 unique vulnerabilities
            for vuln in unique_vulns[:3]:
                info_lines.append(f"  • [red]{vuln}[/red]")
            if vuln_count > 3:
                info_lines.append(f"  ... and {vuln_count - 3} more (see report)")
        else:
            info_lines.append("[green]✅ No vulnerabilities detected[/green]")
        
        # Attack susceptibility (from known vulnerabilities and ports)
        attack_sus = (device.metadata or {}).get("attack_susceptibility", [])
        if attack_sus:
            attack_types = list({a.get("attack_type", "") for a in attack_sus if a.get("attack_type")})
            if attack_types:
                info_lines.append(f"[yellow]🎯 Attack susceptibility:[/yellow] {', '.join(attack_types[:5])}{'…' if len(attack_types) > 5 else ''}")
        
        # Encryption analysis (if available)
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
                info_lines.append(f"{strength_emoji} Encryption: {strength.upper()} (Score: {enc_analysis.get('score', 0)}/100)")
        
        # FDA compliance (if applicable)
        if device.metadata and device.metadata.get("fda_compliance") is not None:
            if device.metadata["fda_compliance"]:
                info_lines.append("[green]✅ FDA compliant[/green]")
            else:
                info_lines.append("[red]❌ Not FDA compliant[/red]")
                if device.metadata.get("fda_issues"):
                    for issue in device.metadata["fda_issues"][:2]:
                        info_lines.append(f"  • [red]{issue}[/red]")
        
        # Microcontroller messages (if available)
        if device.metadata and device.metadata.get("microcontroller"):
            baudrate = device.metadata.get("baudrate", "N/A")
            messages = device.metadata.get("messages", [])
            message_count = device.metadata.get("message_count", 0)
            port = device.metadata.get('port', 'N/A')
            
            info_lines.append(f"\n[cyan]🔧 Microcontroller (USB Serial)[/cyan]")
            info_lines.append(f"  Port: {port}")
            info_lines.append(f"  Speed: {baudrate} baud")
            info_lines.append(f"  Status: {'✅ Active' if messages else '⚠️  No messages'}")
            info_lines.append(f"  Messages: {message_count}")
            
            if messages:
                info_lines.append(f"  [dim]Recent messages:[/dim]")
                for msg in messages[:5]:  # Show first 5
                    # Truncate long messages
                    display_msg = msg[:70] + "..." if len(msg) > 70 else msg
                    # Check if this is a response to test command
                    if "[TEST:" in msg:
                        info_lines.append(f"    [yellow]→ {display_msg}[/yellow]")
                    else:
                        info_lines.append(f"    [green]→ {display_msg}[/green]")
                if len(messages) > 5:
                    info_lines.append(f"    [dim]... and {len(messages) - 5} more[/dim]")
            else:
                info_lines.append(f"  [dim]💡 Microcontroller detected but not sending messages[/dim]")
                info_lines.append(f"  [dim]   May need start command or is in sleep mode[/dim]")
        
        # Create panel
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
        Compute encryption stats for the report. Returns dict of encryption statistics.
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
                # If no analysis, fall back to has_encryption
                if not device.has_encryption:
                    none += 1
                else:
                    moderate += 1  # Default assumption
        
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
        Show a short summary of device encryption analysis.
        """
        if not self.devices:
            return
        
        # Collect simple stats
        total = len(self.devices)
        without_encryption = sum(1 for d in self.devices if not d.has_encryption)
        weak_count = 0
        
        for device in self.devices:
            if device.metadata and "encryption_analysis" in device.metadata:
                analysis = device.metadata["encryption_analysis"]
                if analysis.get("is_weak", False):
                    weak_count += 1
        
        # Show short summary only if there are issues
        if weak_count > 0 or without_encryption > 0:
            console.print(f"[dim]🔐 Encryption: {without_encryption} without encryption, {weak_count} with weak encryption[/dim]")
    
    def save_scan_results(self) -> str:
        """
        Save raw scan data to a JSON file in the project root. Returns path or empty string on error.
        """
        if not self.devices:
            console.print("[yellow]⚠️  No devices to save[/yellow]")
            return ""
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"scan_{timestamp}.json"
        filepath = self.scans_dir / filename
        
        # Prepare data to save
        scan_data = {
            "scan_timestamp": datetime.now().isoformat(),
            "total_devices": len(self.devices),
            "protocols_scanned": list(self.scanners.keys()),
            "devices": [device.to_dict() for device in self.devices]
        }
        
        # Write to JSON file
        try:
            # Convert all values to JSON-serializable
            scan_data_serializable = make_json_serializable(scan_data)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(scan_data_serializable, f, indent=2, ensure_ascii=False)
            
            console.print(f"[green]✅ Scan results saved: {filepath}[/green]")
            return str(filepath)
        except Exception as e:
            console.print(f"[red]❌ Error saving results: {e}[/red]")
            return ""
    
    def generate_report(self) -> dict:
        """
        Generate security analysis report and save to data/reports/. Creates reports in formats:
        - JSON: Structured data for further analysis
        
        Returns dict of paths {'json': path}.
        """
        if not self.devices:
            console.print("[yellow]⚠️  No devices to report[/yellow]")
            return {}
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_paths = {}
        
        # Generate JSON report
        json_path = self._generate_json_report(timestamp)
        if json_path:
            report_paths['json'] = json_path
        
        return report_paths
    
    def export_to_csv(self, output_path: Optional[str] = None) -> str:
        """
        Export scan results to CSV file.
        
        CSV with key device info: name, MAC, type, protocol, security, vulnerabilities (semicolon-separated), metadata.
        output_path: optional; if None uses project root. Returns path or empty string on error.
        """
        if not self.devices:
            console.print("[yellow]⚠️  No devices to export[/yellow]")
            return ""
        
        # Create filename with timestamp
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
            
            # Do not show message – will be shown in main()
            return str(filepath)
        except Exception as e:
            console.print(f"[red]❌ CSV export error: {e}[/red]")
            return ""
    
    def _generate_json_report(self, timestamp: str) -> str:
        """
        Generate JSON security report. timestamp: used in filename. Returns path or empty string on error.
        """
        filename = f"report_{timestamp}.json"
        filepath = self.reports_dir / filename
        
        # Prepare report data
        total_devices = len(self.devices)
        high_risk = [d for d in self.devices if d.security_score < 50]
        medium_risk = [d for d in self.devices if 50 <= d.security_score < 80]
        low_risk = [d for d in self.devices if d.security_score >= 80]
        
        devices_without_encryption = [d for d in self.devices if not d.has_encryption]
        devices_without_pairing = [d for d in self.devices if not d.requires_pairing]
        fda_non_compliant = [d for d in self.devices if not d.metadata.get("fda_compliance", True)]
        
        # Calculate encryption stats
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
            # Convert all values to JSON-serializable
            report_data_serializable = make_json_serializable(report_data)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data_serializable, f, indent=2, ensure_ascii=False)
            
            console.print(f"[green]✅ Generated JSON report: {filepath}[/green]")
            return str(filepath)
        except Exception as e:
            console.print(f"[red]❌ Error generating JSON report: {e}[/red]")
            return ""
    
    def generate_combined_report(self, threat_intel_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate one combined JSON file with: scan data, security report, threat intelligence (if available),
        
        Args:
            threat_intel_data: Threat intelligence data (optional)
        
        Returns path or empty string on error.
        """
        if not self.devices:
            console.print("[yellow]⚠️  No devices to report[/yellow]")
            return ""
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"combined_report_{timestamp}.json"
        filepath = self.reports_dir / filename
        
        # Prepare raw scan data
        scan_data = {
            "scan_timestamp": datetime.now().isoformat(),
            "total_devices": len(self.devices),
            "protocols_scanned": list(self.scanners.keys()),
            "devices": [device.to_dict() for device in self.devices]
        }
        
        # Prepare security analysis (report) data
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
        
        # Link threat intelligence to devices
        devices_with_threat_intel = []
        for device in self.devices:
            device_dict = device.to_dict()
            
            # Find threat intelligence for this device
            device_ip = device_dict.get('ip_address') or device.metadata.get('ip_address') or device.metadata.get('ip')
            if device_ip and threat_intel_data:
                threat_info = threat_intel_data.get(device_ip)
                if threat_info:
                    # Add threat intelligence to device
                    device_dict['threat_intelligence'] = threat_info
                    device_dict['threat_intelligence_linked'] = True
                else:
                    device_dict['threat_intelligence_linked'] = False
            else:
                device_dict['threat_intelligence_linked'] = False
            
            devices_with_threat_intel.append(device_dict)
        
        # Update scan_data with devices that have threat intelligence
        scan_data["devices"] = devices_with_threat_intel
        
        # Merge all data into one file
        combined_data = {
            "report_timestamp": datetime.now().isoformat(),
            "scan": scan_data,
            "analysis": report_data,
            "threat_intelligence": threat_intel_data if threat_intel_data else {}
        }
        
        # Add threat intelligence info
        if threat_intel_data:
            threats_found = sum(1 for r in threat_intel_data.values() if r.get('is_threat', False))
            # Add IP -> devices mapping for easy lookup
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
                "ip_to_devices": ip_to_devices  # IP -> devices mapping
            }
        else:
            combined_data["threat_intelligence_summary"] = {
                "total_ips_checked": 0,
                "threats_found": 0,
                "clean_ips": 0,
                "note": "Threat intelligence not available or disabled"
            }
        
        try:
            # Convert all values to JSON-serializable
            combined_data_serializable = make_json_serializable(combined_data)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(combined_data_serializable, f, indent=2, ensure_ascii=False)
            
            console.print(f"[green]✅ Generated combined report: {filepath}[/green]")
            console.print(f"[dim]   Contains: scan + analysis + threat intelligence[/dim]")
            return str(filepath)
        except Exception as e:
            console.print(f"[red]❌ Error generating combined report: {e}[/red]")
            return ""
    
    def export_to_pdf(self, output_path: Optional[str] = None) -> str:
        """
        Export scan results to PDF file.
        
        Professional layout with header, device table, vulnerabilities, FDA compliance.
        Professional layout with header, device table, vulnerabilities per device, FDA compliance.
        output_path: optional; if None uses project root. Returns path or empty string on error.
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
        except ImportError:
            console.print("[yellow]⚠️  'reportlab' is not installed.[/yellow]")
            console.print("   Install: pip install reportlab")
            return ""
        
        if not self.devices:
            console.print("[yellow]⚠️  No devices to export[/yellow]")
            return ""
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        if output_path:
            filepath = Path(output_path)
        else:
            filename = f"report_{timestamp}.pdf"
            filepath = self.reports_dir / filename
        
        try:
            # Create PDF document
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
                
                # Truncate name if too long
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
            
            # Create table (max 20 rows per page)
            max_rows_per_page = 20
            for i in range(0, len(device_data), max_rows_per_page):
                page_data = device_data[i:i+max_rows_per_page]
                if i > 0:
                    page_data = [device_data[0]] + page_data  # Add header
                
                device_table = Table(page_data, colWidths=[1.5*inch, 1.2*inch, 1*inch, 0.8*inch, 0.6*inch, 0.8*inch, 0.7*inch])
                device_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066CC')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Score centered
                    ('ALIGN', (4, 1), (6, -1), 'CENTER'),  # Icons centered
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
            
            # Do not show message – will be shown in main()
            return str(filepath)
        except Exception as e:
            console.print(f"[red]❌ PDF export error: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
            return ""
    
    def get_devices_by_risk(self) -> dict:
        """
        Group devices by risk level.
        
        Returns:
            Dict of devices grouped by risk
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
    """Export devices to SIEM as JSON Lines. Returns path to generated file."""
    # Save in exports/ directory
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
    """Check threat intelligence for devices. Returns dict of results."""
    results = {}
    
    # Check if AbuseIPDB API key is available
    abuseipdb_key = os.getenv("ABUSEIPDB_API_KEY")
    if not abuseipdb_key:
        return results  # No key – skip
    
    # Collect unique IPs
    ips_to_check = set()
    for device in devices:
        ip = device.metadata.get('ip_address')
        if ip and ip not in ['N/A', 'Unknown', '']:
            ips_to_check.add(ip)
    
    if not ips_to_check:
        return results
    
    # Check AbuseIPDB (with rate limiting)
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
        
        # Check in parallel (max 3 at a time for rate limiting)
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(check_ip, ip): ip for ip in ips_to_check}
            for future in as_completed(futures):
                ip, result = future.result()
                results[ip] = result
    except ImportError:
        pass  # requests not available
    except Exception:
        pass
    
    return results





def _send_report_email(to_addr: str, filepath: str) -> None:
    """Send report (combined_report JSON) by email. SMTP from .env (like ESP32)."""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email import encoders
    except ImportError:
        console.print("[yellow]⚠️  No email/smtplib – skipping report email.[/yellow]")
        return
    smtp_server = os.getenv("SMTP_SERVER") or os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    from_addr = os.getenv("EMAIL_FROM") or user
    if not smtp_server or not user or not password or not to_addr:
        console.print("[yellow]⚠️  Missing SMTP_SERVER/SMTP_USER/SMTP_PASSWORD or address. Check .env[/yellow]")
        return
    if not filepath or not os.path.isfile(filepath):
        console.print("[yellow]⚠️  No report file to send.[/yellow]")
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            body_json = f.read()
    except Exception as e:
        console.print(f"[red]❌ Cannot read report: {e}[/red]")
        return
    msg = MIMEMultipart()
    msg["Subject"] = f"[Scanner] Audit report {os.path.basename(filepath)}"
    msg["From"] = from_addr
    msg["To"] = to_addr
    summary = f"Scan/audit report attached: {os.path.basename(filepath)}\n\nSMTP config as for ESP32 (Proton etc.): docs/CRON_PROTON_ESP32.md"
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
        console.print(f"[green]✅ Report sent by email to {to_addr}[/green]")
    except Exception as e:
        console.print(f"[red]❌ SMTP error (check .env, Proton token, network): {e}[/red]")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Medical Device Security Scanner')
    parser.add_argument('--ble', action='store_true', help='Scan BLE only')
    parser.add_argument('--wifi', action='store_true', help='Scan WiFi only')
    parser.add_argument('--usb', action='store_true', help='Scan USB only')
    parser.add_argument('--nfc', action='store_true', help='Scan NFC only')
    parser.add_argument('--audit', action='store_true', help='Full security audit (vulnerability tests)')
    parser.add_argument('--api', action='store_true', help='Start API server after scan')
    parser.add_argument('--api-port', type=int, default=5000, help='Port for API server (default 5000)')
    parser.add_argument('--no-wifi', action='store_true', help='Skip WiFi scan (only directly connected devices)')
    parser.add_argument('--no-siem', action='store_true', help='Disable automatic SIEM export (enabled by default)')
    parser.add_argument('--no-threat-intel', action='store_true', help='Disable automatic threat intelligence (enabled by default)')
    parser.add_argument('--legacy-reports', action='store_true', help='Also create legacy files (scan_*.json, report_*.json); default is combined_report_*.json only')
    
    # New features
    parser.add_argument('--schedule', type=str, help='Schedule scans (e.g. "daily 09:00", "hourly", "every 30 minutes")')
    parser.add_argument('--monitor', action='store_true', help='Run real-time monitoring')
    parser.add_argument('--interval', type=int, default=300, help='Monitoring interval in seconds (default 300 = 5 min)')
    parser.add_argument('--report-email', metavar='ADR', default=None, help='After scan, send combined_report by email (SMTP from .env, like ESP32)')
    parser.add_argument('--ble-duration', type=int, default=20, metavar='SEC', help='BLE scan duration in seconds (default 20; higher = more chance to detect slow advertisers)')
    

    args = parser.parse_args()
    
    console.print(Panel.fit(
        "[bold cyan]🏥 Medical Device Security Scanner[/bold cyan]\n"
        "[dim]IoT medical device security audit tool[/dim]",
        style="cyan"
    ))
    console.print()
    
    # Choose protocols to scan
    protocols = []
    if args.ble:
        protocols.append('ble')
    if args.wifi:
        protocols.append('wifi')
    if args.usb:
        protocols.append('usb')
    if args.nfc:
        protocols.append('nfc')
    
    # If no protocol selected, scan all (except WiFi if --no-wifi)
    if not protocols:
        protocols = ['ble', 'usb', 'nfc']
        if not args.no_wifi:
            protocols.append('wifi')
    
    run_vulnerability_tests = args.audit
    
    # Create scanner
    scanner = MedicalDeviceScanner(protocols=protocols)
    
    # Scan devices (ble_duration from --ble-duration)
    devices = scanner.scan_all(ble_duration=getattr(args, 'ble_duration', 20))
    
    # Check if any devices were found
    if not devices:
        console.print("[yellow]⚠️  No devices found[/yellow]")
        console.print("[dim]💡 Tip: WiFi scans the whole local network (all devices on WiFi)[/dim]")
        console.print("[dim]   Use --no-wifi to scan only directly connected devices (USB, BLE)[/dim]\n")
    else:
        # Analyze security
        scanner.analyze_security(run_vulnerability_tests=run_vulnerability_tests)
        
        # Display results
        scanner.display_results()
        
        # Show high-risk devices (simplified, readable)
        risk_groups = scanner.get_devices_by_risk()
        if risk_groups["high_risk"]:
            console.print("\n[bold red]⚠️  HIGH-RISK DEVICES:[/bold red]\n")
            
            # Group by protocol
            by_protocol = {}
            for device in risk_groups["high_risk"]:
                protocol = device.protocol.value
                if protocol not in by_protocol:
                    by_protocol[protocol] = []
                by_protocol[protocol].append(device)
            
            # Show by protocol
            protocol_names = {
                "BLE": "📶 Bluetooth Low Energy (BLE)",
                "WiFi": "📡 WiFi (Local network)",
                "USB": "🔌 USB (Directly connected)",
                "NFC": "📱 NFC (Cards/Tags)"
            }
            
            for protocol, devices in by_protocol.items():
                protocol_label = protocol_names.get(protocol, f"🌐 {protocol}")
                console.print(f"[bold cyan]{protocol_label}[/bold cyan] ({len(devices)} devices):")
                
                # Group duplicates (same names)
                name_groups = {}
                for device in devices:
                    name = device.name if device.name != "Unknown" else f"Unknown-{device.mac_address[-5:]}"
                    if name not in name_groups:
                        name_groups[name] = []
                    name_groups[name].append(device)
                
                for name, device_list in name_groups.items():
                    # If only one device with this name
                    if len(device_list) == 1:
                        device = device_list[0]
                        console.print(f"  • [yellow]{name}[/yellow]")
                        console.print(f"    MAC: {device.mac_address} | Score: {device.security_score}/100")
                        if device.vulnerabilities:
                            # Show unique vulnerabilities
                            unique_vulns = list(set(device.vulnerabilities))
                            console.print(f"    ⚠️  Vulnerabilities ({len(unique_vulns)}):")
                            for vuln in unique_vulns[:3]:
                                console.print(f"      - {vuln}")
                            if len(unique_vulns) > 3:
                                console.print(f"      ... and {len(unique_vulns) - 3} more")
                    else:
                        # Multiple devices with same name – show together
                        console.print(f"  • [yellow]{name}[/yellow] ({len(device_list)} devices)")
                        unique_vulns = set()
                        for device in device_list:
                            unique_vulns.update(device.vulnerabilities)
                        if unique_vulns:
                            console.print(f"    ⚠️  Vulnerabilities ({len(unique_vulns)}):")
                            for vuln in list(unique_vulns)[:3]:
                                console.print(f"      - {vuln}")
                            if len(unique_vulns) > 3:
                                console.print(f"      ... and {len(unique_vulns) - 3} more")
                        console.print(f"    [dim]MAC adresy: {', '.join([d.mac_address for d in device_list[:3]])}[/dim]")
                        if len(device_list) > 3:
                            console.print(f"    [dim]... and {len(device_list) - 3} more[/dim]")
                
                console.print()  # Blank line between protocols
        
        # Save results
        # By default only combined_report_*.json (all data in one file)
        # Legacy files (scan_*.json, report_*.json) only if --legacy-reports
        if args.legacy_reports:
            scan_file = scanner.save_scan_results()
            report_files = scanner.generate_report()
            console.print("[dim]   Also created legacy files (scan_*.json, report_*.json) for backward compatibility[/dim]")
        else:
            scan_file = ""
            report_files = {}
            console.print("[dim]   Creating only combined_report_*.json (all data in one file)[/dim]")
        
        # Save to history (if available)
        try:
            from history_db import HistoryDB
            history_db = HistoryDB()
            scan_id = history_db.save_scan(devices, protocols)
            console.print(f"[dim]💾 Saved to history (scan_id: {scan_id})[/dim]")
        except Exception as e:
            console.print(f"[dim]⚠️  Could not save to history: {e}[/dim]")
            history_db = None
        
        # Automatic SIEM export (enabled by default, JSON Lines format)
        if not args.no_siem:
            try:
                timestamp_str = datetime.now().isoformat()
                file_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                siem_file = f"siem_export_{file_timestamp}.jsonl"
                
                console.print("[cyan]📤 Exporting to SIEM (JSON Lines)...[/cyan]")
                export_file = _export_to_siem_jsonl(scanner.devices, siem_file, timestamp_str)
                console.print(f"[green]✅ Saved: {export_file}[/green]")
                # Update path for import_to_splunk.sh
                console.print(f"[dim]💡 Import to Splunk: ./scripts/import_to_splunk.sh[/dim]")
                console.print(f"[dim]   💡 Simpler: use --api to view results in browser[/dim]")
                console.print(f"[dim]   💡 Or import to Splunk/ELK – see docs[/dim]")
            except Exception:
                pass  # Silently skip on error
        
        # Save to history (if available)
        try:
            from history_db import HistoryDB
            history_db = HistoryDB()
            scan_id = history_db.save_scan(devices, protocols)
            console.print(f"[dim]💾 Saved to history (scan_id: {scan_id})[/dim]")
        except Exception as e:
            console.print(f"[dim]⚠️  Could not save to history: {e}[/dim]")
            history_db = None
        
        # Scan function for scheduler/monitor
        def perform_scan():
            """Run full scan – used by scheduler/monitor."""
            # Create new scanner
            scan_scanner = MedicalDeviceScanner(protocols=protocols)
            
            # Scan (ble_duration from --ble-duration flag)
            scan_devices = scan_scanner.scan_all(ble_duration=getattr(args, 'ble_duration', 20))
            
            if scan_devices:
                # Analyze
                scan_scanner.analyze_security(run_vulnerability_tests=run_vulnerability_tests)
                
                # Save to history
                try:
                    from history_db import HistoryDB
                    scan_history_db = HistoryDB()
                    scan_history_db.save_scan(scan_devices, protocols)
                except Exception:
                    pass
                
            
            return scan_devices
        
        # Scheduled scans (--schedule)
        if args.schedule:
            try:
                from scheduler import ScanScheduler
                scheduler = ScanScheduler()
                scheduler.add_schedule(args.schedule, perform_scan)
                scheduler.start()
                
                console.print("\n[green]✅ Scheduler started[/green]")
                console.print("[dim]   Press Ctrl+C to stop[/dim]\n")
                
                # Wait indefinitely
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    scheduler.stop()
                    console.print("\n[yellow]⏹️  Scheduler stopped[/yellow]")
                    return
            except Exception as e:
                console.print(f"[red]❌ Scheduler error: {e}[/red]")
        
        # Real-time monitoring (--monitor)
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
                
                console.print("\n[green]✅ Monitor started[/green]")
                console.print("[dim]   Press Ctrl+C to stop[/dim]\n")
                
                # Wait indefinitely
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    monitor.stop()
                    console.print("\n[yellow]⏹️  Monitor stopped[/yellow]")
                    return
            except Exception as e:
                console.print(f"[red]❌ Monitor error: {e}[/red]")
        
        # Automatic Threat Intelligence check (if API key available)
        threat_intel_results = {}
        if not args.no_threat_intel:
            try:
                import threading
                import queue
                
                # Use queue to pass results from thread
                threat_queue = queue.Queue()
                
                def check_threats():
                    try:
                        results = _check_threat_intelligence(scanner.devices)
                        threat_queue.put(results)
                        
                        if results:
                            threats_found = sum(1 for r in results.values() if r.get('is_threat', False))
                            if threats_found > 0:
                                console.print(f"[yellow]⚠️  Threat Intelligence: Found {threats_found} suspicious IP(s)![/yellow]")
                    except Exception:
                        threat_queue.put({})  # Empty on error
                
                # Run in background (non-blocking)
                threat_thread = threading.Thread(target=check_threats, daemon=True)
                threat_thread.start()
                console.print("[cyan]🔍 Checking threat intelligence (background)...[/cyan]")
                # Show message only if key is not available
                abuseipdb_key = os.getenv("ABUSEIPDB_API_KEY")
                if not abuseipdb_key:
                    console.print(f"[dim]   💡 Add ABUSEIPDB_API_KEY to .env for full functionality[/dim]")
                
                # Wait for threat intelligence to finish (max 30 s)
                threat_thread.join(timeout=30)
                
                # Get results from queue (if available)
                try:
                    threat_intel_results = threat_queue.get(timeout=1)
                except queue.Empty:
                    threat_intel_results = {}  # No results
            except Exception:
                pass  # Silently skip on error
        
        # Generate combined report with all data
        combined_report = scanner.generate_combined_report(threat_intel_data=threat_intel_results if threat_intel_results else None)

        if args.report_email and combined_report and os.path.isfile(combined_report):
            _send_report_email(args.report_email, combined_report)

        console.print("[bold green]✅ Scan complete![/bold green]\n")
        
        # Start API server if requested
        if args.api:
            console.print(f"[cyan]🌐 Starting API server on port {args.api_port}...[/cyan]")
            console.print(f"[dim]Open in browser: http://localhost:{args.api_port}[/dim]\n")
            
            try:
                from api_server import app, shutdown_event, last_request_time
                import threading
                import webbrowser
                import time
                
                # Run server in separate thread
                def run_server():
                    app.run(host='0.0.0.0', port=args.api_port, debug=False, use_reloader=False, threaded=True)
                
                server_thread = threading.Thread(target=run_server, daemon=True)
                server_thread.start()
                
                # Wait a moment for server to start
                time.sleep(2)
                
                # Open browser
                try:
                    webbrowser.open(f'http://localhost:{args.api_port}')
                except:
                    pass
                
                console.print("[green]✅ API Server started![/green]")
                console.print(f"[cyan]   Endpointy:[/cyan]")
                console.print(f"   • http://localhost:{args.api_port}/")
                console.print(f"   • http://localhost:{args.api_port}/dashboard")
                console.print(f"   • http://localhost:{args.api_port}/devices")
                console.print(f"   • http://localhost:{args.api_port}/stats")
                console.print(f"\n[dim]💡 Close the browser to end the scan automatically[/dim]")
                console.print(f"[yellow]   Press Ctrl+C to stop manually[/yellow]\n")
                
                # Wait for browser close (shutdown) or Ctrl+C
                # Check if browser still sends heartbeat
                try:
                    import time as time_module
                    
                    heartbeat_timeout = 3  # Shorter timeout – if no heartbeat for 3 s, close
                    first_request = True
                    last_heartbeat_time = time_module.time()
                    
                    while not shutdown_event.is_set():
                        time.sleep(0.5)
                        
                        # Check if browser still sends heartbeat
                        current_time = time_module.time()
                        time_since_heartbeat = current_time - last_request_time
                        
                        # If there was any request (heartbeat or normal), update time
                        if time_since_heartbeat < 1.5:
                            if first_request:
                                first_request = False
                            last_heartbeat_time = current_time
                        
                        # If no heartbeat for timeout (and there was a request before), close
                        if not first_request:
                            time_since_last_heartbeat = current_time - last_heartbeat_time
                            if time_since_last_heartbeat > heartbeat_timeout:
                                console.print("\n[dim]🔌 Browser closed (no heartbeat) – shutting down server...[/dim]")
                                shutdown_event.set()
                                break
                    
                    console.print("\n[dim]🔌 Closing server...[/dim]")
                    time.sleep(0.5)  # Give time to shut down
                    console.print("[green]✅ Scan complete[/green]")
                except KeyboardInterrupt:
                    console.print("\n[yellow]⚠️  Stopping...[/yellow]")
                    shutdown_event.set()
                except Exception as e:
                    console.print(f"\n[yellow]⚠️  Error: {e}[/yellow]")
                    shutdown_event.set()
                finally:
                    shutdown_event.set()  # Ensure event is set
                    # Force process exit
                    os._exit(0)
                    
            except ImportError:
                console.print("[red]❌ Cannot start API server – Flask not installed[/red]")
                console.print("[yellow]   Install: pip install flask[/yellow]")
            except Exception as e:
                console.print(f"[red]❌ API startup error: {e}[/red]")
        
        # Full audit info
        if not run_vulnerability_tests:
            console.print("\n[dim]ℹ️  Tip: Use --audit flag for detailed vulnerability testing[/dim]")
            console.print("[dim]   Example: python3 src/scanner.py --wifi --audit[/dim]")
        
        # Show security audit results if tests were run
        if run_vulnerability_tests and scanner.vulnerability_tester:
            console.print("\n[bold cyan]🔍 DETAILED VULNERABILITY AUDIT RESULTS:[/bold cyan]\n")
            console.print("[dim]ℹ️  Full security audit was performed with --audit flag[/dim]\n")
            
            total_vulnerable_devices = 0
            for device in scanner.devices:
                if "vulnerability_tests" in device.metadata:
                    tests = device.metadata["vulnerability_tests"]
                    # Filter only real vulnerabilities
                    vulnerable_tests = [t for t in tests if t.get("is_vulnerable", False)]
                    
                    if not vulnerable_tests:
                        continue
                    
                    total_vulnerable_devices += 1
                    
                    # Split into medical ports and rest
                    medical_ports = [104, 11112, 5000]
                    medical_tests = [t for t in vulnerable_tests if t.get("port") in medical_ports or t.get("protocol") in ["DICOM", "HL7"]]
                    other_tests = [t for t in vulnerable_tests if t not in medical_tests]
                    
                    critical_medical = [t for t in medical_tests if t["severity"] == "Krytyczna"]
                    high_medical = [t for t in medical_tests if t["severity"] == "Wysoka"]
                    critical_other = [t for t in other_tests if t["severity"] == "Krytyczna"]
                    high_other = [t for t in other_tests if t["severity"] == "Wysoka"]
                    
                    # Check if it is a router
                    is_router = False
                    if scanner.vulnerability_tester:
                        is_router = scanner.vulnerability_tester._is_router(device)
                    
                    console.print(f"[bold yellow]📋 {device.name}[/bold yellow] (Score: {device.security_score}/100)")
                    if is_router:
                        console.print(f"  [dim]🏠 Router/Gateway – some ports (80, 443, 22, 161) are normal[/dim]")
                    console.print(f"  IP: {device.metadata.get('ip_address', 'N/A')}")
                    
                    # Medical ports
                    if critical_medical or high_medical:
                        console.print(f"\n  [cyan]🏥 MEDICAL PORTS:[/cyan]")
                        if critical_medical:
                            console.print(f"    [red]🔴 Critical ({len(critical_medical)}):[/red]")
                            for test in critical_medical:
                                console.print(f"      • Port {test.get('port', 'N/A')}: {test['name']}")
                        if high_medical:
                            console.print(f"    [yellow]🟠 High ({len(high_medical)}):[/yellow]")
                            for test in high_medical:
                                console.print(f"      • Port {test.get('port', 'N/A')}: {test['name']}")
                    else:
                        console.print(f"  [green]✅ Medical ports: No vulnerabilities[/green]")
                    
                    # Other ports
                    if critical_other or high_other:
                        console.print(f"\n  [blue]🔌 OTHER PORTS:[/blue]")
                        if critical_other:
                            console.print(f"    [red]🔴 Critical ({len(critical_other)}):[/red]")
                            for test in critical_other:
                                console.print(f"      • Port {test.get('port', 'N/A')}: {test['name']}")
                        if high_other:
                            console.print(f"    [yellow]🟠 High ({len(high_other)}):[/yellow]")
                            for test in high_other:
                                console.print(f"      • Port {test.get('port', 'N/A')}: {test['name']}")
                    else:
                        console.print(f"  [green]✅ Other ports: No vulnerabilities[/green]")
                    
                    # Attack susceptibility (from known vulnerabilities)
                    attack_sus = device.metadata.get("attack_susceptibility", [])
                    if attack_sus:
                        console.print(f"\n  [yellow]🎯 ATTACK SUSCEPTIBILITY:[/yellow]")
                        for a in attack_sus[:8]:
                            console.print(f"    • {a.get('attack_type', 'N/A')}: [dim]{a.get('reason', '')}[/dim]")
                        if len(attack_sus) > 8:
                            console.print(f"    [dim]... and {len(attack_sus) - 8} more[/dim]")
                    
                    console.print()  # Blank line between devices
            
            if total_vulnerable_devices == 0:
                console.print("[green]✅ No vulnerabilities in any device![/green]\n")
    
    # Show security audit results if tests were run
    if devices and run_vulnerability_tests and scanner.vulnerability_tester:
        console.print("\n[bold cyan]🔍 DETAILED VULNERABILITY AUDIT RESULTS:[/bold cyan]\n")
        console.print("[dim]ℹ️  Full security audit was performed with --audit flag[/dim]\n")
        
        total_vulnerable_devices = 0
        for device in scanner.devices:
            if "vulnerability_tests" in device.metadata:
                tests = device.metadata["vulnerability_tests"]
                # Filter only real vulnerabilities
                vulnerable_tests = [t for t in tests if t.get("is_vulnerable", False)]
                
                if not vulnerable_tests:
                    continue
                
                total_vulnerable_devices += 1
                
                # Split into medical ports and rest
                medical_ports = [104, 11112, 5000]
                medical_tests = [t for t in vulnerable_tests if t.get("port") in medical_ports or t.get("protocol") in ["DICOM", "HL7"]]
                other_tests = [t for t in vulnerable_tests if t not in medical_tests]
                
                critical_medical = [t for t in medical_tests if t["severity"] == "Critical"]
                high_medical = [t for t in medical_tests if t["severity"] == "High"]
                critical_other = [t for t in other_tests if t["severity"] == "Critical"]
                high_other = [t for t in other_tests if t["severity"] == "High"]
                
                # Check if it is a router
                is_router = False
                if scanner.vulnerability_tester:
                    is_router = scanner.vulnerability_tester._is_router(device)
                
                console.print(f"[bold yellow]📋 {device.name}[/bold yellow] (Score: {device.security_score}/100)")
                if is_router:
                    console.print(f"  [dim]🏠 Router/Gateway – some ports (80, 443, 22, 161) are normal[/dim]")
                console.print(f"  IP: {device.metadata.get('ip_address', 'N/A')}")
                
                # Medical ports
                if critical_medical or high_medical:
                    console.print(f"\n  [cyan]🏥 MEDICAL PORTS:[/cyan]")
                    if critical_medical:
                        console.print(f"    [red]🔴 Critical ({len(critical_medical)}):[/red]")
                        for test in critical_medical:
                            console.print(f"      • Port {test.get('port', 'N/A')}: {test['name']}")
                    if high_medical:
                        console.print(f"    [yellow]🟠 High ({len(high_medical)}):[/yellow]")
                        for test in high_medical:
                            console.print(f"      • Port {test.get('port', 'N/A')}: {test['name']}")
                else:
                    console.print(f"  [green]✅ Medical ports: No vulnerabilities[/green]")
                
                # Other ports
                if critical_other or high_other:
                    console.print(f"\n  [blue]🔌 OTHER PORTS:[/blue]")
                    if critical_other:
                        console.print(f"    [red]🔴 Critical ({len(critical_other)}):[/red]")
                        for test in critical_other:
                            console.print(f"      • Port {test.get('port', 'N/A')}: {test['name']}")
                    if high_other:
                        console.print(f"    [yellow]🟠 High ({len(high_other)}):[/yellow]")
                        for test in high_other:
                            console.print(f"      • Port {test.get('port', 'N/A')}: {test['name']}")
                else:
                    console.print(f"  [green]✅ Other ports: No vulnerabilities[/green]")
                
                # Attack susceptibility
                attack_sus = device.metadata.get("attack_susceptibility", [])
                if attack_sus:
                    console.print(f"\n  [yellow]🎯 ATTACK SUSCEPTIBILITY:[/yellow]")
                    for a in attack_sus[:8]:
                        console.print(f"    • {a.get('attack_type', 'N/A')}: [dim]{a.get('reason', '')}[/dim]")
                    if len(attack_sus) > 8:
                        console.print(f"    [dim]... and {len(attack_sus) - 8} more[/dim]")
                
                console.print()  # Blank line between devices
        
        if total_vulnerable_devices == 0:
            console.print("[green]✅ No vulnerabilities in any device![/green]\n")
    
    


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
