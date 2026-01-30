# Jak AI pomaga w wykrywaniu podatności

W skanerze AI **nie zastępuje** klasycznego wykrywania podatności (porty, CVE, szyfrowanie), tylko **wykorzystuje jego wyniki** i dodaje dwie rzeczy: **wykrywanie anomalii** oraz **predykcję ryzyka**.

---

## 1. Dwa rodzaje „podatności” w projekcie

| Źródło | Co robi | Przykład |
|--------|--------|----------|
| **Klasyczne skanowanie** | Sprawdza porty, CVE, szyfrowanie, parowanie itd. | „Brak szyfrowania”, „Port 22 otwarty – SSH”, „CVE-2020-…” |
| **AI (ML)** | Szuka urządzeń **nietypowych** względem reszty i **przewiduje ryzyko** | „ML Anomaly Detection: …”, predykcja „high risk” |

AI **nie skanuje portów** ani **nie wyszukuje CVE**. Bierze to, co skaner już policzył (security score, liczba podatności, szyfrowanie, protokół itd.), i na tej podstawie:
- oznacza urządzenia **anomalne** (potencjalnie bardziej ryzykowne),
- może **przewidywać**, które urządzenia są bardziej narażone na podatności w przyszłości.

---

## 2. Jak AI pomaga w wykrywaniu – krok po kroku

### Krok 1: Skaner zbiera dane i wykrywa „klasyczne” podatności

Dla każdego urządzenia skaner ustala m.in.:

- security score (0–100),
- liczbę podatności (z portów, CVE, braku szyfrowania itd.),
- czy ma szyfrowanie, czy wymaga parowania,
- protokół (BLE, WiFi, USB, NFC),
- typ urządzenia, RSSI, liczbę otwartych portów, ocenę szyfrowania.

Te dane są **wejściem** dla AI.

### Krok 2: AI buduje „profil” normalnych urządzeń

- Używa **Isolation Forest**, **LOF** i **One-Class SVM** (oraz opcjonalnie **Autoencoder**).
- Uczy się na **wszystkich** urządzeniach z bieżącego skanu (potrzeba min. ok. 10 urządzeń).
- Model wie, jakie **kombinacje cech** są „typowe” w Twojej sieci (np. „większość ma score 70–90, 0–2 podatności, szyfrowanie włączone”).

### Krok 3: Wykrywanie anomalii = „to urządzenie odstaje”

- Dla każdego urządzenia AI liczy **wektor cech** (m.in. security score, liczba podatności, szyfrowanie, protokół, typ).
- Sprawdza, czy ten wektor **odstaje** od reszty (anomalia).
- **Ensemble:** uznaje urządzenie za anomalę, gdy np. 2 z 3 modeli (Isolation Forest, LOF, SVM) tak wskazują.

Jeśli urządzenie jest uznane za **anomalię**:

- W raporcie / metadanych pojawia się **podatność** w stylu:  
  **„ML Anomaly Detection: …”** (z krótkim uzasadnieniem).
- To **nie** jest nowa podatność techniczna (jak CVE), tylko **flaga**: „to urządzenie wygląda inaczej niż reszta i warto je dokładniej sprawdzić”.

Dlatego mówimy, że **AI pomaga w wykrywaniu podatności**: wskazuje urządzenia, które – na podstawie już zebranych danych – są statystycznie nietypowe i przez to mogą być bardziej ryzykowne (np. nieznana konfiguracja, błąd, przyszła podatność).

### Krok 4: Predykcja podatności (opcjonalnie)

- Model **Random Forest** (trenowany na tych samych cechach) może **przewidywać** prawdopodobieństwo, że urządzenie będzie miało problemy (np. wiele podatności) w przyszłości.
- Daje **poziom ryzyka** (low / medium / high) i **rekomendacje**.
- To wsparcie **proaktywne**: „to urządzenie teraz ma np. score 70, ale model ocenia je jako wysokie ryzyko – warto je priorytetowo audytować”.

---

## 3. Jak to wygląda w praktyce

**Scenariusz A – bez AI**  
Skaner znajduje 20 urządzeń. Dla każdego ma: security score, listę podatności (CVE, porty, szyfrowanie). Musisz sam przejrzeć listę i zdecydować, które urządzenia są „podejrzane”.

**Scenariusz B – z AI**  
Na tych samych 20 urządzeniach AI dodatkowo:

- **Wykrywa anomalie:** np. „Urządzenie X ma score 45 i 6 podatności – w tej sieci prawie wszystkie mają score 70+ i 0–2 podatności → anomalia” → dodaje wpis typu **„ML Anomaly Detection: …”**.
- **Predykcja (jeśli włączona):** „Urządzenie Y ma teraz score 65, ale model daje 85% szans na wysokie ryzyko w przyszłości” → możesz je traktować jak wyższy priorytet do audytu.

Czyli: **klasyczne skanowanie** dostarcza „surowych” podatności; **AI** używa tych wyników, żeby:
- **wykrywać** urządzenia nietypowe (anomalie) i opisywać je jako dodatkową „podatność” ML,
- **przewidywać** ryzyko (predykcja podatności).

---

## 4. Kiedy AI się włącza

- **Wykrywanie anomalii** jest uruchamiane **automatycznie** po skanowaniu, jeśli jest **co najmniej ok. 10 urządzeń** (szczegóły w `scanner.py` / `anomaly_detector.py`).
- **Predykcja podatności** i **Autoencoder** są opcjonalne – trzeba je włączyć/wytrenować w kodzie (np. `train_vulnerability_predictor`, `train_deep_learning`); nie działają „same” z wiersza poleceń przy zwykłym `python src/scanner.py`.

---

## 5. Podsumowanie

- **AI nie skanuje portów ani CVE** – korzysta z wyników zwykłego skanera (security score, liczba podatności, szyfrowanie, protokoły itd.).
- **Anomalie** = urządzenia statystycznie „inne” niż reszta → są oznaczane i dopisywane jako **„ML Anomaly Detection”** w podatnościach.
- **Predykcja** = ocena ryzyka na przyszłość (Random Forest) – wsparcie przy priorytetyzacji audytów.
- **Rola AI w wykrywaniu podatności:** wskazuje **które** urządzenia warto traktować jako bardziej ryzykowne (anomalie + predykcja), podczas gdy **konkretne** podatności (CVE, porty, szyfrowanie) nadal pochodzą z klasycznego skanowania.

Więcej szczegółów: `docs/AI_ML.md` oraz moduł `src/anomaly_detector.py`.
