#!/usr/bin/env python3
"""
Compile translation files (.ts -> .qm)
"""

import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
translations_dir = project_root / "translations"

# Find all .ts files
ts_files = list(translations_dir.glob("*.ts"))

if not ts_files:
    print("❌ No .ts files found in translations directory")
    sys.exit(1)

print(f"Found {len(ts_files)} translation file(s)")

for ts_file in ts_files:
    qm_file = ts_file.with_suffix('.qm')
    
    print(f"\nCompiling: {ts_file.name} -> {qm_file.name}")
    
    try:
        # Try lrelease
        result = subprocess.run(['lrelease', str(ts_file), '-qm', str(qm_file)], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Compiled successfully: {qm_file.name}")
        else:
            print(f"❌ Compilation failed: {result.stderr}")
    
    except FileNotFoundError:
        print("❌ lrelease not found. Please install Qt tools:")
        print("   Ubuntu/Debian: sudo apt-get install qttools5-dev-tools")
        print("   macOS: brew install qt6")
        print("   Windows: Install Qt from qt.io")
        sys.exit(1)

print("\n✅ All translations compiled!")
print("\nTo test:")
print("  1. Run PyGameMaker IDE")
print("  2. Go to Tools → Language → 🇫🇷 Français")
print("  3. Restart the IDE")