# 🐍 Python - Od Podstaw do Zaawansowanego

## 📚 Wprowadzenie

Ten dokument zawiera przykłady Pythona od podstaw do zaawansowanych konceptów, z wyjaśnieniami. Każdy przykład możesz skopiować i uruchomić.

---

## 📖 Część 1: Podstawy Pythona

### 1.1. Zmienne i Typy Danych

```python
# Zmienne - przechowują wartości
name = "Jan"  # str (tekst)
age = 25      # int (liczba całkowita)
height = 1.75  # float (liczba dziesiętna)
is_student = True  # bool (True/False)

print(name)        # Wypisze: Jan
print(age)         # Wypisze: 25
print(height)      # Wypisze: 1.75
print(is_student)  # Wypisze: True

# Python automatycznie wykrywa typ
print(type(name))  # <class 'str'>
print(type(age))   # <class 'int'>
```

**Wyjaśnienie:**
- **Zmienna** - nazwa która przechowuje wartość
- **Typ danych** - rodzaj wartości (str, int, float, bool)
- Python automatycznie wykrywa typ (nie musisz go podawać)

---

### 1.2. Listy (Lists)

```python
# Lista - przechowuje wiele wartości
fruits = ["jabłko", "banan", "pomarańcza"]
numbers = [1, 2, 3, 4, 5]
mixed = ["tekst", 42, True]  # Może zawierać różne typy

# Dostęp do elementów (indeksowanie zaczyna się od 0)
print(fruits[0])   # jabłko (pierwszy element)
print(fruits[1])   # banan (drugi element)
print(fruits[-1])  # pomarańcza (ostatni element, -1 to ostatni)

# Dodawanie elementów
fruits.append("winogrono")  # Dodaje na końcu
print(fruits)  # ['jabłko', 'banan', 'pomarańcza', 'winogrono']

# Długość listy
print(len(fruits))  # 4
```

**Wyjaśnienie:**
- **Lista** - uporządkowana kolekcja elementów
- **Indeksowanie** - zaczyna się od 0 (pierwszy element = 0)
- **-1** - ostatni element (od końca)
- **append()** - dodaje element na końcu

---

### 1.3. Słowniki (Dictionaries)

```python
# Słownik - przechowuje pary klucz-wartość
person = {
    "name": "Jan",
    "age": 25,
    "city": "Warszawa"
}

# Dostęp do wartości
print(person["name"])  # Jan
print(person["age"])   # 25

# Dodawanie nowych par
person["email"] = "jan@example.com"
print(person)  # {'name': 'Jan', 'age': 25, 'city': 'Warszawa', 'email': 'jan@example.com'}

# Sprawdzanie czy klucz istnieje
if "age" in person:
    print("Wiek:", person["age"])

# Wszystkie klucze i wartości
print(person.keys())    # dict_keys(['name', 'age', 'city', 'email'])
print(person.values())  # dict_values(['Jan', 25, 'Warszawa', 'jan@example.com'])
```

**Wyjaśnienie:**
- **Słownik** - przechowuje pary klucz-wartość
- **Klucz** - unikalny identyfikator (np. "name")
- **Wartość** - dane przypisane do klucza (np. "Jan")
- **in** - sprawdza czy klucz istnieje

---

### 1.4. Pętle (Loops)

#### Pętla for:

```python
# Pętla for - wykonuje kod dla każdego elementu
fruits = ["jabłko", "banan", "pomarańcza"]

# Iteracja po liście
for fruit in fruits:
    print(fruit)
# Wypisze:
# jabłko
# banan
# pomarańcza

# Iteracja z indeksem
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")
# Wypisze:
# 0: jabłko
# 1: banan
# 2: pomarańcza

# Iteracja po zakresie liczb
for i in range(5):  # 0, 1, 2, 3, 4
    print(i)
```

**Wyjaśnienie:**
- **for** - wykonuje kod dla każdego elementu
- **in** - iteruje po kolekcji
- **enumerate()** - zwraca indeks i wartość
- **range()** - generuje liczby (0, 1, 2, ...)

#### Pętla while:

```python
# Pętla while - wykonuje kod dopóki warunek jest True
count = 0
while count < 5:
    print(count)
    count += 1  # Zwiększ count o 1
# Wypisze: 0, 1, 2, 3, 4
```

**Wyjaśnienie:**
- **while** - wykonuje kod dopóki warunek jest True
- **count += 1** - to samo co `count = count + 1`

---

### 1.5. Warunki (If/Else)

```python
# Warunki - wykonują kod jeśli warunek jest spełniony
age = 20

if age >= 18:
    print("Jesteś pełnoletni")
else:
    print("Jesteś niepełnoletni")

# Wiele warunków
score = 85
if score >= 90:
    print("Ocena: 5")
elif score >= 75:
    print("Ocena: 4")
elif score >= 60:
    print("Ocena: 3")
else:
    print("Ocena: 2")

# Operatory porównania
x = 10
print(x == 10)  # True (równe)
print(x != 5)    # True (różne)
print(x > 5)     # True (większe)
print(x < 20)    # True (mniejsze)
print(x >= 10)   # True (większe lub równe)
print(x <= 15)   # True (mniejsze lub równe)
```

**Wyjaśnienie:**
- **if** - wykonuje kod jeśli warunek jest True
- **else** - wykonuje kod jeśli warunek jest False
- **elif** - sprawdza kolejny warunek
- **==** - porównuje (równe)
- **!=** - różne
- **>**, **<**, **>=**, **<=** - porównania liczbowe

---

### 1.6. Funkcje (Functions)

```python
# Funkcja - blok kodu który można wywołać wielokrotnie
def greet(name):
    """Wita użytkownika"""
    return f"Witaj, {name}!"

# Wywołanie funkcji
message = greet("Jan")
print(message)  # Witaj, Jan!

# Funkcja z wieloma parametrami
def add_numbers(a, b):
    """Dodaje dwie liczby"""
    return a + b

result = add_numbers(5, 3)
print(result)  # 8

# Funkcja z wartościami domyślnymi
def greet_with_title(name, title="Pan"):
    """Wita z tytułem"""
    return f"Witaj, {title} {name}!"

print(greet_with_title("Kowalski"))           # Witaj, Pan Kowalski!
print(greet_with_title("Nowak", "Pani"))       # Witaj, Pani Nowak!
```

**Wyjaśnienie:**
- **def** - definiuje funkcję
- **return** - zwraca wartość
- **parametry** - wartości przekazywane do funkcji
- **wartości domyślne** - używane jeśli nie podasz wartości

---

### 1.7. Klasy (Classes)

```python
# Klasa - szablon do tworzenia obiektów
class Person:
    """Klasa reprezentująca osobę"""
    
    def __init__(self, name, age):
        """Konstruktor - inicjalizuje obiekt"""
        self.name = name  # self.name to atrybut obiektu
        self.age = age
    
    def introduce(self):
        """Metoda - funkcja w klasie"""
        return f"Jestem {self.name}, mam {self.age} lat"
    
    def have_birthday(self):
        """Metoda która zmienia stan obiektu"""
        self.age += 1

# Tworzenie obiektu (instancji klasy)
person1 = Person("Jan", 25)
print(person1.introduce())  # Jestem Jan, mam 25 lat

person1.have_birthday()
print(person1.introduce())  # Jestem Jan, mam 26 lat
```

**Wyjaśnienie:**
- **class** - definiuje klasę
- **__init__** - konstruktor (uruchamia się przy tworzeniu obiektu)
- **self** - odniesienie do obiektu
- **metoda** - funkcja w klasie
- **obiekt** - instancja klasy

---

## 📖 Część 2: Średnio Zaawansowane

### 2.1. List Comprehensions

```python
# List comprehension - krótki sposób na tworzenie list
# Zamiast:
numbers = []
for i in range(5):
    numbers.append(i * 2)
print(numbers)  # [0, 2, 4, 6, 8]

# Możesz napisać:
numbers = [i * 2 for i in range(5)]
print(numbers)  # [0, 2, 4, 6, 8]

# Z warunkiem
even_numbers = [i for i in range(10) if i % 2 == 0]
print(even_numbers)  # [0, 2, 4, 6, 8]

# Z wieloma warunkami
numbers = [i for i in range(20) if i % 2 == 0 and i > 5]
print(numbers)  # [6, 8, 10, 12, 14, 16, 18]
```

**Wyjaśnienie:**
- **List comprehension** - krótki sposób na tworzenie list
- Składnia: `[wyrażenie for element in kolekcja if warunek]`
- Szybsze i bardziej czytelne niż pętla for

---

### 2.2. Dictionary Comprehensions

```python
# Dictionary comprehension - krótki sposób na tworzenie słowników
# Zamiast:
squares = {}
for i in range(5):
    squares[i] = i ** 2
print(squares)  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Możesz napisać:
squares = {i: i ** 2 for i in range(5)}
print(squares)  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Z warunkiem
even_squares = {i: i ** 2 for i in range(10) if i % 2 == 0}
print(even_squares)  # {0: 0, 2: 4, 4: 16, 6: 36, 8: 64}
```

**Wyjaśnienie:**
- **Dictionary comprehension** - krótki sposób na tworzenie słowników
- Składnia: `{klucz: wartość for element in kolekcja if warunek}`

---

### 2.3. Lambda Functions

```python
# Lambda - krótka funkcja bez nazwy
# Zamiast:
def add(x, y):
    return x + y

# Możesz napisać:
add = lambda x, y: x + y
print(add(5, 3))  # 8

# Użycie z map() - aplikuje funkcję do każdego elementu
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x ** 2, numbers))
print(squared)  # [1, 4, 9, 16, 25]

# Użycie z filter() - filtruje elementy
even = list(filter(lambda x: x % 2 == 0, numbers))
print(even)  # [2, 4]

# Użycie z sorted() - sortuje
people = [("Jan", 25), ("Anna", 30), ("Piotr", 20)]
sorted_by_age = sorted(people, key=lambda x: x[1])
print(sorted_by_age)  # [('Piotr', 20), ('Jan', 25), ('Anna', 30)]
```

**Wyjaśnienie:**
- **lambda** - krótka funkcja bez nazwy
- **map()** - aplikuje funkcję do każdego elementu
- **filter()** - filtruje elementy według warunku
- **sorted()** - sortuje kolekcję

---

### 2.4. Generatory (Generators)

```python
# Generator - zwraca wartości jeden po drugim (oszczędza pamięć)
def count_up_to(max_count):
    """Generator - zwraca liczby od 1 do max_count"""
    count = 1
    while count <= max_count:
        yield count  # yield zamiast return
        count += 1

# Użycie generatora
for number in count_up_to(5):
    print(number)
# Wypisze: 1, 2, 3, 4, 5

# Generator expression (krótsza składnia)
squares = (x ** 2 for x in range(5))
for square in squares:
    print(square)
# Wypisze: 0, 1, 4, 9, 16
```

**Wyjaśnienie:**
- **Generator** - zwraca wartości jeden po drugim (nie wszystkie na raz)
- **yield** - zwraca wartość i zatrzymuje się (zamiast return)
- **Oszczędza pamięć** - nie przechowuje wszystkich wartości w pamięci

---

### 2.5. Decorators (Dekoratory)

```python
# Decorator - funkcja która modyfikuje inną funkcję
def my_decorator(func):
    """Dekorator który dodaje tekst przed i po funkcji"""
    def wrapper():
        print("Przed funkcją")
        func()
        print("Po funkcji")
    return wrapper

@my_decorator
def say_hello():
    print("Witaj!")

say_hello()
# Wypisze:
# Przed funkcją
# Witaj!
# Po funkcji

# Decorator z parametrami
def repeat(times):
    """Dekorator który powtarza funkcję"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"Witaj, {name}!")

greet("Jan")
# Wypisze:
# Witaj, Jan!
# Witaj, Jan!
# Witaj, Jan!
```

**Wyjaśnienie:**
- **Decorator** - funkcja która modyfikuje inną funkcję
- **@decorator** - składnia dekoratora
- **wrapper** - funkcja która opakowuje oryginalną funkcję
- ***args, **kwargs** - przyjmuje dowolną liczbę argumentów

---

### 2.6. Context Managers (with)

```python
# Context manager - automatycznie zarządza zasobami
# Zamiast:
file = open("test.txt", "w")
file.write("Hello")
file.close()  # Musisz pamiętać o zamknięciu!

# Możesz napisać:
with open("test.txt", "w") as file:
    file.write("Hello")
# Plik automatycznie się zamknie po wyjściu z bloku 'with'

# Własny context manager
class Timer:
    """Context manager który mierzy czas"""
    def __enter__(self):
        import time
        self.start = time.time()
        return self
    
    def __exit__(self, *args):
        import time
        self.end = time.time()
        print(f"Czas wykonania: {self.end - self.start:.2f} sekund")

# Użycie
with Timer():
    # Kod który mierzymy
    sum(range(1000000))
# Wypisze: Czas wykonania: 0.05 sekund
```

**Wyjaśnienie:**
- **with** - automatycznie zarządza zasobami
- **__enter__** - uruchamia się przy wejściu do bloku
- **__exit__** - uruchamia się przy wyjściu z bloku
- **Automatyczne zamykanie** - nie musisz pamiętać o zamknięciu zasobów

---

## 📖 Część 3: Zaawansowane

### 3.1. Type Hints (Adnotacje Typów)

```python
from typing import List, Dict, Optional, Union

# Type hints - informują jaki typ zwraca funkcja
def add_numbers(a: int, b: int) -> int:
    """Dodaje dwie liczby całkowite"""
    return a + b

# Lista z type hint
def get_names() -> List[str]:
    """Zwraca listę imion"""
    return ["Jan", "Anna", "Piotr"]

# Słownik z type hint
def get_person() -> Dict[str, Union[str, int]]:
    """Zwraca słownik z danymi osoby"""
    return {"name": "Jan", "age": 25}

# Optional - może być None
def find_user(user_id: int) -> Optional[Dict[str, str]]:
    """Znajduje użytkownika lub zwraca None"""
    if user_id == 1:
        return {"name": "Jan"}
    return None

# Union - może być jeden z kilku typów
def process_data(data: Union[str, int]) -> str:
    """Przetwarza dane (str lub int)"""
    return str(data)
```

**Wyjaśnienie:**
- **Type hints** - informują o typach (opcjonalne, ale zalecane)
- **-> int** - funkcja zwraca int
- **List[str]** - lista stringów
- **Dict[str, int]** - słownik: klucze str, wartości int
- **Optional** - może być None
- **Union** - może być jeden z kilku typów

---

### 3.2. Dataclasses

```python
from dataclasses import dataclass, field
from typing import List

# Dataclass - automatycznie generuje metody
@dataclass
class Person:
    """Klasa reprezentująca osobę"""
    name: str
    age: int
    email: str = ""  # Wartość domyślna
    hobbies: List[str] = field(default_factory=list)  # Lista z domyślną wartością

# Automatycznie generuje:
# - __init__() - konstruktor
# - __repr__() - reprezentacja tekstowa
# - __eq__() - porównanie równości

person1 = Person("Jan", 25, "jan@example.com")
person2 = Person("Jan", 25, "jan@example.com")

print(person1)  # Person(name='Jan', age=25, email='jan@example.com', hobbies=[])
print(person1 == person2)  # True (automatyczne porównanie)
```

**Wyjaśnienie:**
- **@dataclass** - automatycznie generuje metody
- **field(default_factory=list)** - domyślna wartość to pusta lista
- **Automatyczne metody** - __init__, __repr__, __eq__

---

### 3.3. Property (Właściwości)

```python
# Property - pozwala używać metod jak atrybutów
class Circle:
    """Klasa reprezentująca koło"""
    
    def __init__(self, radius):
        self._radius = radius  # _ oznacza "prywatny" (konwencja)
    
    @property
    def radius(self):
        """Getter - zwraca promień"""
        return self._radius
    
    @radius.setter
    def radius(self, value):
        """Setter - ustawia promień"""
        if value < 0:
            raise ValueError("Promień nie może być ujemny")
        self._radius = value
    
    @property
    def area(self):
        """Właściwość - oblicza pole"""
        return 3.14159 * self._radius ** 2

# Użycie
circle = Circle(5)
print(circle.radius)  # 5 (używa gettera)
print(circle.area)    # 78.54 (oblicza automatycznie)

circle.radius = 10    # Używa settera
print(circle.area)    # 314.16
```

**Wyjaśnienie:**
- **@property** - pozwala używać metody jak atrybutu
- **@setter** - pozwala ustawiać wartość przez atrybut
- **Getter/Setter** - kontrola dostępu do atrybutów

---

### 3.4. Magic Methods (Metody Specjalne)

```python
# Magic methods - specjalne metody (zaczynają się i kończą __)
class Point:
    """Klasa reprezentująca punkt"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __str__(self):
        """Wywoływane przez str() i print()"""
        return f"Point({self.x}, {self.y})"
    
    def __repr__(self):
        """Wywoływane przez repr()"""
        return f"Point(x={self.x}, y={self.y})"
    
    def __add__(self, other):
        """Wywoływane przez +"""
        return Point(self.x + other.x, self.y + other.y)
    
    def __eq__(self, other):
        """Wywoływane przez =="""
        return self.x == other.x and self.y == other.y
    
    def __len__(self):
        """Wywoływane przez len()"""
        return int((self.x ** 2 + self.y ** 2) ** 0.5)  # Długość wektora

# Użycie
p1 = Point(3, 4)
p2 = Point(1, 2)

print(p1)           # Point(3, 4) - używa __str__
print(p1 + p2)      # Point(4, 6) - używa __add__
print(p1 == p2)     # False - używa __eq__
print(len(p1))      # 5 - używa __len__
```

**Wyjaśnienie:**
- **Magic methods** - specjalne metody (__nazwa__)
- **__str__** - reprezentacja tekstowa (dla użytkownika)
- **__repr__** - reprezentacja techniczna (dla programistów)
- **__add__** - definiuje działanie +
- **__eq__** - definiuje działanie ==
- **__len__** - definiuje działanie len()

---

### 3.5. Exception Handling (Obsługa Wyjątków)

```python
# Exception handling - obsługa błędów
try:
    # Kod który może rzucić błąd
    number = int(input("Podaj liczbę: "))
    result = 10 / number
    print(f"Wynik: {result}")
except ValueError:
    # Obsługa błędu ValueError (nieprawidłowa wartość)
    print("To nie jest liczba!")
except ZeroDivisionError:
    # Obsługa błędu ZeroDivisionError (dzielenie przez zero)
    print("Nie można dzielić przez zero!")
except Exception as e:
    # Obsługa wszystkich innych błędów
    print(f"Wystąpił błąd: {e}")
else:
    # Wykonuje się jeśli nie było błędu
    print("Wszystko OK!")
finally:
    # Zawsze się wykonuje (nawet jeśli był błąd)
    print("Koniec")

# Rzucanie własnych wyjątków
def check_age(age):
    """Sprawdza wiek i rzuca wyjątek jeśli nieprawidłowy"""
    if age < 0:
        raise ValueError("Wiek nie może być ujemny")
    if age > 150:
        raise ValueError("Wiek nie może być większy niż 150")
    return True

try:
    check_age(-5)
except ValueError as e:
    print(f"Błąd: {e}")  # Błąd: Wiek nie może być ujemny
```

**Wyjaśnienie:**
- **try** - kod który może rzucić błąd
- **except** - obsługa błędu
- **else** - wykonuje się jeśli nie było błędu
- **finally** - zawsze się wykonuje
- **raise** - rzuca wyjątek

---

### 3.6. Async/Await (Programowanie Asynchroniczne)

```python
import asyncio

# Async/await - programowanie asynchroniczne (nie blokuje)
async def fetch_data(url):
    """Symuluje pobieranie danych"""
    print(f"Pobieram dane z {url}...")
    await asyncio.sleep(1)  # Symuluje czekanie
    return f"Dane z {url}"

async def main():
    """Główna funkcja async"""
    # Wykonuje się sekwencyjnie (jedno po drugim)
    data1 = await fetch_data("url1")
    data2 = await fetch_data("url2")
    print(data1, data2)
    
    # Wykonuje się równolegle (jednocześnie)
    data1, data2 = await asyncio.gather(
        fetch_data("url1"),
        fetch_data("url2")
    )
    print(data1, data2)

# Uruchomienie
asyncio.run(main())
```

**Wyjaśnienie:**
- **async** - funkcja asynchroniczna
- **await** - czeka na zakończenie operacji
- **asyncio.gather()** - wykonuje wiele operacji równolegle
- **Nie blokuje** - inne operacje mogą działać podczas czekania

---

### 3.7. Enums (Wyliczenia)

```python
from enum import Enum

# Enum - zestaw stałych wartości
class Status(Enum):
    """Status zadania"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Użycie
task_status = Status.IN_PROGRESS
print(task_status)        # Status.IN_PROGRESS
print(task_status.value) # in_progress
print(task_status.name)  # IN_PROGRESS

# Porównanie
if task_status == Status.IN_PROGRESS:
    print("Zadanie w trakcie")

# Iteracja po wszystkich wartościach
for status in Status:
    print(f"{status.name}: {status.value}")
```

**Wyjaśnienie:**
- **Enum** - zestaw stałych wartości
- **value** - wartość enum
- **name** - nazwa enum
- **Bezpieczeństwo typów** - nie można użyć nieprawidłowej wartości

---

### 3.8. Metaclasses (Zaawansowane)

```python
# Metaclass - klasa która tworzy klasy
class Singleton(type):
    """Metaclass który tworzy singleton (tylko jedna instancja)"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=Singleton):
    """Klasa która zawsze ma tylko jedną instancję"""
    def __init__(self):
        print("Tworzę połączenie z bazą danych")

# Użycie
db1 = Database()  # Tworzę połączenie z bazą danych
db2 = Database()  # (nie wypisze nic - używa istniejącej instancji)
print(db1 is db2)  # True (to ten sam obiekt)
```

**Wyjaśnienie:**
- **Metaclass** - klasa która tworzy klasy
- **Singleton** - wzorzec projektowy (tylko jedna instancja)
- **Zaawansowane** - rzadko używane, ale potężne

---

### 3.9. Descriptors (Deskryptory)

```python
# Descriptor - kontroluje dostęp do atrybutu
class PositiveNumber:
    """Descriptor - zapewnia że liczba jest dodatnia"""
    
    def __init__(self, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        return obj.__dict__.get(self.name, 0)
    
    def __set__(self, obj, value):
        if value < 0:
            raise ValueError(f"{self.name} musi być dodatnie")
        obj.__dict__[self.name] = value

class Rectangle:
    """Klasa która używa descriptor"""
    width = PositiveNumber("width")
    height = PositiveNumber("height")
    
    def __init__(self, width, height):
        self.width = width
        self.height = height

# Użycie
rect = Rectangle(5, 10)
print(rect.width)   # 5

try:
    rect.width = -5  # Rzuci ValueError
except ValueError as e:
    print(f"Błąd: {e}")  # Błąd: width musi być dodatnie
```

**Wyjaśnienie:**
- **Descriptor** - kontroluje dostęp do atrybutu
- **__get__** - wywoływane przy odczycie
- **__set__** - wywoływane przy zapisie
- **Kontrola dostępu** - możesz dodać walidację

---

### 3.10. Contextlib (Zaawansowane Context Managers)

```python
from contextlib import contextmanager, suppress

# @contextmanager - łatwy sposób na context manager
@contextmanager
def timer():
    """Context manager który mierzy czas"""
    import time
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        print(f"Czas: {end - start:.2f}s")

# Użycie
with timer():
    sum(range(1000000))

# suppress - ignoruje wyjątki
with suppress(FileNotFoundError):
    # Jeśli plik nie istnieje, błąd jest ignorowany
    with open("nieistniejacy.txt") as f:
        print(f.read())
```

**Wyjaśnienie:**
- **@contextmanager** - łatwy sposób na context manager
- **suppress** - ignoruje wyjątki
- **yield** - zwraca kontrolę do bloku with

---

## 📚 Podsumowanie - Od Podstaw do Zaawansowanego

### Podstawy:
- ✅ Zmienne i typy danych
- ✅ Listy i słowniki
- ✅ Pętle i warunki
- ✅ Funkcje i klasy

### Średnio Zaawansowane:
- ✅ List comprehensions
- ✅ Lambda functions
- ✅ Generatory
- ✅ Decorators
- ✅ Context managers

### Zaawansowane:
- ✅ Type hints
- ✅ Dataclasses
- ✅ Property
- ✅ Magic methods
- ✅ Exception handling
- ✅ Async/await
- ✅ Enums
- ✅ Metaclasses
- ✅ Descriptors

---

**Powodzenia w nauce Pythona! 🚀**
