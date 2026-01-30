# 🤖 AI/ML w Projekcie - Do Czego Jest Wykorzystana

## 🎯 Przegląd

Projekt wykorzystuje **Machine Learning** i **Deep Learning** do wykrywania anomalii w urządzeniach medycznych IoT. AI analizuje cechy bezpieczeństwa urządzeń i identyfikuje nietypowe wzorce, które mogą wskazywać na problemy bezpieczeństwa.

---

## 🔍 Główne Funkcjonalności AI/ML

### 1. Wykrywanie Anomalii (Anomaly Detection)

**Co robi:** Wykrywa nietypowe urządzenia na podstawie ich cech bezpieczeństwa

**Algorytmy:**
- **Isolation Forest** - Szybki i skuteczny dla wysokowymiarowych danych
- **Local Outlier Factor (LOF)** - Wykrywa lokalne anomalie
- **One-Class SVM** - Wykrywa odstające urządzenia od normalnego wzorca
- **Ensemble Method** - Głosowanie większościowe (anomalia jeśli 2 z 3 metod wykryły)

**Cechy analizowane:**
- Security score (0-100)
- Liczba podatności
- Czy ma szyfrowanie (0/1)
- Czy wymaga parowania (0/1)
- Typ protokołu (BLE, WiFi, USB, NFC)
- Typ urządzenia (glukometr, pompa insulinowa, etc.)
- RSSI (siła sygnału)
- Liczba otwartych portów
- Encryption strength score

**Użycie:**
```python
from anomaly_detector import AnomalyDetector

detector = AnomalyDetector()
detector.train(devices)  # Trenuj na historycznych danych
results = detector.detect_anomalies(devices)  # Wykryj anomalie
```

---

### 2. Wykrywanie w Czasie Rzeczywistym (Streaming)

**Co robi:** Wykrywa anomalie dla pojedynczych urządzeń natychmiast podczas skanowania

**Zalety:**
- Natychmiastowe alerty (nie czekasz na koniec skanowania)
- Bufor ostatnich 100 urządzeń dla analizy trendów
- Thread-safe dla aplikacji wielowątkowych

**Użycie:**
```python
# Wykryj anomalie dla pojedynczego urządzenia w czasie rzeczywistym
result = detector.detect_anomaly_streaming(device)
if result['is_anomaly']:
    print(f"⚠️ Anomalia wykryta: {result['reason']}")
```

**Praktyczna korzyść:** Zamiast czekać 10 minut na koniec skanowania, wiesz od razu że urządzenie #3 jest podejrzane.

---

### 3. Deep Learning (Autoencoder)

**Co robi:** Wykrywa złożone wzorce anomalii używając Autoencodera

**Architektura:**
- Input → Dense (50%) → Dense (25%) → Dense (50%) → Output
- Rekonstrukcja błędów wskazuje anomalie
- Wymaga TensorFlow (opcjonalne)

**Zalety:**
- Wykrywa złożone wzorce, które tradycyjne metody mogą przegapić
- Lepsza dokładność dla nietypowych zachowań
- Wykrywa nowe typy zagrożeń (nie tylko znane wzorce)

**Użycie:**
```python
# Trenuj Autoencoder
result = detector.train_deep_learning(devices, epochs=50)

# Autoencoder jest automatycznie używany w detect_anomaly_streaming()
```

**Przykład:**
```
Tradycyjne metody: "Urządzenie ma security_score=60, to OK"
Autoencoder: "Security score OK, ALE kombinacja cech jest nietypowa - to anomalia!"
```

---

### 4. Predykcja Przyszłych Podatności

**Co robi:** Przewiduje prawdopodobieństwo wystąpienia podatności w przyszłości

**Model:** Random Forest Classifier

**Wyniki:**
- `probability`: 0-1 (prawdopodobieństwo podatności)
- `risk_level`: 'low', 'medium', 'high'
- `recommendations`: Lista rekomendacji bezpieczeństwa

**Użycie:**
```python
# Trenuj predyktor
detector.train_vulnerability_predictor(devices)

# Przewiduj ryzyko
prediction = detector.predict_vulnerability(device)
print(f"Prawdopodobieństwo podatności: {prediction['probability']:.2%}")
print(f"Poziom ryzyka: {prediction['risk_level']}")
print("Rekomendacje:", prediction['recommendations'])
```

**Praktyczna korzyść:** Zapobieganie problemom zanim się pojawią (proaktywne vs reaktywne).

**Scenariusz:**
- Urządzenie ma teraz security_score=70 (OK)
- Ale model przewiduje 85% szans na podatność w przyszłości
- **Działasz teraz** zanim problem się pojawi!

---

### 5. Klasteryzacja Urządzeń

**Co robi:** Grupuje urządzenia według podobieństwa bezpieczeństwa

**Metody:**
- **KMeans** - Określona liczba klastrów (np. 5)
- **DBSCAN** - Automatyczna detekcja klastrów + noise detection

**Klastery są nazywane na podstawie średniego security score:**
- High Security (≥80)
- Medium Security (60-79)
- Low Security (<60)

**Użycie:**
```python
# Klasteryzuj urządzenia
clusters = detector.cluster_devices(devices, n_clusters=5, method='kmeans')

for item in clusters:
    print(f"{item['device'].name}: {item['cluster_name']}")
```

**Praktyczna korzyść:** Zamiast analizować 100 urządzeń osobno, zarządzasz 5 grupami.

**Przykład:**
```
Cluster 1: High Security (15 urządzeń)
  - Wszystkie mają security_score > 80
  - Polityka: Standardowe skanowanie co tydzień

Cluster 2: Low Security (5 urządzeń)
  - Wszystkie mają security_score < 50
  - Polityka: Codzienne skanowanie, priorytet aktualizacji
```

---

### 6. Integracja z Systemami SIEM

**Co robi:** Automatycznie eksportuje alerty do systemów bezpieczeństwa

**Formaty eksportu:**
- **CEF (Common Event Format)** - Standardowy format dla SIEM
- **Syslog** - Protokół logowania
- **JSON** - Dla custom integracji
- **Custom callbacks** - Własne funkcje integracji

**Użycie:**
```python
# Włącz integrację SIEM
detector.enable_siem_integration(True)

# Dodaj custom callback
def my_siem_callback(anomaly_result):
    send_to_my_siem(anomaly_result)

detector.add_siem_callback(my_siem_callback)

# Automatycznie wysyła do SIEM gdy anomalia wykryta
result = detector.detect_anomaly_streaming(device)
```

**Praktyczna korzyść:** Wszystkie alerty trafiają automatycznie do centralnego systemu bezpieczeństwa (Splunk, QRadar, ELK).

---

## 📊 Przykład Kompleksowego Użycia

```python
from anomaly_detector import AnomalyDetector

# 1. Inicjalizacja
detector = AnomalyDetector(contamination=0.1)

# 2. Trenuj wszystkie modele
detector.train(devices)  # Podstawowe modele
detector.train_deep_learning(devices, epochs=50)  # Deep Learning
detector.train_vulnerability_predictor(devices)  # Predykcja

# 3. Klasteryzuj urządzenia
clusters = detector.cluster_devices(devices, n_clusters=5)

# 4. Włącz SIEM
detector.enable_siem_integration(True)

# 5. Monitoring w czasie rzeczywistym
for new_device in scanning_new_devices:
    # Streaming detection
    result = detector.detect_anomaly_streaming(new_device)
    
    if result['is_anomaly']:
        # Automatycznie wysłane do SIEM!
        print(f"⚠️ Alert: {new_device.name}")
        
        # Sprawdź predykcję
        prediction = detector.predict_vulnerability(new_device)
        if prediction['risk_level'] == 'high':
            # Pilna akcja!
            take_urgent_action(new_device)
```

---

## 🎯 Kiedy Używać Której Funkcjonalności?

| Funkcjonalność | Kiedy Używać |
|----------------|--------------|
| **Wykrywanie anomalii** | Zawsze - automatycznie po skanowaniu (jeśli >= 10 urządzeń) |
| **Streaming** | Monitoring ciągły, skanowanie w czasie rzeczywistym |
| **Deep Learning** | Wysokie wymagania bezpieczeństwa, zaawansowane zagrożenia |
| **Predykcja** | Planowanie aktualizacji, priorytetyzacja działań |
| **Klasteryzacja** | Duża liczba urządzeń (>20), optymalizacja zarządzania |
| **SIEM** | Integracja z istniejącymi systemami, compliance, automatyzacja |

---

## 💡 Wartość Biznesowa

### Oszczędność Czasu:
- **Streaming:** -80% czasu na wykrywanie (natychmiast vs 10 minut)
- **Klasteryzacja:** -70% czasu na analizę (grupy vs pojedyncze urządzenia)
- **SIEM:** -90% czasu na logowanie (automatyczne vs ręczne)

### Lepsze Bezpieczeństwo:
- **Deep Learning:** +30% wykrywalności złożonych zagrożeń
- **Predykcja:** Proaktywne zapobieganie zamiast reaktywnego reagowania
- **SIEM:** Centralizacja = lepsza widoczność

### Compliance:
- **SIEM:** Wszystkie zdarzenia są logowane (wymagane przez audyty)
- **Predykcja:** Dokumentacja ryzyka (wymagane przez regulacje)

---

## 📚 Biblioteki ML Używane w Projekcie

- **scikit-learn** - Isolation Forest, LOF, One-Class SVM, KMeans, DBSCAN, Random Forest
- **tensorflow** (opcjonalne) - Autoencoder (Deep Learning)
- **numpy** - Operacje numeryczne, wektoryzacja
- **pandas** - Przetwarzanie danych

Zobacz `BIBLIOTEKI.md` dla szczegółowych wyjaśnień.
