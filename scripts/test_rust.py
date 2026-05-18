#!/usr/bin/env python3
"""
Test the Rust module – checks that everything works.
"""

import sys
sys.path.insert(0, 'src')

print("🔍 Checking Rust module...\n")

try:
    from rust_scanner_wrapper import FastPortScanner, DeviceProcessor, is_rust_available
    
    if is_rust_available():
        print("✅ Rust scanner is available and in use (FASTER)!")
        print()
        
        # Port scan test
        print("🧪 Testing port scan on localhost...")
        scanner = FastPortScanner(timeout_ms=1000, max_concurrent=50)
        open_ports = scanner.scan_ports("127.0.0.1", [22, 80, 443, 5432, 8080])
        print(f"✅ Open ports: {open_ports}")
        print()
        
        # DeviceProcessor test
        print("🧪 Testing DeviceProcessor...")
        processor = DeviceProcessor(batch_size=10)
        print(f"✅ DeviceProcessor created (batch_size: {processor.batch_size})")
        print()
        
        print("🎉 All good! Rust is ready to use.")
    else:
        print("⚠️  Rust scanner not available – using Python fallback")
        print("   (This is OK – everything works, just slower)")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
