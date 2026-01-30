# 📊 Jak Zobaczyć Wyniki - PROSTY SPOSÓB

## 🎯 Najprostszy Sposób

### Po prostu użyj flagi `--api`:

```bash
python3 src/scanner.py --api
```

**To wszystko!** Automatycznie:
1. ✅ Skanuje urządzenia
2. ✅ Otwiera przeglądarkę z wynikami
3. ✅ Pokazuje wszystko w ładnym interfejsie

Wszystko w przeglądarce - bez dodatkowej instalacji!

---

## 📱 Co Zobaczysz w Przeglądarce?

Po uruchomieniu `python3 src/scanner.py --api` zobaczysz:

1. **Dashboard** - główny widok z wszystkimi urządzeniami
2. **Lista urządzeń** - wszystkie wykryte urządzenia z szczegółami
3. **Statystyki** - wykresy i podsumowania
4. **Szczegóły** - kliknij urządzenie aby zobaczyć więcej

**Adres:** http://localhost:5000/dashboard

---

## 🛡️ Jeśli Chcesz Użyć SIEM (Opcjonalne)

### Opcja A: Splunk Free (ZALECANE!)

**Splunk jest PROSTSZY - nie wymaga OpenSearch!**

```bash
# 1. Zainstaluj Splunk (5 minut)
# Zobacz: SPLUNK_INSTRUKCJA.md

# 2. Uruchom skaner
python3 src/scanner.py

# 3. Zaimportuj do Splunk
./import_to_splunk.sh

# 4. Otwórz Splunk
# http://localhost:8000
```

**Zalety Splunk:**
- ✅ Najłatwiejsza instalacja (jeden plik)
- ✅ Gotowy dashboard (działa od razu)
- ✅ Nie wymaga OpenSearch/Elasticsearch
- ✅ Profesjonalny interfejs

**Zobacz:** `SPLUNK_INSTRUKCJA.md` (szczegółowa instrukcja)

---

## 💡 Rekomendacja

**Dla większości użytkowników:**
```bash
python3 src/scanner.py --api
```

**To jest najprostsze!** Nie wymaga instalacji niczego dodatkowego.

---

## 📋 Podsumowanie

| Sposób | Trudność | Wymaga Instalacji | Wymaga OpenSearch |
|--------|----------|-------------------|-------------------|
| **`--api`** | ⭐ (najłatwiejsze) | ❌ Nie | ❌ Nie |
| **Splunk Free** | ⭐⭐ | ✅ Tak (1 plik) | ❌ Nie |

**Rekomendacja:**
1. **Najprostsze:** `--api` (bez instalacji)
2. **Dla SIEM:** **Splunk Free** (prosty w instalacji)

**Użyj `--api` lub Splunk!** 🚀
