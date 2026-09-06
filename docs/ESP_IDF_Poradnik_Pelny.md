# ESP‑IDF — Kompletny poradnik + projekt

## Część 1: Instalacja ESP‑IDF na RPi5

Wykonaj poniższe kroki w terminalu RPi5.

### Krok 1: Zainstaluj wymagane pakiety systemowe

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3-pip python3-venv build-essential cmake pkg-config libusb-1.0-0-dev
```

### Krok 2: Pobierz ESP‑IDF (oficjalny framework)

```bash
cd ~
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
```

To pobranie zajmie kilka minut (repozytorium jest duże, ~500 MB).

### Krok 3: Uruchom instalator (pobierze toolchain i biblioteki)

```bash
./install.sh
```

To może zająć 5–10 minut. Pobierze ~1.5 GB toolchain'a (kompilator GCC dla ESP32).

### Krok 4: Aktywuj środowisko (zawsze gdy chcesz pracować z ESP‑IDF)

W każdej nowej sesji terminala wykonaj:

```bash
cd ~/esp-idf
source export.sh
```

To dodaje narzędzia ESP‑IDF do PATH i ustawia zmienne środowiskowe.

### Krok 5: Stwórz katalog na projekty

```bash
mkdir -p ~/projects/esp-wifi-ble-sniffer
cd ~/projects/esp-wifi-ble-sniffer
```

---

## Część 2: Struktura projektu

W katalogu `~/projects/esp-wifi-ble-sniffer/` będą następujące pliki:

```
esp-wifi-ble-sniffer/
├── CMakeLists.txt                 # konfiguracja budowy
├── Kconfig.projbuild              # opcje konfiguracyjne
├── main/
│   ├── CMakeLists.txt
│   ├── wifi_ble_sniffer.c         # główny kod
│   └── Kconfig.in
├── sdkconfig                      # wygenerowane po `idf.py menuconfig`
└── build/                         # katalog budów (tworzony automatycznie)
```

---

## Część 3: Tworzenie plików projektu

Poniżej skopiuj każdy plik dokładnie tak, jak pokazany.

### Plik 1: `CMakeLists.txt` (katalog główny)

```cmake
# Główny plik konfiguracji budowy dla ESP‑IDF
# Ten plik mówi systemowi budowania jak kompilować projekt

cmake_minimum_required(VERSION 3.16)

# Zaimportuj build system ESP‑IDF
include($ENV{IDF_PATH}/tools/cmake/project.cmake)

# Nazwa projektu
project(esp_wifi_ble_sniffer)

# Katalog, gdzie znajduje się kod (main/)
add_subdirectory(main)
```

### Plik 2: `main/CMakeLists.txt`

```cmake
# Plik konfiguracji budowy dla komponentu main (naszego kodu)

idf_component_register(
    SRCS "wifi_ble_sniffer.c"          # plik źródłowy C do kompilacji
    INCLUDE_DIRS "."                   # katalogi nagłówków
    REQUIRES esp_wifi esp_ble          # wymagane komponenty ESP‑IDF (Wi‑Fi, BLE)
)
```

### Plik 3: `Kconfig.projbuild` (opcje projektu)

```
# Konfiguracja właściwa dla tego projektu
# Ten plik definiuje opcje, które možesz zmienić via `idf.py menuconfig`

menu "WiFi BLE Sniffer Config"

    config WIFI_CHANNEL
        int "WiFi Channel to scan"
        default 6
        range 1 13
        help
            Kanał Wi‑Fi do skanowania (1-13 dla 2.4 GHz).

    config SERIAL_BAUD
        int "Serial baud rate"
        default 115200
        help
            Szybkość portu szeregowego (baud).

endmenu
```

### Plik 4: `main/Kconfig.in` (pusty plik dla kompatybilności)

```
# Pusty plik — wymagany przez ESP‑IDF
```

### Plik 5: `main/wifi_ble_sniffer.c` (główny kod)

```c
/*
 * WiFi + BLE Sniffer dla ESP32
 * Zbiera pełne ramki 802.11 (Wi-Fi) i reklamy BLE
 * Wypisuje dane w formacie JSON po Serial (115200 bps)
 * 
 * Kod kompilowany dla ESP32 w ESP-IDF
 */

// === Nagłówki systemowe i bibliotek ===
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

// === Nagłówki ESP-IDF ===
#include "freertos/FreeRTOS.h"                    // system czasu rzeczywistego (RTOS)
#include "freertos/task.h"                        // obsługa tasków (wątków)
#include "esp_wifi.h"                             // API Wi-Fi
#include "esp_event.h"                            // system zdarzeń ESP
#include "esp_log.h"                              // logowanie
#include "nvs_flash.h"                            // pamięć nieulotna (ustawienia)
#include "esp_bt.h"                               // Bluetooth (inicjalizacja)
#include "esp_gap_ble_api.h"                      // BLE GAP (Generic Access Profile)
#include "esp_gattc_api.h"                        // BLE GATT client

// === Tagi dla logowania ===
static const char *TAG_WIFI = "WiFi_Sniffer";
static const char *TAG_BLE = "BLE_Sniffer";

// === Deklaracje zmiennych globalnych ===
static uint32_t packet_count = 0;                 // licznik pakietów (int counter)
static uint32_t ble_adv_count = 0;                // licznik reklam BLE

/*
 * Callback wywoływany przez ESP-IDF gdy radio Wi-Fi odbierze pakiet w trybie promiscuous
 * 
 * Argumenty:
 *   - buf: wskaźnik na strukturę wifi_promiscuous_pkt_t (zawiera ramkę i metadane)
 *   - type: typ pakietu (WIFI_PKT_MGMT, WIFI_PKT_DATA, WIFI_PKT_CTRL)
 */
static void wifi_promiscuous_pkt_handler(void *buf, wifi_promiscuous_pkt_type_t type)
{
    // Rzutuj buf na strukturę dostarczoną przez SDK
    wifi_promiscuous_pkt_t *pkt = (wifi_promiscuous_pkt_t *)buf;
    
    // Wyciągnij metadane z pakietu
    int rssi = pkt->rx_ctrl.rssi;                 // siła sygnału (Received Signal Strength Indicator)
    uint8_t channel = pkt->rx_ctrl.channel;       // kanał Wi-Fi (1-13 na 2.4 GHz)
    uint32_t sig_len = pkt->rx_ctrl.sig_len;      // długość sygnału w bitach
    
    // Wskaźnik na payload (surowe bajty ramki 802.11)
    uint8_t *payload = pkt->payload;
    
    // Struktura nagłówka 802.11 (uproszczona)
    // Bajty 0-3:   Frame Control + Flags
    // Bajty 4-5:   Duration/ID
    // Bajty 6-11:  Adres 1 (BSSID lub receiver)
    // Bajty 12-17: Adres 2 (sender/source MAC)
    // Bajty 18-23: Adres 3 (transmitter/BSSID)
    // ...
    
    // Bezpieczne sprawdzenie minimalnej długości
    if (sig_len < 24) {
        return;  // Za krótka, pomiń
    }
    
    // Wyciągnij MAC źródła (Address 2, bajty 10-15 w typowych ramkach management)
    // UWAGA: pozycja zmienia się w zależności od typu ramki, ale 10-15 to częsty wzór
    uint8_t *source_mac = &payload[10];
    
    // Wyciągnij MAC celu (Address 1, bajty 4-9)
    uint8_t *dest_mac = &payload[4];
    
    // Wyciągnij Frame Control (bajty 0-1) do określenia typu ramki
    uint16_t frame_control = (payload[1] << 8) | payload[0];
    
    // Wyciągnij typ ramki (bity 2-3 z Frame Control)
    uint8_t frame_type = (frame_control >> 2) & 0x03;
    
    // Wypisz JSON do Serial (RPi będzie to czytać linia po linii)
    printf(
        "{\"type\":\"wifi\",\"src_mac\":\"%02X:%02X:%02X:%02X:%02X:%02X\","
        "\"dst_mac\":\"%02X:%02X:%02X:%02X:%02X:%02X\","
        "\"rssi\":%d,\"channel\":%u,\"len\":%lu,\"frame_type\":%u}\n",
        source_mac[0], source_mac[1], source_mac[2], source_mac[3], source_mac[4], source_mac[5],
        dest_mac[0], dest_mac[1], dest_mac[2], dest_mac[3], dest_mac[4], dest_mac[5],
        rssi, channel, sig_len, frame_type
    );
    
    // Inkrementuj licznik (dla diagnostyki)
    packet_count++;
}

/*
 * Callback wywoływany przez stack BLE gdy wykryje reklamę urządzenia BLE
 * 
 * Argumenty:
 *   - event: typ zdarzenia GAP (np. ESP_GAP_BLE_SCAN_RESULT_EVT)
 *   - param: parametry zdarzenia (zawierają dane reklamy)
 */
static void gap_event_handler(esp_gap_ble_cb_event_t event, esp_ble_gap_cb_param_t *param)
{
    // Sprawdź typ zdarzenia — nas interesuje ESP_GAP_BLE_SCAN_RESULT_EVT (nowa reklama odkryta)
    if (event == ESP_GAP_BLE_SCAN_RESULT_EVT) {
        // Wyciągnij parametry wyniku skanowania
        esp_ble_gap_cb_param_t *scan_result = (esp_ble_gap_cb_param_t *)param;
        
        // Sprawdź typ wyniku: search_evt (urządzenie odkryte) vs search_cmpl (skanowanie skończone)
        switch (scan_result->scan_rst.search_evt) {
            case ESP_GAP_SEARCH_INQ_RES_EVT: {
                // Wyciągnij dane reklamy BLE
                uint8_t *bda = scan_result->scan_rst.bda;           // Bluetooth Device Address (MAC)
                int rssi = scan_result->scan_rst.rssi;              // siła sygnału
                uint8_t adv_data_len = scan_result->scan_rst.ble_adv_data_len; // długość danych reklamy
                uint8_t *adv_data = scan_result->scan_rst.ble_adv;  // surowe dane reklamy
                
                // Wypisz JSON
                printf(
                    "{\"type\":\"ble\",\"mac\":\"%02X:%02X:%02X:%02X:%02X:%02X\","
                    "\"rssi\":%d,\"adv_data_len\":%u}\n",
                    bda[0], bda[1], bda[2], bda[3], bda[4], bda[5],
                    rssi, adv_data_len
                );
                
                ble_adv_count++;
                break;
            }
            
            case ESP_GAP_SEARCH_INQ_CMPL_EVT:
                // Skanowanie BLE zostało ukończone (periodycznie w trybie ciągłym)
                // Możesz dodać logowanie statusu jeśli chcesz
                printf("{\"type\":\"ble_status\",\"message\":\"scan_cycle_complete\"}\n");
                break;
            
            default:
                // Inne typy zdarzeń (np. błędy) — ignoruj
                break;
        }
    }
}

/*
 * Inicjalizacja Wi-Fi w trybie promiscuous (sniffer)
 * Urządzenie nie łączy się z AP, tylko słucha wszystkich ramek na wybranym kanale
 */
static void wifi_init_promiscuous(uint8_t channel)
{
    // Utwórz default Wi-Fi konfigurację
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    
    // Zainicjalizuj Wi-Fi stack
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    
    // Ustaw tryb WiFi: WIFI_MODE_NULL = bez łączenia (tylko promiscuous)
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_NULL));
    
    // Włącz promiscuous mode (receiver słucha wszystkich ramek na kanale)
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous(true));
    
    // Ustaw callback — funkcja wywoływana przy każdym odebranym pakiecie
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous_rx_cb(&wifi_promiscuous_pkt_handler));
    
    // (Opcjonalnie) Ustaw filtr promiscuous — NULL = brak filtrowania (wszystkie typy)
    wifi_promiscuous_filter_t filter = {0};
    filter.mask = WIFI_PROMISCUOUS_FILTER_ALL; // otrzymuj wszystkie typy ramek
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous_filter(&filter));
    
    // Uruchom Wi-Fi radio
    ESP_ERROR_CHECK(esp_wifi_start());
    
    // Ustaw kanał Wi-Fi (1-13 na 2.4 GHz; 36-165 na 5 GHz — ale ESP32 zwykle obsługuje 1-14)
    ESP_ERROR_CHECK(esp_wifi_set_channel(channel, WIFI_SECOND_CHAN_NONE));
    
    ESP_LOGI(TAG_WIFI, "WiFi promiscuous mode started on channel %d", channel);
}

/*
 * Inicjalizacja BLE (Bluetooth Low Energy)
 * Konfiguracja GAP (Generic Access Profile) do skanowania reklam
 */
static void ble_init(void)
{
    // Zainicjalizuj kontroler Bluetooth (warstwa fizyczna)
    esp_bt_controller_config_t bt_cfg = BT_CONTROLLER_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_bt_controller_init(&bt_cfg));
    
    // Włącz kontroler
    ESP_ERROR_CHECK(esp_bt_controller_enable(ESP_BT_MODE_BLE));
    
    // Zainicjalizuj Bluedroid stack (protokół BLE)
    ESP_ERROR_CHECK(esp_bluedroid_init());
    
    // Włącz Bluedroid
    ESP_ERROR_CHECK(esp_bluedroid_enable());
    
    // Zarejestruj callback dla zdarzeń GAP (gdy reklama BLE zostanie odkryta)
    ESP_ERROR_CHECK(esp_ble_gap_register_callback(gap_event_handler));
    
    // Skonfiguruj parametry skanowania BLE
    esp_ble_scan_params_t scan_params = {
        .scan_type = BLE_SCAN_TYPE_PASSIVE,       // pasywne skanowanie (słuchaj, nie pytaj)
        .own_addr_type = BLE_ADDR_TYPE_RANDOM,    // użyj losowego adresu
        .scan_filter_policy = BLE_SCAN_FILTER_ALLOW_ALL, // przyjmuj reklamy od wszystkich
        .scan_interval = 0x50,                    // interwał skanowania (~80 ms)
        .scan_window = 0x30,                      // okno skanowania (~48 ms)
        .scan_duplicate = BLE_SCAN_DUPLICATE_DISABLE, // raportuj każdą reklamę (nawet duplikaty)
    };
    
    // Włącz skanowanie BLE z powyższymi parametrami
    // 0 = skanowanie ciągłe (nie skończone)
    ESP_ERROR_CHECK(esp_ble_gap_start_scanning(0, &scan_params, ESP_BLE_SCAN_DUPLICATE_DISABLE));
    
    ESP_LOGI(TAG_BLE, "BLE scanning started");
}

/*
 * Główna funkcja aplikacji — wywoływana raz przy starcie
 */
void app_main(void)
{
    // Wypisz komunikat startowy
    printf("\n\n========== ESP32 WiFi + BLE Sniffer ==========\n");
    printf("Urządzenie: ESP32\n");
    printf("Funkcja: Zbieranie ramek WiFi (promiscuous) i reklam BLE\n");
    printf("Format wyjścia: JSON per linia na Serial (115200 bps)\n");
    printf("============================================\n\n");
    
    // === Inicjalizacja NVS (Non-Volatile Storage) ===
    // Wymagane dla Wi-Fi i BLE
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        // Jeśli NVS jest uszkodzony, wymaż i zainicjalizuj ponownie
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
    
    // === Inicjalizacja event loop (obsługa zdarzeń systemowych) ===
    // Potrzebna do obsługi zdarzeń Wi-Fi i BLE
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    
    // === Inicjalizacja Wi-Fi w trybie promiscuous ===
    // Kanał pobierz z konfiguracji (menuconfig) lub ustaw na stałe
    uint8_t channel = 6; // domyślny kanał (2.437 GHz)
    wifi_init_promiscuous(channel);
    
    // === Inicjalizacja BLE ===
    ble_init();
    
    // === Główna pętla aplikacji ===
    // Wypisz statystyki co 10 sekund
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(10000)); // poczekaj 10 sekund (pdMS_TO_TICKS konwertuje ms na ticki RTOS)
        printf("{\"type\":\"status\",\"wifi_packets\":%lu,\"ble_adverts\":%lu}\n", packet_count, ble_adv_count);
    }
}
```

---

## Część 4: Kompilacja i wgrywanie

Gdy masz już wszystkie pliki w `~/projects/esp-wifi-ble-sniffer/`, wykonaj:

### Krok 1: Przygotuj środowisko

```bash
cd ~/projects/esp-wifi-ble-sniffer
source ~/esp-idf/export.sh
```

### Krok 2: Ustaw target (ESP32)

```bash
idf.py set-target esp32
```

### Krok 3: Kompilacja

```bash
idf.py build
```

To może zająć 1–2 minuty przy pierwszej kompilacji (potem będzie szybciej).

### Krok 4: Sprawdź port USB (podłącz ESP32)

```bash
dmesg | tail
ls /dev/ttyUSB*  # lub /dev/ttyACM*
```

Zapamiętaj port (np. `/dev/ttyUSB0`).

### Krok 5: Wgraj firmware na ESP32

```bash
idf.py -p /dev/ttyUSB0 flash
```

Zamień `/dev/ttyUSB0` na Twój port. Proces wgrywania zajmie ~10–30 sekund.

### Krok 6: Monitor — zobacz wynik w real-time

```bash
idf.py -p /dev/ttyUSB0 monitor
```

Zobaczysz JSON‑line w real-time:
```
========== ESP32 WiFi + BLE Sniffer ==========
Urządzenie: ESP32
...
{"type":"wifi","src_mac":"AA:BB:CC:DD:EE:FF",...
{"type":"ble","mac":"11:22:33:44:55:66",...
```

Aby wyjść z monitora: `Ctrl + ]`

---

## Część 5: Zbieranie danych do pliku CSV (skrypt Python na RPi)

Na RPi stwórz plik `read_sniffer_serial.py`:

```python
#!/usr/bin/env python3
"""
Czyta dane JSON ze Serial (z ESP32) i zapisuje do CSV
Wymagane: pip install pyserial pandas
"""

import serial
import json
import csv
import time
from datetime import datetime
from pathlib import Path

SERIAL_PORT = "/dev/ttyUSB0"    # dostosuj do Twojego portu
BAUDRATE = 115200
OUTPUT_CSV = "sniffer_capture.csv"

def ensure_csv_header():
    """Stwórz CSV z nagłówkami jeśli nie istnieje"""
    if not Path(OUTPUT_CSV).exists():
        with open(OUTPUT_CSV, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp_iso",
                "type",
                "src_mac",
                "dst_mac",
                "mac",
                "rssi",
                "channel",
                "length",
                "frame_type",
                "adv_data_len",
                "message",
                "raw_json"
            ])
        print(f"[INFO] Stworzony plik: {OUTPUT_CSV}")

def read_and_save():
    """Odczyt Serial → parseowanie JSON → zapis CSV"""
    try:
        with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=2) as ser:
            print(f"[INFO] Podłączony do {SERIAL_PORT} @ {BAUDRATE} bps")
            print(f"[INFO] Zapisuję do {OUTPUT_CSV}")
            print("[INFO] Naciśnij Ctrl+C aby zatrzymać\n")
            
            while True:
                try:
                    # Czytaj linia po linii
                    line = ser.readline().decode('utf-8', errors='replace').strip()
                    
                    if not line:
                        continue
                    
                    # Timestamp ISO
                    ts = datetime.utcnow().isoformat()
                    
                    # Spróbuj parsować JSON
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        # Jeśli nie jest JSON, zapisz jako raw
                        with open(OUTPUT_CSV, "a", newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow([ts, "", "", "", "", "", "", "", "", "", "", line])
                        print(f"[RAW] {line}")
                        continue
                    
                    # Wyciągnij pola (mogą być puste w zależności od typu)
                    t = obj.get("type", "")
                    src_mac = obj.get("src_mac", "")
                    dst_mac = obj.get("dst_mac", "")
                    mac = obj.get("mac", "")
                    rssi = obj.get("rssi", "")
                    channel = obj.get("channel", "")
                    length = obj.get("len", "")
                    frame_type = obj.get("frame_type", "")
                    adv_data_len = obj.get("adv_data_len", "")
                    message = obj.get("message", "")
                    
                    # Zapisz do CSV
                    with open(OUTPUT_CSV, "a", newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            ts, t, src_mac, dst_mac, mac, rssi, channel, length,
                            frame_type, adv_data_len, message, line
                        ])
                    
                    # Wypisz na konsolę (dla diagnostyki)
                    print(f"[{t.upper()}] {ts} | RSSI: {rssi} | MAC: {mac or src_mac}")
                
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(f"[ERROR] {e}")
                    time.sleep(0.5)
    
    except serial.SerialException as e:
        print(f"[ERROR] Błąd Serial: {e}")
    except KeyboardInterrupt:
        print("\n[INFO] Zatrzymano. Dane zapisane do CSV.")

if __name__ == "__main__":
    ensure_csv_header()
    read_and_save()
```

Uruchom:

```bash
pip install pyserial pandas
python3 read_sniffer_serial.py
```

Wynik pojawi się w `sniffer_capture.csv`.

---

## Część 6: Co robić dalej

1. **Zbieraj dane kilka minut** — zobaczy się różne AP, urządzenia BLE.
2. **Analiza CSV**:
   ```bash
   python3 << 'EOF'
   import pandas as pd
   df = pd.read_csv('sniffer_capture.csv')
   print(df[df['type'] == 'wifi']['src_mac'].value_counts().head(10))  # Top MACs
   print(f"RSSI średnia: {df[df['type'] == 'wifi']['rssi'].mean()}")    # Średnia siła
   EOF
   ```

3. **Hopping kanałów** — modyfikacja kodu by przechodzić przez kanały 1-13.
4. **Dekodowanie payload'u** — wyciągnąć SSID z beacon frames.
5. **Wizualizacja** — matplotlib do rysowania RSSI vs. czas.

---

## Troubleshooting

- **Port nie znaleziony**: `ls /dev/ttyUSB*`, sprawdź kabel, driver.
- **Kompilacja fail**: `idf.py fullclean && idf.py build`.
- **Mało danych Wi-Fi**: zmień kanał (`wifi_init_promiscuous(1)`, `wifi_init_promiscuous(11)`).
- **BLE tichutko**: sprawdź czy stolik zasilania OK, antena blisko.

---

## Podsumowanie

- **Kod C**: promiscuous + BLE callback → JSON na Serial
- **Python**: czyta Serial → CSV (można analizować)
- **Dalej**: dekodowanie payload'u, hopping, wizualizacja

Powodzenia! 🎯
