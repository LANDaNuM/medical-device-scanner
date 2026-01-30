#!/usr/bin/env python3
"""
Prosty REST API serwer do dostępu do danych skanera.

API umożliwia:
- Pobieranie listy urządzeń (z filtrowaniem)
- Pobieranie szczegółów urządzenia
- Pobieranie raportów
- Statystyki
- Pobieranie skanów

UŻYCIE:
    python src/api_server.py              # Uruchom serwer (domyślnie port 5000)
    python src/api_server.py --port 8080   # Uruchom na porcie 8080
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime
from typing import Optional, List, Dict

# Dodaj ścieżkę do src
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

try:
    from flask import Flask, jsonify, request, Response, render_template_string, render_template_string
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None
    Response = None
    render_template_string = None

from rich.console import Console
from rich.panel import Panel

console = Console()


def json_response(data: Dict, pretty: bool = False) -> Response:
    """
    Zwraca odpowiedź JSON z opcjonalnym formatowaniem.
    
    Args:
        data: Dane do zwrócenia
        pretty: Czy sformatować JSON (z wcięciami)
    
    Returns:
        Flask Response z JSON
    """
    if pretty:
        response = Response(
            json.dumps(data, indent=2, ensure_ascii=False),
            mimetype='application/json'
        )
    else:
        response = jsonify(data)
    return response

# Katalogi z danymi - raporty w głównym katalogu projektu
project_root = Path(__file__).parent.parent
scans_dir = project_root / "reports"
reports_dir = project_root / "reports"
# Utwórz katalogi jeśli nie istnieją
scans_dir.mkdir(exist_ok=True)
reports_dir.mkdir(exist_ok=True)

app = Flask(__name__) if FLASK_AVAILABLE else None


def load_latest_scan() -> Optional[Dict]:
    """Wczytuje najnowszy skan."""
    scan_files = sorted(list(scans_dir.glob("scan_*.json")))
    if not scan_files:
        return None
    
    latest_file = scan_files[-1]
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def load_latest_report() -> Optional[Dict]:
    """Wczytuje najnowszy raport."""
    report_files = sorted(list(reports_dir.glob("report_*.json")))
    if not report_files:
        return None
    
    latest_file = report_files[-1]
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def filter_devices(devices: List[Dict], filters: Dict) -> List[Dict]:
    """Filtruje urządzenia na podstawie parametrów."""
    filtered = devices
    
    # Filtruj po protokole
    if 'protocol' in filters:
        protocol = filters['protocol'].upper()
        filtered = [d for d in filtered if d.get('protocol', '').upper() == protocol]
    
    # Filtruj po security score (min)
    if 'score_min' in filters:
        try:
            score_min = int(filters['score_min'])
            filtered = [d for d in filtered if d.get('security_score', 0) >= score_min]
        except ValueError:
            pass
    
    # Filtruj po security score (max)
    if 'score_max' in filters:
        try:
            score_max = int(filters['score_max'])
            filtered = [d for d in filtered if d.get('security_score', 100) <= score_max]
        except ValueError:
            pass
    
    # Filtruj po szyfrowaniu
    if 'has_encryption' in filters:
        has_enc = filters['has_encryption'].lower() == 'true'
        filtered = [d for d in filtered if d.get('has_encryption', False) == has_enc]
    
    # Wyszukaj po nazwie/MAC
    if 'search' in filters:
        search_term = filters['search'].lower()
        filtered = [
            d for d in filtered
            if search_term in d.get('name', '').lower() or search_term in d.get('mac_address', '').lower()
        ]
    
    return filtered


def render_dashboard_html(devices: List[Dict], summary: Dict, full_data: Dict) -> str:
    """Renderuje pełny graficzny dashboard z raportem."""
    total = summary.get('total_devices', len(devices))
    high_risk = summary.get('high_risk_count', len([d for d in devices if d.get('security_score', 100) < 50]))
    medium_risk = summary.get('medium_risk_count', len([d for d in devices if 50 <= d.get('security_score', 100) < 80]))
    low_risk = summary.get('low_risk_count', len([d for d in devices if d.get('security_score', 100) >= 80]))
    avg_score = summary.get('average_security_score', sum(d.get('security_score', 0) for d in devices) / total if total > 0 else 0)
    
    # Statystyki protokołów
    protocols = {}
    for device in devices:
        proto = device.get('protocol', 'Unknown')
        protocols[proto] = protocols.get(proto, 0) + 1
    
    html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pełny Raport - Medical Device Scanner</title>
    <script>
        // Automatyczne zamykanie serwera przy zamknięciu przeglądarki
        let heartbeatInterval;
        
        // Heartbeat - wysyłaj co sekundę aby pokazać że przeglądarka jest otwarta
        function startHeartbeat() {{
            heartbeatInterval = setInterval(function() {{
                fetch('/heartbeat', {{method: 'GET', keepalive: true}}).catch(() => {{}});
            }}, 1000);
        }}
        
        // Zatrzymaj heartbeat i wyślij shutdown przy zamknięciu
        function stopAndShutdown() {{
            if (heartbeatInterval) {{
                clearInterval(heartbeatInterval);
            }}
            // Spróbuj wszystkie metody
            navigator.sendBeacon('/shutdown');
            fetch('/shutdown', {{method: 'POST', keepalive: true}}).catch(() => {{}});
        }}
        
        window.addEventListener('beforeunload', stopAndShutdown);
        window.addEventListener('unload', stopAndShutdown);
        window.addEventListener('pagehide', stopAndShutdown);
        
        // Rozpocznij heartbeat po załadowaniu strony
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', startHeartbeat);
        }} else {{
            startHeartbeat();
        }}
    </script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .nav {{
            margin-bottom: 20px;
        }}
        .nav a {{
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
            display: inline-block;
            margin-right: 10px;
            margin-bottom: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-value {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .stat-high {{ color: #f44336; }}
        .stat-medium {{ color: #ff9800; }}
        .stat-low {{ color: #4caf50; }}
        .stat-label {{
            color: #666;
            font-size: 1.1em;
        }}
        .section {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .section h2 {{
            margin-bottom: 20px;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .devices-grid {{
            display: grid;
            gap: 20px;
        }}
        .device-card {{
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            background: #f8f9fa;
        }}
        .device-card.high-risk {{ border-left-color: #f44336; background: #ffebee; }}
        .device-card.medium-risk {{ border-left-color: #ff9800; background: #fff3e0; }}
        .device-card.low-risk {{ border-left-color: #4caf50; background: #e8f5e9; }}
        .device-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .device-name {{
            font-size: 1.3em;
            font-weight: bold;
        }}
        .device-score {{
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 1.1em;
        }}
        .score-high {{ background: #f44336; color: white; }}
        .score-medium {{ background: #ff9800; color: white; }}
        .score-low {{ background: #4caf50; color: white; }}
        .device-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .detail-item {{
            padding: 10px;
            background: white;
            border-radius: 5px;
        }}
        .detail-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }}
        .detail-value {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        .vulns {{
            margin-top: 15px;
            padding: 15px;
            background: #fff3cd;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
        }}
        .vuln-item {{
            margin: 8px 0;
            color: #856404;
            padding-left: 20px;
        }}
        .protocol-badge {{
            display: inline-block;
            padding: 5px 12px;
            background: #667eea;
            color: white;
            border-radius: 15px;
            font-size: 0.9em;
            margin: 5px 5px 5px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="nav">
            <a href="/">🏠 Strona główna</a>
            <a href="/devices">📱 Urządzenia</a>
            <a href="/stats">📈 Statystyki</a>
        </div>
        <h1>📊 Pełny Raport Skanowania</h1>
        <p>Data: {summary.get('report_timestamp', 'N/A') if 'report_timestamp' in summary else full_data.get('scan_timestamp', 'N/A')}</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value" style="color: #667eea;">{total}</div>
            <div class="stat-label">Wszystkie urządzenia</div>
        </div>
        <div class="stat-card">
            <div class="stat-value stat-high">{high_risk}</div>
            <div class="stat-label">Wysokie ryzyko</div>
        </div>
        <div class="stat-card">
            <div class="stat-value stat-medium">{medium_risk}</div>
            <div class="stat-label">Średnie ryzyko</div>
        </div>
        <div class="stat-card">
            <div class="stat-value stat-low">{low_risk}</div>
            <div class="stat-label">Niskie ryzyko</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: #667eea;">{avg_score:.1f}</div>
            <div class="stat-label">Średni security score</div>
        </div>
    </div>
    
    <div class="section">
        <h2>📡 Protokoły</h2>
        <div>
"""
    
    for proto, count in protocols.items():
        html += f'<span class="protocol-badge">{proto}: {count}</span>'
    
    html += """
        </div>
    </div>
    
    <div class="section">
        <h2>📱 Wszystkie Urządzenia</h2>
        <div class="devices-grid">
"""
    
    for device in devices:
        score = device.get('security_score', 0)
        risk_class = 'high-risk' if score < 50 else 'medium-risk' if score < 80 else 'low-risk'
        score_class = 'score-high' if score < 50 else 'score-medium' if score < 80 else 'score-low'
        
        vulns = device.get('vulnerabilities', [])
        vulns_html = ""
        if vulns:
            vulns_html = '<div class="vulns"><strong>⚠️ Podatności (' + str(len(vulns)) + '):</strong>'
            for vuln in vulns[:5]:
                vulns_html += f'<div class="vuln-item">• {vuln}</div>'
            if len(vulns) > 5:
                vulns_html += f'<div class="vuln-item">... i {len(vulns) - 5} więcej</div>'
            vulns_html += '</div>'
        
        # Mikrokontroler
        microcontroller_info = ""
        if device.get('metadata', {}).get('microcontroller'):
            meta = device['metadata']
            port = meta.get('port', 'N/A')
            baudrate = meta.get('baudrate', 'N/A')
            messages = meta.get('messages', [])
            microcontroller_info = f"""
            <div class="detail-item">
                <div class="detail-label">🔧 Mikrokontroler</div>
                <div class="detail-value">Port: {port} | {baudrate} baud | {len(messages)} komunikatów</div>
            </div>
            """
        
        # AI Anomaly Detection
        ai_info = ""
        if device.get('metadata', {}).get('anomaly_detection'):
            ai_data = device['metadata']['anomaly_detection']
            if ai_data.get('is_anomaly'):
                ai_info = f"""
            <div class="detail-item" style="background: #ffebee;">
                <div class="detail-label">🤖 AI: Wykryta anomalia</div>
                <div class="detail-value" style="color: #c62828;">Score: {ai_data.get('anomaly_score', 0):.2f} | {ai_data.get('reason', 'N/A')}</div>
            </div>
            """
        
        html += f"""
        <div class="device-card {risk_class}">
            <div class="device-header">
                <div class="device-name">{device.get('name', 'Unknown')}</div>
                <div class="device-score {score_class}">{score}/100</div>
            </div>
            <div class="device-details">
                <div class="detail-item">
                    <div class="detail-label">MAC Address</div>
                    <div class="detail-value">{device.get('mac_address', 'N/A')}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Typ</div>
                    <div class="detail-value">{device.get('device_type', 'unknown')}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Protokół</div>
                    <div class="detail-value">{device.get('protocol', 'N/A')}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Szyfrowanie</div>
                    <div class="detail-value">{'✅ Tak' if device.get('has_encryption') else '❌ Nie'}</div>
                </div>
                {microcontroller_info}
                {ai_info}
            </div>
            {vulns_html}
        </div>
"""
    
    html += """
        </div>
    </div>
</body>
</html>"""
    return html


def render_stats_html(total: int, by_protocol: Dict, by_encryption: Dict, by_risk: Dict, encryption_strength: Dict) -> str:
    """Renderuje graficzny interfejs HTML ze statystykami."""
    html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Statystyki - Medical Device Scanner</title>
    <script>
        // Automatyczne zamykanie serwera przy zamknięciu przeglądarki
        let heartbeatInterval;
        
        // Heartbeat - wysyłaj co sekundę aby pokazać że przeglądarka jest otwarta
        function startHeartbeat() {{
            heartbeatInterval = setInterval(function() {{
                fetch('/heartbeat', {{method: 'GET', keepalive: true}}).catch(() => {{}});
            }}, 1000);
        }}
        
        // Zatrzymaj heartbeat i wyślij shutdown przy zamknięciu
        function stopAndShutdown() {{
            if (heartbeatInterval) {{
                clearInterval(heartbeatInterval);
            }}
            // Spróbuj wszystkie metody
            navigator.sendBeacon('/shutdown');
            fetch('/shutdown', {{method: 'POST', keepalive: true}}).catch(() => {{}});
        }}
        
        window.addEventListener('beforeunload', stopAndShutdown);
        window.addEventListener('unload', stopAndShutdown);
        window.addEventListener('pagehide', stopAndShutdown);
        
        // Rozpocznij heartbeat po załadowaniu strony
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', startHeartbeat);
        }} else {{
            startHeartbeat();
        }}
    </script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .nav a {{
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
            display: inline-block;
            margin-right: 10px;
            margin-bottom: 10px;
        }}
        .section {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .section h2 {{
            margin-bottom: 20px;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }}
        .stat-item {{
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="nav">
            <a href="/">🏠 Strona główna</a>
            <a href="/dashboard">📊 Pełny raport</a>
            <a href="/devices">📱 Urządzenia</a>
        </div>
        <h1>📈 Statystyki Skanowania</h1>
    </div>
    
    <div class="section">
        <h2>📊 Podsumowanie</h2>
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value">{total}</div>
                <div class="stat-label">Wszystkie urządzenia</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" style="color: #f44336;">{by_risk.get('high_risk', 0)}</div>
                <div class="stat-label">Wysokie ryzyko</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" style="color: #ff9800;">{by_risk.get('medium_risk', 0)}</div>
                <div class="stat-label">Średnie ryzyko</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" style="color: #4caf50;">{by_risk.get('low_risk', 0)}</div>
                <div class="stat-label">Niskie ryzyko</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>📡 Protokoły</h2>
        <div class="stats-grid">
"""
    
    for proto, count in by_protocol.items():
        html += f"""
            <div class="stat-item">
                <div class="stat-value">{count}</div>
                <div class="stat-label">{proto}</div>
            </div>
"""
    
    html += """
        </div>
    </div>
    
    <div class="section">
        <h2>🔐 Szyfrowanie</h2>
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value" style="color: #4caf50;">""" + str(by_encryption.get('with', 0)) + """</div>
                <div class="stat-label">Z szyfrowaniem</div>
            </div>
            <div class="stat-item">
                <div class="stat-value" style="color: #f44336;">""" + str(by_encryption.get('without', 0)) + """</div>
                <div class="stat-label">Bez szyfrowania</div>
            </div>
        </div>
    </div>
</body>
</html>"""
    return html


def render_devices_html(devices: List[Dict], filters: Dict) -> str:
    """Renderuje graficzny interfejs HTML z listą urządzeń."""
    html = """<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Urządzenia - Medical Device Scanner</title>
    <script>
        // Automatyczne zamykanie serwera przy zamknięciu przeglądarki
        window.addEventListener('beforeunload', function() {
            navigator.sendBeacon('/shutdown');
        });
        window.addEventListener('unload', function() {
            navigator.sendBeacon('/shutdown');
        });
    </script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .header h1 { font-size: 2em; margin-bottom: 10px; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        .devices-grid {
            display: grid;
            gap: 20px;
        }
        .device-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .device-card.high-risk { border-left-color: #f44336; }
        .device-card.medium-risk { border-left-color: #ff9800; }
        .device-card.low-risk { border-left-color: #4caf50; }
        .device-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .device-name {
            font-size: 1.3em;
            font-weight: bold;
        }
        .device-score {
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
        }
        .score-high { background: #ffebee; color: #c62828; }
        .score-medium { background: #fff3e0; color: #e65100; }
        .score-low { background: #e8f5e9; color: #2e7d32; }
        .device-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }
        .info-item {
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .info-label {
            font-size: 0.9em;
            color: #666;
        }
        .info-value {
            font-weight: bold;
            margin-top: 5px;
        }
        .vulns {
            margin-top: 15px;
            padding: 10px;
            background: #fff3cd;
            border-radius: 5px;
        }
        .vuln-item {
            margin: 5px 0;
            color: #856404;
        }
        .nav {
            margin-bottom: 20px;
        }
        .nav a {
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
            display: inline-block;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="nav">
            <a href="/">🏠 Strona główna</a>
            <a href="/dashboard">📊 Pełny raport</a>
            <a href="/stats">📈 Statystyki</a>
        </div>
        <h1>📱 Wykryte Urządzenia</h1>
        <p>Znaleziono: """ + str(len(devices)) + """ urządzeń</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">""" + str(len(devices)) + """</div>
            <div class="stat-label">Wszystkie urządzenia</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">""" + str(len([d for d in devices if d.get('security_score', 100) < 50])) + """</div>
            <div class="stat-label">Wysokie ryzyko</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">""" + str(len([d for d in devices if d.get('has_encryption', False)])) + """</div>
            <div class="stat-label">Z szyfrowaniem</div>
        </div>
    </div>
    
    <div class="devices-grid">
"""
    
    for device in devices:
        score = device.get('security_score', 0)
        risk_class = 'high-risk' if score < 50 else 'medium-risk' if score < 80 else 'low-risk'
        score_class = 'score-high' if score < 50 else 'score-medium' if score < 80 else 'score-low'
        
        vulns = device.get('vulnerabilities', [])
        vulns_html = ""
        if vulns:
            vulns_html = '<div class="vulns"><strong>⚠️ Podatności:</strong>'
            for vuln in vulns[:5]:
                vulns_html += f'<div class="vuln-item">• {vuln}</div>'
            if len(vulns) > 5:
                vulns_html += f'<div class="vuln-item">... i {len(vulns) - 5} więcej</div>'
            vulns_html += '</div>'
        
        # Mikrokontroler info
        microcontroller_info = ""
        if device.get('metadata', {}).get('microcontroller'):
            meta = device['metadata']
            port = meta.get('port', 'N/A')
            baudrate = meta.get('baudrate', 'N/A')
            messages = meta.get('messages', [])
            microcontroller_info = f"""
            <div class="info-item">
                <div class="info-label">🔧 Mikrokontroler</div>
                <div class="info-value">Port: {port} | {baudrate} baud | {len(messages)} komunikatów</div>
            </div>
            """
        
        html += f"""
        <div class="device-card {risk_class}">
            <div class="device-header">
                <div class="device-name">{device.get('name', 'Unknown')}</div>
                <div class="device-score {score_class}">{score}/100</div>
            </div>
            <div class="device-info">
                <div class="info-item">
                    <div class="info-label">MAC Address</div>
                    <div class="info-value">{device.get('mac_address', 'N/A')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Typ</div>
                    <div class="info-value">{device.get('device_type', 'unknown')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Protokół</div>
                    <div class="info-value">{device.get('protocol', 'N/A')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Szyfrowanie</div>
                    <div class="info-value">{'✅ Tak' if device.get('has_encryption') else '❌ Nie'}</div>
                </div>
                {microcontroller_info}
            </div>
            {vulns_html}
        </div>
"""
    
    html += """
    </div>
</body>
</html>"""
    return html


def simplify_device(device: Dict, detailed: bool = False) -> Dict:
    """Upraszcza urządzenie - usuwa niepotrzebne szczegóły."""
    simplified = {
        'name': device.get('name', 'Unknown'),
        'mac_address': device.get('mac_address', ''),
        'device_type': device.get('device_type', 'unknown'),
        'protocol': device.get('protocol', ''),
        'security_score': device.get('security_score', 0),
        'has_encryption': device.get('has_encryption', False),
        'encryption_type': device.get('encryption_type', 'N/A'),
        'vulnerability_count': len(device.get('vulnerabilities', []))
    }
    
    if detailed:
        simplified.update({
            'manufacturer': device.get('manufacturer'),
            'model': device.get('model'),
            'firmware_version': device.get('firmware_version'),
            'requires_pairing': device.get('requires_pairing', False),
            'rssi': device.get('rssi'),
            'vulnerabilities': device.get('vulnerabilities', []),
            'metadata': {
                'encryption_analysis': device.get('metadata', {}).get('encryption_analysis'),
                'fda_compliance': device.get('metadata', {}).get('fda_compliance'),
                'ip_address': device.get('metadata', {}).get('ip_address')
            }
        })
    
    return simplified


# Globalna zmienna do kontroli shutdown - eksportowana dla scanner.py
import threading
import time
shutdown_event = threading.Event()
last_request_time = time.time()  # Czas ostatniego requestu (heartbeat)

if FLASK_AVAILABLE and app:
    # Zmienna do śledzenia ostatniego requestu (heartbeat)
    import time
    last_request_time = time.time()
    
    @app.route('/shutdown', methods=['POST', 'GET'])
    def shutdown():
        """Zatrzymuje serwer API."""
        global last_request_time
        last_request_time = time.time()
        shutdown_event.set()
        # Zwróć odpowiedź natychmiast (przed zamknięciem serwera)
        return 'Server shutting down...', 200
    
    @app.route('/heartbeat', methods=['GET', 'POST'])
    def heartbeat():
        """Heartbeat - przeglądarka wysyła to co sekundę aby pokazać że jest otwarta."""
        global last_request_time
        last_request_time = time.time()
        return 'OK', 200
    
    @app.before_request
    def update_last_request():
        """Aktualizuj czas ostatniego requestu przy każdym żądaniu."""
        global last_request_time
        last_request_time = time.time()
    
    @app.route('/')
    def index():
        """Strona główna API - przekierowuje do dashboard jeśli są dane."""
        # Sprawdź czy klient chce JSON (np. curl, Postman)
        if request.headers.get('Accept', '').startswith('application/json'):
            return jsonify({
                'name': 'Medical Device Security Scanner API',
                'version': '1.0',
                'endpoints': {
                    '/dashboard': 'Pełny raport (HTML)',
                    '/devices': 'Lista urządzeń (HTML/JSON)',
                    '/stats': 'Statystyki (HTML/JSON)'
                }
            })
        
        # Sprawdź czy są dane - jeśli tak, przekieruj do dashboard
        data = load_latest_report() or load_latest_scan()
        if data:
            from flask import redirect
            return redirect('/dashboard')
        
        # Jeśli brak danych, pokaż stronę startową
        # Dla przeglądarki zwróć HTML
        html_template = """<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Medical Device Security Scanner API</title>
    <script>
        // Automatyczne zamykanie serwera przy zamknięciu przeglądarki
        window.addEventListener('beforeunload', function() {
            navigator.sendBeacon('/shutdown');
        });
        window.addEventListener('unload', function() {
            navigator.sendBeacon('/shutdown');
        });
    </script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        .content {
            padding: 40px;
        }
        .endpoints {
            display: grid;
            gap: 20px;
            margin-top: 30px;
        }
        .endpoint {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 8px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .endpoint:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .endpoint-method {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.9em;
            margin-right: 10px;
        }
        .endpoint-path {
            font-family: 'Courier New', monospace;
            font-size: 1.1em;
            color: #333;
            font-weight: bold;
        }
        .endpoint-desc {
            margin-top: 10px;
            color: #666;
        }
        .test-btn {
            display: inline-block;
            margin-top: 10px;
            padding: 8px 16px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-size: 0.9em;
            transition: background 0.2s;
        }
        .test-btn:hover {
            background: #5568d3;
        }
        .info-box {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .info-box h3 {
            color: #1976d2;
            margin-bottom: 10px;
        }
        .status {
            display: inline-block;
            padding: 6px 12px;
            background: #4caf50;
            color: white;
            border-radius: 20px;
            font-size: 0.9em;
            margin-top: 10px;
        }
        @media (max-width: 768px) {
            .header h1 { font-size: 1.8em; }
            .content { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 Medical Device Security Scanner</h1>
            <p>API v1.0</p>
            <span class="status">● Online</span>
        </div>
        <div class="content">
            <div class="info-box">
                <h3>ℹ️ O API</h3>
                <p>To REST API do skanowania i analizy bezpieczeństwa urządzeń medycznych IoT. 
                Wykrywa urządzenia używające protokołów BLE, WiFi, USB i NFC oraz analizuje ich bezpieczeństwo.</p>
            </div>
            
            <h2>📡 Dostępne Endpointy</h2>
            <div class="endpoints">
                <div class="endpoint">
                    <span class="endpoint-method">📊</span>
                    <span class="endpoint-path">/dashboard</span>
                    <div class="endpoint-desc">
                        Pełny graficzny raport ze skanowania - wszystkie urządzenia, statystyki, wykresy.
                        <br>
                        <a href="/dashboard" class="test-btn">Otwórz raport →</a>
                    </div>
                </div>
                
                <div class="endpoint">
                    <span class="endpoint-method">📱</span>
                    <span class="endpoint-path">/devices</span>
                    <div class="endpoint-desc">
                        Lista wszystkich wykrytych urządzeń medycznych z filtrowaniem.
                        <br>
                        <a href="/devices" class="test-btn">Zobacz urządzenia →</a>
                    </div>
                </div>
                
                <div class="endpoint">
                    <span class="endpoint-method">📈</span>
                    <span class="endpoint-path">/stats</span>
                    <div class="endpoint-desc">
                        Statystyki skanowania (liczba urządzeń, protokoły, bezpieczeństwo).
                        <br>
                        <a href="/stats" class="test-btn">Zobacz statystyki →</a>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee;">
                <a href="/dashboard" style="display: inline-block; padding: 15px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 10px; font-size: 1.1em; font-weight: bold; transition: transform 0.2s;">
                    📊 Zobacz pełny raport →
                </a>
            </div>
        </div>
    </div>
</body>
</html>"""
        return render_template_string(html_template)
    
    @app.route('/devices', methods=['GET'])
    def get_devices():
        """Pobiera listę urządzeń - HTML dla przeglądarki, JSON dla API."""
        # Sprawdź czy klient chce JSON
        wants_json = request.headers.get('Accept', '').startswith('application/json') or request.args.get('format') == 'json'
        
        # Wczytaj najnowszy raport lub skan
        data = load_latest_report() or load_latest_scan()
        if not data:
            if wants_json:
                return json_response({'error': 'No data available'}, pretty=True), 404
            return render_template_string("""
                <html><head><title>Brak danych</title></head>
                <body style="font-family: sans-serif; padding: 40px; text-align: center;">
                    <h1>⚠️ Brak danych</h1>
                    <p>Nie znaleziono żadnych wyników skanowania.</p>
                    <p><a href="/">← Powrót</a></p>
                </body></html>
            """), 404
        
        devices = data.get('devices', [])
        
        # Zastosuj filtry
        filters = request.args.to_dict()
        filtered_devices = filter_devices(devices, filters)
        
        # Jeśli JSON - zwróć JSON
        if wants_json:
            detailed = filters.get('detailed', 'false').lower() == 'true'
            simplified = [simplify_device(d, detailed=detailed) for d in filtered_devices]
            return json_response({'devices': simplified}, pretty=True)
        
        # HTML - zwróć graficzny interfejs
        return render_devices_html(filtered_devices, filters)
    
    @app.route('/devices/<mac>', methods=['GET'])
    def get_device(mac: str):
        """Pobiera szczegóły urządzenia po MAC address."""
        data = load_latest_report() or load_latest_scan()
        if not data:
            pretty = request.args.get('pretty', 'false').lower() == 'true'
            return json_response({'error': 'No data available'}, pretty=pretty), 404
        
        devices = data.get('devices', [])
        device = next((d for d in devices if d.get('mac_address', '').upper() == mac.upper()), None)
        
        if not device:
            pretty = request.args.get('pretty', 'false').lower() == 'true'
            return json_response({'error': 'Device not found'}, pretty=pretty), 404
        
        pretty = request.args.get('pretty', 'false').lower() == 'true'
        return json_response(simplify_device(device, detailed=True), pretty=pretty)
    
    @app.route('/report', methods=['GET'])
    def get_report():
        """Pobiera najnowszy raport - HTML dla przeglądarki."""
        wants_json = request.headers.get('Accept', '').startswith('application/json') or request.args.get('format') == 'json'
        
        report = load_latest_report()
        if not report:
            if wants_json:
                return json_response({'error': 'No report available'}, pretty=True), 404
            return render_template_string("""
                <html><head><title>Brak raportu</title></head>
                <body style="font-family: sans-serif; padding: 40px; text-align: center;">
                    <h1>⚠️ Brak raportu</h1>
                    <p>Nie znaleziono żadnego raportu. Uruchom skanowanie najpierw.</p>
                    <p><a href="/">← Powrót</a></p>
                </body></html>
            """), 404
        
        if wants_json:
            return json_response(report, pretty=True)
        
        # HTML - przekieruj do dashboard
        from flask import redirect
        return redirect('/dashboard')
    
    @app.route('/scan', methods=['GET'])
    def get_scan():
        """Pobiera najnowszy skan - HTML dla przeglądarki."""
        wants_json = request.headers.get('Accept', '').startswith('application/json') or request.args.get('format') == 'json'
        
        scan = load_latest_scan()
        if not scan:
            if wants_json:
                return json_response({'error': 'No scan available'}, pretty=True), 404
            return render_template_string("""
                <html><head><title>Brak skanu</title></head>
                <body style="font-family: sans-serif; padding: 40px; text-align: center;">
                    <h1>⚠️ Brak skanu</h1>
                    <p>Nie znaleziono żadnego skanu. Uruchom skanowanie najpierw.</p>
                    <p><a href="/">← Powrót</a></p>
                </body></html>
            """), 404
        
        if wants_json:
            return json_response(scan, pretty=True)
        
        # HTML - przekieruj do dashboard
        from flask import redirect
        return redirect('/dashboard')
    
    @app.route('/dashboard', methods=['GET'])
    def dashboard():
        """Pełny graficzny dashboard z raportem."""
        data = load_latest_report() or load_latest_scan()
        if not data:
            return render_template_string("""
                <html><head><title>Brak danych</title></head>
                <body style="font-family: sans-serif; padding: 40px; text-align: center;">
                    <h1>⚠️ Brak danych</h1>
                    <p>Nie znaleziono żadnych wyników skanowania.</p>
                    <p>Uruchom: <code>python3 src/scanner.py</code></p>
                    <p><a href="/">← Powrót</a></p>
                </body></html>
            """), 404
        
        devices = data.get('devices', [])
        summary = data.get('summary', {})
        
        return render_dashboard_html(devices, summary, data)
    
    @app.route('/stats', methods=['GET'])
    def get_stats():
        """Pobiera statystyki - HTML dla przeglądarki."""
        wants_json = request.headers.get('Accept', '').startswith('application/json') or request.args.get('format') == 'json'
        
        data = load_latest_report() or load_latest_scan()
        if not data:
            if wants_json:
                return jsonify({'error': 'No data available'}), 404
            return render_template_string("""
                <html><head><title>Brak danych</title></head>
                <body style="font-family: sans-serif; padding: 40px; text-align: center;">
                    <h1>⚠️ Brak danych</h1>
                    <p><a href="/">← Powrót</a></p>
                </body></html>
            """), 404
        
        devices = data.get('devices', [])
        
        # Statystyki
        total = len(devices)
        by_protocol = {}
        by_encryption = {'with': 0, 'without': 0}
        by_score = {'high_risk': 0, 'medium_risk': 0, 'low_risk': 0}
        encryption_strength = {'strong': 0, 'moderate': 0, 'weak': 0, 'none': 0}
        
        for device in devices:
            # Po protokole
            protocol = device.get('protocol', 'unknown')
            by_protocol[protocol] = by_protocol.get(protocol, 0) + 1
            
            # Po szyfrowaniu
            if device.get('has_encryption', False):
                by_encryption['with'] += 1
            else:
                by_encryption['without'] += 1
            
            # Po security score
            score = device.get('security_score', 0)
            if score < 50:
                by_score['high_risk'] += 1
            elif score < 80:
                by_score['medium_risk'] += 1
            else:
                by_score['low_risk'] += 1
            
            # Po sile szyfrowania
            enc_analysis = device.get('metadata', {}).get('encryption_analysis', {})
            if enc_analysis:
                strength = enc_analysis.get('strength', 'unknown')
                if strength in encryption_strength:
                    encryption_strength[strength] += 1
        
        if wants_json:
            return json_response({
                'total_devices': total,
                'by_protocol': by_protocol,
                'by_encryption': by_encryption,
                'by_risk': by_score,
                'encryption_strength': encryption_strength
            }, pretty=True)
        
        # HTML - zwróć graficzny interfejs
        return render_stats_html(total, by_protocol, by_encryption, by_score, encryption_strength)


def main():
    """Uruchamia serwer API."""
    if not FLASK_AVAILABLE:
        console.print("[red]❌ Flask nie jest zainstalowany![/red]")
        console.print("[yellow]   Zainstaluj: pip install flask[/yellow]")
        sys.exit(1)
    
    # Parsuj argumenty
    port = 5000
    if len(sys.argv) > 1:
        if '--port' in sys.argv:
            idx = sys.argv.index('--port')
            if idx + 1 < len(sys.argv):
                try:
                    port = int(sys.argv[idx + 1])
                except ValueError:
                    console.print("[red]❌ Nieprawidłowy port[/red]")
                    sys.exit(1)
        elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
            console.print("[cyan]Użycie:[/cyan]")
            console.print("  python src/api_server.py              # Port 5000")
            console.print("  python src/api_server.py --port 8080   # Port 8080")
            sys.exit(0)
    
    console.print(Panel.fit(
        "[bold cyan]🌐 Medical Device Scanner API Server[/bold cyan]\n"
        f"[dim]Running on http://localhost:{port}[/dim]",
        style="cyan"
    ))
    console.print()
    console.print("[green]✅ API Server started![/green]")
    console.print(f"[dim]Endpoints:[/dim]")
    console.print(f"  [cyan]GET[/cyan] http://localhost:{port}/")
    console.print(f"  [cyan]GET[/cyan] http://localhost:{port}/devices")
    console.print(f"  [cyan]GET[/cyan] http://localhost:{port}/devices/<mac>")
    console.print(f"  [cyan]GET[/cyan] http://localhost:{port}/report")
    console.print(f"  [cyan]GET[/cyan] http://localhost:{port}/scan")
    console.print(f"  [cyan]GET[/cyan] http://localhost:{port}/stats")
    console.print()
    console.print("[yellow]Press Ctrl+C to stop[/yellow]")
    console.print()
    
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == "__main__":
    main()
