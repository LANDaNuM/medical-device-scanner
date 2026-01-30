# 🔌 Jak podłączyć wszystko od zera (dla początkujących)

Ten przewodnik wyjaśnia **krok po kroku**, jak fizycznie połączyć komputer, Raspberry Pi i ESP32, **bez ekranu** przy Pi i **bez zewnętrznego programatora** do ESP32.

---

## 📌 Najważniejsze na początek

1. **Nie łączysz wszystkiego w jeden łańcuch.**  
   Komputer, Raspberry Pi i ESP32 pracują osobno – łączysz je tylko wtedy, gdy coś robisz (programujesz / łączysz się zdalnie).

2. **Raspberry Pi bez ekranu = normalna sprawa.**  
   Do Pi wchodzisz **zdalnie** z komputera (SSH) albo konfigurujesz go **przed pierwszym uruchomieniem** na karcie (headless setup). Ekran nie jest potrzebny.

3. **ESP32 nie potrzebuje programatora.**  
   Twoja płytka ma **USB (CH340)** – programujesz ją jak pendrive: kabel USB z komputera do ESP32. Żadnego zewnętrznego programatora nie kupujesz.

Poniżej jest to rozpisane dokładnie.

---

## 1️⃣ Co do czego podłączasz (schemat)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  TWOJA SIEC DOMOWA (WiFi + opcjonalnie Ethernet)                        │
│                                                                         │
│   [Router WiFi]                                                         │
│        │                                                                 │
│        ├──────────────┬──────────────┬──────────────┐                  │
│        │              │              │              │                   │
│        ▼              ▼              ▼              ▼                   │
│   [Laptop/PC]    [Raspberry Pi]   [ESP32]     (telefon, inne)          │
│   (WiFi/Ethernet) (WiFi/Ethernet) (WiFi)                               │
│                                                                         │
│   • Wszystko w jednej sieci = mogą się "widzieć" (skaner, API, itd.)   │
└─────────────────────────────────────────────────────────────────────────┘

PROGRAMOWANIE / KONFIGURACJA (tylko gdy coś robisz):

   [Laptop/PC]  ──USB kabel──►  [ESP32]     → wgrywasz firmware (Arduino IDE)
   [Laptop/PC]  ──SSH (WiFi)──► [Raspberry Pi] → wpisujesz komendy, instalujesz
```

Czyli:
- **Na co dzień:** wszystko stoi w tej samej sieci WiFi (albo Pi po kablu do routera). Nie musisz mieć „komputer → Raspberry → mikrokontroler” w jednym fizycznym łańcuchu.
- **Gdy programujesz ESP32:** łączysz **tylko** komputer z ESP32 kablem USB.
- **Gdy konfigurujesz Raspberry Pi:** łączysz się do Pi **zdalnie** z komputera (SSH przez WiFi/Ethernet). Ekran do Pi nie jest potrzebny.

---

## 2️⃣ Raspberry Pi bez ekranu – skąd wiesz, co się instaluje?

Pi **nie musi** mieć podłączonego monitora. Masz dwie drogi.

### Opcja A: Konfiguracja „headless” przed pierwszym włączeniem (najprostsza)

1. **Karta pamięci (128 GB)** – włożysz ją do komputera (przez adapter USB).
2. **Program Raspberry Pi Imager** (na komputerze):
   - Pobierz: https://www.raspberrypi.com/software/
   - Uruchom, wybierz **Raspberry Pi OS** (np. z desktopem lub bez – do skanera wystarczy wersja „Lite”).
   - **Ważne:** w Imagerze jest ikona **„Ustawienia” (tryb zaawansowany)**. Tam możesz:
     - włączyć **SSH** (logowanie: `pi` / hasło które ustawisz),
     - ustawić **nazwę hosta** (np. `medical-scanner`),
     - skonfigurować **WiFi** (nazwa sieci + hasło),
     - ustawić **użytkownika i hasło**.
   - Zapisz system na karcie.
3. **Włóż kartę do Raspberry Pi**, podłącz Pi **zasilaczem** i **WiFi** (lub kablem Ethernet do routera). Nie podłączasz monitora.
4. **Poczekaj 2–5 minut** aż Pi się uruchomi i połączy z WiFi.
5. **Z komputera** (w tej samej sieci WiFi) połączysz się przez **SSH** – wtedy „widzisz”, co się instaluje, bo wszystkie komendy wpisujesz na swoim laptopie.

### Opcja B: Ekran tylko raz (jeśli masz TV/monitor z HDMI)

- Podłącz Pi do monitora/TV kablem HDMI, klawiaturę USB.
- Włącz Pi, zaloguj się, włącz SSH i WiFi w ustawieniach.
- Potem możesz odłączyć ekran i dalej pracować tylko przez SSH z komputera.

**Podsumowanie:** „Co się instaluje” widzisz na **ekranie swojego komputera** – w oknie terminala/SSH, gdzie wpisujesz komendy (`sudo apt install ...`, `pip install ...`, itd.). Na Pi nie musi być żadnego ekranu.

---

## 3️⃣ Jak połączyć się z Raspberry Pi przez SSH (bez ekranu)

### Co wpisać – IP czy nazwa?
**Opcja 1: Użyj nazwy hosta (najprostsze – nie musisz znać IP)**  
W Imagerze w **Hostname** ustawiłeś np. `medicalscanner`. Wtedy łączysz się tak:

```bash
ssh UŻYTKOWNIK@medicalscanner.local
```

Zamień **UŻYTKOWNIK** na login z sekcji **User** w Imagerze (np. `pi` albo ten, który podałeś).  
Przykład: `ssh pi@medicalscanner.local`  
Hasło = to z sekcji **User** w Imagerze.

**Opcja 2: Użyj adresu IP**  
Jeśli `nazwa.local` nie działa, potrzebujesz IP Raspberry Pi. Możesz je znaleźć tak:

- **Router:** wejdź w panel routera (np. 192.168.1.1 lub 192.168.0.1), lista urządzeń / DHCP – szukaj „raspberrypi” lub ustawionej nazwy hosta. Obok będzie IP, np. `192.168.1.105`.
- **Skanowanie sieci z komputera** (Linux/Mac): `ping medicalscanner.local` – często wyświetli się IP. Albo: `arp -a` po kilku minutach od włączenia Pi.
- **Windows:** w routerze albo użyj `ping medicalscanner.local` w PowerShell – czasem pokaże IP.

Potem łączysz się:

```bash
ssh UŻYTKOWNIK@192.168.1.105
```

(zamień `192.168.1.105` na IP Twojego Pi i `UŻYTKOWNIK` na swój login).

---

**Krok po kroku:**

1. **Sprawdź, czy Pi jest w tej samej sieci** co komputer (WiFi lub Ethernet do tego samego routera).
2. **Na komputerze** otwórz terminal (Linux/Mac) albo PowerShell (Windows). Wpisz:
   - `ssh pi@medicalscanner.local` (jeśli hostname to `medicalscanner`),
   - albo `ssh pi@192.168.1.XXX` (gdy znasz IP).
3. Przy pierwszym połączeniu zapyta „Are you sure...?” – wpisz `yes` i Enter.
4. Podaj **hasło** z Imagera (sekcja User). Przy wpisywaniu nic się nie wyświetla – to normalne, wpisz i Enter.
5. **Jak się połączysz**, wszystkie kolejne komendy (`sudo apt update`, `pip install`, `git clone`, `python src/scanner.py`) wpisujesz w tym oknie – wykonują się **na Pi**. Dlatego „wiesz, co się instaluje” – widzisz to w terminalu.

Dokładną listę komend do instalacji projektu na Pi masz w `docs/WYKORZYSTANIE_ESP32_RASPBERRY_PI.md` (sekcja „Raspberry Pi 5 jako Główny Serwer”).

---

## 4️⃣ Programowanie ESP32 – czy potrzebny jest programator?

**Nie.** Twoja płytka to **ESP32 z USB (CH340)** – ma wbudowany układ, który przez zwykły port USB „udaje” programator.

- **Potrzebujesz tylko:**  
  - komputera z Arduino IDE (lub PlatformIO),  
  - kabla **USB (USB-A lub USB-C)** od komputera do ESP32.

**Podłączenie:**  
Komputer ←── kabel USB ──→ ESP32 (port USB na płytce).

**Co zrobić w komputerze:**
1. Zainstalować sterownik **CH340** (jeśli system go nie wykrywa):
   - Windows: często trzeba doinstalować (wyszukaj „CH340 driver Windows”).
   - Linux: zwykle działa od razu; czasem trzeba dodać użytkownika do grupy `dialout`:  
     `sudo usermod -a -G dialout $USER` i wylogować się / zrestartować.
2. W Arduino IDE:  
   **Narzędzia → Płytka → ESP32 Arduino → ESP32 Dev Module**  
   oraz **Narzędzia → Port** → wybrać port, który pojawił się po podłączeniu ESP32 (np. `COM3` w Windows, `/dev/ttyUSB0` w Linux).
3. Otworzyć przykładowy `.ino` z `esp32_examples/`, wcisnąć **Upload**.

Żadnego zewnętrznego programatora (JTAG, USBasp itp.) **nie** kupujesz ani nie podłączasz.

---

## 5️⃣ Kolejność działań (co robić po kolei)

| Krok | Gdzie | Co robisz |
|------|--------|-----------|
| 1 | **Komputer** | Pobierz Raspberry Pi Imager, nagraj OS na kartę z włączonym SSH i WiFi. |
| 2 | **Raspberry Pi** | Włóż kartę, podłącz zasilanie i sieć (WiFi lub Ethernet). Bez ekranu. |
| 3 | **Komputer** | Po kilku minutach: `ssh pi@medical-scanner.local` (lub `ssh pi@IP_PI`). |
| 4 | **Przez SSH (na Pi)** | Zainstaluj system (apt), Pythona, git, sklonuj projekt, venv, `pip install -r requirements.txt` – komendy z `WYKORZYSTANIE_ESP32_RASPBERRY_PI.md`. |
| 5 | **Komputer** | Zainstaluj Arduino IDE, dodaj obsługę ESP32, sterownik CH340 jeśli trzeba. |
| 6 | **Komputer + ESP32** | Podłącz ESP32 **tylko** do komputera USB. W Arduino IDE wybierz płytkę i port, wgraj np. `ESP32_Glukometr_BLE.ino`. |
| 7 | **Sieć** | Upewnij się, że Raspberry Pi i ESP32 (po wgraniu programu z WiFi) są w **tej samej sieci WiFi** co komputer. |
| 8 | **Raspberry Pi (przez SSH)** | Uruchom skaner: `python src/scanner.py --ble --wifi`. Wtedy Pi „zobaczy” ESP32 w sieci / po BLE. |

Nie ma etapu „komputer → Raspberry → mikrokontroler” jako jednego kabla. Jest:  
- **komputer ↔ Pi** przez sieć (SSH),  
- **komputer ↔ ESP32** przez USB (tylko przy programowaniu).

---

## 6️⃣ Potrzebne kable i akcesoria (minimalnie)

| Co | Do czego |
|----|----------|
| Karta microSD (np. 32–128 GB) | Raspberry Pi (w zestawie masz 128 GB). |
| Zasilacz do Raspberry Pi 5 | Oficjalny lub zgodny (np. 5 V / 5 A, USB-C). |
| Kabel Ethernet (opcjonalnie) | Łatwiejsze pierwsze uruchomienie Pi (router → Pi). |
| **Kabel USB (USB-A lub USB-C)** | **Komputer ↔ ESP32** (programowanie). Do Pi nie łączysz ESP32 kablem. |
| (Opcjonalnie) Monitor HDMI + kabel | Tylko jeśli chcesz raz skonfigurować Pi z ekranem. |

Żadnego programatora zewnętrznego do ESP32 nie potrzebujesz.

---

## 7️⃣ Gdzie szukać dalszych instrukcji

- **Raspberry Pi (instalacja systemu, SSH):**  
  https://www.raspberrypi.com/documentation/computers/getting-started.html  
- **Raspberry Pi Imager (w tym headless / WiFi / SSH):**  
  https://www.raspberrypi.com/software/
- **Instalacja projektu na Pi (komendy):**  
  `docs/WYKORZYSTANIE_ESP32_RASPBERRY_PI.md` w tym repo.
- **ESP32 w Arduino IDE (płytki, port):**  
  `esp32_examples/README.md` w tym repo.

---

## 8️⃣ Jedna lista komend do wklejenia na Raspberry Pi (przez SSH)

Po połączeniu z Pi (`ssh pi@medical-scanner.local` lub `ssh pi@IP_PI`) możesz wkleić poniższe bloki **po kolei** (nie wszystko naraz, jeśli nie znasz się na tym – każdy blok to jeden etap).

**1) Aktualizacja systemu i instalacja podstawowych narzędzi:**
```bash

```

**2) Sklonowanie projektu:**

- **Jeśli repozytorium jest PUBLICZNE** – nie podawaj loginu ani hasła, po prostu:
  ```bash
  cd ~
  git clone https://github.com/LANDaNuM/medical-device-scanner.git medical-device-scanner-main
  cd medical-device-scanner-main
  ```
  (GitHub nie przyjmuje już zwykłego hasła; do publicznego repo nie trzeba się logować.)

- **Jeśli repozytorium jest PRYWATNE** – zamiast hasła musisz użyć **Personal Access Token (PAT)**:
  1. GitHub → Settings → Developer settings → Personal access tokens → Generate new token.
  2. Zaznacz zakres np. `repo`.
  3. Skopiuj token (wygląda jak `ghp_xxxxxxxx`). Przy `git clone` lub przy pierwszym `git push` jako **hasło** wklej ten token (nie hasło do konta).
  Alternatywa: skopiuj folder projektu na Pendrive i na Pi wgraj do `~/medical-device-scanner-main`.

**3) Środowisko Python i zależności:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

**4) Test skanera (BLE + WiFi):**
```bash
source venv/bin/activate
python src/scanner.py --ble --wifi
```

Za każdym razem gdy się logujesz przez SSH i chcesz uruchomić skaner, wpisujesz:
```bash
cd ~/medical-device-scanner-main
source venv/bin/activate
python src/scanner.py --ble --wifi
```

**Jeśli przy WiFi skaner pisze „Używam podstawowego skanowania (ping + socket)”:**  
Na Linuxie (w tym Raspberry Pi) **skanowanie ARP** (wykrywanie hostów po adresach MAC) wymaga **uprawnień root**. Bez tego używane jest tylko podstawowe skanowanie (ping + porty). Żeby włączyć pełne skanowanie WiFi (scapy + ARP), uruchom **z zachowaniem venv**:
```bash
cd ~/medical-device-scanner-main
source venv/bin/activate
sudo -E python3 src/scanner.py --ble --wifi
```
`-E` sprawia, że sudo nie resetuje zmiennych środowiskowych – Python i pakiety z venv nadal działają. Po podaniu hasła do sudo skaner użyje scapy i ARP zamiast tylko ping + socket.

To jest **wszystko**, co „instaluje się” na Raspberry Pi w tym projekcie – widzisz to w oknie SSH na swoim komputerze. Ekran przy Pi nie jest potrzebny.

---

## 9️⃣ Rozwiązywanie problemów: „No route to host”, Raspberry nie widać w routerze

Jeśli **SSH zwraca „No route to host”** albo **w routerze nie ma Raspberry na liście urządzeń**, to Pi **w ogóle nie jest w sieci** – router go nie widzi. Sprawdź po kolei:

### 1. Zasilanie
- **Raspberry Pi 5** potrzebuje dobrego zasilacza (np. oficjalny 27 W / 5 V). Słaby zasilacz = Pi się restartuje albo nie wstaje, wtedy nie dostanie IP.
- Sprawdź, czy **czerwona dioda (PWR)** na płytce się świeci i nie mruga w kółko (miganie = problem z zasilaniem).
- Zielona dioda (ACT) może mrugać przy odczycie karty – to normalne.

### 2. Czy Pi w ogóle się uruchamia?
- Odłącz zasilanie, odczekaj 10 s, podłącz ponownie.
- Poczekaj **3–5 minut** – pierwszy start lub po długiej przerwie trwa dłużej.
- Jeśli masz **monitor HDMI** – podłącz na chwilę i zobacz, czy jest obraz (boot, logowanie). Jeśli nie ma obrazu w ogóle, problem może być z kartą lub zasilaniem.

### 3. WiFi vs Ethernet
- **Jeśli Pi łączy się przez WiFi:** w Imagerze musiały być ustawione **dokładna nazwa sieci (SSID)** i **hasło**. Literówka = brak sieci. Router ma tę samą sieć co wczoraj? (np. nie przełączyłeś na „Gość" albo inny WiFi?) WiFi czasem się „gubi” po restarcie routera lub Pi – wtedy Pi nie pojawia się w sieci mimo że wczoraj działało.
- **Jeśli masz kabel Ethernet:** podłącz Pi **bezpośrednio do routera**. Urządzenie zwykle od razu dostaje IP i widać je w routerze – połączenie SSH działa od razu. **Ethernet jest pewniejszy** niż WiFi przy pracy bez ekranu (brak problemów z WiFi po restarcie). W razie „no route to host” lub braku Pi w routerze – najpierw spróbuj LAN.

### 4. Karta SD
- Uszkodzona lub uszkodzony system na karcie = Pi nie bootuje albo nie ładuje sieci. Możesz **przetestować**: wyciągnij kartę, włóż do komputera i sprawdź, czy widać partycję `boot` (i ewentualnie `rootfs`). Jeśli karta się nie pokazuje lub nie da się odczytać, spróbuj **nagrania systemu od zera** w Raspberry Pi Imager (z WiFi, User, SSH), potem włożenia karty do Pi i cierpliwego czekania 5 minut.

### 5. Router
- Odśwież listę urządzeń w routerze (czasem trzeba odświeżyć stronę lub wejść ponownie).
- Sprawdź, czy nie ma **blokady MAC** albo **limitu liczby urządzeń** – wtedy nowe urządzenie nie dostanie IP i nie pojawi się na liście.

### 6. Co zrobić krok po kroku (bez monitora)
1. **Zasilacz** – upewnij się, że to odpowiedni zasilacz do Pi 5.
2. **Ethernet** – jeśli możesz, podłącz Pi kablem do routera, odczekaj 5 minut, sprawdź listę urządzeń w routerze.
3. **Jeśli nadal brak:** wyciągnij kartę, w komputerze **przeładuj obraz w Imagerze** z ustawieniem **Wi‑Fi** (SSID + hasło) i **SSH**, zapisz na kartę, włóż z powrotem do Pi i włącz. Poczekaj 5 minut i znów sprawdź router.
4. **Jeśli masz monitor HDMI** – podłącz na chwilę, żeby zobaczyć, czy Pi w ogóle startuje i czy nie ma błędów sieci (np. „could not connect to WiFi”).

„No route to host” przy tej samej komendzie co wczoraj zwykle oznacza, że **Pi dziś nie ma adresu IP** – albo nie wystartował, albo nie połączył się z siecią (WiFi/Ethernet). Najpierw doprowadź do tego, żeby **Raspberry pojawił się w routerze**; wtedy SSH i ta sama komenda znów zadziałają.
