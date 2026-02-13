# 📤 Raporty z Raspberry Pi na główny PC (do Splunka)

Skaner zapisuje raporty na Pi w katalogach `exports/` i `reports/`. Na głównym PC możesz mieć Splunk i wygodny podgląd. Oto szybkie i skuteczne sposoby przenoszenia plików.

---

## Metoda 1: PC pobiera z Pi (najprostsza)

Uruchamiasz komendę **na PC** – wtedy nie musisz nic konfigurować na Pi.

### Wymagania
- Pi i PC w tej samej sieci (WiFi/LAN).
- Na Pi włączony **SSH** (`sudo raspi-config` → Interface Options → SSH → Enable).
- Znasz adres Pi (np. `192.168.1.50`) i użytkownika (np. `pi`).

### Jednorazowe pobranie (scp)

Na **PC** (Linux/macOS w terminalu, na Windows: PowerShell lub np. WinSCP):

```bash
# Utwórz na PC folder na raporty (np. ~/splunk_import)
mkdir -p ~/splunk_import

# Pobierz wszystkie raporty SIEM z Pi (zamień pi@192.168.1.50 na swój login@adres_Pi)
scp pi@192.168.1.50:~/medical-device-scanner-main/exports/siem_export_*.jsonl ~/splunk_import/

# Opcjonalnie: pobierz też combined_report (do pełnego podglądu)
scp pi@192.168.1.50:~/medical-device-scanner-main/exports/combined_report_*.json ~/splunk_import/
```

Hasło: podaj hasło użytkownika `pi` gdy scp zapyta.

### Automatyczne pobieranie co jakiś czas (rsync)

**Na PC** – jeden raz ustaw, potem uruchamiaj ręcznie lub przez cron:

```bash
# Na PC: synchronizuj folder exports z Pi do ~/splunk_import
rsync -avz --include='siem_export_*.jsonl' --include='combined_report_*.json' --include='*/' --exclude='*' \
  pi@192.168.1.50:~/medical-device-scanner-main/exports/ \
  ~/splunk_import/
```

- **-a** – zachowaj daty/uprawnienia  
- **-v** – pokaż co kopiuje  
- **-z** – kompresja w trakcie transferu  

Żeby PC sam co dzień pobierał raporty (cron na PC):

```bash
crontab -e
# dodaj (zamień ścieżkę i adres Pi):
0 9 * * * rsync -az pi@192.168.1.50:~/medical-device-scanner-main/exports/*.jsonl ~/splunk_import/
```

---

## Metoda 2: Pi wysyła raporty na PC (automat po skanie)

Pi po skanie sam kopiuje pliki na PC. Wymaga **SSH z Pi do PC** (klucz bez hasła).

### Krok 1: Na PC – włącz SSH i przygotuj folder

**Linux na PC:**

```bash
# Zainstaluj serwer SSH (jeśli nie ma)
sudo apt install openssh-server   # Debian/Ubuntu

# Utwórz katalog na raporty
mkdir -p ~/splunk_import
```

**Windows na PC:** włącz „OpenSSH Server” (Ustawienia → Aplikacje → Opcjonalne funkcje) lub użyj WSL i tam katalog + sshd.

### Krok 2: Na Pi – klucz SSH do logowania na PC bez hasła

Na **Raspberry Pi**:

```bash
# Wygeneruj klucz (jeśli nie masz)
ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519

# Skopiuj klucz na PC (zamień PC_USER@PC_IP na np. janek@192.168.1.10)
ssh-copy-id PC_USER@PC_IP
```

Wpisz hasło do PC jeden raz – potem Pi będzie mógł się logować bez hasła.

### Krok 3: Skrypt na Pi do wysyłki raportów

Użyj skryptu z repozytorium:

```bash
# Na Pi, w katalogu projektu
./scripts/sync_reports_to_pc.sh
```

Przed pierwszym uruchomieniem ustaw w skrypcie (lub w zmiennych) **PC_USER** i **PC_IP** oraz **ścieżkę na PC** – szczegóły w sekcji „Skrypt sync_reports_to_pc.sh” poniżej.

### Krok 4: Automat po skanie (cron na Pi)

Żeby po każdym zaplanowanym skanie raporty od razu lądowały na PC:

```bash
crontab -e
```

Dodaj linię (np. skan o 3:00, potem sync):

```cron
0 3 * * * cd /home/pi/medical-device-scanner-main && ./venv/bin/python src/scanner.py --audit --report-email twoj@email.me && ./scripts/sync_reports_to_pc.sh
```

Albo osobno: skan o 3:00, sync o 3:45:

```cron
0 3 * * * cd /home/pi/medical-device-scanner-main && ./venv/bin/python src/scanner.py --audit --report-email twoj@email.me
45 3 * * * cd /home/pi/medical-device-scanner-main && ./scripts/sync_reports_to_pc.sh
```

---

## Metoda 3: Udział sieciowy (Samba) – folder Pi jako dysk na PC

Folder `exports/` z Pi pojawia się na PC jako zwykły katalog (dysk sieciowy). Splunk na PC może czytać pliki bez kopiowania (monitorowany katalog) albo możesz je kopiować ręcznie.

### Na Pi – udostępnij folder przez Sambę

```bash
sudo apt install samba
sudo mkdir -p /home/pi/medical-device-scanner-main/exports
```

Edytuj konfigurację Samby:

```bash
sudo nano /etc/samba/smb.conf
```

Na końcu pliku dodaj:

```ini
[scanner-exports]
path = /home/pi/medical-device-scanner-main/exports
browseable = yes
read only = yes
guest ok = no
valid users = pi
```

Zrestartuj Sambę:

```bash
sudo systemctl restart smbd
```

Ustaw hasło Samba dla użytkownika `pi` (do logowania z PC):

```bash
sudo smbpasswd -a pi
```

### Na PC – podłącz udział

- **Windows:** Eksplorator → Adres: `\\192.168.1.50\scanner-exports` (zamień na IP Pi). Zaloguj się użytkownikiem `pi` i hasłem Samba.
- **Linux:** w menedżerze plików „Połącz z serwerem” / `smb://192.168.1.50/scanner-exports` lub `mount -t cifs ...`.

W Splunk na PC możesz dodać monitorowany katalog wskazujący na ten udział (Settings → Data inputs → Files & Directories) lub kopiować stamtąd pliki do lokalnego `~/splunk_import` i importować je jak zwykle.

---

## Którą metodę wybrać?

| Sytuacja | Metoda |
|----------|--------|
| Chcę szybko raz pobrać pliki | **1 – scp** na PC |
| Chcę, żeby PC sam co dzień ściągał raporty | **1 – rsync + cron na PC** |
| Chcę, żeby Pi sam wysyłał na PC po skanie | **2 – skrypt + cron na Pi** |
| Chcę widzieć folder Pi na PC jak dysk | **3 – Samba** |

Do Splunka na PC wystarczą pliki **`siem_export_*.jsonl`** z `exports/`. Pełne raporty **`combined_report_*.json`** są dodatkowo do podglądu lub zaawansowanej analizy.

---

## Skrypt `scripts/sync_reports_to_pc.sh`

Skrypt kopiuje zawartość `exports/` z Pi na PC przez `rsync` (przez SSH).

**Przed pierwszym uruchomieniem** edytuj na początku skryptu zmienne:

- `PC_USER` – użytkownik na PC (np. `janek`)
- `PC_IP` – adres IP PC w sieci (np. `192.168.1.10`)
- `PC_PATH` – katalog na PC, do którego mają trafiać raporty (np. `~/splunk_import`)

Uruchomienie: w katalogu projektu na Pi: `./scripts/sync_reports_to_pc.sh`. Można dodać do crona jak w Metodzie 2.
