# Cron + Proton (ESP32) – wszystko w jednym miejscu

Jedna strona z pełną konfiguracją: **cron** (zaplanowane skanowanie) i **Proton Mail** (SMTP) do raportów z ESP32 na Raspberry Pi.

---

## 1. Konfiguracja Proton (plik `.env`)

W katalogu projektu na Raspberry Pi (np. `/home/erno_jajo/medical-device-scanner-main`) utwórz lub edytuj plik **`.env`**:

```env
# === Proton Mail SMTP (raporty ESP32: --report-email, --alert-email) ===
SMTP_SERVER=smtp.protonmail.ch
SMTP_PORT=587
SMTP_USER=twoj_adres@twojadomena.pl
SMTP_PASSWORD=token_smtp_z_proton
EMAIL_FROM=twoj_adres@twojadomena.pl
```

**Skąd wziąć wartości:**

| Zmienna        | Wartość |
|----------------|---------|
| `SMTP_SERVER`  | Zawsze `smtp.protonmail.ch` |
| `SMTP_PORT`    | Zawsze `587` |
| `SMTP_USER`    | Adres e-mail **na własnej domenie** w Proton (np. `raporty@twojadomena.pl`) |
| `SMTP_PASSWORD`| **Token SMTP** z Proton (Ustawienia → Proton Mail → IMAP/SMTP → SMTP tokens → Generate). **Nie** hasło do logowania. |
| `EMAIL_FROM`   | Ten sam co `SMTP_USER` |

**Uwaga:** Token SMTP w Proton działa tylko z adresem na **własnej domenie** (domena dodana w Proton). Adresy `@proton.me` nie mają SMTP z tokenem.

---

## 2. Cron – pełna linia z flagami

Wklej do crona **jedną linię** (zamień ścieżkę i adres e-mail):

```cron
20 14 * * * cd /home/erno_jajo/medical-device-scanner-main && python3 scripts/esp32_serial_reader.py --out raporty/esp32_$(date +\%Y\%m\%d).json --enrich --duration 300 --report-email macospedros@proton.me
```

**Edycja crona:** `crontab -e` → wklej linię → zapisz (w nano: Ctrl+O, Enter, Ctrl+X).

---

## 3. Znaczenie pól w cronie i flag

| Fragment | Znaczenie |
|----------|-----------|
| `20 14 * * *` | **Kiedy:** minuta 20, godzina 14 (14:20), codziennie. Kolejność: minuta, godzina, dzień, miesiąc, dzień tygodnia. |
| `cd /home/erno_jajo/medical-device-scanner-main` | Katalog projektu na Pi (zamień na swoją ścieżkę). |
| `--out raporty/esp32_$(date +\%Y\%m\%d).json` | Plik raportu: `raporty/esp32_YYYYMMDD.json` (data z dnia uruchomienia). W cronie `%` muszą być jako `\%`. |
| `--enrich` | Wzbogacanie: producent (OUI), typ urządzenia, podpowiedzi podatności. |
| `--duration 300` | Skan trwa 300 s (5 min), potem zapis raportu i e-mail. |
| `--report-email macospedros@proton.me` | Adres, **na który** wysłać raport (może być dowolna skrzynka). |

**Inna godzina:** np. codziennie 8:00 → `0 8 * * *` (minuta 0, godzina 8).

---

## 4. Katalog na raporty

Przed pierwszym uruchomieniem crona utwórz katalog (jeśli nie istnieje):

```bash
mkdir -p /home/erno_jajo/medical-device-scanner-main/raporty
```

---

## 5. Sprawdzenie

- Lista zadań crona: `crontab -l`
- Test ręczny (ESP32 podłączony USB):  
  `cd /home/erno_jajo/medical-device-scanner-main && python3 scripts/esp32_serial_reader.py --out raporty/test.json --enrich --duration 30 --report-email twoj@email.me`

---

## 6. Wymagania

- Raspberry Pi: włączone, w sieci (LAN/WiFi).
- ESP32: podłączony do Pi przez **USB** (port wolny).
- W Proton: domena własna dodana, adres na domenie utworzony, **token SMTP** wygenerowany i wklejony do `.env` jako `SMTP_PASSWORD`.

Pełna lista flag skryptu: [FLAGI.md – Mikrokontroler (ESP32)](FLAGI.md#-mikrokontroler-esp32).

---

## 7. Cron dla audytu (scanner.py --audit) + raport e-mail

Możesz zaplanować **pełny audyt** (testy podatności, skan portów) tak samo jak ESP32 – jedna linia w crontab. Raport zapisuje się w `exports/combined_report_*.json` i **można go wysłać emailem** flagą `--report-email` (ta sama konfiguracja SMTP w `.env` co dla ESP32).

**Przykład – codziennie o 3:00, raport na maila (zamień ścieżkę i adres):**
```cron
0 3 * * * cd /home/erno_jajo/medical-device-scanner-main && ./venv/bin/python src/scanner.py --audit --report-email twoj@email.me 2>&1 | logger -t scanner-audit
```

**Raz w tygodniu (niedziela 3:00) z mailem:**
```cron
0 3 * * 0 cd /home/erno_jajo/medical-device-scanner-main && ./venv/bin/python src/scanner.py --audit --report-email twoj@email.me 2>&1 | logger -t scanner-audit
```

Test ręczny: `cd /ścieżka/do/projektu && ./venv/bin/python src/scanner.py --audit --report-email twoj@email.me`  
Więcej flag: [FLAGI_NAJCZESCIEJ_UZYWANE.md](FLAGI_NAJCZESCIEJ_UZYWANE.md).
