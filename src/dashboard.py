#!/usr/bin/env python3
"""
Web dashboard for visualizing and analyzing medical devices.

Uses Streamlit. Shows: scan stats, security charts, ML anomalies, device list with filtering, data export.
Usage: streamlit run src/dashboard.py
"""

import sys
from pathlib import Path
import json
from datetime import datetime
from typing import List, Dict, Optional

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

try:
    from device import Device
    from scanner import MedicalDeviceScanner
    from anomaly_detector import AnomalyDetector
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    print(f"Module import error: {e}")


def load_latest_scan() -> Optional[Dict]:
    """Load latest scan."""
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
    """Load latest report."""
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
    """Convert device list to DataFrame."""
    if not PANDAS_AVAILABLE:
        return None
    data = []
    for device in devices:
        row = {
            'Name': device.get('name', 'Unknown'),
            'MAC Address': device.get('mac_address', ''),
            'Type': device.get('device_type', 'unknown'),
            'Protocol': device.get('protocol', ''),
            'Security Score': device.get('security_score', 0),
            'Encryption': 'Yes' if device.get('has_encryption', False) else 'No',
            'Pairing': 'Yes' if device.get('requires_pairing', False) else 'No',
            'Vulnerability Count': len(device.get('vulnerabilities', [])),
            'Manufacturer': device.get('manufacturer', 'N/A'),
            'Model': device.get('model', 'N/A'),
        }
        data.append(row)
    return pd.DataFrame(data)


def main():
    """Main dashboard function."""
    if not STREAMLIT_AVAILABLE:
        st.error("❌ Streamlit is not installed!")
        st.code("pip install streamlit")
        return
    if not MODULES_AVAILABLE:
        st.error("❌ Cannot import project modules!")
        return
    st.set_page_config(
        page_title="Medical Device Security Scanner",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🏥 Medical Device Security Scanner")
    st.markdown("**Dashboard for IoT medical device security analysis**")
    st.sidebar.title("⚙️ Options")
    data_source = st.sidebar.radio(
        "Data source:",
        ["Latest scan", "Latest report", "New scan"]
    )
    
    # Wczytaj dane
    devices_data = []
    scan_info = {}
    
    if data_source == "Latest scan":
        scan_data = load_latest_scan()
        if scan_data:
            devices_data = scan_data.get('devices', [])
            scan_info = {
                'timestamp': scan_data.get('scan_timestamp', ''),
                'total': scan_data.get('total_devices', 0),
                'protocols': scan_data.get('protocols_scanned', [])
            }
        else:
            st.warning("⚠️ No scans available. Run the scanner first.")
            st.code("python src/scanner.py")
            return
    
    elif data_source == "Latest report":
        report_data = load_latest_report()
        if report_data:
            devices_data = report_data.get('devices', [])
            scan_info = {
                'timestamp': report_data.get('report_timestamp', ''),
                'total': report_data.get('summary', {}).get('total_devices', 0),
                'protocols': []
            }
        else:
            st.warning("⚠️ No reports available. Run the scanner first.")
            st.code("python src/scanner.py")
            return
    
    else:  # New scan
        st.info("💡 To run a new scan, use the scanner from the command line:")
        st.code("python src/scanner.py")
        st.info("Then refresh this page and select 'Latest scan'.")
        return
    if not devices_data:
        st.error("❌ No data to display!")
        return
    
    if scan_info.get('timestamp'):
        st.sidebar.markdown("---")
        st.sidebar.markdown("**📅 Scan date:**")
        st.sidebar.text(scan_info['timestamp'][:19])
        st.sidebar.markdown(f"**📊 Devices:** {scan_info['total']}")
        if scan_info.get('protocols'):
            st.sidebar.markdown(f"**📡 Protocols:** {', '.join(scan_info['protocols'])}")
    st.header("📊 Statistics")
    col1, col2, col3, col4 = st.columns(4)
    total_devices = len(devices_data)
    high_risk = len([d for d in devices_data if d.get('security_score', 100) < 50])
    medium_risk = len([d for d in devices_data if 50 <= d.get('security_score', 100) < 80])
    low_risk = len([d for d in devices_data if d.get('security_score', 100) >= 80])
    avg_score = sum(d.get('security_score', 0) for d in devices_data) / total_devices if total_devices > 0 else 0
    with col1:
        st.metric("Total Devices", total_devices)
    with col2:
        st.metric("🔴 High Risk", high_risk)
    with col3:
        st.metric("🟡 Medium Risk", medium_risk)
    with col4:
        st.metric("🟢 Low Risk", low_risk)
    st.metric("📈 Average Security Score", f"{avg_score:.1f}/100")
    if PLOTLY_AVAILABLE and PANDAS_AVAILABLE:
        st.header("📈 Visualizations")
        df = devices_to_dataframe(devices_data)
        col1, col2 = st.columns(2)
        with col1:
            fig_score = px.histogram(
                df,
                x='Security Score',
                nbins=20,
                title='Security Score Distribution',
                labels={'Security Score': 'Security Score', 'count': 'Device count'},
                color_discrete_sequence=['#667eea']
            )
            fig_score.update_layout(showlegend=False)
            st.plotly_chart(fig_score, use_container_width=True)
        with col2:
            fig_vuln = px.bar(
                df.groupby('Vulnerability Count').size().reset_index(name='Count'),
                x='Vulnerability Count',
                y='Count',
                title='Vulnerability Distribution',
                labels={'Vulnerability Count': 'Vulnerability count', 'Count': 'Device count'},
                color_discrete_sequence=['#f093fb']
            )
            st.plotly_chart(fig_vuln, use_container_width=True)
        col1, col2 = st.columns(2)
        with col1:
            protocol_counts = df['Protocol'].value_counts()
            fig_protocol = px.pie(
                values=protocol_counts.values,
                names=protocol_counts.index,
                title='Protocol Distribution',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_protocol, use_container_width=True)
        with col2:
            encryption_counts = df['Encryption'].value_counts()
            fig_enc = px.pie(
                values=encryption_counts.values,
                names=encryption_counts.index,
                title='Encryption Distribution',
                color_discrete_map={'Yes': '#4caf50', 'No': '#f44336'}
            )
            st.plotly_chart(fig_enc, use_container_width=True)
        fig_scatter = px.scatter(
            df,
            x='Security Score',
            y='Vulnerability Count',
            color='Protocol',
            size='Security Score',
            hover_data=['Name', 'MAC Address'],
            title='Security Score vs Vulnerability Count',
            labels={'Security Score': 'Security Score', 'Vulnerability Count': 'Vulnerability Count'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.header("🔒 Vulnerabilities – Overview of All Devices")
    all_vulnerabilities = []
    vulnerability_to_devices = {}
    for device in devices_data:
        device_name = device.get('name', 'Unknown')
        device_mac = device.get('mac_address', 'N/A')
        vulnerabilities = device.get('vulnerabilities', [])
        for vuln in vulnerabilities:
            if isinstance(vuln, str):
                vuln_title = vuln
                vuln_severity = 'Unknown'
                vuln_cve = 'N/A'
                vuln_description = vuln
            elif isinstance(vuln, dict):
                vuln_title = vuln.get('title', vuln.get('name', 'Unknown Vulnerability'))
                vuln_severity = vuln.get('severity', vuln.get('level', 'Unknown'))
                vuln_cve = vuln.get('cve', vuln.get('cve_id', 'N/A'))
                vuln_description = vuln.get('description', vuln.get('details', ''))
            else:
                vuln_title = str(vuln)
                vuln_severity = 'Unknown'
                vuln_cve = 'N/A'
                vuln_description = str(vuln)
            
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
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔴 Unique Vulnerabilities", total_unique_vulns)
    with col2:
        st.metric("📊 Occurrences", total_vuln_instances)
    with col3:
        critical_count = len([v for v in vulnerability_to_devices.values() if v['severity'].lower() in ['critical', 'krytyczna']])
        st.metric("⚠️ Critical", critical_count)
    with col4:
        high_count = len([v for v in vulnerability_to_devices.values() if v['severity'].lower() in ['high', 'wysoka']])
        st.metric("🔴 High", high_count)
    if total_unique_vulns > 0:
        if PLOTLY_AVAILABLE:
            severity_counts = {}
            for vuln_data in vulnerability_to_devices.values():
                s = vuln_data['severity']
                severity_counts[s] = severity_counts.get(s, 0) + len(vuln_data['devices'])
            if severity_counts:
                col1, col2 = st.columns(2)
                with col1:
                    fig_severity = px.bar(
                        x=list(severity_counts.keys()),
                        y=list(severity_counts.values()),
                        title='Vulnerabilities by Risk Level',
                        labels={'x': 'Risk Level', 'y': 'Occurrence count'},
                        color=list(severity_counts.keys()),
                        color_discrete_map={
                            'Critical': '#d32f2f',
                            'High': '#f57c00',
                            'Medium': '#fbc02d',
                            'Low': '#388e3c'
                        }
                    )
                    st.plotly_chart(fig_severity, use_container_width=True)
                with col2:
                    sorted_vulns = sorted(
                        vulnerability_to_devices.items(),
                        key=lambda x: len(x[1]['devices']),
                        reverse=True
                    )[:10]
                    _sev_color = {'Critical': '#d32f2f', 'High': '#f57c00', 'Medium': '#fbc02d', 'Low': '#388e3c'}
                    top_vulns_data = {
                        'Vulnerability': [v[1]['title'][:50] + '...' if len(v[1]['title']) > 50 else v[1]['title'] for v in sorted_vulns],
                        'Occurrences': [len(v[1]['devices']) for v in sorted_vulns],
                        'Severity': [v[1]['severity'] for v in sorted_vulns]
                    }
                    fig_top = px.bar(
                        x=top_vulns_data['Occurrences'],
                        y=top_vulns_data['Vulnerability'],
                        orientation='h',
                        title='Top 10 Most Common Vulnerabilities',
                        labels={'x': 'Occurrence count', 'y': 'Vulnerability'},
                        color=top_vulns_data['Severity'],
                        color_discrete_map={**_sev_color}
                    )
                    fig_top.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig_top, use_container_width=True)
        
        st.subheader("📋 All Vulnerabilities List")
        _severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        def _sev_key(v):
            return (_severity_order.get(v[1]['severity'], 4), -len(v[1]['devices']))
        sorted_vulnerabilities = sorted(vulnerability_to_devices.items(), key=_sev_key)
        col1, col2 = st.columns(2)
        with col1:
            sev_options = ["All"] + sorted(set(v[1]['severity'] for v in sorted_vulnerabilities))
            filter_severity = st.selectbox("🔍 Filter by Severity:", sev_options)
        with col2:
            search_vuln = st.text_input("🔍 Search vulnerabilities:", "")
        filtered_vulns = sorted_vulnerabilities
        if filter_severity != "All":
            filtered_vulns = [v for v in filtered_vulns if v[1]['severity'] == filter_severity]
        if search_vuln:
            filtered_vulns = [
                v for v in filtered_vulns
                if search_vuln.lower() in v[1]['title'].lower() or
                   search_vuln.lower() in v[1]['description'].lower() or
                   search_vuln.lower() in v[1]['cve'].lower()
            ]
        
        st.write(f"**Found {len(filtered_vulns)} vulnerabilities**")
        for vuln_key, vuln_data in filtered_vulns:
            severity_color = {'Critical': '🔴', 'High': '🟠', 'Medium': '🟡', 'Low': '🟢'}.get(vuln_data['severity'], '⚪')
            with st.expander(
                f"{severity_color} **{vuln_data['title']}** - {vuln_data['severity']} "
                f"({len(vuln_data['devices'])} devices)",
                expanded=False
            ):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**CVE:** {vuln_data['cve']}")
                    if vuln_data['description']:
                        st.write(f"**Description:** {vuln_data['description']}")
                with col2:
                    st.write(f"**Occurrences:** {len(vuln_data['devices'])}")
                    st.write(f"**Severity:** {vuln_data['severity']}")
                st.write("**Devices with this vulnerability:**")
                devices_list = []
                for device_info in vuln_data['devices']:
                    devices_list.append({
                        'Name': device_info['name'],
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
        st.success("✅ No vulnerabilities detected on any device!")
    st.header("🤖 Anomaly Detection (ML)")
    if st.checkbox("🔍 Run anomaly detection"):
        try:
            from device import Device, DeviceType, Protocol
            devices = []
            for d in devices_data:
                try:
                    device = Device(
                        mac_address=d.get('mac_address', ''),
                        name=d.get('name', 'Unknown'),
                        device_type=DeviceType.UNKNOWN,
                        protocol=Protocol.BLE,
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
                with st.spinner("🔄 Training ML model..."):
                    train_result = detector.train(devices)
                if train_result.get('trained'):
                    st.success(f"✅ Model trained on {train_result['devices_count']} devices!")
                    with st.spinner("🔍 Detecting anomalies..."):
                        anomaly_results = detector.detect_anomalies(devices)
                    stats = detector.get_anomaly_statistics(anomaly_results)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Anomalies", stats['anomalies_count'])
                    with col2:
                        st.metric("Anomaly %", f"{stats['anomalies_percentage']:.1f}%")
                    with col3:
                        st.metric("Avg Anomaly Score", f"{stats['avg_anomaly_score']:.2f}")
                    anomalies = [r for r in anomaly_results if r['is_anomaly']]
                    if anomalies:
                        st.subheader("⚠️ Detected Anomalies")
                        for result in anomalies:
                            device = result['device']
                            with st.expander(f"🔴 {device.name} (Score: {device.security_score}/100)"):
                                st.write(f"**MAC:** {device.mac_address}")
                                st.write(f"**Anomaly Score:** {result['anomaly_score']:.2f}")
                                st.write(f"**Method:** {result['method']}")
                                st.write(f"**Reason:** {result['reason']}")
                                if device.vulnerabilities:
                                    st.write("**Vulnerabilities:**")
                                    for vuln in device.vulnerabilities[:5]:
                                        st.write(f"- {vuln}")
                    else:
                        st.success("✅ No anomalies detected!")
            else:
                st.warning(f"⚠️ Not enough devices for anomaly detection (minimum 10, you have {len(devices)})")
        except Exception as e:
            st.error(f"❌ Anomaly detection error: {e}")
    st.header("📱 Device List")
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_protocol = st.selectbox(
            "Filter by protocol:",
            ["All"] + list(set(d.get('protocol', '') for d in devices_data))
        )
    with col2:
        filter_risk = st.selectbox(
            "Filter by risk:",
            ["All", "High (<50)", "Medium (50-79)", "Low (≥80)"]
        )
    with col3:
        filter_encryption = st.selectbox(
            "Filter by encryption:",
            ["All", "With encryption", "Without encryption"]
        )
    filtered_devices = devices_data
    if filter_protocol != "All":
        filtered_devices = [d for d in filtered_devices if d.get('protocol') == filter_protocol]
    if filter_risk != "All":
        if filter_risk == "High (<50)":
            filtered_devices = [d for d in filtered_devices if d.get('security_score', 100) < 50]
        elif filter_risk == "Medium (50-79)":
            filtered_devices = [d for d in filtered_devices if 50 <= d.get('security_score', 100) < 80]
        else:
            filtered_devices = [d for d in filtered_devices if d.get('security_score', 100) >= 80]
    if filter_encryption != "All":
        has_enc = filter_encryption == "With encryption"
        filtered_devices = [d for d in filtered_devices if d.get('has_encryption', False) == has_enc]
    st.write(f"**Found {len(filtered_devices)} devices**")
    if PANDAS_AVAILABLE:
        df_filtered = devices_to_dataframe(filtered_devices)
        st.dataframe(df_filtered, use_container_width=True, height=400)
        st.subheader("💾 Data Export")
        csv = df_filtered.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"devices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        for device in filtered_devices[:50]:
            with st.expander(f"{device.get('name', 'Unknown')} - Score: {device.get('security_score', 0)}/100"):
                st.json(device)


if __name__ == "__main__":
    if not STREAMLIT_AVAILABLE:
        print("❌ Streamlit is not installed!")
        print("Install: pip install streamlit")
        sys.exit(1)
    main()
