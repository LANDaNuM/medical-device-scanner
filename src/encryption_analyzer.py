#!/usr/bin/env python3
"""
Encryption analysis for medical devices: detect weak/legacy algorithms, generate improvement recommendations, score strength.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


class EncryptionStrength(Enum):
    """Encryption strength."""
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    NONE = "none"
    UNKNOWN = "unknown"


@dataclass
class EncryptionAnalysis:
    """Result of device encryption analysis."""
    encryption_type: str
    strength: EncryptionStrength
    is_weak: bool
    issues: List[str]
    recommendations: List[str]
    score: int


class EncryptionAnalyzer:
    """Analyzes encryption of medical devices."""
    WEAK_ALGORITHMS = [
        "DES", "3DES", "RC4", "MD5", "SHA1", "RSA-1024",
        "TLS 1.0", "TLS 1.1", "SSL 2.0", "SSL 3.0",
        "WEP", "WPA", "WPA2-TKIP"
    ]
    
    MODERATE_ALGORITHMS = [
        "AES-128", "RSA-2048", "TLS 1.2", "WPA2-CCMP"
    ]
    STRONG_ALGORITHMS = [
        "AES-256", "ChaCha20-Poly1305", "TLS 1.3", "WPA3",
        "RSA-4096", "ECDSA", "Ed25519"
    ]
    
    ENCRYPTION_STRENGTH_MAP = {
        "No encryption": EncryptionStrength.NONE,
        "Brak szyfrowania": EncryptionStrength.NONE,
        "DES": EncryptionStrength.WEAK,
        "3DES": EncryptionStrength.WEAK,
        "RC4": EncryptionStrength.WEAK,
        "TLS 1.0": EncryptionStrength.WEAK,
        "TLS 1.1": EncryptionStrength.WEAK,
        "SSL": EncryptionStrength.WEAK,
        "WEP": EncryptionStrength.WEAK,
        "WPA": EncryptionStrength.WEAK,
        "AES-128": EncryptionStrength.MODERATE,
        "TLS 1.2": EncryptionStrength.MODERATE,
        "WPA2": EncryptionStrength.MODERATE,
        "HTTPS": EncryptionStrength.MODERATE,
        "AES-256": EncryptionStrength.STRONG,
        "TLS 1.3": EncryptionStrength.STRONG,
        "WPA3": EncryptionStrength.STRONG,
        "LE Secure Connections": EncryptionStrength.STRONG,
    }
    
    def analyze(self, encryption_type: Optional[str], has_encryption: bool) -> EncryptionAnalysis:
        """Analyze device encryption. Returns EncryptionAnalysis."""
        if not has_encryption or not encryption_type:
            return EncryptionAnalysis(
                encryption_type="No encryption",
                strength=EncryptionStrength.NONE,
                is_weak=True,
                issues=["No encryption – all data sent in clear"],
                recommendations=[
                    "Enable encryption for all connections",
                    "Use TLS 1.3 or at least TLS 1.2",
                    "For BLE: use LE Secure Connections (AES-256)",
                    "For WiFi: use WPA3 or WPA2 with AES-CCMP"
                ],
                score=0
            )
        encryption_type_lower = encryption_type.lower()
        issues = []
        recommendations = []
        strength = EncryptionStrength.UNKNOWN
        is_weak = False
        for key, value in self.ENCRYPTION_STRENGTH_MAP.items():
            if key.lower() in encryption_type_lower:
                strength = value
                break
        if strength == EncryptionStrength.UNKNOWN:
            strength = self._detect_strength_from_name(encryption_type)
        for weak_alg in self.WEAK_ALGORITHMS:
            if weak_alg.lower() in encryption_type_lower:
                is_weak = True
                issues.append(f"Uses weak algorithm: {weak_alg}")
                recommendations.extend(self._get_recommendations_for_weak_algorithm(weak_alg))
        if strength == EncryptionStrength.MODERATE:
            issues.append("Uses moderate encryption – can be improved")
            recommendations.extend([
                "Consider upgrading to AES-256",
                "Use TLS 1.3 instead of TLS 1.2",
                "For BLE: consider LE Secure Connections"
            ])
        if "tls 1.0" in encryption_type_lower or "tls 1.1" in encryption_type_lower:
            is_weak = True
            issues.append("Uses legacy TLS (1.0/1.1) – vulnerable")
            recommendations.append("Upgrade to TLS 1.3 or at least TLS 1.2")
        if "ssl" in encryption_type_lower and "tls" not in encryption_type_lower:
            is_weak = True
            issues.append("Uses legacy SSL – very unsafe")
            recommendations.append("Upgrade to TLS 1.3 immediately")
        if "wep" in encryption_type_lower or ("wpa" in encryption_type_lower and "wpa2" not in encryption_type_lower and "wpa3" not in encryption_type_lower):
            is_weak = True
            issues.append("Uses legacy WiFi (WEP/WPA) – easy to break")
            recommendations.append("Upgrade to WPA3 or at least WPA2 with AES-CCMP")
        if "aes-128" in encryption_type_lower:
            issues.append("AES-128 is acceptable but AES-256 is stronger")
            recommendations.append("Consider upgrading to AES-256 for better security")
        score = self._calculate_encryption_score(strength, is_weak, len(issues))
        if not recommendations:
            if strength == EncryptionStrength.STRONG:
                recommendations.append("Encryption is strong – keep current configuration")
            elif strength == EncryptionStrength.MODERATE:
                recommendations.append("Consider upgrading to stronger algorithms")
        
        return EncryptionAnalysis(
            encryption_type=encryption_type,
            strength=strength,
            is_weak=is_weak,
            issues=issues,
            recommendations=recommendations,
            score=score
        )
    
    def _detect_strength_from_name(self, encryption_type: str) -> EncryptionStrength:
        """Detect encryption strength from type name."""
        encryption_type_lower = encryption_type.lower()
        for strong in ["aes-256", "tls 1.3", "wpa3", "chacha20", "ed25519", "ecdsa"]:
            if strong in encryption_type_lower:
                return EncryptionStrength.STRONG
        for moderate in ["aes-128", "tls 1.2", "wpa2", "rsa-2048"]:
            if moderate in encryption_type_lower:
                return EncryptionStrength.MODERATE
        for weak in ["des", "rc4", "md5", "sha1", "tls 1.0", "tls 1.1", "ssl", "wep", "wpa"]:
            if weak in encryption_type_lower:
                return EncryptionStrength.WEAK
        
        if "network-level" in encryption_type_lower or "application-level" in encryption_type_lower:
            return EncryptionStrength.MODERATE
        
        return EncryptionStrength.UNKNOWN
    
    def _get_recommendations_for_weak_algorithm(self, algorithm: str) -> List[str]:
        """Return recommendations for a weak algorithm."""
        recommendations_map = {
            "DES": ["Replace DES with AES-256", "DES is obsolete and easy to break"],
            "3DES": ["Replace 3DES with AES-256", "3DES is slow and obsolete"],
            "RC4": ["Replace RC4 with ChaCha20-Poly1305 or AES-GCM", "RC4 has known vulnerabilities"],
            "MD5": ["Replace MD5 with SHA-256 or SHA-3", "MD5 is vulnerable to collisions"],
            "SHA1": ["Replace SHA1 with SHA-256 or SHA-3", "SHA1 is obsolete"],
            "RSA-1024": ["Replace RSA-1024 with RSA-2048 or larger", "RSA-1024 is too weak"],
            "TLS 1.0": ["Upgrade to TLS 1.3 immediately", "TLS 1.0 has known vulnerabilities (POODLE, BEAST)"],
            "TLS 1.1": ["Upgrade to TLS 1.3 immediately", "TLS 1.1 has known vulnerabilities"],
            "SSL": ["Upgrade to TLS 1.3 immediately", "SSL is fully obsolete and unsafe"],
            "WEP": ["Upgrade to WPA3 immediately", "WEP can be broken in minutes"],
            "WPA": ["Upgrade to WPA3 or at least WPA2", "WPA is obsolete"],
            "WPA2-TKIP": ["Use WPA2 with AES-CCMP instead of TKIP", "TKIP is weaker than AES-CCMP"]
        }
        return recommendations_map.get(algorithm, ["Replace legacy algorithm with a modern one"])
    
    def _calculate_encryption_score(self, strength: EncryptionStrength, is_weak: bool, issues_count: int) -> int:
        """Compute encryption score (0-100)."""
        base_scores = {
            EncryptionStrength.STRONG: 90,
            EncryptionStrength.MODERATE: 60,
            EncryptionStrength.WEAK: 30,
            EncryptionStrength.NONE: 0,
            EncryptionStrength.UNKNOWN: 50
        }
        
        score = base_scores.get(strength, 50)
        
        score -= issues_count * 10
        if is_weak:
            score -= 20
        return max(0, min(100, score))
    
    def generate_report(self, analyses: List[EncryptionAnalysis]) -> str:
        """Generate encryption analysis report. Returns report text."""
        if not analyses:
            return "No devices to analyze"
        total = len(analyses)
        strong = sum(1 for a in analyses if a.strength == EncryptionStrength.STRONG)
        moderate = sum(1 for a in analyses if a.strength == EncryptionStrength.MODERATE)
        weak = sum(1 for a in analyses if a.strength == EncryptionStrength.WEAK)
        none = sum(1 for a in analyses if a.strength == EncryptionStrength.NONE)
        weak_count = sum(1 for a in analyses if a.is_weak)
        
        avg_score = sum(a.score for a in analyses) / total if total > 0 else 0
        
        report = f"""
Encryption Analysis Report
==========================

Summary:
  Total devices: {total}
  🔴 Strong encryption: {strong} ({strong/total*100:.1f}%)
  🟡 Moderate encryption: {moderate} ({moderate/total*100:.1f}%)
  🟠 Weak encryption: {weak} ({weak/total*100:.1f}%)
  ❌ No encryption: {none} ({none/total*100:.1f}%)
  ⚠️  Devices with weak algorithms: {weak_count} ({weak_count/total*100:.1f}%)
  📊 Average encryption score: {avg_score:.1f}/100

"""
        
        devices_with_issues = [a for a in analyses if a.issues]
        if devices_with_issues:
            report += "\nDevices with encryption issues:\n"
            report += "-" * 50 + "\n"
            for analysis in devices_with_issues:
                report += f"\n{analysis.encryption_type} (Score: {analysis.score}/100)\n"
                report += f"  Strength: {analysis.strength.value}\n"
                if analysis.issues:
                    report += "  Issues:\n"
                    for issue in analysis.issues:
                        report += f"    • {issue}\n"
                if analysis.recommendations:
                    report += "  Recommendations:\n"
                    for rec in analysis.recommendations:
                        report += f"    → {rec}\n"
        
        return report
