# 📤 Komendy Git do Aktualizacji Projektu na GitHub

## 🔍 Sprawdzenie Statusu

```bash
# Sprawdź status repozytorium
git status

# Sprawdź czy masz skonfigurowany remote GitHub
git remote -v

# Sprawdź historię commitów
git log --oneline -5

# Sprawdź które pliki są śledzone
git ls-files
```

---

## 🔗 Konfiguracja Remote (jeśli nie masz)

### Opcja 1: HTTPS (łatwiejsze, wymaga loginu)
```bash
# Dodaj remote (ZASTĄP URL swoim repozytorium)
git remote add origin https://github.com/TWOJA-NAZWA/TWOJE-REPO.git

# Sprawdź czy zostało dodane
git remote -v
```

### Opcja 2: SSH (wymaga skonfigurowanego klucza SSH)
```bash
# Dodaj remote (ZASTĄP URL swoim repozytorium)
git remote add origin git@github.com:TWOJA-NAZWA/TWOJE-REPO.git

# Sprawdź czy zostało dodane
git remote -v
```

### Zmiana istniejącego remote:
```bash
# Usuń stary remote
git remote remove origin

# Dodaj nowy remote
git remote add origin https://github.com/TWOJA-NAZWA/TWOJE-REPO.git
```

---

## 📝 Commitowanie Zmian

### Sprawdź co się zmieniło:
```bash
# Zobacz wszystkie zmiany
git status

# Zobacz szczegóły zmian
git diff

# Zobacz tylko nazwy zmienionych plików
git status --short
```

### Dodaj zmiany:
```bash
# Dodaj wszystkie zmiany
git add .

# Lub dodaj konkretne pliki
git add src/scanner.py
git add src/vulnerability_tester.py
git add docs/ULEPSZENIA_PODATNOSCI.md

# Dodaj wszystkie pliki w katalogu
git add src/
git add docs/
git add scripts/
```

### Commit z opisem:
```bash
# Prosty commit
git commit -m "Opis zmian"

# Przykłady:
git commit -m "Usunięto funkcjonalność email, ulepszono wykrywanie podatności"
git commit -m "Dodano testy podatności dla BLE, USB, NFC"
git commit -m "Aktualizacja dokumentacji"
git commit -m "Reorganizacja projektu - przeniesiono pliki do docs/ i scripts/"
git commit -m "Dodano nowe funkcjonalności i poprawki"
```

---

## 📤 Push na GitHub

### Pierwszy push (ustaw upstream):
```bash
# Push na branch main (USTAWIA upstream automatycznie)
git push -u origin main

# Lub użyj pełnej komendy (to samo co -u):
git push --set-upstream origin main

# Lub jeśli Twój branch nazywa się master
git push -u origin master

# Lub push na konkretny branch
git push -u origin nazwa-brancha
```

### ⚠️ Błąd: "The current branch main has no upstream branch"

Jeśli widzisz ten błąd:
```bash
fatal: The current branch main has no upstream branch.
To push the current branch and set the remote as upstream, use
    git push --set-upstream origin main
```

**Rozwiązanie:** Użyj komendy którą Git sugeruje:
```bash
git push --set-upstream origin main
# LUB krócej:
git push -u origin main
```

Po pierwszym pushu z `-u`, kolejne pushy będą działać z samym `git push`.

### Kolejne pushy (po pierwszym):
```bash
# Prosty push (działa tylko jeśli ustawiłeś upstream z -u)
git push

# Lub z podaniem brancha (zawsze działa)
git push origin main
```

### Force push (TYLKO jeśli wiesz co robisz!):
```bash
# ⚠️ UWAGA: Nadpisuje historię na GitHubie!
git push --force origin main
```

---

## 🔄 Pełny Workflow (od zera)

```bash
# 1. Sprawdź status
git status

# 2. Dodaj wszystkie zmiany
git add .

# 3. Commit z opisem
git commit -m "Opis Twoich zmian"

# 4. Push na GitHub
# Jeśli pierwszy raz (lub widzisz błąd "no upstream branch"):
git push -u origin main

# Jeśli już ustawiłeś upstream wcześniej:
git push
```

### 🔍 Sprawdź czy masz ustawiony upstream:
```bash
# Sprawdź tracking branch
git branch -vv

# Jeśli widzisz "[origin/main]" to upstream jest ustawiony
# Jeśli nie widzisz, użyj: git push -u origin main
```

---

## 🆘 Rozwiązywanie Problemów

### Błąd: "The current branch main has no upstream branch"

**Problem:** Próbujesz zrobić `git push` ale Git nie wie gdzie pushować.

**Rozwiązanie:**
```bash
# Ustaw upstream i push jednocześnie
git push -u origin main

# Lub jeśli Twój branch nazywa się inaczej:
git push -u origin nazwa-twojego-brancha
```

**Sprawdź czy działa:**
```bash
# Po ustawieniu upstream, sprawdź:
git branch -vv
# Powinieneś zobaczyć: * main [origin/main] ...

# Teraz `git push` będzie działać bez `-u`
```

### Jeśli masz konflikt z remote:
```bash
# Pobierz zmiany z GitHub
git fetch origin

# Zobacz różnice
git diff main origin/main

# Zmerguj zmiany
git pull origin main

# Rozwiąż konflikty (jeśli są), potem:
git add .
git commit -m "Rozwiązano konflikty"
git push
```

### Jeśli zapomniałeś dodać plik do commita:
```bash
# Dodaj plik do ostatniego commita
git add zapomniany_plik.py
git commit --amend --no-edit

# Push (może wymagać force push)
git push --force-with-lease origin main
```

### Jeśli chcesz cofnąć ostatni commit (lokalnie):
```bash
# Cofnij commit, ale zostaw zmiany
git reset --soft HEAD~1

# Cofnij commit i zmiany (UWAGA: usuwa zmiany!)
git reset --hard HEAD~1
```

### Jeśli chcesz zmienić nazwę brancha:
```bash
# Zmień nazwę lokalnego brancha
git branch -m stara-nazwa nowa-nazwa

# Push nowego brancha
git push -u origin nowa-nazwa

# Usuń stary branch na GitHubie
git push origin --delete stara-nazwa
```

---

## 📋 Przydatne Skróty

```bash
# Status w jednej linii
git status -s

# Krótki log
git log --oneline -10

# Zobacz różnice w konkretnym pliku
git diff src/scanner.py
git diff docs/GITHUB_KOMENDY.md

# Zobacz co zostało zmienione w ostatnim commicie
git show

# Zobacz wszystkie branche
git branch -a

# Przełącz się na branch
git checkout nazwa-brancha

# Utwórz nowy branch
git checkout -b nowy-branch
```

---

## ✅ Szybki Checklist Przed Pushem

- [ ] `git status` - sprawdź co się zmieniło
- [ ] `git add .` - dodaj zmiany
- [ ] `git commit -m "..."` - commit z opisem
- [ ] `git push` - wyślij na GitHub

---

## 🔐 Uwagi o Bezpieczeństwie

1. **NIE commituj pliku `.env`** - zawiera klucze API! (jest w `.gitignore`)
2. **Sprawdź `.gitignore`** - upewnij się że wrażliwe pliki są ignorowane
3. **Katalogi `reports/` i `exports/` są ignorowane** - nie commituj wygenerowanych raportów
4. **Używaj `--force-with-lease` zamiast `--force`** - bezpieczniejsze
5. **Nie pushuj dużych plików** - użyj Git LFS lub usuń z historii

## 📁 Struktura Projektu (po reorganizacji)

Projekt został zreorganizowany:
- **`docs/`** - Wszystkie pliki dokumentacji (.md)
- **`scripts/`** - Skrypty pomocnicze (.sh, .py)
- **`src/`** - Kod źródłowy Python
- **`reports/`** - Wygenerowane raporty (ignorowane przez Git)
- **`exports/`** - Eksporty SIEM (ignorowane przez Git)

**Przykłady commitowania:**
```bash
# Dodaj zmiany w dokumentacji
git add docs/
git commit -m "Aktualizacja dokumentacji"

# Dodaj zmiany w kodzie
git add src/
git commit -m "Poprawki w kodzie"

# Dodaj skrypty
git add scripts/
git commit -m "Dodano nowe skrypty"

# Dodaj wszystko oprócz reports/ i exports/ (są ignorowane)
git add .
git commit -m "Aktualizacja projektu"
```

---

## 📚 Dodatkowe Zasoby

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

---

**💡 Wskazówka:** Zapisz ten plik i używaj jako referencji przy każdej aktualizacji projektu!
