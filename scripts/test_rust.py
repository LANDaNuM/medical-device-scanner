#!/usr/bin/env python3
"""
Test modułu Rust - sprawdza czy wszystko działa.
"""

import sys
sys.path.insert(0, 'src')

print("🔍 Sprawdzam moduł Rust...\n")

try:
    from rust_scanner_wrapper import FastPortScanner, DeviceProcessor, is_rust_available
    
    if is_rust_available():
        print("✅ Rust scanner jest dostępny i używany (SZYBSZE)!")
        print()
        
        # Test skanowania portów
        print("🧪 Test skanowania portów na localhost...")
        scanner = FastPortScanner(timeout_ms=1000, max_concurrent=50)
        open_ports = scanner.scan_ports("127.0.0.1", [22, 80, 443, 5432, 8080])
        print(f"✅ Otwarte porty: {open_ports}")
        print()
        
        # Test DeviceProcessor
        print("🧪 Test DeviceProcessor...")
        processor = DeviceProcessor(batch_size=10)
        print(f"✅ DeviceProcessor utworzony (batch_size: {processor.batch_size})")
        print()
        
        print("🎉 Wszystko działa! Rust jest gotowy do użycia.")
    else:
        print("⚠️  Rust scanner niedostępny - używam Python fallback")
        print("   (To jest OK - wszystko działa, tylko wolniej)")
        
except Exception as e:
    print(f"❌ Błąd: {e}")
    import traceback
    traceback.print_exc()
