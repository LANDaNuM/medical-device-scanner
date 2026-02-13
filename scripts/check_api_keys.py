#!/usr/bin/env python3
"""
Verify API keys.
Checks that API keys are correctly configured and working.
"""

import os
import sys
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    project_dir = Path(__file__).parent.parent
    env_file = project_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded .env from: {env_file}")
    else:
        load_dotenv()
        print("⚠️  .env file not found – using system environment variables")
except ImportError:
    print("⚠️  python-dotenv not installed – using system environment variables")

print("\n" + "="*60)
print("🔍 API KEY VERIFICATION")
print("="*60 + "\n")

# Check VirusTotal
virustotal_key = os.getenv("VIRUSTOTAL_API_KEY")
if virustotal_key:
    print(f"✅ VIRUSTOTAL_API_KEY: {'*' * (len(virustotal_key) - 4) + virustotal_key[-4:]}")
    print("   Testing connection...")
    try:
        import requests
        headers = {"x-apikey": virustotal_key}
        response = requests.get(
            "https://www.virustotal.com/api/v3/ip_addresses/8.8.8.8",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            print("   ✅ Key works!")
        elif response.status_code == 401:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'Invalid API key')
            print(f"   ❌ ERROR: Invalid API key")
            print(f"   📝 Details: {error_msg}")
            print(f"   🔗 Get a new key: https://www.virustotal.com/gui/join-us")
        elif response.status_code == 403:
            print(f"   ❌ ERROR: No permission (key may be inactive)")
            print(f"   🔗 Check status: https://www.virustotal.com/gui/join-us")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Test error: {e}")
else:
    print("❌ VIRUSTOTAL_API_KEY: NOT SET")
    print("   🔗 Get key: https://www.virustotal.com/gui/join-us")

print()

# Check Shodan
shodan_key = os.getenv("SHODAN_API_KEY")
if shodan_key:
    print(f"✅ SHODAN_API_KEY: {'*' * (len(shodan_key) - 4) + shodan_key[-4:]}")
    print("   Testing connection...")
    try:
        import requests
        response = requests.get(
            "https://api.shodan.io/api-info",
            params={"key": shodan_key},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Key works!")
            print(f"   📊 Plan: {data.get('plan', 'unknown')}")
            print(f"   📊 Credits: {data.get('query_credits', 'unknown')}")
        elif response.status_code == 401:
            error_data = response.json()
            error_msg = error_data.get('error', 'Invalid API key')
            print(f"   ❌ ERROR: Invalid API key")
            print(f"   📝 Details: {error_msg}")
            print(f"   🔗 Get a new key: https://account.shodan.io/register")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Test error: {e}")
else:
    print("❌ SHODAN_API_KEY: NOT SET (optional)")
    print("   🔗 Get key: https://account.shodan.io/register")

print()

# Check NVD
nvd_key = os.getenv("NVD_API_KEY")
if nvd_key:
    print(f"✅ NVD_API_KEY: {'*' * (len(nvd_key) - 4) + nvd_key[-4:]}")
    print("   ✅ Key configured (NVD does not require a live test)")
else:
    print("❌ NVD_API_KEY: NOT SET (optional)")
    print("   🔗 Get key: https://nvd.nist.gov/developers/request-an-api-key")

print()

# Check Vulners
vulners_key = os.getenv("VULNERS_API_KEY")
if vulners_key:
    print(f"✅ VULNERS_API_KEY: {'*' * (len(vulners_key) - 4) + vulners_key[-4:]}")
    print("   ✅ Key configured")
else:
    print("❌ VULNERS_API_KEY: NOT SET (optional)")
    print("   🔗 Get key: https://vulners.com/register")

print("\n" + "="*60)
print("📝 INSTRUCTIONS:")
print("="*60)
print("1. If keys don't work, check they are correct in .env")
print("2. Copy .env.example to .env: cp .env.example .env")
print("3. Edit .env and paste your API keys")
print("4. Run this script again: python3 scripts/check_api_keys.py")
print("="*60)
