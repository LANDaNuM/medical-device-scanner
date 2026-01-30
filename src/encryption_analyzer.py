#!/usr/bin/env python3
"""
Moduł do szczegółowej analizy szyfrowania urządzeń medycznych.

Ten moduł:
- Analizuje algorytmy szyfrowania używane przez urządzenia
- Wykrywa słabe algorytmy i przestarzałe standardy
- Generuje rekomendacje ulepszeń
- Ocenia siłę szyfrowania
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


class EncryptionStrength(Enum):
    """Siła szyfrowania"""
    STRONG = "strong"  # Silne szyfrowanie
    MODERATE = "moderate"  # Umiarkowane szyfrowanie
    WEAK = "weak"  # Słabe szyfrowanie
    NONE = "none"  # Brak szyfrowania
    UNKNOWN = "unknown"  # Nieznane


@dataclass
class EncryptionAnalysis:
    """
    Wynik analizy szyfrowania urządzenia.
    """
    encryption_type: str  # Typ szyfrowania (np. "AES-128", "TLS 1.2")
    strength: EncryptionStrength  # Siła szyfrowania
    is_weak: bool  # Czy szyfrowanie jest słabe
    issues: List[str]  # Lista problemów z szyfrowaniem
    recommendations: List[str]  # Rekomendacje ulepszeń
    score: int  # Wynik szyfrowania (0-100)


class EncryptionAnalyzer:
    """
    Klasa do analizy szyfrowania urządzeń medycznych.
    """
    
    # Słabe algorytmy i przestarzałe standardy
    WEAK_ALGORITHMS = [
        "DES", "3DES", "RC4", "MD5", "SHA1", "RSA-1024",
        "TLS 1.0", "TLS 1.1", "SSL 2.0", "SSL 3.0",
        "WEP", "WPA", "WPA2-TKIP"
    ]
    
    # Umiarkowane algorytmy (akceptowalne, ale można lepiej)
    MODERATE_ALGORITHMS = [
        "AES-128", "RSA-2048", "TLS 1.2", "WPA2-CCMP"
    ]
    
    # Silne algorytmy (zalecane)
    STRONG_ALGORITHMS = [
        "AES-256", "ChaCha20-Poly1305", "TLS 1.3", "WPA3",
        "RSA-4096", "ECDSA", "Ed25519"
    ]
    
    # Mapowanie typów szyfrowania do siły
    ENCRYPTION_STRENGTH_MAP = {
        # Brak szyfrowania
        "No encryption": EncryptionStrength.NONE,
        "Brak szyfrowania": EncryptionStrength.NONE,
        
        # Słabe
        "DES": EncryptionStrength.WEAK,
        "3DES": EncryptionStrength.WEAK,
        "RC4": EncryptionStrength.WEAK,
        "TLS 1.0": EncryptionStrength.WEAK,
        "TLS 1.1": EncryptionStrength.WEAK,
        "SSL": EncryptionStrength.WEAK,
        "WEP": EncryptionStrength.WEAK,
        "WPA": EncryptionStrength.WEAK,
        
        # Umiarkowane
        "AES-128": EncryptionStrength.MODERATE,
        "TLS 1.2": EncryptionStrength.MODERATE,
        "WPA2": EncryptionStrength.MODERATE,
        "HTTPS": EncryptionStrength.MODERATE,
        
        # Silne
        "AES-256": EncryptionStrength.STRONG,
        "TLS 1.3": EncryptionStrength.STRONG,
        "WPA3": EncryptionStrength.STRONG,
        "LE Secure Connections": EncryptionStrength.STRONG,
    }
    
    def analyze(self, encryption_type: Optional[str], has_encryption: bool) -> EncryptionAnalysis:
        """
        Analizuje szyfrowanie urządzenia.
        
        Args:
            encryption_type: Typ szyfrowania (np. "AES-128", "TLS 1.2")
            has_encryption: Czy urządzenie ma szyfrowanie
        
        Returns:
            Obiekt EncryptionAnalysis z wynikami analizy
        """
        # Jeśli brak szyfrowania
        if not has_encryption or not encryption_type:
            return EncryptionAnalysis(
                encryption_type="No encryption",
                strength=EncryptionStrength.NONE,
                is_weak=True,
                issues=["Brak szyfrowania - wszystkie dane przesyłane jawnie"],
                recommendations=[
                    "Włącz szyfrowanie dla wszystkich połączeń",
                    "Użyj TLS 1.3 lub TLS 1.2 minimum",
                    "Dla BLE: użyj LE Secure Connections (AES-256)",
                    "Dla WiFi: użyj WPA3 lub WPA2 z AES-CCMP"
                ],
                score=0
            )
        
        encryption_type_lower = encryption_type.lower()
        issues = []
        recommendations = []
        strength = EncryptionStrength.UNKNOWN
        is_weak = False
        
        # Sprawdź siłę szyfrowania
        for key, value in self.ENCRYPTION_STRENGTH_MAP.items():
            if key.lower() in encryption_type_lower:
                strength = value
                break
        
        # Jeśli nie znaleziono w mapie, spróbuj wykryć po nazwie
        if strength == EncryptionStrength.UNKNOWN:
            strength = self._detect_strength_from_name(encryption_type)
        
        # Sprawdź słabe algorytmy
        for weak_alg in self.WEAK_ALGORITHMS:
            if weak_alg.lower() in encryption_type_lower:
                is_weak = True
                issues.append(f"Używa słabego algorytmu: {weak_alg}")
                recommendations.extend(self._get_recommendations_for_weak_algorithm(weak_alg))
        
        # Sprawdź umiarkowane algorytmy
        if strength == EncryptionStrength.MODERATE:
            issues.append("Używa umiarkowanego szyfrowania - można ulepszyć")
            recommendations.extend([
                "Rozważ uaktualnienie do AES-256",
                "Użyj TLS 1.3 zamiast TLS 1.2",
                "Dla BLE: rozważ LE Secure Connections"
            ])
        
        # Sprawdź specyficzne problemy
        if "tls 1.0" in encryption_type_lower or "tls 1.1" in encryption_type_lower:
            is_weak = True
            issues.append("Używa przestarzałej wersji TLS (1.0/1.1) - podatna na ataki")
            recommendations.append("Uaktualnij do TLS 1.3 lub minimum TLS 1.2")
        
        if "ssl" in encryption_type_lower and "tls" not in encryption_type_lower:
            is_weak = True
            issues.append("Używa przestarzałego SSL - bardzo niebezpieczne")
            recommendations.append("Natychmiast uaktualnij do TLS 1.3")
        
        if "wep" in encryption_type_lower or "wpa" in encryption_type_lower and "wpa2" not in encryption_type_lower and "wpa3" not in encryption_type_lower:
            is_weak = True
            issues.append("Używa przestarzałego standardu WiFi (WEP/WPA) - łatwe do złamania")
            recommendations.append("Uaktualnij do WPA3 lub minimum WPA2 z AES-CCMP")
        
        if "aes-128" in encryption_type_lower:
            issues.append("AES-128 jest akceptowalne, ale AES-256 jest bardziej bezpieczne")
            recommendations.append("Rozważ uaktualnienie do AES-256 dla lepszego bezpieczeństwa")
        
        # Oblicz wynik (0-100)
        score = self._calculate_encryption_score(strength, is_weak, len(issues))
        
        # Jeśli brak rekomendacji, dodaj ogólne
        if not recommendations:
            if strength == EncryptionStrength.STRONG:
                recommendations.append("Szyfrowanie jest silne - utrzymaj obecną konfigurację")
            elif strength == EncryptionStrength.MODERATE:
                recommendations.append("Rozważ uaktualnienie do silniejszych algorytmów")
        
        return EncryptionAnalysis(
            encryption_type=encryption_type,
            strength=strength,
            is_weak=is_weak,
            issues=issues,
            recommendations=recommendations,
            score=score
        )
    
    def _detect_strength_from_name(self, encryption_type: str) -> EncryptionStrength:
        """
        Wykrywa siłę szyfrowania na podstawie nazwy.
        
        Args:
            encryption_type: Typ szyfrowania
        
        Returns:
            Siła szyfrowania
        """
        encryption_type_lower = encryption_type.lower()
        
        # Sprawdź silne
        for strong in ["aes-256", "tls 1.3", "wpa3", "chacha20", "ed25519", "ecdsa"]:
            if strong in encryption_type_lower:
                return EncryptionStrength.STRONG
        
        # Sprawdź umiarkowane
        for moderate in ["aes-128", "tls 1.2", "wpa2", "rsa-2048"]:
            if moderate in encryption_type_lower:
                return EncryptionStrength.MODERATE
        
        # Sprawdź słabe
        for weak in ["des", "rc4", "md5", "sha1", "tls 1.0", "tls 1.1", "ssl", "wep", "wpa"]:
            if weak in encryption_type_lower:
                return EncryptionStrength.WEAK
        
        # Jeśli zawiera "network-level" lub "application-level", to umiarkowane
        if "network-level" in encryption_type_lower or "application-level" in encryption_type_lower:
            return EncryptionStrength.MODERATE
        
        return EncryptionStrength.UNKNOWN
    
    def _get_recommendations_for_weak_algorithm(self, algorithm: str) -> List[str]:
        """
        Zwraca rekomendacje dla słabego algorytmu.
        
        Args:
            algorithm: Nazwa słabego algorytmu
        
        Returns:
            Lista rekomendacji
        """
        recommendations_map = {
            "DES": ["Zastąp DES algorytmem AES-256", "DES jest przestarzały i łatwy do złamania"],
            "3DES": ["Zastąp 3DES algorytmem AES-256", "3DES jest wolny i przestarzały"],
            "RC4": ["Zastąp RC4 algorytmem ChaCha20-Poly1305 lub AES-GCM", "RC4 ma znane podatności"],
            "MD5": ["Zastąp MD5 algorytmem SHA-256 lub SHA-3", "MD5 jest podatny na kolizje"],
            "SHA1": ["Zastąp SHA1 algorytmem SHA-256 lub SHA-3", "SHA1 jest przestarzały"],
            "RSA-1024": ["Zastąp RSA-1024 kluczem RSA-2048 lub większym", "RSA-1024 jest zbyt słaby"],
            "TLS 1.0": ["Natychmiast uaktualnij do TLS 1.3", "TLS 1.0 ma znane podatności (POODLE, BEAST)"],
            "TLS 1.1": ["Natychmiast uaktualnij do TLS 1.3", "TLS 1.1 ma znane podatności"],
            "SSL": ["Natychmiast uaktualnij do TLS 1.3", "SSL jest całkowicie przestarzały i niebezpieczny"],
            "WEP": ["Natychmiast uaktualnij do WPA3", "WEP można złamać w kilka minut"],
            "WPA": ["Uaktualnij do WPA3 lub minimum WPA2", "WPA jest przestarzały"],
            "WPA2-TKIP": ["Użyj WPA2 z AES-CCMP zamiast TKIP", "TKIP jest słabszy niż AES-CCMP"]
        }
        
        return recommendations_map.get(algorithm, ["Zastąp przestarzałym algorytmem nowoczesnym"])
    
    def _calculate_encryption_score(self, strength: EncryptionStrength, is_weak: bool, issues_count: int) -> int:
        """
        Oblicza wynik szyfrowania (0-100).
        
        Args:
            strength: Siła szyfrowania
            is_weak: Czy szyfrowanie jest słabe
            issues_count: Liczba problemów
        
        Returns:
            Wynik szyfrowania (0-100)
        """
        # Bazowy wynik na podstawie siły
        base_scores = {
            EncryptionStrength.STRONG: 90,
            EncryptionStrength.MODERATE: 60,
            EncryptionStrength.WEAK: 30,
            EncryptionStrength.NONE: 0,
            EncryptionStrength.UNKNOWN: 50
        }
        
        score = base_scores.get(strength, 50)
        
        # Odejmij punkty za problemy
        score -= issues_count * 10
        
        # Jeśli słabe, odejmij dodatkowe punkty
        if is_weak:
            score -= 20
        
        # Upewnij się, że wynik jest w zakresie 0-100
        return max(0, min(100, score))
    
    def generate_report(self, analyses: List[EncryptionAnalysis]) -> str:
        """
        Generuje raport z analizy szyfrowania.
        
        Args:
            analyses: Lista analiz szyfrowania
        
        Returns:
            Tekst raportu
        """
        if not analyses:
            return "Brak urządzeń do analizy"
        
        # Statystyki
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
        
        # Urządzenia z problemami
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
