"""
Image Compare Tool - Main Entry Point
Created: 2026-03-07
Author: Byung Geun (BG) Jun

Launches the PyQt5-based Image Compare application.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from image_compare_app_pyqt5 import main

if __name__ == "__main__":
    main()
