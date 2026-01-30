# 🔧 Rozwiązanie Konfliktu z GitHub

## Problem
GitHub odrzucił push, ponieważ na zdalnym repozytorium są zmiany, których nie masz lokalnie.

## ✅ Rozwiązanie - Krok po Kroku

### Opcja 1: Pull i Merge (Zalecane)

```bash
# 1. Pobierz zmiany z GitHub i zmerguj je
git pull origin main --allow-unrelated-histories

# Jeśli pojawi się pytanie o autentykację:
# - Dla HTTPS: podaj username i Personal Access Token (nie hasło!)
# - Dla SSH: użyj klucza SSH

# 2. Jeśli są konflikty, rozwiąż je:
# - Otwórz pliki z konfliktami (będą oznaczone <<<<<<<)
# - Usuń markery konfliktów i zostaw właściwy kod
# - Zapisz pliki

# 3. Dodaj rozwiązane pliki
git add .

# 4. Zakończ merge
git commit -m "Merge zmian z GitHub"

# 5. Wypchnij zmiany
git push origin main
```

### Opcja 2: Zmień na SSH (jeśli masz klucz SSH)

```bash
# 1. Zmień URL remote na SSH
git remote set-url origin git@github.com:LANDaNuM/medical-device-scanner.git

# 2. Sprawdź
git remote -v

# 3. Pull i merge
git pull origin main --allow-unrelated-histories

# 4. Push
git push origin main
```

### Opcja 3: Force Push (⚠️ UWAGA: Nadpisze zmiany na GitHubie!)

**Używaj TYLKO jeśli wiesz, że zmiany na GitHubie nie są ważne!**

```bash
# 1. Force push (nadpisze zmiany na GitHubie)
git push --force-with-lease origin main

# Lub bardziej agresywnie (nie zalecane):
# git push --force origin main
```

---

## 🔐 Autentykacja GitHub

### HTTPS - Personal Access Token

1. **Utwórz Personal Access Token:**
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token (classic)
   - Wybierz scope: `repo` (pełny dostęp do repozytoriów)
   - Skopiuj token

2. **Użyj tokenu jako hasła:**
   ```bash
   git pull origin main
   # Username: LANDaNuM
   # Password: [wklej token tutaj]
   ```

### SSH - Klucz SSH

1. **Sprawdź czy masz klucz SSH:**
   ```bash
   ls -la ~/.ssh/id_*.pub
   ```

2. **Jeśli nie masz, utwórz:**
   ```bash
   ssh-keygen -t ed25519 -C "twoj-email@example.com"
   ```

3. **Dodaj klucz do GitHub:**
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # Skopiuj output i dodaj do GitHub → Settings → SSH and GPG keys
   ```

4. **Zmień remote na SSH:**
   ```bash
   git remote set-url origin git@github.com:LANDaNuM/medical-device-scanner.git
   ```

---

## 🎯 Szybkie Rozwiązanie (Jeśli chcesz nadpisać GitHub)

**⚠️ UWAGA: To usunie zmiany na GitHubie!**

```bash
# 1. Force push (nadpisze GitHub Twoimi lokalnymi zmianami)
git push --force-with-lease origin main
```

---

## 📋 Co Zrobić Teraz?

1. **Jeśli zmiany na GitHubie są ważne:**
   - Użyj Opcji 1 (Pull i Merge)
   - Rozwiąż konflikty ręcznie

2. **Jeśli zmiany na GitHubie NIE są ważne:**
   - Użyj Opcji 3 (Force Push)
   - ⚠️ Uważaj - to nadpisze GitHub!

3. **Jeśli chcesz uniknąć problemów z autentykacją:**
   - Skonfiguruj SSH (Opcja 2)
   - Lub użyj Personal Access Token

---

## 💡 Wskazówki

- **Zawsze używaj `--force-with-lease` zamiast `--force`** - bezpieczniejsze
- **Sprawdź zmiany na GitHubie przed force push** - możesz stracić ważne dane
- **Skonfiguruj SSH** - wygodniejsze niż HTTPS z tokenem
