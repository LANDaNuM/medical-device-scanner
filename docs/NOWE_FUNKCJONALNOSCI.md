# 🚀 Nowe Funkcjonalności - Instrukcja

## ✅ Co Zostało Dodane

### 1. 📅 Scheduled Scans (Zaplanowane Skanowania)
### 2. 📧 Email Notifications (Powiadomienia Email)
### 3. 📈 History & Trends (Historia i Trendy)
### 4. 🔍 Real-time Monitoring (Monitoring w Czasie Rzeczywistym)

---

## 📅 1. Scheduled Scans

Automatyczne skanowanie o określonych godzinach.

### Użycie:

```bash
# Codziennie o 9:00
python3 src/scanner.py --schedule "daily 09:00"

# Co godzinę
python3 src/scanner.py --schedule "hourly"

# Co 30 minut
python3 src/scanner.py --schedule "every 30 minutes"

# Co 2 godziny
python3 src/scanner.py --schedule "every 2 hours"
```

### Przykłady:

```bash
# Codziennie o 9:00 rano
python3 src/scanner.py --schedule "daily 09:00"

# Co 6 godzin
python3 src/scanner.py --schedule "every 6 hours"

# Z konkretnymi protokołami
python3 src/scanner.py --wifi --schedule "daily 09:00"

# Z audytem bezpieczeństwa
python3 src/scanner.py --audit --schedule "daily 09:00"
```

### Zatrzymywanie:

Naciśnij `Ctrl+C` aby zatrzymać scheduler.

---

## 📧 2. Email Notifications

Wysyłanie raportów i alertów emailem.

### Konfiguracja (.env):

```bash
# Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=twoj_email@gmail.com
SMTP_PASSWORD=twoje_haslo_aplikacji  # Użyj "App Password"
EMAIL_FROM=twoj_email@gmail.com

# Outlook
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USER=twoj_email@outlook.com
SMTP_PASSWORD=twoje_haslo
EMAIL_FROM=twoj_email@outlook.com

# ProtonMail (wymaga ProtonMail Bridge)
SMTP_SERVER=127.0.0.1
SMTP_PORT=1025
SMTP_USER=twoj_email@protonmail.com
SMTP_PASSWORD=twoje_haslo_protonmail
EMAIL_FROM=twoj_email@protonmail.com
```

**⚠️ WAŻNE dla ProtonMail:**
ProtonMail **nie obsługuje bezpośredniego SMTP**. Musisz użyć **ProtonMail Bridge**:

1. **Zainstaluj ProtonMail Bridge:**
   - Pobierz: https://proton.me/mail/bridge
   - Zainstaluj na swoim komputerze

2. **Uruchom ProtonMail Bridge:**
   - Zaloguj się swoim kontem ProtonMail
   - Bridge utworzy lokalny serwer SMTP na `127.0.0.1:1025`

3. **Konfiguracja w .env:**
   ```bash
   SMTP_SERVER=127.0.0.1
   SMTP_PORT=1025
   SMTP_USER=twoj_email@protonmail.com
   SMTP_PASSWORD=twoje_haslo_protonmail  # To samo co w Bridge
   EMAIL_FROM=twoj_email@protonmail.com
   ```

4. **Uwaga:** ProtonMail Bridge musi być **uruchomiony** podczas wysyłania emaili!

### Użycie:

```bash
# Wyślij raport emailem po skanowaniu
python3 src/scanner.py --email admin@hospital.com

# Wyślij do wielu odbiorców
python3 src/scanner.py --email admin@hospital.com security@hospital.com

# Z załącznikami (raporty PDF, JSON)
python3 src/scanner.py --email admin@hospital.com
```

### Alerty (z monitoringiem):

```bash
# Alerty o nowych urządzeniach i zmianach ryzyka
python3 src/scanner.py --monitor --email-alerts admin@hospital.com
```

---

## 📈 3. History & Trends

Automatyczne zapisywanie historii skanowań do bazy danych SQLite.

### Automatyczne:

Historia jest **automatycznie zapisywana** przy każdym skanowaniu!

### Plik bazy danych:

```
history.db  # W katalogu projektu
```

### Funkcje:

- ✅ Zapis każdego skanowania
- ✅ Historia urządzeń (zmiany security score)
- ✅ Wykrywanie nowych urządzeń
- ✅ Trendy bezpieczeństwa (ostatnie 30 dni)
- ✅ Statystyki

### Użycie w kodzie:

```python
from history_db import HistoryDB

# Pobierz historię
history_db = HistoryDB()
recent_scans = history_db.get_recent_scans(limit=10)

# Pobierz trendy
trends = history_db.get_trends(days=30)

# Wykryj nowe urządzenia
new_devices = history_db.detect_new_devices(current_devices)
```

---

## 🔍 4. Real-time Monitoring

Ciągłe skanowanie w tle z alertami.

### Użycie:

```bash
# Monitoring co 5 minut (domyślnie)
python3 src/scanner.py --monitor

# Monitoring co 1 minutę
python3 src/scanner.py --monitor --interval 60

# Z alertami email
python3 src/scanner.py --monitor --email-alerts admin@hospital.com

# Tylko WiFi, co 10 minut
python3 src/scanner.py --wifi --monitor --interval 600
```

### Co robi:

1. **Skanuje w pętlach** (co X sekund)
2. **Wykrywa nowe urządzenia** - alertuje gdy pojawi się nowe
3. **Wykrywa zmiany ryzyka** - alertuje gdy security score spadnie o ≥20 punktów
4. **Zapisuje do historii** - każdy skan jest zapisywany
5. **Wysyła alerty email** - jeśli skonfigurowane

### Przykłady:

```bash
# Podstawowy monitoring (co 5 minut)
python3 src/scanner.py --monitor

# Szybki monitoring (co 1 minutę) - tylko WiFi
python3 src/scanner.py --wifi --monitor --interval 60

# Monitoring z alertami email
python3 src/scanner.py --monitor --email-alerts admin@hospital.com security@hospital.com

# Monitoring z pełnym audytem (co 30 minut)
python3 src/scanner.py --audit --monitor --interval 1800
```

### Zatrzymywanie:

Naciśnij `Ctrl+C` aby zatrzymać monitor.

---

## 🎯 Kombinacje

### Codzienne raporty emailem:

```bash
python3 src/scanner.py --schedule "daily 09:00" --email admin@hospital.com
```

### Monitoring z alertami:

```bash
python3 src/scanner.py --monitor --interval 300 --email-alerts admin@hospital.com
```

### Pełna automatyzacja:

```bash
# Codziennie o 9:00, z raportem emailem
python3 src/scanner.py --schedule "daily 09:00" --email admin@hospital.com --audit
```

---

## 📊 Historia i Trendy - API

### Pobierz ostatnie skanowania:

```python
from history_db import HistoryDB

history_db = HistoryDB()
scans = history_db.get_recent_scans(limit=10)

for scan in scans:
    print(f"Data: {scan.timestamp}")
    print(f"Urządzeń: {scan.total_devices}")
    print(f"Średni score: {scan.avg_security_score}")
```

### Pobierz trendy:

```python
trends = history_db.get_trends(days=30)

# Wykresy:
# trends['timestamps'] - daty
# trends['avg_scores'] - średnie security scores
# trends['high_risk'] - liczba urządzeń wysokiego ryzyka
```

### Wykryj nowe urządzenia:

```python
new_devices = history_db.detect_new_devices(current_devices)
if new_devices:
    print(f"Wykryto {len(new_devices)} nowych urządzeń!")
```

---

## ⚙️ Instalacja Zależności

```bash
pip install -r requirements.txt
```

**Nowe zależności:**
- `schedule>=1.2.0` - dla scheduled scans
- `APScheduler>=3.10.0` - alternatywa (opcjonalne)

---

## 💡 Wskazówki

1. **Email:** Użyj "App Password" dla Gmail (nie zwykłego hasła)
2. **Monitoring:** Dla szybkiego monitoringu użyj `--interval 60` (1 minuta)
3. **Historia:** Baza danych `history.db` rośnie - możesz ją okresowo czyścić
4. **Scheduler:** Działa w tle - możesz zamknąć terminal (ale lepiej użyć `screen` lub `tmux`)

---

## ❓ Problemy?

### Email nie działa:
- Sprawdź konfigurację SMTP w `.env`
- Dla Gmail: użyj "App Password" (nie zwykłego hasła)
- Sprawdź firewall (port 587/465)

### Scheduler/Monitor nie działa:
- Sprawdź czy nie ma błędów w logach
- Upewnij się że masz zainstalowane zależności: `pip install schedule`

### Historia nie zapisuje:
- Sprawdź uprawnienia do zapisu w katalogu projektu
- Sprawdź czy `history.db` jest tworzony

---

## 🎉 Gotowe!

Wszystkie 4 funkcjonalności są gotowe do użycia! 🚀
