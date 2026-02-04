# 👀 Jak Przeglądać combined_report_*.json - Najlepsze Narzędzia

## 🎯 Najprostsze i Najlepsze Opcje

### 1. 🌐 API Server (--api) - **NAJPROSTSZE!** ⭐

**Dlaczego najlepsze:**
- ✅ **Gotowe od razu** - nie wymaga instalacji dodatkowych narzędzi
- ✅ **Przejrzysty interfejs** - piękny HTML dashboard
- ✅ **Wszystkie dane** - urządzenia, statystyki, threat intelligence
- ✅ **Filtrowanie** - łatwe wyszukiwanie urządzeń
- ✅ **Automatycznie** - używa najnowszego raportu

**Jak użyć:**
```bash
# 1. Uruchom skaner z API
python3 src/scanner.py --api

# 2. Otwórz w przeglądarce:
# http://localhost:5000
```

**Co zobaczysz:**
- 📊 Pełny raport ze wszystkimi urządzeniami
- 📱 Lista urządzeń z filtrowaniem
- 📈 Statystyki skanowania
- 🔍 Szczegóły każdego urządzenia
- 🚨 Threat intelligence powiązany z urządzeniami

**Zalety:**
- Nie musisz instalować niczego
- Piękny interfejs graficzny
- Automatycznie używa najnowszego raportu
- Łatwe nawigowanie

---

### 2. 📝 VS Code (lub inny edytor) - **Dla Programistów**

**Dlaczego dobre:**
- ✅ **Formatowanie JSON** - automatyczne
- ✅ **Kolorowanie składni** - łatwe czytanie
- ✅ **Wyszukiwanie** - Ctrl+F
- ✅ **Foldowanie** - zwijanie sekcji

**Jak użyć:**
1. Otwórz VS Code (lub inny edytor)
2. Otwórz plik: `reports/combined_report_*.json`
3. VS Code automatycznie sformatuje JSON

**Zalety:**
- Działa od razu (jeśli masz VS Code)
- Pełna kontrola nad danymi
- Możesz edytować (jeśli chcesz)

**Wady:**
- Duże pliki mogą być wolne
- Brak wizualizacji

---

### 3. 🔧 jq (wiersz poleceń) - **Dla Zaawansowanych**

**Dlaczego dobre:**
- ✅ **Szybkie** - działa w terminalu
- ✅ **Filtrowanie** - łatwe wyszukiwanie
- ✅ **Formatowanie** - piękne wyświetlanie JSON
- ✅ **Ekstrakcja** - wyciąganie konkretnych danych

**Instalacja:**
```bash
# Ubuntu/Debian:
sudo apt-get install jq

# Fedora:
sudo dnf install jq

# macOS:
brew install jq
```

**Podstawowe użycie:**
```bash
# Piękne formatowanie całego pliku
cat reports/combined_report_*.json | jq '.'

# Zobacz tylko urządzenia
cat reports/combined_report_*.json | jq '.scan.devices[]'

# Zobacz statystyki
cat reports/combined_report_*.json | jq '.analysis.summary'

# Znajdź urządzenie po IP
cat reports/combined_report_*.json | jq '.scan.devices[] | select(.ip_address == "192.168.1.5")'

# Zobacz urządzenia wysokiego ryzyka
cat reports/combined_report_*.json | jq '.scan.devices[] | select(.security_score < 50)'

# Zobacz threat intelligence
cat reports/combined_report_*.json | jq '.threat_intelligence'

# Zobacz urządzenia z threat intelligence
cat reports/combined_report_*.json | jq '.scan.devices[] | select(.threat_intelligence_linked == true)'
```

**Zalety:**
- Bardzo szybkie
- Można używać w skryptach
- Potężne filtrowanie

**Wady:**
- Wymaga instalacji
- Wiersz poleceń (nie graficzny)

---

### 4. 🌐 JSON Viewer Online (dla szybkiego podglądu)

**Dlaczego dobre:**
- ✅ **Nie wymaga instalacji** - działa w przeglądarce
- ✅ **Formatowanie** - automatyczne
- ✅ **Foldowanie** - zwijanie sekcji
- ✅ **Wyszukiwanie** - Ctrl+F

**Jak użyć:**
1. Otwórz: https://jsonviewer.stack.hu/ lub https://jsonformatter.org/json-viewer
2. Skopiuj zawartość `combined_report_*.json`
3. Wklej do edytora online

**Zalety:**
- Działa wszędzie (tylko przeglądarka)
- Nie wymaga instalacji

**Wady:**
- Duże pliki mogą być wolne
- Musisz kopiować/wklejać
- Brak prywatności (dane w przeglądarce)

---

### 5. 📊 Python Script (custom viewer)

**Dlaczego dobre:**
- ✅ **Pełna kontrola** - możesz dostosować
- ✅ **Własne filtry** - co chcesz zobaczyć
- ✅ **Automatyzacja** - możesz zautomatyzować

**Przykładowy skrypt:**
```python
#!/usr/bin/env python3
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Wczytaj raport
report_file = Path("reports/combined_report_2026-02-04_16-01-11.json")
with open(report_file, 'r') as f:
    data = json.load(f)

# Pokaż statystyki
summary = data['analysis']['summary']
console.print(Panel.fit(
    f"[bold]📊 Statystyki Skanowania[/bold]\n"
    f"Urządzeń: {summary['total_devices']}\n"
    f"Wysokie ryzyko: {summary['high_risk_count']}\n"
    f"Średnie ryzyko: {summary['medium_risk_count']}\n"
    f"Średni score: {summary['average_security_score']:.1f}",
    title="Podsumowanie"
))

# Pokaż urządzenia
table = Table(title="Urządzenia")
table.add_column("Nazwa", style="cyan")
table.add_column("IP", style="magenta")
table.add_column("Score", style="green")
table.add_column("Protokół", style="yellow")

for device in data['scan']['devices']:
    name = device.get('display_name', device.get('name', 'Unknown'))
    ip = device.get('ip_address', 'N/A')
    score = device.get('security_score', 0)
    protocol = device.get('protocol', 'N/A')
    
    table.add_row(name, ip, str(score), protocol)

console.print(table)
```

**Zalety:**
- Pełna kontrola
- Możesz dostosować do swoich potrzeb

**Wady:**
- Wymaga znajomości Pythona
- Trzeba napisać skrypt

---

## 🎯 Moja Rekomendacja

### ⭐ **Dla większości użytkowników: API Server (--api)**

**Dlaczego:**
- ✅ Najprostsze - nie wymaga instalacji
- ✅ Przejrzyste - piękny interfejs graficzny
- ✅ Wszystkie dane - urządzenia, statystyki, threat intel
- ✅ Filtrowanie - łatwe wyszukiwanie
- ✅ Automatycznie - używa najnowszego raportu

**Jak:**
```bash
python3 src/scanner.py --api
# Otwórz: http://localhost:5000
```

### 🔧 **Dla programistów: jq + VS Code**

**Dlaczego:**
- ✅ Szybkie - działa w terminalu
- ✅ Potężne - zaawansowane filtrowanie
- ✅ Formatowanie - piękne wyświetlanie JSON

**Jak:**
```bash
# Zainstaluj jq
sudo apt-get install jq

# Użyj
cat reports/combined_report_*.json | jq '.scan.devices[]'
```

---

## 📋 Szybkie Porównanie

| Narzędzie | Prostość | Przejrzystość | Instalacja | Zalecane dla |
|-----------|----------|--------------|------------|--------------|
| **API Server (--api)** ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Wbudowane | Wszyscy |
| **VS Code** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ Jeśli masz | Programiści |
| **jq** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⚠️ Wymaga | Zaawansowani |
| **JSON Viewer Online** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ Nie | Szybki podgląd |
| **Python Script** | ⭐⭐ | ⭐⭐⭐⭐ | ⚠️ Wymaga | Custom |

---

## 💡 Praktyczne Przykłady

### Przykład 1: Szybki podgląd (API Server)

```bash
python3 src/scanner.py --api
# Otwórz: http://localhost:5000/dashboard
```

**Zobaczysz:**
- Wszystkie urządzenia w czytelnej formie
- Statystyki
- Threat intelligence
- Filtrowanie

---

### Przykład 2: Znajdź konkretne urządzenie (jq)

```bash
# Znajdź urządzenie po IP
cat reports/combined_report_*.json | jq '.scan.devices[] | select(.ip_address == "192.168.1.5")'

# Znajdź urządzenia wysokiego ryzyka
cat reports/combined_report_*.json | jq '.scan.devices[] | select(.security_score < 50) | {name: .display_name, ip: .ip_address, score: .security_score}'
```

---

### Przykład 3: Zobacz tylko statystyki (jq)

```bash
cat reports/combined_report_*.json | jq '.analysis.summary'
```

**Wynik:**
```json
{
  "total_devices": 5,
  "high_risk_count": 2,
  "medium_risk_count": 3,
  "average_security_score": 45.2
}
```

---

## 🎯 Podsumowanie

**Najprostsze i najprzejrzystsze:**
1. ⭐ **API Server (`--api`)** - dla większości użytkowników
2. **VS Code** - dla programistów
3. **jq** - dla zaawansowanych

**Zalecenie:** Użyj **API Server** - to jest najprostsze i najprzejrzystsze rozwiązanie!

```bash
python3 src/scanner.py --api
# Otwórz: http://localhost:5000
```

**Gotowe!** 🎉
