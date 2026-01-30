#!/bin/bash
# Skrypt do dodania remote GitHub i pushowania zmian

echo "🔗 Konfiguracja GitHub Remote"
echo ""

# Sprawdź czy remote już istnieje
if git remote get-url origin &>/dev/null; then
    echo "✅ Remote 'origin' już istnieje:"
    git remote -v
    echo ""
    read -p "Czy chcesz go zmienić? (t/n): " zmienic
    if [ "$zmienic" = "t" ] || [ "$zmienic" = "T" ]; then
        git remote remove origin
    else
        echo "Używam istniejącego remote."
        git push -u origin main
        exit 0
    fi
fi

echo "Podaj URL swojego repozytorium GitHub:"
echo "Przykłady:"
echo "  - HTTPS: https://github.com/twoja-nazwa/nazwa-repo.git"
echo "  - SSH:   git@github.com:twoja-nazwa/nazwa-repo.git"
echo ""
read -p "URL: " github_url

if [ -z "$github_url" ]; then
    echo "❌ URL nie może być pusty!"
    exit 1
fi

# Dodaj remote
echo ""
echo "📝 Dodaję remote..."
git remote add origin "$github_url"

# Sprawdź czy się udało
if [ $? -eq 0 ]; then
    echo "✅ Remote dodany pomyślnie!"
    echo ""
    git remote -v
    echo ""
    
    # Sprawdź branch
    current_branch=$(git branch --show-current)
    echo "🌿 Aktualny branch: $current_branch"
    echo ""
    
    # Zapytaj czy pushować
    read -p "Czy chcesz teraz wypchnąć zmiany na GitHub? (t/n): " pushowac
    if [ "$pushowac" = "t" ] || [ "$pushowac" = "T" ]; then
        echo ""
        echo "📤 Wypycham zmiany..."
        git push -u origin "$current_branch"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Sukces! Zmiany zostały wypchnięte na GitHub!"
        else
            echo ""
            echo "❌ Błąd podczas pushowania. Sprawdź:"
            echo "   1. Czy masz dostęp do repozytorium"
            echo "   2. Czy repozytorium istnieje na GitHubie"
            echo "   3. Czy masz poprawne uprawnienia"
        fi
    else
        echo ""
        echo "ℹ️  Remote został dodany. Możesz teraz użyć:"
        echo "   git push -u origin $current_branch"
    fi
else
    echo "❌ Błąd podczas dodawania remote!"
    exit 1
fi
