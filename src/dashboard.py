#!/usr/bin/env python3
"""
Dashboard webowy do wizualizacji i analizy urządzeń medycznych.

Używa Streamlit do szybkiego stworzenia interaktywnego dashboardu.
Dashboard pokazuje:
- Statystyki skanowania
- Wykresy bezpieczeństwa
- Wykryte anomalie (ML)
- Lista urządzeń z filtrowaniem
- Eksport danych

UŻYCIE:
    streamlit run src/dashboard.py
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import List, Dict, Optional

# Dodaj ścieżkę do src
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Import modułów projektu
try:
    from device import Device
    from scanner import MedicalDeviceScanner
    from anomaly_detector import AnomalyDetector
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    print(f"Błąd importu modułów: {e}")


def load_latest_scan() -> Optional[Dict]:
    """Wczytuje najnowszy skan."""
    scans_dir = Path(__file__).parent.parent / "reports"
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
    reports_dir = Path(__file__).parent.parent / "reports"
    report_files = sorted(list(reports_dir.glob("report_*.json")))
    if not report_files:
        return None
    
    latest_file = report_files[-1]
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def devices_to_dataframe(devices: List[Dict]) -> pd.DataFrame:
    """Konwertuje listę urządzeń na DataFrame."""
    if not PANDAS_AVAILABLE:
        return None
    
    data = []
    for device in devices:
        row = {
            'Nazwa': device.get('name', 'Unknown'),
            'MAC Address': device.get('mac_address', ''),
            'Typ': device.get('device_type', 'unknown'),
            'Protokół': device.get('protocol', ''),
            'Security Score': device.get('security_score', 0),
            'Szyfrowanie': 'Tak' if device.get('has_encryption', False) else 'Nie',
            'Parowanie': 'Tak' if device.get('requires_pairing', False) else 'Nie',
            'Liczba Podatności': len(device.get('vulnerabilities', [])),
            'Producent': device.get('manufacturer', 'N/A'),
            'Model': device.get('model', 'N/A'),
        }
        data.append(row)
    
    return pd.DataFrame(data)


def main():
    """Główna funkcja dashboardu."""
    if not STREAMLIT_AVAILABLE:
        st.error("❌ Streamlit nie jest zainstalowany!")
        st.code("pip install streamlit")
        return
    
    if not MODULES_AVAILABLE:
        st.error("❌ Nie można zaimportować modułów projektu!")
        return
    
    # Konfiguracja strony
    st.set_page_config(
        page_title="Medical Device Security Scanner",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Nagłówek
    st.title("🏥 Medical Device Security Scanner")
    st.markdown("**Dashboard do analizy bezpieczeństwa urządzeń medycznych IoT**")
    
    # Sidebar
    st.sidebar.title("⚙️ Opcje")
    
    # Wybór źródła danych
    data_source = st.sidebar.radio(
        "Źródło danych:",
        ["Najnowszy skan", "Najnowszy raport", "Nowe skanowanie"]
    )
    
    # Wczytaj dane
    devices_data = []
    scan_info = {}
    
    if data_source == "Najnowszy skan":
        scan_data = load_latest_scan()
        if scan_data:
            devices_data = scan_data.get('devices', [])
            scan_info = {
                'timestamp': scan_data.get('scan_timestamp', ''),
                'total': scan_data.get('total_devices', 0),
                'protocols': scan_data.get('protocols_scanned', [])
            }
        else:
            st.warning("⚠️ Brak dostępnych skanów. Uruchom skaner najpierw.")
            st.code("python src/scanner.py")
            return
    
    elif data_source == "Najnowszy raport":
        report_data = load_latest_report()
        if report_data:
            devices_data = report_data.get('devices', [])
            scan_info = {
                'timestamp': report_data.get('report_timestamp', ''),
                'total': report_data.get('summary', {}).get('total_devices', 0),
                'protocols': []
            }
        else:
            st.warning("⚠️ Brak dostępnych raportów. Uruchom skaner najpierw.")
            st.code("python src/scanner.py")
            return
    
    else:  # Nowe skanowanie
        st.info("💡 Aby wykonać nowe skanowanie, użyj skanera z linii poleceń:")
        st.code("python src/scanner.py")
        st.info("Następnie odśwież tę stronę i wybierz 'Najnowszy skan'.")
        return
    
    if not devices_data:
        st.error("❌ Brak danych do wyświetlenia!")
        return
    
    # Informacje o skanie
    if scan_info.get('timestamp'):
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**📅 Data skanu:**")
        st.sidebar.text(scan_info['timestamp'][:19])
        st.sidebar.markdown(f"**📊 Urządzeń:** {scan_info['total']}")
        if scan_info.get('protocols'):
            st.sidebar.markdown(f"**📡 Protokoły:** {', '.join(scan_info['protocols'])}")
    
    # Statystyki ogólne
    st.header("📊 Statystyki")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_devices = len(devices_data)
    high_risk = len([d for d in devices_data if d.get('security_score', 100) < 50])
    medium_risk = len([d for d in devices_data if 50 <= d.get('security_score', 100) < 80])
    low_risk = len([d for d in devices_data if d.get('security_score', 100) >= 80])
    avg_score = sum(d.get('security_score', 0) for d in devices_data) / total_devices if total_devices > 0 else 0
    
    with col1:
        st.metric("Total Urządzeń", total_devices)
    with col2:
        st.metric("🔴 Wysokie Ryzyko", high_risk)
    with col3:
        st.metric("🟡 Średnie Ryzyko", medium_risk)
    with col4:
        st.metric("🟢 Niskie Ryzyko", low_risk)
    
    st.metric("📈 Średni Security Score", f"{avg_score:.1f}/100")
    
    # Wykresy
    if PLOTLY_AVAILABLE and PANDAS_AVAILABLE:
        st.header("📈 Wizualizacje")
        
        # Przygotuj dane
        df = devices_to_dataframe(devices_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Wykres Security Score
            fig_score = px.histogram(
                df,
                x='Security Score',
                nbins=20,
                title='Rozkład Security Score',
                labels={'Security Score': 'Security Score', 'count': 'Liczba urządzeń'},
                color_discrete_sequence=['#667eea']
            )
            fig_score.update_layout(showlegend=False)
            st.plotly_chart(fig_score, use_container_width=True)
        
        with col2:
            # Wykres podatności
            fig_vuln = px.bar(
                df.groupby('Liczba Podatności').size().reset_index(name='Liczba'),
                x='Liczba Podatności',
                y='Liczba',
                title='Rozkład Podatności',
                labels={'Liczba Podatności': 'Liczba podatności', 'Liczba': 'Liczba urządzeń'},
                color_discrete_sequence=['#f093fb']
            )
            st.plotly_chart(fig_vuln, use_container_width=True)
        
        # Wykres protokołów
        col1, col2 = st.columns(2)
        
        with col1:
            protocol_counts = df['Protokół'].value_counts()
            fig_protocol = px.pie(
                values=protocol_counts.values,
                names=protocol_counts.index,
                title='Rozkład Protokołów',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_protocol, use_container_width=True)
        
        with col2:
            # Wykres szyfrowania
            encryption_counts = df['Szyfrowanie'].value_counts()
            fig_enc = px.pie(
                values=encryption_counts.values,
                names=encryption_counts.index,
                title='Rozkład Szyfrowania',
                color_discrete_map={'Tak': '#4caf50', 'Nie': '#f44336'}
            )
            st.plotly_chart(fig_enc, use_container_width=True)
        
        # Wykres Security Score vs Podatności
        fig_scatter = px.scatter(
            df,
            x='Security Score',
            y='Liczba Podatności',
            color='Protokół',
            size='Security Score',
            hover_data=['Nazwa', 'MAC Address'],
            title='Security Score vs Liczba Podatności',
            labels={'Security Score': 'Security Score', 'Liczba Podatności': 'Liczba Podatności'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Sekcja Podatności
    st.header("🔒 Podatności - Przegląd Wszystkich Urządzeń")
    
    # Zbierz wszystkie podatności ze wszystkich urządzeń
    all_vulnerabilities = []
    vulnerability_to_devices = {}  # Mapowanie podatność -> lista urządzeń
    
    for device in devices_data:
        device_name = device.get('name', 'Unknown')
        device_mac = device.get('mac_address', 'N/A')
        vulnerabilities = device.get('vulnerabilities', [])
        
        for vuln in vulnerabilities:
            # Obsługa różnych formatów podatności:
            # 1. String (prosty tekst)
            # 2. Dict (słownik z szczegółami)
            if isinstance(vuln, str):
                # Prosty string - konwertuj na format słownika
                vuln_title = vuln
                vuln_severity = 'Unknown'
                vuln_cve = 'N/A'
                vuln_description = vuln
            elif isinstance(vuln, dict):
                # Słownik - wyciągnij dane
                vuln_title = vuln.get('title', vuln.get('name', 'Unknown Vulnerability'))
                vuln_severity = vuln.get('severity', vuln.get('level', 'Unknown'))
                vuln_cve = vuln.get('cve', vuln.get('cve_id', 'N/A'))
                vuln_description = vuln.get('description', vuln.get('details', ''))
            else:
                # Fallback - konwertuj na string
                vuln_title = str(vuln)
                vuln_severity = 'Unknown'
                vuln_cve = 'N/A'
                vuln_description = str(vuln)
            
            # Klucz do grupowania (tytuł + severity)
            vuln_key = f"{vuln_title}|{vuln_severity}"
            
            if vuln_key not in vulnerability_to_devices:
                vulnerability_to_devices[vuln_key] = {
                    'title': vuln_title,
                    'severity': vuln_severity,
                    'cve': vuln_cve,
                    'description': vuln_description,
                    'devices': []
                }
            
            vulnerability_to_devices[vuln_key]['devices'].append({
                'name': device_name,
                'mac': device_mac,
                'security_score': device.get('security_score', 0)
            })
    
    total_unique_vulns = len(vulnerability_to_devices)
    total_vuln_instances = sum(len(v['devices']) for v in vulnerability_to_devices.values())
    
    # Statystyki podatności
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔴 Unikalne Podatności", total_unique_vulns)
    with col2:
        st.metric("📊 Wystąpienia", total_vuln_instances)
    with col3:
        critical_count = len([v for v in vulnerability_to_devices.values() if v['severity'].lower() in ['critical', 'krytyczna', 'critical']])
        st.metric("⚠️ Krytyczne", critical_count)
    with col4:
        high_count = len([v for v in vulnerability_to_devices.values() if v['severity'].lower() in ['high', 'wysoka', 'high']])
        st.metric("🔴 Wysokie", high_count)
    
    if total_unique_vulns > 0:
        # Rozkład podatności według severity
        if PLOTLY_AVAILABLE:
            severity_counts = {}
            for vuln_data in vulnerability_to_devices.values():
                severity = vuln_data['severity']
                if severity not in severity_counts:
                    severity_counts[severity] = 0
                severity_counts[severity] += len(vuln_data['devices'])
            
            if severity_counts:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Wykres podatności według severity
                    fig_severity = px.bar(
                        x=list(severity_counts.keys()),
                        y=list(severity_counts.values()),
                        title='Podatności według Poziomu Ryzyka',
                        labels={'x': 'Poziom Ryzyka', 'y': 'Liczba Wystąpień'},
                        color=list(severity_counts.keys()),
                        color_discrete_map={
                            'Critical': '#d32f2f',
                            'Krytyczna': '#d32f2f',
                            'High': '#f57c00',
                            'Wysoka': '#f57c00',
                            'Medium': '#fbc02d',
                            'Średnia': '#fbc02d',
                            'Low': '#388e3c',
                            'Niska': '#388e3c'
                        }
                    )
                    st.plotly_chart(fig_severity, use_container_width=True)
                
                with col2:
                    # Top 10 najczęstszych podatności
                    sorted_vulns = sorted(
                        vulnerability_to_devices.items(),
                        key=lambda x: len(x[1]['devices']),
                        reverse=True
                    )[:10]
                    
                    top_vulns_data = {
                        'Podatność': [v[1]['title'][:50] + '...' if len(v[1]['title']) > 50 else v[1]['title'] for v in sorted_vulns],
                        'Wystąpienia': [len(v[1]['devices']) for v in sorted_vulns],
                        'Severity': [v[1]['severity'] for v in sorted_vulns]
                    }
                    
                    fig_top = px.bar(
                        x=top_vulns_data['Wystąpienia'],
                        y=top_vulns_data['Podatność'],
                        orientation='h',
                        title='Top 10 Najczęstszych Podatności',
                        labels={'x': 'Liczba Wystąpień', 'y': 'Podatność'},
                        color=top_vulns_data['Severity'],
                        color_discrete_map={
                            'Critical': '#d32f2f',
                            'Krytyczna': '#d32f2f',
                            'High': '#f57c00',
                            'Wysoka': '#f57c00',
                            'Medium': '#fbc02d',
                            'Średnia': '#fbc02d',
                            'Low': '#388e3c',
                            'Niska': '#388e3c'
                        }
                    )
                    fig_top.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig_top, use_container_width=True)
        
        # Lista wszystkich podatności
        st.subheader("📋 Lista Wszystkich Podatności")
        
        # Sortuj podatności według severity i liczby wystąpień
        sorted_vulnerabilities = sorted(
            vulnerability_to_devices.items(),
            key=lambda x: (
                {'Critical': 0, 'Krytyczna': 0, 'High': 1, 'Wysoka': 1, 'Medium': 2, 'Średnia': 2, 'Low': 3, 'Niska': 3}.get(x[1]['severity'], 4),
                -len(x[1]['devices'])  # Więcej wystąpień = wyżej
            )
        )
        
        # Filtry
        col1, col2 = st.columns(2)
        with col1:
            filter_severity = st.selectbox(
                "🔍 Filtruj według Severity:",
                ["Wszystkie"] + list(set(v[1]['severity'] for v in sorted_vulnerabilities))
            )
        with col2:
            search_vuln = st.text_input("🔍 Szukaj podatności:", "")
        
        # Filtruj
        filtered_vulns = sorted_vulnerabilities
        if filter_severity != "Wszystkie":
            filtered_vulns = [v for v in filtered_vulns if v[1]['severity'] == filter_severity]
        if search_vuln:
            filtered_vulns = [
                v for v in filtered_vulns
                if search_vuln.lower() in v[1]['title'].lower() or
                   search_vuln.lower() in v[1]['description'].lower() or
                   search_vuln.lower() in v[1]['cve'].lower()
            ]
        
        st.write(f"**Znaleziono {len(filtered_vulns)} podatności**")
        
        # Wyświetl każdą podatność
        for vuln_key, vuln_data in filtered_vulns:
            severity_color = {
                'Critical': '🔴',
                'Krytyczna': '🔴',
                'High': '🟠',
                'Wysoka': '🟠',
                'Medium': '🟡',
                'Średnia': '🟡',
                'Low': '🟢',
                'Niska': '🟢'
            }.get(vuln_data['severity'], '⚪')
            
            with st.expander(
                f"{severity_color} **{vuln_data['title']}** - {vuln_data['severity']} "
                f"({len(vuln_data['devices'])} urządzeń)",
                expanded=False
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**CVE:** {vuln_data['cve']}")
                    if vuln_data['description']:
                        st.write(f"**Opis:** {vuln_data['description']}")
                
                with col2:
                    st.write(f"**Wystąpienia:** {len(vuln_data['devices'])}")
                    st.write(f"**Severity:** {vuln_data['severity']}")
                
                # Lista urządzeń z tą podatnością
                st.write("**Urządzenia z tą podatnością:**")
                devices_list = []
                for device_info in vuln_data['devices']:
                    devices_list.append({
                        'Nazwa': device_info['name'],
                        'MAC Address': device_info['mac'],
                        'Security Score': device_info['security_score']
                    })
                
                if PANDAS_AVAILABLE and devices_list:
                    df_devices = pd.DataFrame(devices_list)
                    st.dataframe(df_devices, use_container_width=True, hide_index=True)
                else:
                    for device_info in vuln_data['devices']:
                        st.write(f"- {device_info['name']} ({device_info['mac']}) - Score: {device_info['security_score']}/100")
    else:
        st.success("✅ Brak wykrytych podatności na wszystkich urządzeniach!")
    
    # Wykrywanie anomalii (ML)
    st.header("🤖 Wykrywanie Anomalii (ML)")
    
    if st.checkbox("🔍 Uruchom wykrywanie anomalii"):
        try:
            # Konwertuj dane na obiekty Device (uproszczone)
            from device import Device, DeviceType, Protocol
            
            devices = []
            for d in devices_data:
                try:
                    device = Device(
                        mac_address=d.get('mac_address', ''),
                        name=d.get('name', 'Unknown'),
                        device_type=DeviceType.UNKNOWN,  # Uproszczenie
                        protocol=Protocol.BLE,  # Uproszczenie
                        has_encryption=d.get('has_encryption', False),
                        requires_pairing=d.get('requires_pairing', False),
                        security_score=d.get('security_score', 0),
                        vulnerabilities=d.get('vulnerabilities', []),
                        metadata=d.get('metadata', {})
                    )
                    devices.append(device)
                except Exception:
                    continue
            
            if len(devices) >= 10:
                detector = AnomalyDetector(contamination=0.1)
                
                # Trenuj model
                with st.spinner("🔄 Trenowanie modelu ML..."):
                    train_result = detector.train(devices)
                
                if train_result.get('trained'):
                    st.success(f"✅ Model wytrenowany na {train_result['devices_count']} urządzeniach!")
                    
                    # Wykryj anomalie
                    with st.spinner("🔍 Wykrywanie anomalii..."):
                        anomaly_results = detector.detect_anomalies(devices)
                    
                    # Statystyki
                    stats = detector.get_anomaly_statistics(anomaly_results)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Anomalie", stats['anomalies_count'])
                    with col2:
                        st.metric("Procent Anomalii", f"{stats['anomalies_percentage']:.1f}%")
                    with col3:
                        st.metric("Średni Score Anomalii", f"{stats['avg_anomaly_score']:.2f}")
                    
                    # Lista anomalii
                    anomalies = [r for r in anomaly_results if r['is_anomaly']]
                    if anomalies:
                        st.subheader("⚠️ Wykryte Anomalie")
                        for result in anomalies:
                            device = result['device']
                            with st.expander(f"🔴 {device.name} (Score: {device.security_score}/100)"):
                                st.write(f"**MAC:** {device.mac_address}")
                                st.write(f"**Anomaly Score:** {result['anomaly_score']:.2f}")
                                st.write(f"**Metoda:** {result['method']}")
                                st.write(f"**Powód:** {result['reason']}")
                                if device.vulnerabilities:
                                    st.write("**Podatności:**")
                                    for vuln in device.vulnerabilities[:5]:
                                        st.write(f"- {vuln}")
                    else:
                        st.success("✅ Nie wykryto anomalii!")
            else:
                st.warning(f"⚠️ Za mało urządzeń do wykrywania anomalii (minimum 10, masz {len(devices)})")
        except Exception as e:
            st.error(f"❌ Błąd wykrywania anomalii: {e}")
    
    # Lista urządzeń
    st.header("📱 Lista Urządzeń")
    
    # Filtry
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_protocol = st.selectbox(
            "Filtruj po protokole:",
            ["Wszystkie"] + list(set(d.get('protocol', '') for d in devices_data))
        )
    with col2:
        filter_risk = st.selectbox(
            "Filtruj po ryzyku:",
            ["Wszystkie", "Wysokie (<50)", "Średnie (50-79)", "Niskie (≥80)"]
        )
    with col3:
        filter_encryption = st.selectbox(
            "Filtruj po szyfrowaniu:",
            ["Wszystkie", "Z szyfrowaniem", "Bez szyfrowania"]
        )
    
    # Filtruj urządzenia
    filtered_devices = devices_data
    if filter_protocol != "Wszystkie":
        filtered_devices = [d for d in filtered_devices if d.get('protocol') == filter_protocol]
    if filter_risk != "Wszystkie":
        if filter_risk == "Wysokie (<50)":
            filtered_devices = [d for d in filtered_devices if d.get('security_score', 100) < 50]
        elif filter_risk == "Średnie (50-79)":
            filtered_devices = [d for d in filtered_devices if 50 <= d.get('security_score', 100) < 80]
        else:
            filtered_devices = [d for d in filtered_devices if d.get('security_score', 100) >= 80]
    if filter_encryption != "Wszystkie":
        has_enc = filter_encryption == "Z szyfrowaniem"
        filtered_devices = [d for d in filtered_devices if d.get('has_encryption', False) == has_enc]
    
    st.write(f"**Znaleziono {len(filtered_devices)} urządzeń**")
    
    # Tabela urządzeń
    if PANDAS_AVAILABLE:
        df_filtered = devices_to_dataframe(filtered_devices)
        st.dataframe(df_filtered, use_container_width=True, height=400)
        
        # Eksport
        st.subheader("💾 Eksport Danych")
        csv = df_filtered.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Pobierz CSV",
            data=csv,
            file_name=f"devices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        # Prosta lista jeśli pandas nie jest dostępny
        for device in filtered_devices[:50]:  # Maksymalnie 50
            with st.expander(f"{device.get('name', 'Unknown')} - Score: {device.get('security_score', 0)}/100"):
                st.json(device)


if __name__ == "__main__":
    if not STREAMLIT_AVAILABLE:
        print("❌ Streamlit nie jest zainstalowany!")
        print("Zainstaluj: pip install streamlit")
        sys.exit(1)
    
    main()
