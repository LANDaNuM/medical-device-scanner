#!/usr/bin/env python3
"""
SQLite-backed scan history storage.

Provides: saving scan results, retrieving history, trend analysis (security score over time), new device detection.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from device import Device


@dataclass
class ScanHistory:
    """Single scan entry in history."""
    scan_id: int
    timestamp: datetime
    total_devices: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    avg_security_score: float
    devices: List[Dict]


class HistoryDB:
    """Manages scan history database."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize DB. db_path: path to DB file (default: project_root/history.db)."""
        if db_path is None:
            project_root = Path(__file__).parent.parent
            db_path = project_root / "history.db"
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_devices INTEGER NOT NULL,
                high_risk_count INTEGER NOT NULL,
                medium_risk_count INTEGER NOT NULL,
                low_risk_count INTEGER NOT NULL,
                avg_security_score REAL NOT NULL,
                protocols TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                mac_address TEXT NOT NULL,
                name TEXT,
                device_type TEXT,
                protocol TEXT,
                security_score INTEGER,
                has_encryption INTEGER,
                requires_pairing INTEGER,
                vulnerability_count INTEGER,
                device_data TEXT,
                FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_scan_timestamp ON scans(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_device_mac ON scan_devices(mac_address)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_device_scan ON scan_devices(scan_id)
        """)
        
        conn.commit()
        conn.close()
    
    def save_scan(self, devices: List[Device], protocols: List[str]) -> int:
        """Save scan results to DB. Returns saved scan ID."""
        timestamp = datetime.now().isoformat()
        total_devices = len(devices)
        high_risk = len([d for d in devices if d.security_score < 50])
        medium_risk = len([d for d in devices if 50 <= d.security_score < 80])
        low_risk = len([d for d in devices if d.security_score >= 80])
        avg_score = sum(d.security_score for d in devices) / total_devices if total_devices > 0 else 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scans (timestamp, total_devices, high_risk_count, medium_risk_count, 
                             low_risk_count, avg_security_score, protocols)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, total_devices, high_risk, medium_risk, low_risk, avg_score, json.dumps(protocols)))
        
        scan_id = cursor.lastrowid
        for device in devices:
            device_dict = device.to_dict()
            cursor.execute("""
                INSERT INTO scan_devices (scan_id, mac_address, name, device_type, protocol,
                                        security_score, has_encryption, requires_pairing,
                                        vulnerability_count, device_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scan_id,
                device.mac_address,
                device.name,
                device.device_type.value,
                device.protocol.value,
                device.security_score,
                1 if device.has_encryption else 0,
                1 if device.requires_pairing else 0,
                len(device.vulnerabilities),
                json.dumps(device_dict)
            ))
        
        conn.commit()
        conn.close()
        
        return scan_id
    
    def get_recent_scans(self, limit: int = 10) -> List[ScanHistory]:
        """Get most recent scans. limit: max number of scans. Returns list of ScanHistory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM scans
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        scans = []
        for row in cursor.fetchall():
            cursor.execute("""
                SELECT device_data FROM scan_devices
                WHERE scan_id = ?
            """, (row['id'],))
            
            devices = []
            for device_row in cursor.fetchall():
                devices.append(json.loads(device_row['device_data']))
            
            scans.append(ScanHistory(
                scan_id=row['id'],
                timestamp=datetime.fromisoformat(row['timestamp']),
                total_devices=row['total_devices'],
                high_risk_count=row['high_risk_count'],
                medium_risk_count=row['medium_risk_count'],
                low_risk_count=row['low_risk_count'],
                avg_security_score=row['avg_security_score'],
                devices=devices
            ))
        
        conn.close()
        return scans
    
    def get_device_history(self, mac_address: str, limit: int = 20) -> List[Dict]:
        """Get history for a device by MAC. limit: max entries. Returns list of history entries."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT sd.*, s.timestamp as scan_timestamp
            FROM scan_devices sd
            JOIN scans s ON sd.scan_id = s.id
            WHERE sd.mac_address = ?
            ORDER BY s.timestamp DESC
            LIMIT ?
        """, (mac_address, limit))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'timestamp': row['scan_timestamp'],
                'security_score': row['security_score'],
                'vulnerability_count': row['vulnerability_count'],
                'has_encryption': bool(row['has_encryption']),
                'device_data': json.loads(row['device_data'])
            })
        
        conn.close()
        return history
    
    def get_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get security trends for the last days. Returns dict with timestamps, avg_scores, risk counts, etc."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        from datetime import timedelta
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT timestamp, avg_security_score, high_risk_count, 
                   medium_risk_count, low_risk_count, total_devices
            FROM scans
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        """, (start_date,))
        
        trends = {
            'timestamps': [],
            'avg_scores': [],
            'high_risk': [],
            'medium_risk': [],
            'low_risk': [],
            'total_devices': []
        }
        
        for row in cursor.fetchall():
            trends['timestamps'].append(row['timestamp'])
            trends['avg_scores'].append(row['avg_security_score'])
            trends['high_risk'].append(row['high_risk_count'])
            trends['medium_risk'].append(row['medium_risk_count'])
            trends['low_risk'].append(row['low_risk_count'])
            trends['total_devices'].append(row['total_devices'])
        
        conn.close()
        return trends
    
    def detect_new_devices(self, current_devices: List[Device]) -> List[Device]:
        """Detect devices not seen before. Returns list of new devices."""
        if not current_devices:
            return []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT mac_address FROM scan_devices")
        known_macs = {row[0] for row in cursor.fetchall()}
        conn.close()
        new_devices = [d for d in current_devices if d.mac_address not in known_macs]
        
        return new_devices
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics from history. Returns dict with total_scans, unique_devices, last_scan, avg_security_score_30d."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM scans")
        total_scans = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(DISTINCT mac_address) as count FROM scan_devices")
        unique_devices = cursor.fetchone()['count']
        cursor.execute("SELECT MAX(timestamp) as last_scan FROM scans")
        last_scan = cursor.fetchone()['last_scan']
        from datetime import timedelta
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
        cursor.execute("""
            SELECT AVG(avg_security_score) as avg_score
            FROM scans
            WHERE timestamp >= ?
        """, (start_date,))
        avg_score_30d = cursor.fetchone()['avg_score'] or 0
        
        conn.close()
        
        return {
            'total_scans': total_scans,
            'unique_devices': unique_devices,
            'last_scan': last_scan,
            'avg_security_score_30d': round(avg_score_30d, 2)
        }
