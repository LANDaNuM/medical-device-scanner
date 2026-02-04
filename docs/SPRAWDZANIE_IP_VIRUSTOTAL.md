# 🔍 Sprawdzanie Szczegółów IP w VirusTotal

## Problem

Jeśli widzisz komunikat:
```
VirusTotal: IP flagged as malicious (1 detections)
```

Chcesz wiedzieć:
- **Który antywirus wykrył zagrożenie?**
- **Jaki typ zagrożenia?**
- **Szczegóły detekcji?**

---

## ✅ Rozwiązanie

### 1. **Automatycznie w raporcie (nowa funkcjonalność)**

Po uruchomieniu skanowania, szczegóły detekcji są teraz automatycznie wyświetlane w podatnościach:

```
VirusTotal: IP flagged as malicious (1 detections) - wykryte przez: Avast, Kaspersky (+2 więcej)
```

### 2. **Użyj skryptu pomocniczego**

Najszybszy sposób na sprawdzenie szczegółów:

```bash
python3 scripts/check_ip_details.py <IP_ADDRESS>
```

**Przykład:**
```bash
python3 scripts/check_ip_details.py 192.168.1.100
```

**Wynik:**
- 📊 Podsumowanie (reputacja, liczba detekcji)
- 🌐 Informacje o sieci (ASN, kraj, sieć)
- ⚠️ **Szczegółowa tabela detekcji** - które antywirusy wykryły zagrożenie
- 🔗 Link do pełnego raportu w VirusTotal

### 3. **Sprawdź w pliku JSON**

Szczegóły są zapisane w `reports/combined_report_*.json`:

```json
{
  "devices": [
    {
      "metadata": {
        "external_apis": {
          "virustotal": {
            "malicious": 1,
            "suspicious": 0,
            "detections": [
              {
                "engine": "Avast",
                "category": "malicious",
                "result": "Trojan.Generic",
                "method": "static"
              }
            ]
          }
        }
      }
    }
  ]
}
```

### 4. **Sprawdź bezpośrednio w VirusTotal**

Otwórz w przeglądarce:
```
https://www.virustotal.com/gui/ip-address/<IP_ADDRESS>
```

**Przykład:**
```
https://www.virustotal.com/gui/ip-address/192.168.1.100
```

---

## 📋 Co oznaczają kategorie?

- **`malicious`** - Złośliwe (wykryte przez antywirusy jako zagrożenie)
- **`suspicious`** - Podejrzane (może być zagrożeniem)
- **`harmless`** - Bezpieczne
- **`undetected`** - Nie wykryto (brak danych)

---

## 🔧 Wymagania

Aby zobaczyć szczegóły detekcji, musisz mieć:

1. **Klucz API VirusTotal** w pliku `.env`:
   ```
   VIRUSTOTAL_API_KEY=twoj_klucz_api
   ```

2. **Rejestracja w VirusTotal** (darmowe):
   - https://www.virustotal.com/gui/join-us
   - Darmowy tier: 4 zapytania/minutę

---

## 💡 Przykłady użycia

### Sprawdź IP z raportu:
```bash
# 1. Znajdź IP w raporcie
cat reports/combined_report_*.json | jq '.scan.devices[] | select(.metadata.external_apis.virustotal.malicious > 0) | .metadata.ip_address'

# 2. Sprawdź szczegóły
python3 scripts/check_ip_details.py <IP>
```

### Sprawdź wszystkie podejrzane IP:
```bash
# Wyciągnij wszystkie IP z detekcjami
cat reports/combined_report_*.json | jq -r '.scan.devices[] | select(.metadata.external_apis.virustotal.malicious > 0) | .metadata.ip_address' | while read ip; do
    echo "=== Sprawdzam $ip ==="
    python3 scripts/check_ip_details.py "$ip"
    echo ""
done
```

---

## ⚠️ Ważne uwagi

1. **Prywatne IP (192.168.x.x, 10.x.x.x)** - VirusTotal może nie mieć pełnych danych dla prywatnych adresów IP
2. **Rate limiting** - Darmowy tier: max 4 zapytania/minutę
3. **Cache** - Wyniki są cachowane przez 24h (nie obciąża API)

---

## 📊 Przykładowy wynik skryptu

```
🔍 Sprawdzam szczegóły IP: 192.168.1.100

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ VirusTotal Results                                                                ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 📊 Podsumowanie                                                                   │
│                                                                                    │
│ Reputacja: 0                                                                       │
│ 🔴 Malicious: 1                                                                    │
│ 🟡 Suspicious: 0                                                                   │
│ 🟢 Harmless: 0                                                                     │
│ ⚪ Undetected: 0                                                                   │
└────────────────────────────────────────────────────────────────────────────────────┘

⚠️  Szczegóły detekcji (1 antywirusów wykryło zagrożenie):

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Detekcje antywirusów                                                              ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Antywirus │ Kategoria  │ Wynik            │ Metoda                                │
├───────────┼────────────┼──────────────────┼───────────────────────────────────────┤
│ Avast     │ malicious  │ Trojan.Generic   │ static                                 │
└───────────┴────────────┴──────────────────┴───────────────────────────────────────┘

💡 Więcej szczegółów: https://www.virustotal.com/gui/ip-address/192.168.1.100
```

---

## 🆘 Pomoc

Jeśli nie widzisz szczegółów:
1. Sprawdź czy masz `VIRUSTOTAL_API_KEY` w `.env`
2. Sprawdź czy IP jest poprawne
3. Sprawdź czy nie przekroczyłeś limitu API (4 req/min)
4. Użyj bezpośredniego linku do VirusTotal
