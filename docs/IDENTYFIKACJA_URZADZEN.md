# 🔍 Identyfikacja Urządzeń - Jak Znaleźć Konkretne Urządzenie

## 🎯 Problem

Po skanowaniu widzisz:
- MAC adresy: `BC:10:2F:FC:E1:87`
- IP adresy: `192.168.1.5`
- Nazwy: `192.168.1.5` (dla WiFi) lub `SJI Industry Company` (dla BLE)
- Wyniki VirusTotal: `IP flagged as malicious (1 detections)`

**Ale nie wiesz które urządzenie to jest!**

---

## ✅ Rozwiązanie

Skaner teraz automatycznie:
1. **Tworzy czytelne nazwy urządzeń** (`display_name`)
2. **Generuje unikalne fingerprinty** (`device_fingerprint`)
3. **Powiązuje threat intelligence z urządzeniami**
4. **Dodaje mapowanie IP → urządzenia**

---

## 📊 Nowe Pola w Raportach JSON

### 1. `display_name` - Czytelna Nazwa Urządzenia

**Co to jest:**
- Czytelna nazwa urządzenia do wyświetlenia
- Automatycznie generowana z dostępnych informacji

**Przykłady:**
```json
{
  "name": "192.168.1.5",
  "display_name": "Glukometr (192.168.1.5)",
  ...
}
```

```json
{
  "name": "SJI Industry Company",
  "display_name": "SJI Industry Company",
  ...
}
```

**Priorytet generowania:**
1. Nazwa urządzenia (jeśli nie jest IP)
2. Producent + Model
3. Typ urządzenia + IP/MAC
4. Protokół + IP/MAC

---

### 2. `device_fingerprint` - Unikalny Fingerprint

**Co to jest:**
- Unikalny identyfikator urządzenia składający się z wielu cech
- Używany do identyfikacji urządzenia nawet jeśli MAC/IP się zmieni

**Format:**
```
PROTOKOL|TYP_URZADZENIA|PRODUCENT|MODEL|MAC:XXXXXX|IP:XXX.XXX.XXX.XXX
```

**Przykłady:**
```json
{
  "device_fingerprint": "WiFi|unknown|||MAC:010000|IP:192.168.1.5",
  ...
}
```

```json
{
  "device_fingerprint": "BLE|glucose_meter|SJI Industry Company||MAC:E1:87",
  ...
}
```

**Zastosowanie:**
- Identyfikacja urządzenia nawet po zmianie MAC (random MAC)
- Śledzenie urządzenia w czasie
- Porównywanie urządzeń między skanowaniami

---

### 3. `ip_address` - IP na Głównym Poziomie

**Co to jest:**
- IP adres urządzenia na głównym poziomie (łatwy dostęp)
- Wcześniej był tylko w `metadata.ip_address`

**Przykład:**
```json
{
  "mac_address": "00:00:01:05:00:00",
  "name": "192.168.1.5",
  "ip_address": "192.168.1.5",  // ← Nowe pole!
  ...
}
```

---

### 4. `threat_intelligence` - Powiązane z Urządzeniem

**Co to jest:**
- Informacje o threat intelligence bezpośrednio w urządzeniu
- Wcześniej były tylko w sekcji `threat_intelligence` (tylko IP)

**Przykład:**
```json
{
  "mac_address": "00:00:01:05:00:00",
  "name": "192.168.1.5",
  "display_name": "Urządzenie WiFi (192.168.1.5)",
  "ip_address": "192.168.1.5",
  "threat_intelligence": {
    "ip": "192.168.1.5",
    "is_threat": true,
    "abuse_score": 45,
    "reputation": "malicious",
    "sources": {
      "abuseipdb": {...},
      "virustotal": {
        "malicious": 1,
        "suspicious": 0,
        "harmless": 61,
        "undetected": 32
      }
    }
  },
  "threat_intelligence_linked": true,  // ← Czy threat intel jest powiązany
  ...
}
```

---

### 5. `threat_intelligence_summary.ip_to_devices` - Mapowanie IP → Urządzenia

**Co to jest:**
- Mapowanie IP adresów do urządzeń
- Ułatwia znalezienie urządzenia dla danego IP

**Przykład:**
```json
{
  "threat_intelligence_summary": {
    "total_ips_checked": 5,
    "threats_found": 1,
    "clean_ips": 4,
    "ip_to_devices": {
      "192.168.1.5": [
        {
          "display_name": "Urządzenie WiFi (192.168.1.5)",
          "mac_address": "00:00:01:05:00:00",
          "device_fingerprint": "WiFi|unknown|||MAC:010000|IP:192.168.1.5",
          "protocol": "WiFi"
        }
      ],
      "192.168.1.1": [
        {
          "display_name": "Router (192.168.1.1)",
          "mac_address": "00:00:01:01:00:00",
          "device_fingerprint": "WiFi|unknown|||MAC:010000|IP:192.168.1.1",
          "protocol": "WiFi"
        }
      ]
    }
  }
}
```

---

## 🔍 Jak Znaleźć Urządzenie?

### Przykład 1: Masz IP z VirusTotal

**Problem:** VirusTotal pokazuje `192.168.1.5` jako malicious, ale nie wiesz które to urządzenie.

**Rozwiązanie:**

```bash
# W raporcie JSON:
cat reports/combined_report_*.json | jq '.scan.devices[] | select(.ip_address == "192.168.1.5")'
```

**Lub:**

```bash
# Sprawdź mapowanie IP → urządzenia:
cat reports/combined_report_*.json | jq '.threat_intelligence_summary.ip_to_devices["192.168.1.5"]'
```

**Wynik:**
```json
[
  {
    "display_name": "Urządzenie WiFi (192.168.1.5)",
    "mac_address": "00:00:01:05:00:00",
    "device_fingerprint": "WiFi|unknown|||MAC:010000|IP:192.168.1.5",
    "protocol": "WiFi"
  }
]
```

---

### Przykład 2: Masz MAC Adres

**Problem:** Widzisz MAC `BC:10:2F:FC:E1:87` ale nie wiesz co to za urządzenie.

**Rozwiązanie:**

```bash
cat reports/combined_report_*.json | jq '.scan.devices[] | select(.mac_address == "BC:10:2F:FC:E1:87")'
```

**Wynik:**
```json
{
  "mac_address": "BC:10:2F:FC:E1:87",
  "name": "SJI Industry Company",
  "display_name": "SJI Industry Company",
  "device_fingerprint": "BLE|unknown|SJI Industry Company||MAC:E1:87",
  "device_type": "unknown",
  "protocol": "BLE",
  "manufacturer": "SJI Industry Company",
  ...
}
```

---

### Przykład 3: Znajdź Wszystkie Urządzenia z Threat Intelligence

**Problem:** Chcesz zobaczyć wszystkie urządzenia które mają threat intelligence.

**Rozwiązanie:**

```bash
cat reports/combined_report_*.json | jq '.scan.devices[] | select(.threat_intelligence_linked == true)'
```

**Lub urządzenia z zagrożeniami:**

```bash
cat reports/combined_report_*.json | jq '.scan.devices[] | select(.threat_intelligence.is_threat == true)'
```

---

### Przykład 4: Znajdź Urządzenie po Fingerprint

**Problem:** Chcesz śledzić urządzenie między skanowaniami (nawet jeśli MAC się zmieni).

**Rozwiązanie:**

```bash
# Znajdź urządzenie po fingerprint:
cat reports/combined_report_*.json | jq '.scan.devices[] | select(.device_fingerprint | contains("WiFi|unknown"))'
```

---

## 📋 Podsumowanie

### Nowe Pola w Raportach:

1. **`display_name`** - Czytelna nazwa urządzenia
2. **`device_fingerprint`** - Unikalny fingerprint
3. **`ip_address`** - IP na głównym poziomie
4. **`threat_intelligence`** - Threat intel powiązany z urządzeniem
5. **`threat_intelligence_linked`** - Czy threat intel jest powiązany
6. **`threat_intelligence_summary.ip_to_devices`** - Mapowanie IP → urządzenia

### Jak Używać:

1. **Znajdź urządzenie po IP:**
   ```bash
   jq '.scan.devices[] | select(.ip_address == "192.168.1.5")'
   ```

2. **Znajdź urządzenie po MAC:**
   ```bash
   jq '.scan.devices[] | select(.mac_address == "BC:10:2F:FC:E1:87")'
   ```

3. **Znajdź urządzenia z threat intelligence:**
   ```bash
   jq '.scan.devices[] | select(.threat_intelligence_linked == true)'
   ```

4. **Sprawdź mapowanie IP → urządzenia:**
   ```bash
   jq '.threat_intelligence_summary.ip_to_devices["192.168.1.5"]'
   ```

---

## 💡 Wskazówki

1. **Używaj `display_name`** - to jest najczytelniejsza nazwa urządzenia
2. **Używaj `device_fingerprint`** - do śledzenia urządzeń w czasie
3. **Sprawdź `threat_intelligence`** - bezpośrednio w urządzeniu, nie musisz szukać w sekcji `threat_intelligence`
4. **Używaj `ip_to_devices`** - do szybkiego wyszukiwania urządzenia dla danego IP

---

**Teraz zawsze będziesz wiedział które urządzenie to jest!** 🎯
