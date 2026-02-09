#!/usr/bin/env python3
"""
Quick launcher for Thymio Playground testing
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from widgets.thymio_playground import ThymioPlaygroundWindow

def main():
    app = QApplication(sys.argv)
    
    # Create and show the playground window
    playground = ThymioPlaygroundWindow()
    playground.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
