#!/usr/bin/env python3
"""
Skrypt do weryfikacji kluczy API.
Sprawdza czy klucze API są poprawnie skonfigurowane i działają.
"""

import os
import sys
from pathlib import Path

# Załaduj zmienne środowiskowe
try:
    from dotenv import load_dotenv
    project_dir = Path(__file__).parent
    env_file = project_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Załadowano plik .env z: {env_file}")
    else:
        load_dotenv()
        print("⚠️  Plik .env nie istnieje - używam zmiennych środowiskowych systemu")
except ImportError:
    print("⚠️  python-dotenv nie jest zainstalowany - używam zmiennych środowiskowych systemu")

print("\n" + "="*60)
print("🔍 WERYFIKACJA KLUCZY API")
print("="*60 + "\n")

# Sprawdź VirusTotal
virustotal_key = os.getenv("VIRUSTOTAL_API_KEY")
if virustotal_key:
    print(f"✅ VIRUSTOTAL_API_KEY: {'*' * (len(virustotal_key) - 4) + virustotal_key[-4:]}")
    print("   Testowanie połączenia...")
    try:
        import requests
        headers = {"x-apikey": virustotal_key}
        response = requests.get(
            "https://www.virustotal.com/api/v3/ip_addresses/8.8.8.8",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            print("   ✅ Klucz działa poprawnie!")
        elif response.status_code == 401:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Invalid API key')
            print(f"   ❌ BŁĄD: Nieprawidłowy klucz API")
            print(f"   📝 Szczegóły: {error_msg}")
            print(f"   🔗 Uzyskaj nowy klucz: https://www.virustotal.com/gui/join-us")
        elif response.status_code == 403:
            print(f"   ❌ BŁĄD: Brak uprawnień (klucz może być nieaktywny)")
            print(f"   🔗 Sprawdź status: https://www.virustotal.com/gui/join-us")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Błąd testowania: {e}")
else:
    print("❌ VIRUSTOTAL_API_KEY: NIE USTAWIONY")
    print("   🔗 Uzyskaj klucz: https://www.virustotal.com/gui/join-us")

print()

# Sprawdź Shodan
shodan_key = os.getenv("SHODAN_API_KEY")
if shodan_key:
    print(f"✅ SHODAN_API_KEY: {'*' * (len(shodan_key) - 4) + shodan_key[-4:]}")
    print("   Testowanie połączenia...")
    try:
        import requests
        response = requests.get(
            "https://api.shodan.io/api-info",
            params={"key": shodan_key},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Klucz działa poprawnie!")
            print(f"   📊 Plan: {data.get('plan', 'unknown')}")
            print(f"   📊 Limity: {data.get('query_credits', 'unknown')} kredytów")
        elif response.status_code == 401:
            error_data = response.json()
            error_msg = error_data.get('error', 'Invalid API key')
            print(f"   ❌ BŁĄD: Nieprawidłowy klucz API")
            print(f"   📝 Szczegóły: {error_msg}")
            print(f"   🔗 Uzyskaj nowy klucz: https://account.shodan.io/register")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Błąd testowania: {e}")
else:
    print("❌ SHODAN_API_KEY: NIE USTAWIONY (opcjonalne)")
    print("   🔗 Uzyskaj klucz: https://account.shodan.io/register")

print()

# Sprawdź NVD
nvd_key = os.getenv("NVD_API_KEY")
if nvd_key:
    print(f"✅ NVD_API_KEY: {'*' * (len(nvd_key) - 4) + nvd_key[-4:]}")
    print("   ✅ Klucz skonfigurowany (NVD nie wymaga testowania)")
else:
    print("❌ NVD_API_KEY: NIE USTAWIONY (opcjonalne)")
    print("   🔗 Uzyskaj klucz: https://nvd.nist.gov/developers/request-an-api-key")

print()

# Sprawdź Vulners
vulners_key = os.getenv("VULNERS_API_KEY")
if vulners_key:
    print(f"✅ VULNERS_API_KEY: {'*' * (len(vulners_key) - 4) + vulners_key[-4:]}")
    print("   ✅ Klucz skonfigurowany")
else:
    print("❌ VULNERS_API_KEY: NIE USTAWIONY (opcjonalne)")
    print("   🔗 Uzyskaj klucz: https://vulners.com/register")

print("\n" + "="*60)
print("📝 INSTRUKCJE:")
print("="*60)
print("1. Jeśli klucze nie działają, sprawdź czy są poprawne w pliku .env")
print("2. Skopiuj .env.example do .env: cp .env.example .env")
print("3. Edytuj .env i wklej swoje klucze API")
print("4. Uruchom ponownie ten skrypt: python3 check_api_keys.py")
print("="*60)
