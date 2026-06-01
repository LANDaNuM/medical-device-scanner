# 📚 **KOMPLETNY SAMOUCZEK PYTHONA** 
## Od Podstaw do Zaawansowanych Technik

---

# ⚡ **ZADANIA PRAKTYCZNE** (Rozdziały 1-9)

## **ZADANIE 1: Kalkulator BMI (Rozdział 3)**

```python
# TODO: Napisz program który:
# 1. Pyta użytkownika o imię, wzrost (w metrach), wagę (w kg)
# 2. Oblicza BMI = waga / (wzrost ** 2)
# 3. Wypisuje wynik z jednym miejscem dziesiętnym
# 4. Na podstawie BMI wypisuje status:
#    - BMI < 18.5: "Niedowaga"
#    - BMI 18.5-24.9: "Normalna waga"
#    - BMI 25-29.9: "Nadwaga"
#    - BMI >= 30: "Otyłość"

# HINT: użyj f-stringów i if-elif-else
```

**Oczekiwany output:**
```
Podaj imię: Adam
Podaj wzrost (m): 1.80
Podaj wagę (kg): 75
Cześć Adam!
Twoje BMI wynosi: 23.1
Status: Normalna waga
```

---

## **ZADANIE 2: Tabliczka mnożenia (Rozdział 6)**

```python
# TODO: Napisz program który:
# 1. Pyta użytkownika o liczbę
# 2. Wypisuje tabliczkę mnożenia od 1 do 10
# 3. Formatuj ładnie (np. "7 × 5 = 35")

# HINT: użyj pętli for i f-stringów
```

**Oczekiwany output (dla liczby 7):**
```
7 × 1 = 7
7 × 2 = 14
7 × 3 = 21
...
7 × 10 = 70
```

---

## **ZADANIE 3: Gra Zgadnij liczbę (Rozdział 6)**

```python
# TODO: Napisz grę gdzie:
# 1. Losuje liczbę od 1 do 100 (import random; random.randint(1, 100))
# 2. Prosi gracza o zgadnięcie
# 3. Podpowiada "Za mało!" lub "Za dużo!"
# 4. Liczy próby i wypisuje gdy się uda
# 5. Pyta czy zagrać jeszcze raz

# HINT: użyj while True i break
```

**Oczekiwany output:**
```
Zgadnij liczbę (1-100): 50
Za mało!
Zgadnij liczbę (1-100): 75
Za dużo!
Zgadnij liczbę (1-100): 63
✅ Zgadłeś! Potrzebowałeś 3 prób!
Zagrać jeszcze raz? (tak/nie): nie
Do widzenia!
```

---

## **ZADANIE 4: Kalkulator operacji (Rozdział 7)**

```python
# TODO: Napisz program z funkcjami:
# 1. Funkcja dodaj(a, b) -> zwraca a + b
# 2. Funkcja odejmij(a, b) -> zwraca a - b
# 3. Funkcja pomnóż(a, b) -> zwraca a * b
# 4. Funkcja podziel(a, b) -> zwraca a / b (ale sprawdź czy b != 0!)
# 5. Główny program pyta użytkownika jaką operację chce

# HINT: Dodaj type hints! def dodaj(a: float, b: float) -> float:
```

**Oczekiwany output:**
```
Wybierz operację: 1=dodaj, 2=odejmij, 3=pomnóż, 4=podziel: 1
Pierwsza liczba: 10
Druga liczba: 5
Wynik: 15
```

---

## **ZADANIE 5: Czy liczba jest pierwsza? (Rozdział 7)**

```python
# TODO: Napisz funkcję czy_pierwsza(n: int) -> bool która:
# 1. Zwraca True jeśli liczba jest pierwsza
# 2. Zwraca False jeśli nie
# 3. Główny program pyta o liczbę i wypisuje rezultat

# HINT: Liczba pierwsza to liczba podzielna tylko przez 1 i siebie
# Nie sprawdzaj do n, tylko do sqrt(n)
```

**Oczekiwany output:**
```
Podaj liczbę: 17
17 jest liczbą pierwszą ✅
```

---

## **ZADANIE 6: Statystyka słów (Rozdział 8)**

```python
# TODO: Napisz program który:
# 1. Prosi użytkownika o tekst
# 2. Liczy ile razy każde słowo się pojawia
# 3. Wypisuje słowa i ich liczbę (posortowane od największej liczby)

# HINT: użyj split(), słownika, pętli, sorted()
```

**Oczekiwany output:**
```
Wpisz tekst: ala ma kota ala ma psa ala
Statystyka słów:
- ala: 3 razy
- ma: 2 razy
- kota: 1 raz
- psa: 1 raz
```

---

## **ZADANIE 7: Lista kontaktów (Rozdział 8)**

```python
# TODO: Stwórz program do zarządzania kontaktami:
# 1. Menu z opcjami: 1=Dodaj, 2=Wyszukaj, 3=Wypisz wszystkie, 4=Usuń, 5=Wyjdź
# 2. Każdy kontakt ma: imię, nr telefonu, email
# 3. Zapisuj w słowniku, np: {"Adam": {"telefon": "123", "email": "..."}}

# HINT: Główna pętla while True, switch-like struktura
```

**Oczekiwany output:**
```
=== MENEDŻER KONTAKTÓW ===
1. Dodaj kontakt
2. Wyszukaj kontakt
3. Wypisz wszystkie
4. Usuń kontakt
5. Wyjdź
Wybór: 1
Imię: Adam
Telefon: 123456789
Email: adam@example.com
✅ Kontakt dodany!
```

---

## **ZADANIE 8: Walidacja emaila (Rozdział 9)**

```python
# TODO: Napisz funkcję czy_email_poprawny(email: str) -> bool która:
# 1. Sprawdza czy zawiera @
# 2. Sprawdza czy zawiera . po @
# 3. Sprawdza czy coś jest przed @ (długość > 0)
# 4. Sprawdza czy coś jest po . (długość > 0)
# 5. Zwraca True/False

# HINT: Rozdziel na części email.split("@")
```

**Oczekiwany output:**
```
Podaj email: adam@example.com
✅ Email jest poprawny!

Podaj email: adamexample.com
❌ Email jest niepoprawny!
```

---

## **ZADANIE 9: Liczenie statystyk tekstowych (Rozdział 9)**

```python
# TODO: Stwórz program który:
# 1. Prosi użytkownika o tekst
# 2. Liczy: liczbę słów, liczbę liter, liczbę linii
# 3. Znajduje najczęstszą literę
# 4. Wypisuje wszystkie statystyki

# HINT: len(), split(), count(), Counter z collections
```

**Oczekiwany output:**
```
Wpisz tekst: Ala ma kota. Kota ma dziewięć żyć.
=== STATYSTYKA TEKSTOWA ===
Słów: 9
Liter (bez spacji): 29
Linii: 1
Najczęstsza litera: a (4 razy)
```

---

## **ZADANIE 10: Quiz wielokrotny wybór (Rozdział 6 + 8)**

```python
# TODO: Stwórz quiz z pytaniami, np:
# pytania = [
#     {
#         "pytanie": "Jaka jest stolica Polski?",
#         "opcje": ["A) Warszawa", "B) Kraków", "C) Wrocław"],
#         "poprawna": 0  # indeks prawidłowej odpowiedzi
#     },
#     ...
# ]

# Program powinien:
# 1. Wypisać pytanie i opcje
# 2. Pobrać odpowiedź użytkownika
# 3. Sprawdzić czy prawidłowa
# 4. Policzyć punkty
# 5. Wypisać wynik na koniec
```

**Oczekiwany output:**
```
=== QUIZ ===
Pytanie 1/3: Jaka jest stolica Polski?
A) Warszawa
B) Kraków
C) Wrocław
Twoja odpowiedź: A
✅ Prawidłowo!

Pytanie 2/3: ...

=== WYNIK ===
Uzyskałeś 2/3 punktów (66%)
```

---

---

# **ROZDZIAŁ 10: Moduły i biblioteki**

## **10.1 Co to jest moduł?**

Moduł to **plik .py** zawierający kod, który możesz reużywać.

```python
# plik: kalkulator.py
def dodaj(a, b):
    return a + b

def odejmij(a, b):
    return a - b

# inny plik: main.py
import kalkulator

wynik = kalkulator.dodaj(5, 3)
print(wynik)  # Output: 8
```

## **10.2 Import - różne sposoby**

### **Podstawowy import:**

```python
import math

print(math.pi)           # 3.14159...
print(math.sqrt(16))    # 4.0
print(math.sin(math.pi / 2))  # 1.0
```

### **Import wybranych funkcji:**

```python
from math import pi, sqrt

print(pi)      # 3.14159...
print(sqrt(16))  # 4.0
# math.sqrt nie działa! (nie importowaliśmy całego math)
```

### **Import z aliasem:**

```python
import math as m

print(m.pi)
print(m.sqrt(16))
```

### **Import wszystkiego (⚠️ NIE POLECAM):**

```python
from math import *

print(pi)  # Działa, ale nie wiadomo skąd to pochodzi
# Nie polecam - zaciemnia kod!
```

## **10.3 Najważniejsze moduły standardowe**

### **random - liczby losowe**

```python
import random

# Liczba losowa od 1 do 100
liczba = random.randint(1, 100)

# Liczba losowa od 0.0 do 1.0
ułamek = random.random()

# Losowy element z listy
owoce = ["jabłko", "banan", "pomarańcza"]
owoc = random.choice(owoce)

# Losowa permutacja listy
karty = [1, 2, 3, 4, 5]
random.shuffle(karty)
print(karty)  # Np. [3, 1, 4, 2, 5]
```

### **datetime - daty i czasy**

```python
from datetime import datetime, timedelta

# Obecny czas
teraz = datetime.now()
print(teraz)  # 2025-06-01 14:30:45.123456

# Roczenie datos
dzisiaj = datetime.now()
jutro = dzisiaj + timedelta(days=1)
print(jutro)

# Formatowanie
print(dzisiaj.strftime("%Y-%m-%d"))  # 2025-06-01
print(dzisiaj.strftime("%H:%M:%S"))  # 14:30:45

# Parsowanie
data_str = "2025-06-01"
data = datetime.strptime(data_str, "%Y-%m-%d")
print(data)
```

### **os - system operacyjny**

```python
import os

# Obecny folder roboczy
folder = os.getcwd()
print(folder)  # /Users/adam/projekt

# Listowanie plików
pliki = os.listdir(".")
print(pliki)

# Sprawdzenie czy plik istnieje
if os.path.exists("dane.txt"):
    print("Plik istnieje!")

# Tworzenie folderu
os.makedirs("nowy_folder", exist_ok=True)

# Ścieżka do pliku
sciezka = os.path.join("folder", "plik.txt")
print(sciezka)  # folder/plik.txt (lub folder\plik.txt na Windows)
```

### **json - parsowanie JSON**

```python
import json

# Zmiana Python dict → JSON string
dane = {
    "imie": "Adam",
    "wiek": 25,
    "miasta": ["Kraków", "Warszawa"]
}

json_string = json.dumps(dane)
print(json_string)
# {"imie": "Adam", "wiek": 25, "miasta": ["Kraków", "Warszawa"]}

# Zmiana JSON string → Python dict
json_data = '{"imie": "Adam", "wiek": 25}'
slownik = json.loads(json_data)
print(slownik["imie"])  # Adam

# Zapis do pliku
with open("dane.json", "w") as f:
    json.dump(dane, f)

# Odczyt z pliku
with open("dane.json", "r") as f:
    dane_z_pliku = json.load(f)
print(dane_z_pliku)
```

### **re - wyrażenia regularne (REGEX)**

Wyrażenia regularne to **pattern matching** - szukanie tekstu.

```python
import re

tekst = "Email: adam@example.com, Telefon: 123-456-789"

# Znalezienie emaila
email = re.search(r"[\w.-]+@[\w.-]+\.\w+", tekst)
if email:
    print(email.group())  # adam@example.com

# Znalezienie wszystkich liczb
liczby = re.findall(r"\d+", tekst)
print(liczby)  # ['123', '456', '789']

# Zamiana
nowy_tekst = re.sub(r"\d", "X", tekst)
print(nowy_tekst)  # Email: adam@example.com, Telefon: XXX-XXX-XXX

# Sprawdzenie czy string pasuje do wzoru
if re.match(r"^\d{3}-\d{3}-\d{3}$", "123-456-789"):
    print("To numer telefonu!")
```

## **10.4 requests - pobieranie danych z internetu**

```python
import requests

# Pobieranie zawartości strony
response = requests.get("https://api.example.com/data")

# Status odpowiedzi
print(response.status_code)  # 200 = OK, 404 = Not Found

# Tekst odpowiedzi
print(response.text)

# JSON
dane = response.json()
print(dane)

# Wysyłanie danych
dane_do_wysłania = {"imie": "Adam", "wiek": 25}
response = requests.post("https://api.example.com/users", json=dane_do_wysłania)
```

## **10.5 Tworzenie własnego modułu**

### **Plik: my_math.py**

```python
"""Mój moduł matematyczny"""

def silnia(n):
    """Zwraca n!"""
    if n <= 1:
        return 1
    return n * silnia(n - 1)

def nwd(a, b):
    """Największy wspólny dzielnik"""
    while b:
        a, b = b, a % b
    return a

def nww(a, b):
    """Najmniejsza wspólna wielokrotność"""
    return abs(a * b) // nwd(a, b)
```

### **Plik: main.py**

```python
from my_math import silnia, nwd

print(silnia(5))  # 120
print(nwd(12, 8))  # 4
```

## **10.6 pip - instalacja pakietów**

Python ma ogromny ekosystem pakietów! Instalujesz je przez **pip**.

```bash
# Instalacja pakietu
pip install requests

# Instalacja konkretnej wersji
pip install requests==2.28.0

# Usunięcie pakietu
pip uninstall requests

# Lista zainstalowanych pakietów
pip list

# Zapis wymagań do pliku
pip freeze > requirements.txt

# Instalacja z pliku wymagań
pip install -r requirements.txt
```

## **10.7 Popularne pakiety**

| Pakiet | Do czego | Instalacja |
|--------|----------|-----------|
| **requests** | Pobieranie danych z internetu | `pip install requests` |
| **numpy** | Obliczenia numeryczne, macierze | `pip install numpy` |
| **pandas** | Analiza danych, tablice | `pip install pandas` |
| **matplotlib** | Wykresy | `pip install matplotlib` |
| **django** | Framework web | `pip install django` |
| **flask** | Lightweight web framework | `pip install flask` |
| **pygame** | Gry | `pip install pygame` |
| **beautifulsoup4** | Scraping HTML | `pip install beautifulsoup4` |

---

# **ROZDZIAŁ 11: Obsługa błędów (Try-Except)**

## **11.1 Co to jest błąd?**

Błędy pojawiają się gdy coś idzie nie tak:

```python
# ❌ Błąd: dzielenie przez zero
wynik = 10 / 0  # ZeroDivisionError

# ❌ Błąd: element nie istnieje
lista = [1, 2, 3]
print(lista[10])  # IndexError

# ❌ Błąd: klucz nie istnieje
slownik = {"imie": "Adam"}
print(slownik["wiek"])  # KeyError

# ❌ Błąd: zły typ
liczba = int("abc")  # ValueError
```

## **11.2 Try-Except - obsługa błędów**

```python
try:
    # Kod który może się wysypać
    liczba = int(input("Wpisz liczbę: "))
    wynik = 10 / liczba
except ValueError:
    # Gdy nie jest liczbą
    print("❌ To nie jest liczba!")
except ZeroDivisionError:
    # Gdy dzielisz przez zero
    print("❌ Nie możesz dzielić przez zero!")
```

**Oczekiwany output:**
```
Wpisz liczbę: abc
❌ To nie jest liczba!
```

## **11.3 Rodzaje błędów (Exceptions)**

```python
# ValueError - zły typ
int("abc")  # ValueError: invalid literal for int()

# ZeroDivisionError - dzielenie przez zero
10 / 0  # ZeroDivisionError: division by zero

# IndexError - indeks poza zakresem
lista = [1, 2, 3]
lista[10]  # IndexError: list index out of range

# KeyError - klucz nie istnieje
slownik = {"imie": "Adam"}
slownik["wiek"]  # KeyError: 'wiek'

# TypeError - zły typ operandu
"5" + 5  # TypeError: can only concatenate str (not "int") to str

# AttributeError - atrybut nie istnieje
class Osoba:
    def __init__(self, imie):
        self.imie = imie

adam = Osoba("Adam")
adam.wiek  # AttributeError: 'Osoba' object has no attribute 'wiek'

# FileNotFoundError - plik nie istnieje
with open("nieistniejacy_plik.txt") as f:
    pass  # FileNotFoundError: [Errno 2] No such file or directory

# NameError - zmienna nie istnieje
print(zmienna_ktorej_nie_ma)  # NameError: name 'zmienna_ktorej_nie_ma' is not defined
```

## **11.4 Struktury try-except**

### **Catch wszystkich błędów:**

```python
try:
    liczba = int(input("Liczba: "))
    wynik = 10 / liczba
except Exception as e:
    # Łapie WSZYSTKIE błędy
    print(f"❌ Błąd: {e}")
```

### **Wiele except:**

```python
try:
    # kod
    pass
except ValueError:
    print("Błąd: złe dane")
except ZeroDivisionError:
    print("Błąd: dzielenie przez zero")
except Exception as e:
    print(f"Inny błąd: {e}")
```

### **Else i finally:**

```python
try:
    liczba = int(input("Liczba: "))
    wynik = 10 / liczba
except ZeroDivisionError:
    print("❌ Dzielenie przez zero!")
except ValueError:
    print("❌ To nie jest liczba!")
else:
    # Wykonuje się jeśli NIE było błędu
    print(f"✅ Wynik: {wynik}")
finally:
    # Wykonuje się ZAWSZE
    print("Koniec programu")
```

## **11.5 Raise - rzucanie własnych błędów**

```python
def dodaj_liczby(a, b):
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Parametry muszą być liczbami!")
    if a < 0 or b < 0:
        raise ValueError("Liczby muszą być dodatnie!")
    return a + b

try:
    wynik = dodaj_liczby(-5, 3)
except ValueError as e:
    print(f"❌ Błąd: {e}")
```

## **11.6 Context managers - with statement**

```python
# ❌ Stary sposób - trzeba ręcznie zamykać plik
f = open("plik.txt", "r")
tekst = f.read()
f.close()

# ✅ Nowy sposób - plik zamyka się automatycznie
with open("plik.txt", "r") as f:
    tekst = f.read()
# Plik jest zamknięty!
```

## **11.7 Praktyczne przykłady**

### **Przykład 1: Bezpieczny kalkulator**

```python
def kalkulator():
    while True:
        try:
            a = float(input("Pierwsza liczba: "))
            operacja = input("Operacja (+, -, *, /): ")
            b = float(input("Druga liczba: "))
            
            if operacja == "+":
                wynik = a + b
            elif operacja == "-":
                wynik = a - b
            elif operacja == "*":
                wynik = a * b
            elif operacja == "/":
                if b == 0:
                    raise ZeroDivisionError("Nie możesz dzielić przez zero!")
                wynik = a / b
            else:
                raise ValueError("Zła operacja!")
            
            print(f"Wynik: {wynik}")
            
        except ValueError:
            print("❌ Wpisz liczbę!")
        except ZeroDivisionError as e:
            print(f"❌ {e}")
        except Exception as e:
            print(f"❌ Błąd: {e}")

kalkulator()
```

### **Przykład 2: Bezpieczne czytanie pliku**

```python
def czytaj_plik(nazwa_pliku):
    try:
        with open(nazwa_pliku, "r") as f:
            zawartość = f.read()
        print(f"✅ Przeczytano {len(zawartość)} znaków")
        return zawartość
    except FileNotFoundError:
        print(f"❌ Plik '{nazwa_pliku}' nie istnieje!")
        return None
    except PermissionError:
        print(f"❌ Brak dostępu do pliku!")
        return None
    except Exception as e:
        print(f"❌ Błąd: {e}")
        return None

tekst = czytaj_plik("dane.txt")
```

### **Przykład 3: Walidacja danych użytkownika**

```python
def pobierz_wiek():
    while True:
        try:
            wiek = int(input("Podaj wiek: "))
            if wiek < 0:
                raise ValueError("Wiek nie może być ujemny!")
            if wiek > 150:
                raise ValueError("Wiek jest zbyt duży!")
            return wiek
        except ValueError as e:
            print(f"❌ {e}. Spróbuj jeszcze raz.")

wiek = pobierz_wiek()
print(f"Twój wiek: {wiek}")
```

---

# **ROZDZIAŁ 12: Programowanie Obiektowe (OOP)**

## **12.1 Co to jest OOP?**

OOP to **paradygmat programowania** gdzie organizujesz kod w **obiekty** i **klasy**.

**Analogia:**
- **Klasa** = plans domu (opisy, instrukcje)
- **Obiekt** = konkretny dom zbudowany według planów

```python
# ❌ Programowanie proceduralne (stary sposób)
imie1 = "Adam"
wiek1 = 25
imie2 = "Katarzyna"
wiek2 = 30

# ✅ Programowanie obiektowe (nowy sposób)
class Osoba:
    def __init__(self, imie, wiek):
        self.imie = imie
        self.wiek = wiek

adam = Osoba("Adam", 25)
kasia = Osoba("Katarzyna", 30)
```

## **12.2 Klasy i obiekty - podstawy**

```python
# Definiowanie klasy
class Pies:
    # Konstruktor - uruchamia się gdy tworzysz obiekt
    def __init__(self, imie, rasa):
        self.imie = imie  # atrybut
        self.rasa = rasa  # atrybut
    
    # Metoda - funkcja należąca do klasy
    def szczekaj(self):
        print(f"{self.imie} szczeka: Hau hau!")
    
    def opis(self):
        return f"Pies {self.imie} rasy {self.rasa}"

# Tworzenie obiektów
burek = Pies("Burek", "Owczarek niemiecki")
maks = Pies("Maks", "Jamnik")

# Dostęp do atrybutów
print(burek.imie)  # Burek
print(burek.rasa)  # Owczarek niemiecki

# Wywoływanie metod
burek.szczekaj()  # Burek szczeka: Hau hau!
print(maks.opis())  # Pies Maks rasy Jamnik
```

## **12.3 __init__ i self**

```python
class Samochód:
    def __init__(self, marka, model, rok):
        self.marka = marka
        self.model = model
        self.rok = rok
        self.predkosc = 0  # Domyślna wartość
    
    def przyspiesz(self, prędkość):
        self.predkosc += prędkość
        print(f"Samochód przyspiesza do {self.predkosc} km/h")
    
    def hamuj(self):
        self.predkosc = 0
        print("Samochód zahamował!")

# self odnosi się do konkretnego obiektu
auto = Samochód("BMW", "X5", 2023)
print(auto.marka)  # BMW
auto.przyspiesz(50)  # Samochód przyspiesza do 50 km/h
```

## **12.4 Atrybuty klasy vs instance**

```python
class Konto:
    oprocentowanie = 0.03  # Atrybut klasy (wspólny dla wszystkich)
    
    def __init__(self, wlasciciel, saldo):
        self.wlasciciel = wlasciciel  # Atrybut instance
        self.saldo = saldo  # Atrybut instance

konto1 = Konto("Adam", 1000)
konto2 = Konto("Kasia", 2000)

print(konto1.oprocentowanie)  # 0.03 (z klasy)
print(konto2.oprocentowanie)  # 0.03 (z klasy)
print(konto1.saldo)  # 1000 (indywidualne)
print(konto2.saldo)  # 2000 (indywidualne)
```

## **12.5 Dziedziczenie (Inheritance)**

Dziedziczenie pozwala na **reużywanie kodu** między klasami.

```python
# Klasa bazowa (parent)
class Zwierze:
    def __init__(self, imie):
        self.imie = imie
    
    def wydaj_glos(self):
        print(f"{self.imie} wydaje głos")

# Klasa pochodna (child)
class Pies(Zwierze):
    def wydaj_glos(self):  # Przesłonięcie metody
        print(f"{self.imie} szczeka: Hau hau!")

class Kot(Zwierze):
    def wydaj_glos(self):
        print(f"{self.imie} miauczy: Miau!")

# Użycie
burek = Pies("Burek")
burek.wydaj_glos()  # Burek szczeka: Hau hau!

fluffy = Kot("Fluffy")
fluffy.wydaj_glos()  # Fluffy miauczy: Miau!
```

### **super() - dostęp do metod rodzica**

```python
class Zwierze:
    def __init__(self, imie, wiek):
        self.imie = imie
        self.wiek = wiek
    
    def opis(self):
        return f"{self.imie}, wiek: {self.wiek}"

class Pies(Zwierze):
    def __init__(self, imie, wiek, rasa):
        super().__init__(imie, wiek)  # Wołaj konstruktor rodzica
        self.rasa = rasa
    
    def opis(self):
        opis_rodzica = super().opis()  # Wołaj metodę rodzica
        return f"{opis_rodzica}, rasa: {self.rasa}"

burek = Pies("Burek", 3, "Owczarek niemiecki")
print(burek.opis())
# Output: Burek, wiek: 3, rasa: Owczarek niemiecki
```

## **12.6 Polimorfizm (Polymorphism)**

Polimorfizm pozwala na **różne zachowania** zależnie od typu obiektu.

```python
class Zwierze:
    def wydaj_glos(self):
        pass

class Pies(Zwierze):
    def wydaj_glos(self):
        return "Hau hau!"

class Kot(Zwierze):
    def wydaj_glos(self):
        return "Miau!"

class Krowa(Zwierze):
    def wydaj_glos(self):
        return "Muuu!"

# Polimorfizm - ta sama funkcja, różne rezultaty
zwierzeta = [Pies(), Kot(), Krowa()]

for zwierze in zwierzeta:
    print(zwierze.wydaj_glos())

# Output:
# Hau hau!
# Miau!
# Muuu!
```

## **12.7 Enkapsulacja (Encapsulation)**

Enkapsulacja to **ukrywanie wewnętrznych szczegółów** klasy.

```python
class Konto:
    def __init__(self, wlasciciel, saldo):
        self.wlasciciel = wlasciciel
        self.__saldo = saldo  # Prywatny atrybut (__)
    
    def wplac(self, kwota):
        if kwota > 0:
            self.__saldo += kwota
            print(f"Wpłacono {kwota}")
        else:
            print("Kwota musi być dodatnia!")
    
    def wyplac(self, kwota):
        if kwota > self.__saldo:
            print("Niewystarczające środki!")
        else:
            self.__saldo -= kwota
            print(f"Wypłacono {kwota}")
    
    def sprawdz_saldo(self):
        return self.__saldo

konto = Konto("Adam", 1000)
konto.wplac(500)  # Wpłacono 500
print(konto.sprawdz_saldo())  # 1500
konto.__saldo = 999999  # ❌ To nie zadziała (Python go zmieni na _Konto__saldo)
```

## **12.8 Praktyczne przykłady**

### **Przykład 1: System pracowników**

```python
class Pracownik:
    def __init__(self, imie, stanowisko, pensja):
        self.imie = imie
        self.stanowisko = stanowisko
        self.__pensja = pensja  # Prywatna
    
    def podwyzka(self, procent):
        self.__pensja *= (1 + procent / 100)
        print(f"✅ {self.imie} dostał podwyżkę!")
    
    def opis(self):
        return f"{self.imie} ({self.stanowisko}): {self.__pensja:.2f} PLN"

class Manager(Pracownik):
    def __init__(self, imie, stanowisko, pensja, zespol):
        super().__init__(imie, stanowisko, pensja)
        self.zespol = zespol
    
    def podwyzka(self, procent):
        super().podwyzka(procent * 1.5)  # Manager dostaje większą podwyżkę

adam = Pracownik("Adam", "Junior Developer", 3000)
maria = Manager("Maria", "Senior Developer", 5000, ["Adam", "Piotr"])

print(adam.opis())  # Adam (Junior Developer): 3000.00 PLN
adam.podwyzka(10)
print(adam.opis())  # Adam (Junior Developer): 3300.00 PLN
```

### **Przykład 2: System urządzeń (dla Twojego scannera!)**

```python
class Urzadzenie:
    def __init__(self, mac_address, nazwa):
        self.mac_address = mac_address
        self.nazwa = nazwa
        self.__podatnosci = []
    
    def dodaj_podatnosc(self, cve):
        self.__podatnosci.append(cve)
        print(f"❌ Dodano podatność: {cve}")
    
    def oblicz_score(self):
        """Wyższy score = bezpieczniej"""
        score = 100
        score -= len(self.__podatnosci) * 25
        return max(0, score)  # Min 0
    
    def raport(self):
        print(f"\n=== {self.nazwa} ({self.mac_address}) ===")
        print(f"Podatności: {len(self.__podatnosci)}")
        print(f"Security Score: {self.oblicz_score()}/100")
        if self.__podatnosci:
            print("CVEs:", ", ".join(self.__podatnosci))

# Użycie
glukometr = Urzadzenie("AA:BB:CC:DD:EE:01", "GlucoSmart Pro")
glukometr.dodaj_podatnosc("CVE-2024-0001")
glukometr.dodaj_podatnosc("CVE-2024-0002")
glukometr.raport()

# Output:
# === GlucoSmart Pro (AA:BB:CC:DD:EE:01) ===
# Podatności: 2
# Security Score: 50/100
# CVEs: CVE-2024-0001, CVE-2024-0002
```

---

# **ROZDZIAŁ 13: Zaawansowane techniki**

## **13.1 List Comprehensions - tworzenie list w jednej linii**

```python
# ❌ Stary sposób
liczby = []
for i in range(10):
    liczby.append(i ** 2)
print(liczby)

# ✅ List comprehension
liczby = [i ** 2 for i in range(10)]
print(liczby)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# Z warunkieiem
parzyscie = [i for i in range(10) if i % 2 == 0]
print(parzyscie)  # [0, 2, 4, 6, 8]

# Transformacja stringów
slowa = ["ala", "bob", "charlie"]
wielkie = [s.upper() for s in slowa]
print(wielkie)  # ['ALA', 'BOB', 'CHARLIE']
```

## **13.2 Dictionary Comprehensions**

```python
# ❌ Stary sposób
slownik = {}
for i in range(5):
    slownik[i] = i ** 2

# ✅ Dict comprehension
slownik = {i: i ** 2 for i in range(5)}
print(slownik)  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Z warunkiem
parzyscie = {i: i ** 2 for i in range(10) if i % 2 == 0}
print(parzyscie)  # {0: 0, 2: 4, 4: 16, 6: 36, 8: 64}
```

## **13.3 Lambda funkcje**

Lambda to **anonimowa funkcja** w jednej linii.

```python
# ❌ Normalna funkcja
def kwadrat(x):
    return x ** 2

# ✅ Lambda
kwadrat = lambda x: x ** 2
print(kwadrat(5))  # 25

# Lambda z wieloma parametrami
dodaj = lambda a, b: a + b
print(dodaj(3, 5))  # 8

# Lambda w map()
liczby = [1, 2, 3, 4, 5]
podwojone = map(lambda x: x * 2, liczby)
print(list(podwojone))  # [2, 4, 6, 8, 10]

# Lambda w filter()
liczby = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
parzyscie = filter(lambda x: x % 2 == 0, liczby)
print(list(parzyscie))  # [2, 4, 6, 8, 10]
```

## **13.4 Dekoratory**

Dekoratory to **funkcje, które modyfikują inne funkcje**.

```python
# Prosty dekorator
def moj_dekorator(funkcja):
    def wrapper():
        print("=== Początek ===")
        funkcja()
        print("=== Koniec ===")
    return wrapper

@moj_dekorator
def pozdrowienie():
    print("Cześć!")

pozdrowienie()

# Output:
# === Początek ===
# Cześć!
# === Koniec ===
```

### **Dekorator z parametrami:**

```python
def powtarzaj(ilosc):
    def dekorator(funkcja):
        def wrapper():
            for i in range(ilosc):
                funkcja()
        return wrapper
    return dekorator

@powtarzaj(3)
def pozdrowienie():
    print("Cześć!")

pozdrowienie()

# Output:
# Cześć!
# Cześć!
# Cześć!
```

### **Dekorator pomiarowy (praktycznie):**

```python
import time

def zmierz_czas(funkcja):
    def wrapper(*args, **kwargs):
        start = time.time()
        wynik = funkcja(*args, **kwargs)
        koniec = time.time()
        print(f"⏱️  Funkcja {funkcja.__name__} trwała {koniec - start:.4f}s")
        return wynik
    return wrapper

@zmierz_czas
def powolna_funkcja():
    time.sleep(1)
    return "Gotowe!"

print(powolna_funkcja())

# Output:
# ⏱️  Funkcja powolna_funkcja trwała 1.0010s
# Gotowe!
```

## **13.5 Generatory i yield**

Generatory to **funkcje, które produkują wartości na żądanie** (zamiast wszystkie naraz).

```python
# ❌ Zwracanie listy (zużywa pamięć)
def liczby_do_miliona():
    liczby = []
    for i in range(1000000):
        liczby.append(i)
    return liczby

# ✅ Generator (oszczędza pamięć)
def liczby_do_miliona_gen():
    for i in range(1000000):
        yield i  # Zwraca wartość, ale pamiętacie gdzie się zatrzymał

# Użycie
for liczba in liczby_do_miliona_gen():
    print(liczba)
    if liczba > 5:
        break
```

### **Praktycznie - odczyt dużych plików:**

```python
def czytaj_plik_liniami(nazwa_pliku):
    with open(nazwa_pliku, "r") as f:
        for linia in f:
            yield linia.strip()

# Czyta plik linia po linii (nie wczytuje całego do pamięci)
for linia in czytaj_plik_liniami("duzy_plik.txt"):
    print(linia)
```

## **13.6 Context Managers (with statement)**

```python
# Plik się zamyka automatycznie
with open("plik.txt", "r") as f:
    tekst = f.read()

# Można też tworzyć własne
class MenedzerZasobow:
    def __enter__(self):
        print("📂 Otwieram zasób")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("📂 Zamykam zasób")
        return False

with MenedzerZasobow():
    print("Używam zasobu")

# Output:
# 📂 Otwieram zasób
# Używam zasobu
# 📂 Zamykam zasób
```

## **13.7 *args i **kwargs**

```python
# *args - wieloargumentowy (tuple)
def suma(*args):
    return sum(args)

print(suma(1, 2, 3, 4, 5))  # 15

# **kwargs - argumenty nazwane (dictionary)
def opis_osoby(**kwargs):
    for klucz, wartosc in kwargs.items():
        print(f"{klucz}: {wartosc}")

opis_osoby(imie="Adam", wiek=25, zawod="Developer")

# Output:
# imie: Adam
# wiek: 25
# zawod: Developer

# Oba razem
def funkcja(a, b, *args, **kwargs):
    print(f"a={a}, b={b}")
    print(f"args={args}")
    print(f"kwargs={kwargs}")

funkcja(1, 2, 3, 4, 5, imie="Adam", wiek=25)

# Output:
# a=1, b=2
# args=(3, 4, 5)
# kwargs={'imie': 'Adam', 'wiek': 25}
```

## **13.8 Type Hints (Type Annotations)**

Type hints pomagają pisać czystszy kod.

```python
# Bez type hints
def dodaj(a, b):
    return a + b

# Z type hints
def dodaj(a: int, b: int) -> int:
    return a + b

# ZListY
from typing import List, Dict, Optional

def przetwarzaj_liczby(liczby: List[int]) -> int:
    return sum(liczby)

def pobierz_uzytkownika(id: int) -> Optional[Dict[str, str]]:
    # Optional[X] = X lub None
    if id == 1:
        return {"imie": "Adam", "wiek": "25"}
    return None

print(przetwarzaj_liczby([1, 2, 3, 4]))  # 10
print(pobierz_uzytkownika(1))  # {'imie': 'Adam', 'wiek': '25'}
```

---

# **ROZDZIAŁ 14: Praktyczne Projekty**

## **PROJEKT 1: System zarządzania zadaniami (TODO)**

```python
import json
import os
from datetime import datetime

class ZadanieApp:
    def __init__(self, plik_dane="zadania.json"):
        self.plik_dane = plik_dane
        self.zadania = self.wczytaj_zadania()
    
    def wczytaj_zadania(self):
        if os.path.exists(self.plik_dane):
            with open(self.plik_dane, "r") as f:
                return json.load(f)
        return []
    
    def zapisz_zadania(self):
        with open(self.plik_dane, "w") as f:
            json.dump(self.zadania, f, indent=2)
    
    def dodaj_zadanie(self, nazwa, priorytet="sredni"):
        zadanie = {
            "id": len(self.zadania) + 1,
            "nazwa": nazwa,
            "priorytet": priorytet,
            "wykonane": False,
            "data_utworzenia": datetime.now().isoformat()
        }
        self.zadania.append(zadanie)
        self.zapisz_zadania()
        print(f"✅ Zadanie dodane: {nazwa}")
    
    def usun_zadanie(self, id):
        self.zadania = [z for z in self.zadania if z["id"] != id]
        self.zapisz_zadania()
        print(f"✅ Zadanie usunięte")
    
    def oznacz_jako_wykonane(self, id):
        for z in self.zadania:
            if z["id"] == id:
                z["wykonane"] = True
        self.zapisz_zadania()
        print(f"✅ Zadanie oznaczone jako wykonane")
    
    def wypisz_zadania(self):
        print("\n=== MOJE ZADANIA ===")
        for z in self.zadania:
            status = "✓" if z["wykonane"] else "○"
            print(f"{status} [{z['id']}] {z['nazwa']} ({z['priorytet']})")
    
    def run(self):
        while True:
            print("\n1. Dodaj zadanie")
            print("2. Wypisz zadania")
            print("3. Oznacz jako wykonane")
            print("4. Usuń zadanie")
            print("5. Wyjdź")
            
            wybor = input("Wybór: ")
            
            if wybor == "1":
                nazwa = input("Nazwa: ")
                priorytet = input("Priorytet (niski/sredni/wysoki): ")
                self.dodaj_zadanie(nazwa, priorytet)
            elif wybor == "2":
                self.wypisz_zadania()
            elif wybor == "3":
                id = int(input("ID zadania: "))
                self.oznacz_jako_wykonane(id)
            elif wybor == "4":
                id = int(input("ID zadania: "))
                self.usun_zadanie(id)
            elif wybor == "5":
                break

if __name__ == "__main__":
    app = ZadanieApp()
    app.run()
```

## **PROJEKT 2: Web scraper - pobieranie danych z internetu**

```python
import requests
from bs4 import BeautifulSoup
import json

class WebScraper:
    def __init__(self, url):
        self.url = url
        self.dane = []
    
    def pobierz_strone(self):
        try:
            response = requests.get(self.url, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                print(f"❌ Status: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Błąd: {e}")
            return None
    
    def parsuj_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        return soup
    
    def zapisz_json(self, nazwa_pliku):
        with open(nazwa_pliku, "w") as f:
            json.dump(self.dane, f, indent=2)
        print(f"✅ Dane zapisane do {nazwa_pliku}")

# Przykład użycia
scraper = WebScraper("https://example.com")
html = scraper.pobierz_strone()
if html:
    soup = scraper.parsuj_html(html)
    # Parsuj dane...
```

## **PROJEKT 3: Kalkulator finansowy**

```python
class Kalkulator:
    def __init__(self):
        self.historia = []
    
    def splata_kredytu(self, kwota, oprocentowanie, lata):
        """Oblicza miesięczną ratę kredytu"""
        miesiace = lata * 12
        stopa_miesieczna = oprocentowanie / 100 / 12
        
        if stopa_miesieczna == 0:
            rata = kwota / miesiace
        else:
            rata = kwota * (stopa_miesieczna * (1 + stopa_miesieczna)**miesiace) / \
                   ((1 + stopa_miesieczna)**miesiace - 1)
        
        lacznie = rata * miesiace
        odsetki = lacznie - kwota
        
        wynik = {
            "rata_miesieczna": round(rata, 2),
            "lacznie": round(lacznie, 2),
            "odsetki": round(odsetki, 2)
        }
        self.historia.append(wynik)
        return wynik
    
    def procent_skladany(self, kapital, stopa, lata):
        """Oblicza procent składany"""
        wynik = kapital * (1 + stopa/100) ** lata
        self.historia.append(round(wynik, 2))
        return round(wynik, 2)

calc = Kalkulator()
splata = calc.splata_kredytu(kwota=100000, oprocentowanie=5, lata=20)
print(f"Miesięczna rata: {splata['rata_miesieczna']} PLN")
print(f"Razem do spłaty: {splata['lacznie']} PLN")
print(f"Odsetki: {splata['odsetki']} PLN")
```

## **PROJEKT 4: Aplikacja pogodowa (z API)**

```python
import requests

class WeatherApp:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def pobierz_pogode(self, miasto):
        try:
            params = {
                "q": miasto,
                "appid": self.api_key,
                "units": "metric"
            }
            response = requests.get(self.base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return self.parsuj_pogode(data)
            else:
                print(f"❌ Nie znaleziono miasta!")
                return None
        except Exception as e:
            print(f"❌ Błąd: {e}")
            return None
    
    def parsuj_pogode(self, data):
        return {
            "miasto": data["name"],
            "temperatura": data["main"]["temp"],
            "odczuwalna": data["main"]["feels_like"],
            "opiswidoczyzenie": data["weather"][0]["description"],
            "wilgotnosc": data["main"]["humidity"],
            "predkosc_wiatru": data["wind"]["speed"]
        }
    
    def wypisz_pogode(self, pogoda):
        if pogoda:
            print(f"\n🌍 Pogoda w mieście: {pogoda['miasto']}")
            print(f"🌡️  Temperatura: {pogoda['temperatura']}°C")
            print(f"🤔 Odczuwalna: {pogoda['odczuwalna']}°C")
            print(f"💨 Wiatr: {pogoda['predkosc_wiatru']} m/s")
            print(f"💧 Wilgotność: {pogoda['wilgotnosc']}%")
            print(f"📝 Opis: {pogoda['opis']}")

# Użycie (potrzebny API key z OpenWeatherMap)
# app = WeatherApp("YOUR_API_KEY")
# pogoda = app.pobierz_pogode("Kraków")
# app.wypisz_pogode(pogoda)
```

## **PROJEKT 5: Analiza logów (dla Twojego scannera!)**

```python
import re
from collections import Counter
from datetime import datetime

class AnalizatorLogow:
    def __init__(self, plik_log):
        self.plik_log = plik_log
        self.logi = self.wczytaj_logi()
    
    def wczytaj_logi(self):
        logi = []
        try:
            with open(self.plik_log, "r") as f:
                for linia in f:
                    logi.append(linia.strip())
            return logi
        except FileNotFoundError:
            print(f"❌ Plik {self.plik_log} nie istnieje!")
            return []
    
    def filtruj_bledu(self, poziom="ERROR"):
        return [log for log in self.logi if poziom in log]
    
    def znajdz_ip(self):
        pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        ips = []
        for log in self.logi:
            match = re.search(pattern, log)
            if match:
                ips.append(match.group())
        return Counter(ips)
    
    def statystyka(self):
        bledy = self.filtruj_bledu("ERROR")
        ostrzezenia = self.filtruj_bledu("WARNING")
        
        print(f"=== STATYSTYKA LOGÓW ===")
        print(f"Łącznie linii: {len(self.logi)}")
        print(f"Błędy: {len(bledy)}")
        print(f"Ostrzeżenia: {len(ostrzezenia)}")
        
        ips = self.znajdz_ip()
        if ips:
            print(f"\nTop IP:")
            for ip, liczba in ips.most_common(5):
                print(f"  {ip}: {liczba}x")

# Użycie
# analizator = AnalizatorLogow("app.log")
# analizator.statystyka()
```

---

# **PODSUMOWANIE**

Gratulacje! 🎉 Ukończyłeś **kompletny samouczek Pythona**!

## **Co teraz?**

1. **Ćwicz zadania** z rozdziałów 1-9
2. **Pracuj nad projektami** z rozdziału 14
3. **Czytaj dokumentację**: https://docs.python.org/3/
4. **GitHub**: Szukaj Open Source projektów do nauki
5. **Kaggle**: Konkursy i zbiory danych

## **Gdzie aplikować wiedzę?**

- Twój **Medical Device Scanner** - teraz naprawisz błędy!
- Automatyzacja zadań
- Web scraping
- Analiza danych
- Machine Learning
- Web development

## **Kolejne kroki po Pythonie:**

- **Git & GitHub** - kontrola wersji
- **SQL** - bazy danych
- **Web frameworks** - Django, Flask (już znasz!)
- **API REST** - tworzenie API
- **Docker** - konteneryzacja

---

**Powodzenia! 🚀 Teraz jesteś gotów do naprawienia Twojego scannera!** 💪
