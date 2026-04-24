"""
Image Analysis GUI Application
Created: 2026-03-07
Author: Byung Geun (BG) Jun

Main entry point for the Image Analysis GUI application.
"""

import sys
import os

# Add the project root directory to sys.path so that gui/core/utils modules can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Main function to run the Image Analysis GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Image Analysis GUI")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
