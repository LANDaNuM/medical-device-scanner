# Dodanie flagi --report-email do scanner.py

Jeśli komenda `grep -n "report-email" src/scanner.py` nic nie pokazuje, w Twojej kopii brakuje obsługi wysyłki raportu mailem. Dodaj poniższe fragmenty **ręcznie**.

---

## 1. Funkcja wysyłki e-mail (przed `def main():`)

Znajdź w `src/scanner.py` fragment:

```python
    return results


def main():
    """Główna funkcja - punkt wejścia programu"""
```

**Przed** linią `def main():` (czyli po `return results` i dwóch pustych liniach) wklej **cały** poniższy blok:

```python
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


```

(Zachowaj potem jedną pustą linię przed `def main():`.)

---

## 2. Argument parsera (w funkcji `main()`)

Znajdź te dwie linie:

```python
    parser.add_argument('--interval', type=int, default=300, help='Interwał monitoringu w sekundach (domyślnie 300 = 5 minut)')
    
    args = parser.parse_args()
```

**Między nimi** (po linii z `--interval`, przed `args = parser.parse_args()`) dodaj **jedną** linię:

```python
    parser.add_argument('--report-email', metavar='ADR', default=None, help='Po zakończeniu skanowania wyślij raport (combined_report) emailem (SMTP z .env, jak ESP32)')
```

---

## 3. Wywołanie wysyłki (po wygenerowaniu raportu)

Znajdź fragment:

```python
        combined_report = scanner.generate_combined_report(threat_intel_data=threat_intel_results if threat_intel_results else None)
        
        console.print("[bold green]✅ Skanowanie zakończone![/bold green]\n")
```

**Między nimi** (po `generate_combined_report(...)`, przed `console.print`) wklej:

```python
        # Wyślij raport emailem jeśli podano --report-email (SMTP z .env, jak ESP32)
        if args.report_email and combined_report and os.path.isfile(combined_report):
            _send_report_email(args.report_email, combined_report)
        
```

---

## Sprawdzenie

Zapisz plik i w katalogu projektu uruchom:

```bash
grep -n "report-email" src/scanner.py
```

Powinny pojawić się co najmniej 2 linie (argument i warunek `args.report_email`). Potem:

```bash
python3 src/scanner.py --help
```

W pomocy powinna być opcja `--report-email ADR`.

Konfiguracja SMTP (Proton itd.) jak dla ESP32: [CRON_PROTON_ESP32.md](CRON_PROTON_ESP32.md).
