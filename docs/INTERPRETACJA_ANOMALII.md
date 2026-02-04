# 🤖 Interpretacja Wyników Wykrywania Anomalii (AI/ML)

## 📊 Co Oznacza "Anomaly Score: 0.33"?

### Skala Anomaly Score

**Anomaly Score** to wartość od **0.0 do 1.0**, gdzie:
- **0.0 - 0.3** = Niska anomalia (urządzenie może być nieco nietypowe, ale prawdopodobnie bezpieczne)
- **0.3 - 0.6** = Średnia anomalia (urządzenie jest nietypowe - wymaga uwagi)
- **0.6 - 0.8** = Wysoka anomalia (urządzenie jest bardzo nietypowe - podejrzane)
- **0.8 - 1.0** = Bardzo wysoka anomalia (urządzenie jest ekstremalnie nietypowe - prawdopodobnie zagrożenie)

### Twój Wynik: Score 0.33

**Score 0.33** oznacza:
- ✅ **Średnia anomalia** - urządzenie jest nietypowe w porównaniu do innych
- ⚠️ **Wymaga uwagi** - warto sprawdzić szczegóły
- 🔍 **Nie jest ekstremalnie podejrzane** - ale różni się od normy

---

## 🔬 Co to są "Isolation Forest" i "One-Class SVM"?

### Isolation Forest
- **Co robi:** Wykrywa urządzenia, które są "odizolowane" od reszty
- **Jak działa:** Buduje las drzew decyzyjnych i sprawdza, jak łatwo można "izolować" urządzenie
- **Kiedy wykrywa:** Urządzenia z nietypowymi kombinacjami cech (np. niski security score + wiele podatności + brak szyfrowania)

### One-Class SVM
- **Co robi:** Uczy się "normalnego" wzorca i wykrywa odstępstwa
- **Jak działa:** Tworzy granicę wokół normalnych urządzeń i wykrywa te poza granicą
- **Kiedy wykrywa:** Urządzenia, które nie pasują do wzorca "normalnych" urządzeń

### Ensemble (Głosowanie Większościowe)
- **Co robi:** Używa wielu algorytmów jednocześnie
- **Jak działa:** Jeśli **2 z 3** algorytmów wykryją anomalie, urządzenie jest oznaczone jako anomalia
- **Zaleta:** Bardziej niezawodne niż pojedynczy algorytm

---

## 📋 Jak Interpretować Wyniki?

### Przykład 1: Score 0.33 (Twój Wynik)

```
AI: Wykryta anomalia
Score: 0.33 | Detected by: Isolation Forest, One-Class SVM
```

**Interpretacja:**
- ✅ **2 z 3 algorytmów** wykryły anomalie (Isolation Forest + One-Class SVM)
- ⚠️ **Score 0.33** = średnia anomalia
- 🔍 **Co to oznacza:** Urządzenie ma nietypową kombinację cech bezpieczeństwa

**Możliwe przyczyny:**
- Niski security score (< 50)
- Wiele podatności (> 3)
- Brak szyfrowania + brak autoryzacji
- Nietypowy protokół dla danego typu urządzenia

**Co zrobić:**
1. Sprawdź szczegóły urządzenia w raporcie
2. Zobacz listę podatności
3. Sprawdź security score
4. Jeśli to urządzenie medyczne - rozważ poprawę bezpieczeństwa

---

### Przykład 2: Score 0.75 (Wysoka Anomalia)

```
AI: Wykryta anomalia
Score: 0.75 | Detected by: Isolation Forest, LOF, One-Class SVM
```

**Interpretacja:**
- 🔴 **Wszystkie 3 algorytmy** wykryły anomalie
- ⚠️ **Score 0.75** = wysoka anomalia
- 🚨 **Co to oznacza:** Urządzenie jest bardzo nietypowe i podejrzane

**Możliwe przyczyny:**
- Bardzo niski security score (< 20)
- Wiele krytycznych podatności
- Brak wszystkich zabezpieczeń
- Nietypowe porty otwarte

**Co zrobić:**
1. **Natychmiast sprawdź** urządzenie
2. Sprawdź czy to nie jest atak/intruz
3. Rozważ odłączenie urządzenia od sieci
4. Zgłoś do działu IT/bezpieczeństwa

---

### Przykład 3: Score 0.15 (Niska Anomalia)

```
AI: Wykryta anomalia
Score: 0.15 | Detected by: Isolation Forest
```

**Interpretacja:**
- ✅ **Tylko 1 algorytm** wykrył anomalie
- 🟢 **Score 0.15** = niska anomalia
- 💡 **Co to oznacza:** Urządzenie jest lekko nietypowe, ale prawdopodobnie bezpieczne

**Możliwe przyczyny:**
- Nieco niższy security score niż średnia
- 1-2 podatności
- Nietypowy protokół (ale bezpieczny)

**Co zrobić:**
1. Sprawdź szczegóły (może być OK)
2. Monitoruj urządzenie
3. Nie wymaga natychmiastowej akcji

---

## 🎯 Co Analizuje AI?

AI analizuje następujące cechy urządzenia:

1. **Security Score** (0-100)
   - Niski score = wyższa anomalia

2. **Liczba Podatności**
   - Wiele podatności = wyższa anomalia

3. **Szyfrowanie**
   - Brak szyfrowania = wyższa anomalia

4. **Autoryzacja**
   - Brak wymagania parowania = wyższa anomalia

5. **Protokół**
   - Nietypowy protokół dla danego typu = wyższa anomalia

6. **Typ Urządzenia**
   - Nieznany typ = wyższa anomalia

7. **Metadane**
   - Nietypowe porty, brak informacji = wyższa anomalia

---

## 📊 Przykładowe Interpretacje

### Score 0.33 + "Detected by: Isolation Forest, One-Class SVM"

**Co to oznacza:**
- Urządzenie ma **nietypową kombinację cech**
- **2 z 3 algorytmów** wykryły anomalie
- **Średnia anomalia** - nie jest ekstremalnie podejrzane, ale wymaga uwagi

**Możliwe scenariusze:**
1. **Urządzenie medyczne z niskim bezpieczeństwem**
   - Niski security score (np. 30/100)
   - Brak szyfrowania
   - 3-5 podatności
   - **Akcja:** Sprawdź szczegóły, rozważ poprawę bezpieczeństwa

2. **Urządzenie z nietypowym protokołem**
   - WiFi urządzenie z otwartymi portami medycznymi
   - Nietypowa kombinacja cech
   - **Akcja:** Sprawdź czy to rzeczywiście urządzenie medyczne

3. **Urządzenie z wieloma podatnościami**
   - Security score OK (np. 60/100)
   - Ale wiele podatności (np. 6+)
   - **Akcja:** Sprawdź listę podatności

---

## 🔍 Jak Sprawdzić Szczegóły?

### 1. W Raporcie JSON

```bash
cat reports/combined_report_*.json | jq '.scan.devices[] | select(.metadata.anomaly_detection.is_anomaly == true)'
```

### 2. W Dashboard (--api)

Otwórz w przeglądarce:
```
http://localhost:5000/dashboard
```

Szukaj sekcji "🤖 AI: Wykryta anomalia"

### 3. W Terminalu

Podczas skanowania zobaczysz:
```
🔍 Wykryte anomalie:
  • Device Name (Score: 0.33)
    Metoda: ensemble
    Powód: Detected by: Isolation Forest, One-Class SVM
    Szczegóły: isolation_forest: 0.35, lof: 0.20, one_class_svm: 0.45
```

---

## ⚠️ Kiedy Się Martwić?

### 🟢 Nie Martw Się (Score < 0.3)
- Niska anomalia
- Prawdopodobnie bezpieczne
- Monitoruj, ale nie wymaga natychmiastowej akcji

### 🟡 Uwaga (Score 0.3 - 0.6)
- Średnia anomalia
- Wymaga sprawdzenia
- Sprawdź szczegóły urządzenia
- Rozważ poprawę bezpieczeństwa

### 🟠 Podejrzane (Score 0.6 - 0.8)
- Wysoka anomalia
- Podejrzane urządzenie
- Sprawdź natychmiast
- Rozważ odłączenie od sieci

### 🔴 Krytyczne (Score > 0.8)
- Bardzo wysoka anomalia
- Prawdopodobnie zagrożenie
- **Natychmiast sprawdź**
- Rozważ odłączenie i zgłoszenie

---

## 💡 Praktyczne Przykłady

### Przykład: Urządzenie Medyczne z Niskim Bezpieczeństwem

```
Device: Glucose Meter XYZ
Security Score: 25/100
Anomaly Score: 0.33
Detected by: Isolation Forest, One-Class SVM
```

**Dlaczego anomalia?**
- Security score 25/100 (bardzo niski)
- Brak szyfrowania
- 4 podatności
- Brak autoryzacji

**Interpretacja:**
- Urządzenie jest **nietypowe** (ma bardzo niskie bezpieczeństwo)
- **Nie jest atakiem**, ale **wymaga poprawy bezpieczeństwa**
- **Akcja:** Zaktualizuj firmware, włącz szyfrowanie

---

### Przykład: Podejrzane Urządzenie w Sieci

```
Device: Unknown Device (192.168.1.100)
Security Score: 10/100
Anomaly Score: 0.85
Detected by: Isolation Forest, LOF, One-Class SVM
```

**Dlaczego anomalia?**
- Bardzo niski security score (10/100)
- Wiele krytycznych podatności (8+)
- Brak wszystkich zabezpieczeń
- Nieznany typ urządzenia

**Interpretacja:**
- Urządzenie jest **ekstremalnie nietypowe**
- **Może być zagrożeniem**
- **Akcja:** Natychmiast sprawdź, rozważ odłączenie

---

## 🎓 Podsumowanie

### Twój Wynik: Score 0.33

✅ **Co to oznacza:**
- Średnia anomalia
- Urządzenie jest nietypowe w porównaniu do innych
- Wymaga uwagi, ale nie jest ekstremalnie podejrzane

🔍 **Co zrobić:**
1. Sprawdź szczegóły urządzenia w raporcie
2. Zobacz security score i listę podatności
3. Sprawdź czy to urządzenie medyczne
4. Rozważ poprawę bezpieczeństwa jeśli to urządzenie medyczne

⚠️ **Kiedy się martwić:**
- Score > 0.6 = wysoka anomalia (podejrzane)
- Score > 0.8 = bardzo wysoka anomalia (prawdopodobnie zagrożenie)

---

## 📚 Więcej Informacji

- **Algorytmy ML:** Isolation Forest, LOF, One-Class SVM
- **Metoda:** Ensemble (głosowanie większościowe)
- **Cechy analizowane:** Security score, podatności, szyfrowanie, protokół, typ urządzenia
- **Skala:** 0.0 (normalne) - 1.0 (ekstremalnie anomalne)
